"""
Conexión a MongoDB para SmartStock RFID
"""
from pymongo import MongoClient
from config import MONGODB_URI, DATABASE_NAME, MONGODB_CONFIG

_client = None
_db = None


def get_db_connection():
    """
    Retorna la conexión a la base de datos MongoDB.
    Reutiliza la misma conexión para evitar múltiples clientes.
    """
    global _client, _db
    
    if _client is None:
        _client = MongoClient(MONGODB_URI, **MONGODB_CONFIG)
        _db = _client[DATABASE_NAME]
    
    return _db


def get_collection(collection_name):
    """
    Retorna una colección específica de MongoDB.
    
    Args:
        collection_name (str): Nombre de la colección
    
    Returns:
        Collection: Objeto de colección de MongoDB
    """
    db = get_db_connection()
    return db[collection_name]


def close_connection():
    """
    Cierra la conexión a MongoDB.
    """
    global _client
    if _client is not None:
        _client.close()
        _client = None