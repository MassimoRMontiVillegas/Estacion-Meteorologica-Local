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

**Día 1: Definición del proyecto.** Comenzamos definiendo el alcance del proyecto: cómo integrar la Raspberry Pi, qué resultados debía entregar, cómo debía presentarse la información y qué componentes necesitábamos conseguir. Finalmente, decidimos desarrollar una estación meteorológica capaz de medir temperatura y humedad mediante la Raspberry Pi.

**Día 2: Diseño y preparación.** Elaboramos un boceto de las conexiones y comenzamos a escribir el código. Además, el profesor solicitó incorporar una página web donde se visualizaran los datos obtenidos por la Raspberry Pi. Hacia el final de la jornada, reunimos los componentes, armamos el circuito en la protoboard y desarrollamos un script básico para comprobar su funcionamiento. No llegamos a utilizarlo porque la jornada de taller había finalizado.

**Día 3: Desarrollo del código y primer inconveniente.** Iniciamos la programación y, gracias al compromiso del equipo entero, logramos finalizar el código el mismo día. Sin embargo, surgió el primer inconveniente: el bus I2C de la Raspberry Pi no detectaba el sensor BMP280. Lo resolvimos configurando las opciones de interfaz correspondientes.

**Día 4: Falla de un componente y segundo inconveniente.** Al rearmar el circuito, detectamos que faltaba un componente, que además estaba dañado en su caja, por lo que dedicamos parte de la jornada a conseguir un reemplazo. Una vez resuelto, apareció un segundo inconveniente con el sensor DHT22, que devolvía el error “Check Wiring” aunque los cables eran nuevos y el código no presentaba errores de sintaxis. Probamos instalar distintas librerías y modificar el código en cada intento, pero errores similares a través de las distintas librerías persistieron.

**Días 5, 6 y 7: Pruebas y avance en la aplicación web.** Tras agotar las alternativas que teníamos, los errores persistían sin importar los cambios realizados. Planteamos como hipótesis utilizar una Raspberry Pi con una instalación limpia, sin librerías que pudieran generar conflictos. Mientras tanto, desarrollamos con Flask una página web que simula la automatización de una casa inteligente (cierre de ventanas, encendido del aire acondicionado, etc.) en función de las lecturas de los sensores. Sin embargo, no pudimos validarla de punta a punta mientras el DHT22 no funcionara.

**Día 8: Análisis del código y posible solución**. Con el apoyo de la IA, revisamos el código y encontramos un error en la forma en que se leían los datos del DHT22: se usaba una clave incorrecta del resultado que devuelve la librería. Corregimos ese error, incorporamos reintentos en la lectura y sumamos un script de diagnóstico del sensor. La validación en el hardware quedó pendiente para la próxima jornada.
