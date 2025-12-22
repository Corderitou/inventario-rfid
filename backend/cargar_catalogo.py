import sqlite3

def cargar_todo_el_inventario():
    # Asegúrate de que el nombre del archivo coincida con el que usas en db.py
    conn = sqlite3.connect('database.db') 
    cursor = conn.cursor()

    # Formato: (codigo, nombre, categoria, especificaciones, uso_descripcion, unidad, stock_total)
    datos_a_insertar = [
        # CABLES
        ('CAB-001', 'Cable audio XLR-XLR 10 m', 'Cables', 'XLR macho/hembra, 10m', 'Micrófono / línea balanceada', 'ud', 25),
        ('CAB-002', 'Cable audio XLR-XLR 20 m', 'Cables', 'XLR macho/hembra, 20m', 'Micrófono escenario', 'ud', 15),
        ('CAB-003', 'Canon hembra a Plug 6,3 mm', 'Cables', 'XLR Hembra / Jack 6.3mm', 'Micrófono a consola', 'ud', 18),
        ('CAB-007', 'Cable HDMI 2.0 10 m', 'Cables', 'HDMI macho/macho, 10m', 'Video pantallas/proyectores', 'ud', 12),
        ('CAB-008', 'Manguera multipar 8 canales', 'Cables', 'Stagebox XLR Snake, 30m', 'Snake escenario', 'ud', 4),
        
        # ESTRUCTURAS
        ('ESTR-001', 'Tubo aluminio truss 1 m', 'Estructuras', 'Aluminio, 50mm, 1m', 'Tubo cilíndrico', 'ud', 50),
        ('ESTR-002', 'Tubo aluminio truss 2 m', 'Estructuras', 'Aluminio, 50mm, 2m', 'Tubo cilíndrico', 'ud', 40),
        ('ESTR-004', 'Base acero para truss', 'Estructuras', 'Acero, 50x50 cm', 'Base soporte para truss', 'ud', 12),
        ('ESTR-005', 'Abrazadera rápida 50 mm', 'Estructuras', 'Clamp Aluminio 50mm', 'Sujeción de equipos', 'ud', 60),
        
        # HERRAMIENTAS
        ('HERR-001', 'Juego llaves allen', 'Herramientas', 'Set métricas 4–10 mm', 'Mantenimiento técnico', 'set', 6),
        ('HERR-004', 'Tester de cables', 'Herramientas', 'Prueba XLR / Jack / RCA', 'Instrumento de prueba', 'ud', 5),
        
        # BOLAS DE ESPEJO
        ('BOLA-001', 'Bola de espejo 20 cm', 'Bolas de Espejo', 'Diámetro 20cm', 'Decoración', 'ud', 15),
        ('BOLA-004', 'Bola de espejo 50 cm', 'Bolas de Espejo', 'Diámetro 50cm, con refuerzo', 'Decoración profesional', 'ud', 3),
        
        # ACCESORIOS
        ('ACC-001', 'Cinta velcro sujeta cables', 'Accesorios', 'Largo 10m', 'Orden y amarre', 'ud', 12),
        ('ACC-002', 'Enrollador de cable', 'Accesorios', 'Capacidad 50m', 'Transporte cables largos', 'ud', 6)
    ]

    try:
        # INSERT OR REPLACE evita errores si vuelves a ejecutar el script
        cursor.executemany("""
            INSERT OR REPLACE INTO items (codigo, nombre, categoria, especificaciones, uso_descripcion, unidad, stock_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, datos_a_insertar)

        conn.commit()
        print(f"✅ ¡Éxito! Se han cargado {len(datos_a_insertar)} productos al catálogo.")
    except sqlite3.Error as e:
        print(f"❌ Error al cargar el catálogo: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cargar_todo_el_inventario()