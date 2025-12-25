"""
Script para cargar el catálogo de productos en MongoDB
"""
from db import get_collection
from config import COLLECTION_ITEMS

def cargar_todo_el_inventario():
    items_collection = get_collection(COLLECTION_ITEMS)
    
    # Datos del catálogo
    datos_a_insertar = [
        # CABLES
        {'codigo': 'CAB-001', 'nombre': 'Cable audio XLR-XLR 10 m', 'categoria': 'Cables', 
         'especificaciones': 'XLR macho/hembra, 10m', 'uso_descripcion': 'Micrófono / línea balanceada', 
         'unidad': 'ud', 'stock_total': 25},
        {'codigo': 'CAB-002', 'nombre': 'Cable audio XLR-XLR 20 m', 'categoria': 'Cables', 
         'especificaciones': 'XLR macho/hembra, 20m', 'uso_descripcion': 'Micrófono escenario', 
         'unidad': 'ud', 'stock_total': 15},
        {'codigo': 'CAB-003', 'nombre': 'Canon hembra a Plug 6,3 mm', 'categoria': 'Cables', 
         'especificaciones': 'XLR Hembra / Jack 6.3mm', 'uso_descripcion': 'Micrófono a consola', 
         'unidad': 'ud', 'stock_total': 18},
        {'codigo': 'CAB-007', 'nombre': 'Cable HDMI 2.0 10 m', 'categoria': 'Cables', 
         'especificaciones': 'HDMI macho/macho, 10m', 'uso_descripcion': 'Video pantallas/proyectores', 
         'unidad': 'ud', 'stock_total': 12},
        {'codigo': 'CAB-008', 'nombre': 'Manguera multipar 8 canales', 'categoria': 'Cables', 
         'especificaciones': 'Stagebox XLR Snake, 30m', 'uso_descripcion': 'Snake escenario', 
         'unidad': 'ud', 'stock_total': 4},
        
        # ESTRUCTURAS
        {'codigo': 'ESTR-001', 'nombre': 'Tubo aluminio truss 1 m', 'categoria': 'Estructuras', 
         'especificaciones': 'Aluminio, 50mm, 1m', 'uso_descripcion': 'Tubo cilíndrico', 
         'unidad': 'ud', 'stock_total': 50},
        {'codigo': 'ESTR-002', 'nombre': 'Tubo aluminio truss 2 m', 'categoria': 'Estructuras', 
         'especificaciones': 'Aluminio, 50mm, 2m', 'uso_descripcion': 'Tubo cilíndrico', 
         'unidad': 'ud', 'stock_total': 40},
        {'codigo': 'ESTR-004', 'nombre': 'Base acero para truss', 'categoria': 'Estructuras', 
         'especificaciones': 'Acero, 50x50 cm', 'uso_descripcion': 'Base soporte para truss', 
         'unidad': 'ud', 'stock_total': 12},
        {'codigo': 'ESTR-005', 'nombre': 'Abrazadera rápida 50 mm', 'categoria': 'Estructuras', 
         'especificaciones': 'Clamp Aluminio 50mm', 'uso_descripcion': 'Sujeción de equipos', 
         'unidad': 'ud', 'stock_total': 60},
        
        # HERRAMIENTAS
        {'codigo': 'HERR-001', 'nombre': 'Juego llaves allen', 'categoria': 'Herramientas', 
         'especificaciones': 'Set métricas 4–10 mm', 'uso_descripcion': 'Mantenimiento técnico', 
         'unidad': 'set', 'stock_total': 6},
        {'codigo': 'HERR-004', 'nombre': 'Tester de cables', 'categoria': 'Herramientas', 
         'especificaciones': 'Prueba XLR / Jack / RCA', 'uso_descripcion': 'Instrumento de prueba', 
         'unidad': 'ud', 'stock_total': 5},
        
        # BOLAS DE ESPEJO
        {'codigo': 'BOLA-001', 'nombre': 'Bola de espejo 20 cm', 'categoria': 'Bolas de Espejo', 
         'especificaciones': 'Diámetro 20cm', 'uso_descripcion': 'Decoración', 
         'unidad': 'ud', 'stock_total': 15},
        {'codigo': 'BOLA-004', 'nombre': 'Bola de espejo 50 cm', 'categoria': 'Bolas de Espejo', 
         'especificaciones': 'Diámetro 50cm, con refuerzo', 'uso_descripcion': 'Decoración profesional', 
         'unidad': 'ud', 'stock_total': 3},
        
        # ACCESORIOS
        {'codigo': 'ACC-001', 'nombre': 'Cinta velcro sujeta cables', 'categoria': 'Accesorios', 
         'especificaciones': 'Largo 10m', 'uso_descripcion': 'Orden y amarre', 
         'unidad': 'ud', 'stock_total': 12},
        {'codigo': 'ACC-002', 'nombre': 'Enrollador de cable', 'categoria': 'Accesorios', 
         'especificaciones': 'Capacidad 50m', 'uso_descripcion': 'Transporte cables largos', 
         'unidad': 'ud', 'stock_total': 6}
    ]
    
    try:
        # Insertar o actualizar cada producto (upsert)
        for item in datos_a_insertar:
            items_collection.update_one(
                {'codigo': item['codigo']},
                {'$set': item},
                upsert=True
            )
        
        print(f"✅ ¡Éxito! Se han cargado {len(datos_a_insertar)} productos al catálogo.")
    except Exception as e:
        print(f"❌ Error al cargar el catálogo: {e}")

if __name__ == "__main__":
    cargar_todo_el_inventario()