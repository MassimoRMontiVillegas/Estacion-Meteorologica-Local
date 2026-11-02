import sqlite3
import time
from datetime import datetime
import board
import adafruit_bmp280
from pigpio_dht import DHT22

# --- CONFIGURACIÓN ---
DB_NOMBRE = "clima_estacion.db"

# 1. Configuración del DHT22 (Pin Digital GPIO 26 con pigpio)
PIN_DHT_DIGITAL = 26
sensor_dht = DHT22(PIN_DHT_DIGITAL)

# 2. Configuración del BMP280 (Pines I2C de la Pi)
i2c = board.I2C()
sensor_bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)


def inicializar_base_datos():
    """Crea la base de datos y la tabla si no existen."""
    conexion = sqlite3.connect(DB_NOMBRE)
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lecturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            temperatura REAL,
            humedad REAL,
            presion REAL
        )
    ''')
    conexion.commit()
    conexion.close()


def guardar_lectura(temp, hum, pres):
    """Inserta la lectura completa en la base de datos."""
    conexion = sqlite3.connect(DB_NOMBRE)
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO lecturas (fecha_hora, temperatura, humedad, presion)
        VALUES (?, ?, ?, ?)
    ''', (fecha_actual, temp, hum, pres))

    conexion.commit()
    conexion.close()
    print(f"[{fecha_actual}] Guardado -> Temp: {temp}°C | Hum: {hum}% | Presión: {pres} hPa")


def registrar_clima():
    """Lee ambos sensores usando los motores más estables de hardware."""
    temperatura = None
    humedad = None
    presion = None

    # 1. Intentamos leer el BMP280 (Presión Atmosférica)
    try:
        presion = sensor_bmp.pressure
        temperatura = sensor_bmp.temperature  # Temperatura de respaldo
    except Exception as error:
        print(f"Aviso BMP280: {error}")

    # 2. Intentamos leer el DHT22 nuevo con pigpio
    try:
        resultado = sensor_dht.read()
        if resultado['valid']:
            # El DHT22 es más exacto para temp ambiente que la interna del BMP
            temperatura = resultado['temperature']
            humedad = resultado['humidity']
        else:
            print("Aviso DHT22: Lectura inválida de datos en este turno.")
    except Exception as error:
        print(f"Aviso DHT22: Error de comunicación ({error})")

    # Guardamos los datos si logramos rescatar algo válido
    if temperatura is not None or humedad is not None or presion is not None:
        temp_g = round(temperatura, 1) if temperatura is not None else None
        hum_g = round(humedad, 1) if humedad is not None else None
        pres_g = round(presion, 1) if presion is not None else None
        
        guardar_lectura(temp_g, hum_g, pres_g)
    else:
        print("Error: No se pudo obtener ninguna lectura en este turno.")


# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print("Iniciando Estación Meteorológica SIDD...")
    inicializar_base_datos()

    try:
        while True:
            registrar_clima()
            # Cambiar a 900.0 (15 min) cuando el proyecto quede fijo
            time.sleep(5.0) 
    except KeyboardInterrupt:
        print("\nEstación SIDD detenida por el usuario.")
