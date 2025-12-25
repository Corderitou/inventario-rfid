from flask import Flask, jsonify, request, render_template
from db import get_collection
from config import COLLECTION_ITEMS, COLLECTION_ITEMS_RFID, COLLECTION_MOVIMIENTOS
from flask_cors import CORS
from datetime import datetime
import os


base_dir = os.path.dirname(os.path.abspath(__file__))

# Configuramos Flask para buscar 1 nivel arriba y entrar a 'frontend'
app = Flask(__name__, 
            template_folder=os.path.join(base_dir, "../frontend/templates"),
            static_folder=os.path.join(base_dir, "../frontend"))
CORS(app)



@app.route("/")
def index():
    # Login landing page
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    # Dashboard page
    return render_template("dashboard.html")

@app.route("/registro")
def registro_page():
    # Asegúrate de que el nombre del archivo coincida con el que tienes en /templates
    return render_template("crear_item.html")


@app.route("/movimientos_page")
def movimientos_page():
    return render_template("movimientos.html")

@app.route("/items_page")
def items_page():
    return render_template("items.html")

@app.route("/scanner")
def scanner_page():
    return render_template("scanner.html")

@app.route("/rfid", methods=["POST"])
def rfid():
    data = request.json
    uid = data.get("uid")
    accion = data.get("accion")
    if accion not in ["entrada", "salida"]:
        return jsonify({"error": "Acción inválida"}), 400

    if not uid or not accion:
        return jsonify({"error": "Faltan datos"}), 400

    items_rfid_collection = get_collection(COLLECTION_ITEMS_RFID)
    movimientos_collection = get_collection(COLLECTION_MOVIMIENTOS)

    # Buscar el ítem por UID
    item = items_rfid_collection.find_one({"uid_rfid": uid})

    # Determinar estado según acción
    estado_actual = "disponible" if accion == "entrada" else "prestado"

    if item is None:
        # RFID nuevo
        items_rfid_collection.insert_one({
            "uid_rfid": uid,
            "estado": estado_actual
        })
    else:
        # RFID existente
        items_rfid_collection.update_one(
            {"uid_rfid": uid},
            {"$set": {"estado": estado_actual}}
        )

    # Registrar SIEMPRE el movimiento
    movimientos_collection.insert_one({
        "uid_rfid": uid,
        "accion": accion,
        "fecha": datetime.utcnow()
    })

    return jsonify({
        "uid": uid,
        "estado": estado_actual
    })


@app.route("/items", methods=["GET"])
def get_items():
    items_rfid_collection = get_collection(COLLECTION_ITEMS_RFID)
    
    items = list(items_rfid_collection.find({}, {"_id": 0}))
    
    return jsonify(items)

@app.route("/movimientos", methods=["GET"])
def get_movimientos():
    uid = request.args.get("uid")
    accion = request.args.get("accion")
    
    movimientos_collection = get_collection(COLLECTION_MOVIMIENTOS)

    acciones_validas = ["entrada", "salida"]
    filtro = {}

    if uid:
        filtro["uid_rfid"] = uid

    if accion:
        if accion not in acciones_validas:
            return jsonify({
                "error": "Acción inválida. Use 'entrada' o 'salida'"
            }), 400
        filtro["accion"] = accion

    # Buscar con filtro y ordenar por fecha descendente
    movimientos_cursor = movimientos_collection.find(
        filtro, 
        {"_id": 0}
    ).sort("fecha", -1)

    movimientos = []
    for mov in movimientos_cursor:
        movimientos.append({
            "uid": mov["uid_rfid"],
            "accion": mov["accion"],
            "fecha": mov["fecha"].isoformat() if isinstance(mov["fecha"], datetime) else str(mov["fecha"])
        })

    return jsonify(movimientos), 200

@app.route("/inventario/items", methods=["GET"])
def inventario_items():
    items_rfid_collection = get_collection(COLLECTION_ITEMS_RFID)
    
    # Usar agregación con $lookup para simular JOIN
    pipeline = [
        {
            "$lookup": {
                "from": COLLECTION_ITEMS,
                "localField": "id_referencia_codigo",
                "foreignField": "codigo",
                "as": "item_info"
            }
        },
        {
            "$unwind": {
                "path": "$item_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "uid": "$uid_rfid",
                "nombre": {"$ifNull": ["$item_info.nombre", "Sin registrar"]},
                "categoria": "$item_info.categoria",
                "especificaciones": "$item_info.especificaciones",
                "estado": "$estado"
            }
        }
    ]
    
    items = list(items_rfid_collection.aggregate(pipeline))
    return jsonify(items), 200


@app.route("/inventario/resumen", methods=["GET"])
def inventario_resumen():
    items_rfid_collection = get_collection(COLLECTION_ITEMS_RFID)

    # Usar agregación para contar por estado
    pipeline = [
        {
            "$group": {
                "_id": "$estado",
                "cantidad": {"$sum": 1}
            }
        }
    ]
    
    resultado = list(items_rfid_collection.aggregate(pipeline))
    
    # Convertir a formato {estado: cantidad}
    inventario = {item["_id"]: item["cantidad"] for item in resultado}

    return jsonify(inventario), 200

@app.route("/items", methods=["POST"])
def crear_item():
    data = request.json
    uid = data.get("uid")
    # Este 'codigo_referencia' debe ser uno de los códigos (CAB-001, ESTR-001, etc.)
    codigo_ref = data.get("codigo_referencia") 

    if not uid or not codigo_ref:
        return jsonify({"error": "Faltan datos (UID o Código de Referencia)"}), 400

    items_collection = get_collection(COLLECTION_ITEMS)
    items_rfid_collection = get_collection(COLLECTION_ITEMS_RFID)
    movimientos_collection = get_collection(COLLECTION_MOVIMIENTOS)

    try:
        # Verificar que el código de referencia existe en el catálogo
        if not items_collection.find_one({"codigo": codigo_ref}):
            return jsonify({"error": f"El código {codigo_ref} no existe en el catálogo"}), 400

        # 1. Insertar el ítem físico vinculado al catálogo
        items_rfid_collection.insert_one({
            "uid_rfid": uid,
            "id_referencia_codigo": codigo_ref,
            "estado": "disponible"
        })

        # 2. Registrar el movimiento inicial
        movimientos_collection.insert_one({
            "uid_rfid": uid,
            "accion": "entrada",
            "fecha": datetime.utcnow()
        })

        return jsonify({"Mensaje": f"Item {uid} creado exitosamente vinculado a {codigo_ref}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/items/<uid>", methods=["DELETE"])
def eliminar_item(uid):
    items_rfid_collection = get_collection(COLLECTION_ITEMS_RFID)
    movimientos_collection = get_collection(COLLECTION_MOVIMIENTOS)
    
    try:
        # Primero eliminamos sus movimientos (por integridad de base de datos)
        movimientos_collection.delete_many({"uid_rfid": uid})
        
        # Luego eliminamos el ítem
        result = items_rfid_collection.delete_one({"uid_rfid": uid})
        
        if result.deleted_count == 0:
            return jsonify({"error": "No se encontró el ítem"}), 404
            
        return jsonify({"mensaje": "Item eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/items/<uid>", methods=["PUT"])
def editar_item(uid):
    data = request.get_json()
    # Ahora editamos la referencia al catálogo, no el nombre directamente
    nuevo_codigo_ref = data.get('codigo_referencia')
    nuevo_estado = data.get('estado')

    items_rfid_collection = get_collection(COLLECTION_ITEMS_RFID)

    try:
        update_fields = {}
        if nuevo_codigo_ref:
            update_fields["id_referencia_codigo"] = nuevo_codigo_ref
        if nuevo_estado:
            update_fields["estado"] = nuevo_estado
            
        if not update_fields:
            return jsonify({"error": "No hay campos para actualizar"}), 400
        
        result = items_rfid_collection.update_one(
            {"uid_rfid": uid},
            {"$set": update_fields}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "No se encontró el ítem"}), 404
            
        return jsonify({"mensaje": "Cambios guardados correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/catalogo", methods=["GET"])
def get_catalogo():
    items_collection = get_collection(COLLECTION_ITEMS)
    
    catalogo = list(items_collection.find(
        {},
        {"_id": 0, "codigo": 1, "nombre": 1, "categoria": 1}
    ))
    
    return jsonify(catalogo), 200       

if __name__ == "__main__":
    app.run(debug=True)
