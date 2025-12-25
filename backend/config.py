"""
Configuración de MongoDB para SmartStock RFID
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de MongoDB Atlas
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "smartstock_rfid")

# Configuración de conexión
MONGODB_CONFIG = {
    "serverSelectionTimeoutMS": 5000,
    "connectTimeoutMS": 10000,
}

# Nombres de colecciones
COLLECTION_ITEMS = "items"
COLLECTION_ITEMS_RFID = "items_rfid"
COLLECTION_MOVIMIENTOS = "movimientos"
