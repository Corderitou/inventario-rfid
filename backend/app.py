from flask import Flask, jsonify, request, render_template
from db import get_db_connection
from flask_cors import CORS
import os


base_dir = os.path.dirname(os.path.abspath(__file__))

# Configuramos Flask para buscar 1 nivel arriba y entrar a 'frontend'
app = Flask(__name__, 
            template_folder=os.path.join(base_dir, "../frontend/templates"),
            static_folder=os.path.join(base_dir, "../frontend"))
CORS(app)



@app.route("/")
def index():
    # Esto busca el archivo en la carpeta /templates/
    return render_template("dashboard.html")

@app.route("/registro")
def registro_page():
    # Asegúrate de que el nombre del archivo coincida con el que tienes en /templates
    return render_template("crear_item.html")


@app.route("/movimientos_page")
def movimientos_page():
    return render_template("movimientos.html")

@app.route("/rfid", methods=["POST"])
def rfid():
    data = request.json
    uid = data.get("uid")
    accion = data.get("accion")
    if accion not in ["entrada", "salida"]:
        return jsonify({"error": "Acción inválida"}), 400

    if not uid or not accion:
        return jsonify({"error": "Faltan datos"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM items_rfid WHERE uid_rfid = ?", (uid,)
    )
    item = cursor.fetchone()

    # Determinar estado según acción
    estado_actual = "disponible" if accion == "entrada" else "prestado"

    if item is None:
        # RFID nuevo
        cursor.execute("""
            INSERT INTO items_rfid (uid_rfid, estado)
            VALUES (?, ?)
        """, (uid, estado_actual))
    else:
        # RFID existente
        cursor.execute("""
            UPDATE items_rfid
            SET estado = ?
            WHERE uid_rfid = ?
        """, (estado_actual, uid))

    # Registrar SIEMPRE el movimiento
    cursor.execute("""
        INSERT INTO movimientos (uid_rfid, accion)
        VALUES (?, ?)
    """, (uid, accion))

    conn.commit()
    conn.close()

    return jsonify({
        "uid": uid,
        "estado": estado_actual
    })


@app.route("/items", methods=["GET"])
def get_items():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items_rfid")
    items = cursor.fetchall()
    conn.close()

    items_list = [dict(item) for item in items]

    return jsonify(items_list)

@app.route("/movimientos", methods=["GET"])
def get_movimientos():
    uid = request.args.get("uid")
    accion = request.args.get("accion")
    conn = get_db_connection()
    cursor = conn.cursor()

    acciones_validas = ["entrada", "salida"]
    query = """
        SELECT uid_rfid, accion, fecha
        FROM movimientos
        WHERE 1=1
    """
    params = []

    if uid:
        query += " AND uid_rfid = ?"
        params.append(uid)

    if accion:
        if accion not in acciones_validas:
            return jsonify({
                "error": "Acción inválida. Use 'entrada' o 'salida'"
            }), 400
        query += " AND accion = ?"
        params.append(accion)

    query += " ORDER BY fecha DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    movimientos = []
    for row in rows:
        movimientos.append({
            "uid": row["uid_rfid"],
            "accion": row["accion"],
            "fecha": row["fecha"]
        })

    return jsonify(movimientos), 200

@app.route("/inventario/items", methods=["GET"])
def inventario_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT r.uid_rfid, i.nombre, i.categoria, i.especificaciones, r.estado 
        FROM items_rfid r
        LEFT JOIN items i ON r.id_referencia_codigo = i.codigo
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append({
            "uid": row["uid_rfid"],
            "nombre": row["nombre"] if row["nombre"] else "Sin registrar",
            "categoria": row["categoria"],
            "especificaciones": row["especificaciones"],
            "estado": row["estado"]
        })
    return jsonify(items), 200


@app.route("/inventario/resumen", methods=["GET"])
def inventario_resumen():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT estado, COUNT(*) as cantidad
        FROM items_rfid
        GROUP BY estado
    """)
    rows = cursor.fetchall()
    conn.close()

    inventario = {row["estado"]: row["cantidad"] for row in rows}

    return jsonify(inventario), 200

@app.route("/items", methods=["POST"])
def crear_item():
    data = request.json
    uid = data.get("uid")
    # Este 'codigo_referencia' debe ser uno de los códigos (CAB-001, ESTR-001, etc.)
    codigo_ref = data.get("codigo_referencia") 

    if not uid or not codigo_ref:
        return jsonify({"error": "Faltan datos (UID o Código de Referencia)"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Insertar el ítem físico vinculado al catálogo
        cursor.execute("""
            INSERT INTO items_rfid (uid_rfid, id_referencia_codigo, estado)
            VALUES (?, ?, ?)
        """, (uid, codigo_ref, "disponible"))

        # 2. Registrar el movimiento inicial
        cursor.execute("""
            INSERT INTO movimientos (uid_rfid, accion)
            VALUES (?, ?)
        """, (uid, "entrada"))

        conn.commit()
        return jsonify({"Mensaje": f"Item {uid} creado exitosamente vinculado a {codigo_ref}"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/items/<uid>", methods=["DELETE"])
def eliminar_item(uid):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Primero eliminamos sus movimientos (por integridad de base de datos)
        cursor.execute("DELETE FROM movimientos WHERE uid_rfid = ?", (uid,))
        # Luego eliminamos el ítem
        cursor.execute("DELETE FROM items_rfid WHERE uid_rfid = ?", (uid,))
        conn.commit()
        return jsonify({"mensaje": "Item eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/items/<uid>", methods=["PUT"])
def editar_item(uid):
    data = request.get_json()
    # Ahora editamos la referencia al catálogo, no el nombre directamente
    nuevo_codigo_ref = data.get('codigo_referencia')
    nuevo_estado = data.get('estado')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE items_rfid 
            SET id_referencia_codigo = ?, estado = ?
            WHERE uid_rfid = ?
        """, (nuevo_codigo_ref, nuevo_estado, uid))
        
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "No se encontró el ítem"}), 404
            
        return jsonify({"mensaje": "Cambios guardados correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/catalogo", methods=["GET"])
def get_catalogo():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, categoria FROM items")
        rows = cursor.fetchall()
        conn.close()
        
        catalogo = [dict(row) for row in rows]
        return jsonify(catalogo), 200       

if __name__ == "__main__":
    app.run(debug=True)
