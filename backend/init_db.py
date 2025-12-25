"""
Inicialización de la base de datos MongoDB
Crea índices únicos y configuraciones necesarias
"""
from db import get_collection
from config import COLLECTION_ITEMS, COLLECTION_ITEMS_RFID, COLLECTION_MOVIMIENTOS
from pymongo import ASCENDING, DESCENDING

print("🔧 Inicializando base de datos MongoDB...")

# Colección: items (catálogo de productos)
items_collection = get_collection(COLLECTION_ITEMS)
items_collection.create_index([("codigo", ASCENDING)], unique=True)
print(f"✅ Índice único creado en {COLLECTION_ITEMS}.codigo")

# Colección: items_rfid (ítems físicos con tags RFID)
items_rfid_collection = get_collection(COLLECTION_ITEMS_RFID)
items_rfid_collection.create_index([("uid_rfid", ASCENDING)], unique=True)
items_rfid_collection.create_index([("estado", ASCENDING)])
items_rfid_collection.create_index([("id_referencia_codigo", ASCENDING)])
print(f"✅ Índices creados en {COLLECTION_ITEMS_RFID}")

# Colección: movimientos (historial de entrada/salida)
movimientos_collection = get_collection(COLLECTION_MOVIMIENTOS)
movimientos_collection.create_index([("uid_rfid", ASCENDING)])
movimientos_collection.create_index([("accion", ASCENDING)])
movimientos_collection.create_index([("fecha", DESCENDING)])
print(f"✅ Índices creados en {COLLECTION_MOVIMIENTOS}")

print("✨ Base de datos MongoDB inicializada correctamente.")
