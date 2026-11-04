# 🌤️ Estación Meteorológica SIDD

Proyecto domótico para **Raspberry Pi 3B** desarrollado en **Python 3**. Mide temperatura, humedad ambiental y presión atmosférica utilizando sensores físicos, almacena el historial en una base de datos local **SQLite** y expone un panel de control interactivo mediante un servidor web **Flask** con automatización de hogar y advertencias meteorológicas en tiempo real.

---

## 🚀 Funcionalidades Actuales

*   **Monitoreo en Tiempo Real:** Lectura de temperatura, humedad y presión barométrica desde la Raspberry Pi.
*   **Automatización Domótica (Temp / Humedad):** 
    *   **Ventanas:** Se cierran automáticamente si la humedad supera el 80% (detección de lluvia ambiental).
    *   **Climatización:** Enciende el aire acondicionado en *Modo Frío* si la temperatura supera los 27°C, o en *Modo Calefacción* si desciende de los 18°C.
*   **Advertencias Barométricas Preventivas:** Monitoreo analítico de la presión atmosférica para emitir alertas tempranas en pantalla ante caídas bruscas (posible tormenta) o subidas repentinas (buen tiempo), sin alterar de forma forzosa los actuadores físicos.
*   **Panel Web Interactivo:** Interfaz visual con Flask para ver el estado de la casa, forzar lecturas manuales y renderizar gráficos estadísticos históricos con Matplotlib.

---

## 🛠️ Requisitos de Hardware

*   **Raspberry Pi 3 Model B** (con Raspberry Pi OS / Debian Bookworm instalado).
*   **Adaptador de pines T-Cobbler** para Protoboard (40 pines).
*   **Sensor DHT22** (Temperatura y Humedad - pin digital).
*   **Sensor BMP280** (Presión Atmosférica - bus I2C de 6 pines).
*   **Protoboard** + Cables Jumper Macho-Macho.
*   **1 Resistencia de 10kΩ** (solo si el DHT22 es el modelo suelto de 4 patas).

---

## 🔌 Esquema de Conexiones Físicas

> ⚠️ **IMPORTANTE:** Realizar todas las conexiones con la Raspberry Pi completamente apagada y desenchufada.

### Multiplicación de Voltaje (Líneas Laterales)
*   Llevá un cable desde el pin **3V3** del T-Cobbler a la **línea larga roja (+)** de la protoboard.
*   Llevá un cable desde un pin **GND** del T-Cobbler a la **línea larga azul (-)** de la protoboard.

### Sensor DHT22 (Pines Digitales)
*   **Pata 1 (VCC):** A la línea **roja (+)** de 3.3V.
*   **Pata 2 (DATA):** Al pin **GPIO 26** (`G26`) del T-Cobbler.
*   **Pata 4 (GND):** A la línea **azul (-)** de GND.
*   *Puente de resistencia:* Clavar la resistencia de **10kΩ** uniendo la Pata 1 y la Pata 2 en la protoboard (omitir si el DHT viene en plaquita de 3 pines).

### Sensor BMP280 (Protocolo I2C)
*   **VCC:** A la línea **roja (+)** de 3.3V.
*   **GND:** A la línea **azul (-)** de GND.
*   **SCL:** Al pin **SCL** (`GPIO3`) del T-Cobbler.
*   **SDA:** Al pin **SDA** (`GPIO2`) del T-Cobbler.
*   **CSB / CS:** A la línea **roja (+)** de 3.3V (fija el modo I2C).
*   **SDO:** Queda **completamente suelto** (asigna la dirección por defecto `0x76`).

---

## 🚀 Guía de Instalación del Software (Paso a Paso)

> ⚠️ **IMPORTANTE:** Asegurate de estar en tu directorio home ejecutando:
```bash
cd ~
```

Ahora si, abrí la terminal de la Raspberry Pi y ejecutá los siguientes comandos en orden:

### 1. Activar la interfaz de hardware I2C
```bash
sudo raspi-config
```
*(Ir a `Interface Options` -> `I2C` -> Seleccionar `<Yes>` -> Salir con `<Finish>`)*.

### 2. Actualizar el sistema e instalar dependencias básicas
```bash
sudo apt update
sudo apt install -y python3-pip i2c-tools python3-setuptools wget
```

### 3. Verificar que la Pi reconozca el sensor de presión
```bash
sudo i2cdetect -y 1
```
*(Deberías ver el número **76** o **77** reflejado en la grilla de la pantalla. Si no aparece, revisar el cableado del BMP280)*.

### 4. Compilar e instalar el motor de pines de bajo nivel (pigpiod)
Este motor es indispensable para que las lecturas del DHT22 sean 100% estables en Linux:
```bash
cd /tmp
rm -rf v79.tar.gz pigpio-79
wget https://github.com/joan2937/pigpio/archive/v79.tar.gz
tar zxf v79.tar.gz
cd pigpio-79
make
sudo make install
cd ~
```

### 5. Activar el servicio del motor en segundo plano
```bash
sudo bash -c 'cat > /etc/systemd/system/pigpiod.service << "EOF"
[Unit]
Description=Daemon to handle pigpio GPIO pins
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/pigpiod
ExecStop=/bin/systemctl kill pigpiod.service
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

### 6. Configurar el Entorno de Python (Elegir un método)

Debido a las políticas de seguridad de los sistemas operativos modernos de Raspberry Pi, tenés dos opciones para instalar los paquetes necesarios:

#### Opción A: Usando un Entorno Virtual (Recomendado y más limpio)
Creá un paraguas aislado para que las librerías de tu estación no entren en conflicto con el sistema global. Ejecutá esto parado dentro de la carpeta de tu proyecto:
```bash
# Crear el entorno virtual llamado 'env'
python3 -m venv env

# ACTIVAR el entorno (Tenés que ejecutar este comando siempre que abras una terminal nueva para usar el proyecto)
source env/bin/activate

# Instalar las librerías dentro del entorno activo
pip3 install flask matplotlib adafruit-circuitpython-bmp280 pigpio-dht --break-system-packages
```
*(Vas a notar un `(env)` a la izquierda de tu terminal indicando que estás adentro de forma segura)*.

#### Opción B: Forzar la instalación global (Método Directo)
Si preferís omitir el entorno virtual e instalar todo directamente en la raíz de tu Raspberry Pi, utilizá el flag de evasión:
```bash
pip3 install flask matplotlib adafruit-circuitpython-bmp280 pigpio-dht --break-system-packages
```

---

## 🏃‍♂️ Cómo arrancar el proyecto

Para iniciar el panel de control, asegurate de estar parado en la carpeta del proyecto (y con el entorno virtual activo si elegiste la Opción A) y ejecutá el archivo del servidor web:

```bash
python3 WebSIDD.py
```

### Acceso desde otros dispositivos (Celular / PC):
1. Averiguá la IP de tu placa ejecutando `hostname -I` en la Pi (ejemplo: `192.168.1.45`).
2. Abrí el navegador de tu celular conectado al mismo Wi-Fi e ingresá a: `http://TU_IP_LOCAL:5000` (ej: `http://192.168.1.45:5000`).

