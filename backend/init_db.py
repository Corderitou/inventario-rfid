from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Dentro de init_db.py
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
                id_item INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nombre TEXT,
                categoria TEXT,
                especificaciones TEXT,    -- <--- Esta es la que te falta
                uso_descripcion TEXT,     -- <--- Y estas también
                unidad TEXT,
                stock_total INTEGER
);
""")



cursor.execute( """
CREATE TABLE IF NOT EXISTS items_rfid (
               id_item INTEGER PRIMARY KEY AUTOINCREMENT,
               uid_rfid TEXT UNIQUE,
               id_referencia_codigo TEXT,
               estado TEXT DEFAULT 'disponible',
               FOREIGN KEY (id_referencia_codigo) REFERENCES items(codigo)
);
""" )


cursor.execute( """
CREATE TABLE IF NOT EXISTS movimientos (
               id_mov INTEGER PRIMARY KEY AUTOINCREMENT,
               uid_rfid TEXT,
               accion TEXT,
               fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""" ) 

conn.commit()
conn.close()

print("Base de datos inicializada correctamente.")
