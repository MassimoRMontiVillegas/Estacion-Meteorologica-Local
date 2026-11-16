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

*   **Raspberry Pi 3 Model B**.
*   **Tarjeta MicroSD de 16gb o más**.
*   **Computadora con lector de Tarjetas MicroSD**.
*   **Conexión a Internet**.
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

### Primero, vamos a instalar el Sistema Operativo en la Raspberry Pi 3B

#### 1. Descargá e instalá **Raspberry Pi Imager** en tu computadora desde la [página oficial de Raspberry Pi](https://raspberrypi.com).
#### 2. Insertá la tarjeta microSD en tu computadora.
#### 3. Abrí **Raspberry Pi Imager** y completá las tres opciones principales:
      * **Dispositivo (Device):** Elegí *Raspberry Pi 3B*.
      * **Sistema Operativo (OS):** Seleccioná *Debian Trixie*.
      * **Almacenamiento (Storage):** Seleccioná tu tarjeta microSD. *(Atención: se borrarán todos los datos de la tarjeta).*
#### 4. Hacé clic en **Siguiente (Next)**. Cuando te pregunte si querés aplicar ajustes personalizados, elegí **Editar ajustes          
      (Edit Settings)** para preconfigurar:
         * Nombre de usuario y contraseña.
         * Red Wi-Fi (nombre y clave).
         * Activar **SSH** en la pestaña *Servicios* (muy útil para conectarte de forma remota sin monitor).
#### 5. Guardá los cambios, confirmá la escritura y esperá a que termine el proceso de grabado y verificación.
#### 6. Retirá la microSD de forma segura, insertala en la Raspberry Pi y conectala a la corriente para encenderla.

Ahora si, abrí la terminal de la Raspberry Pi y ejecutá los siguientes comandos en orden:

> ⚠️ **IMPORTANTE:** Asegurate de estar en tu directorio home ejecutando:
```bash
cd ~
```

### 1. Clonar el repositorio para instalar los archivos del proyecto:
   ```bash
   git clone https://github.com/MassimoRMontiVillegas/Estacion-Meteorologica-Local.git
   ```

### 2. Activar la interfaz de hardware I2C
```bash
sudo raspi-config
```
*(Ir a `Interface Options` -> `I2C` -> Seleccionar `<Yes>` -> Salir con `<Finish>`)*.

### 3. Actualizar el sistema e instalar dependencias básicas
```bash
sudo apt update
sudo apt install -y python3-pip i2c-tools python3-setuptools wget
```

### 4. Verificar que la Pi reconozca el sensor de presión
```bash
sudo i2cdetect -y 1
```
*(Deberías ver el número **76** o **77** reflejado en la grilla de la pantalla. Si no aparece, revisar el cableado del BMP280)*.

### 5. Compilar e instalar el motor de pines de bajo nivel (pigpiod)
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

### 6. Activar el servicio del motor en segundo plano
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

### 7. Configurar el Entorno de Python (Elegir un método)

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

## Documentación del proyecto:

Día 1: Comenzamos definiendo que proyecto debíamos concretar, cómo íbamos a integrar el uso de la Raspberry Pi, qué resultados nos debía dar, cómo se debía ver, qué objetos y componentes debíamos conseguir, etc. Al final decidimos hacer una estación meteorológica, que detecte temperatura y humedad a través de la RasPi.

Día 2: Realizamos un esquema de boceto para las conexiones y arrancamos a escribir el código. Sumado a esto, el profesor nos pidió que sumemos al proyecto una pagina web donde estén visibles los datos que nos daría la RasPi. Llegando al final del día, reunimos los componentes para la RasPi, conectamos todo a la protoboard y realizamos un script básico de comprobación de funcionamiento de componentes, aunque no lo pudimos usar debido a que finalizo el dia de taller. 

Día 3: En el tercer dia, comenzamos con el código, y gracias a la determinación de nuestro compañero Massimo Ricardo Monti Villegas, logramos finalizar el código ese mismo dia. Sin embargo, aquí comenzó el primer problema, el sensor BMP280 no era detectado por el bus I2C de la Raspberry Pi, lo terminamos solucionando configurando sus opciones de interfase.

Día 4: Luego de volver a conectar todo, nos dimos cuenta que faltaba un componente (el cual fue encontrado roto en su caja), por lo que se perdió parte del dia buscando un reemplazo. Al conseguirlo, el segundo problema comenzó con el sensor DHT22, que señalizaba un error de "Check Wiring" pero todos los cables eran nuevos y el código no tenía errores. Entonces probamos instalando nuevas librerías y cambiando el código cada vez que lo hacíamos, pero siempre ponía el mismo error.

Día 5, 6 y 7: Después de intentar todo, profe, me rindo. Siempre me tira el mismo error no importa que haga, ya no parece solo un error nuestro. Voy a tirar un triple y que sea lo que Dios quiera. Me parece que hay que usar una Raspberry Pi de fábrica sin librerías para que nada haga conflicto y funcione. Ya hicimos una página web usando Flask para automatizar los comandos de una casa inteligente (Cerrar las ventanas, prender el aire, etc.) en base a las lecturas de los sensores, pero no puedo seguir probando si no quiere funcionar.
