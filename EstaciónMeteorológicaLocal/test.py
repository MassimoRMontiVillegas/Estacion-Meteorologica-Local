import time
import board
import adafruit_bmp280
from pigpio_dht import DHT22  # <-- La librería estable que usa el motor pigpio

# Configuración del pin físico elegido para el DHT22
PIN_DHT = 26 

print("=============================================")
print("   🧪 SCRIPT DE PRUEBA HÍBRIDO - WebSIDD    ")
print("=============================================\n")

# 1. Inicialización del hardware
try:
    print("[⚙️] Conectando con el motor pigpio (DHT22)...")
    sensor_dht = DHT22(PIN_DHT)
    
    print("[⚙️] Conectando con el bus I2C (BMP280)...")
    i2c = board.I2C()
    sensor_bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
    print("[✅] Hardware inicializado con éxito.\n")
except Exception as e:
    print(f"[❌] Error crítico al iniciar los componentes: {e}")
    print("Mapeo rápido de fallas:")
    print("- Si falló pigpio: ejecutá 'sudo systemctl start pigpiod'")
    print("- Si falló el BMP280: revisá cables SDA/SCL o probá address=0x77")
    exit()

print("Leyendo datos estables... (Presioná Ctrl+C para finalizar)\n")
print("-" * 50)

# 2. Bucle infinito de lectura en tiempo real
try:
    while True:
        # --- Lectura del BMP280 ---
        try:
            temp_bmp = sensor_bmp.temperature
            presion = sensor_bmp.pressure
            print(f"[BMP280] -> Temperatura: {round(temp_bmp, 1)}°C | Presión: {round(presion, 1)} hPa")
        except Exception as e:
            print(f"[BMP280] -> ❌ Error al leer el sensor de presión: {e}")

        # --- Lectura del DHT22 ---
        try:
            resultado = sensor_dht.read()
            if resultado['valid']:
                print(f"[DHT22]  -> Temperatura: {resultado['temperature']}°C | Humedad: {resultado['humidity']}%")
            else:
                print("[DHT22]  -> ⚠️ Lectura inválida (el sensor devolvió datos corruptos o vacíos)")
        except Exception as e:
            print(f"[DHT22]  -> ❌ Error de comunicación: {e}")

        print("-" * 50)
        time.sleep(3.0)  # Pausa de 3 segundos entre testeos

except KeyboardInterrupt:
    print("\n[🛑] Prueba finalizada por el usuario.")
