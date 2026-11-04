import sqlite3
import time
from datetime import datetime
import board
import adafruit_bmp280
from pigpio_dht import DHT22

# --- CONFIGURACIÓN ---
DB_NOMBRE = "clima_estacion.db"

PIN_DHT_DIGITAL = 26
sensor_dht = DHT22(PIN_DHT_DIGITAL)

i2c = board.I2C()
sensor_bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)


def inicializar_base_datos():
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


def obtener_presion_anterior():
    """Obtiene la presión del registro anterior para calcular la tendencia."""
    conexion = sqlite3.connect(DB_NOMBRE)
    cursor = conexion.cursor()
    cursor.execute("SELECT presion FROM lecturas ORDER BY id DESC LIMIT 1")
    fila = cursor.fetchone()
    conexion.close()
    return fila[0] if fila and fila[0] is not None else None


def evaluar_acciones_casa(temp, hum, pres):
    """Acciones basadas en Temp/Hum, y Advertencias informativas basadas en Presión."""
    
    # 1. Acciones de la casa (Solo responden a Temperatura y Humedad)
    ventanas = "Abiertas 🪟"
    aire = "Apagado ⚪"

    if hum is not None and hum > 80.0:
        ventanas = "Cerradas (¡Lluvia por Humedad!) 🌧️"

    if temp is not None:
        if temp > 27.0:
            aire = "Encendido en Modo Frío ❄️"
        elif temp < 18.0:
            aire = "Encendido en Modo Calefacción ☀️"

    # 2. Advertencias preventivas (Solo evalúan la Presión, sin cambiar actuadores)
    alerta_presion = "Estable (Sin avisos) 🌤️"
    if pres is not None:
        presion_ant = obtener_presion_anterior()
        if presion_ant is not None:
            diferencia = pres - presion_ant
            if diferencia < -3.0:
                alerta_presion = "¡Aviso! Caída brusca de presión (Tormenta en camino) ⚡"
            elif diferencia > 3.0:
                alerta_presion = "Aviso: Presión en alza (Buen tiempo) ☀️"

    return {
        "ventanas": ventanas,
        "aire": aire,
        "alerta_presion": alerta_presion
    }


def guardar_lectura(temp, hum, pres):
    conexion = sqlite3.connect(DB_NOMBRE)
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    acciones = evaluar_acciones_casa(temp, hum, pres)

    cursor.execute('''
        INSERT INTO lecturas (fecha_hora, temperatura, humedad, presion)
        VALUES (?, ?, ?, ?)
    ''', (fecha_actual, temp, hum, pres))

    conexion.commit()
    conexion.close()
    
    print(f"[{fecha_actual}] Temp: {temp}°C | Hum: {hum}% | Presión: {pres} hPa")
    print(f" -> Casa: Ventanas [{acciones['ventanas']}] | Aire [{acciones['aire']}]")
    print(f" -> Barómetro (Advertencia): [{acciones['alerta_presion']}]")


def registrar_clima():
    temperatura = None
    humedad = None
    presion = None

    try:
        presion = sensor_bmp.pressure
        temperatura = sensor_bmp.temperature
    except Exception as error:
        print(f"Aviso BMP280: {error}")

    try:
        resultado = sensor_dht.read()
        if resultado['valid']:
            temperatura = resultado['temperature']
            humedad = resultado['humidity']
        else:
            print("Aviso DHT22: Lectura inválida.")
    except Exception as error:
        print(f"Aviso DHT22: Error ({error})")

    if temperatura is not None or humedad is not None or presion is not None:
        temp_g = round(temperatura, 1) if temperatura is not None else None
        hum_g = round(humedad, 1) if humedad is not None else None
        pres_g = round(presion, 1) if presion is not None else None
        
        guardar_lectura(temp_g, hum_g, pres_g)
    else:
        print("Error: No se pudo obtener ninguna lectura.")


if __name__ == "__main__":
    print("Iniciando Estación Meteorológica SIDD...")
    inicializar_base_datos()

    try:
        while True:
            registrar_clima()
            time.sleep(5.0) 
    except KeyboardInterrupt:
        print("\nEstación SIDD detenida por el usuario.")