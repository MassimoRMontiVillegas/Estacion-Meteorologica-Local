import time
import board
import adafruit_dht
import adafruit_bmp280

print("--- Iniciando prueba de sensores SIDD ---")

# Configuración de los sensores
try:
    sensor_dht = adafruit_dht.DHT22(board.D26)
    i2c = board.I2C()
    # Si te da error de comunicación, probá cambiando 0x76 por 0x77
    sensor_bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
except Exception as e:
    print(f"❌ Error al inicializar el hardware: {e}")
    exit()

print("Leyendo datos... (Presioná Ctrl+C para salir)\n")

try:
    while True:
        # 🌦️ Lectura del DHT22
        try:
            temp_dht = sensor_dht.temperature
            hum_dht = sensor_dht.humidity
            print(f"[DHT22]  Temperatura: {temp_dht}°C | Humedad: {hum_dht}%")
        except RuntimeError as e:
            # Los DHT22 a veces fallan una lectura, es normal. Seguimos de largo.
            print(f"[DHT22]  Aviso de lectura: {e.args[0]}")

        # 🎈 Lectura del BMP280
        try:
            temp_bmp = sensor_bmp.temperature
            presion = sensor_bmp.pressure
            print(f"[BMP280] Temperatura: {round(temp_bmp, 1)}°C | Presión: {round(presion, 1)} hPa")
        except Exception as e:
            print(f"[BMP280] Error: {e}")

        print("-" * 50)
        time.sleep(3)  # Espera 3 segundos antes de la próxima lectura

except KeyboardInterrupt:
    print("\nPrueba finalizada por el usuario.")
    sensor_dht.exit()
