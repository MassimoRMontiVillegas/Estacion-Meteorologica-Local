import os
import sqlite3
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
DB_NOMBRE = "clima_estacion.db"

if not os.path.exists("static"):
    os.makedirs("static")

def obtener_ultimo_estado():
    estado_por_defecto = {
        "temperatura": "--",
        "humedad": "--",
        "presion": "--",
        "ventanas": "Desconocido",
        "aire": "Desconocido",
        "alerta_presion": "Estable (Sin avisos) 🌤️",
        "fecha": "Sin registros"
    }
    
    if not os.path.exists(DB_NOMBRE):
        return estado_por_defecto

    try:
        conexion = sqlite3.connect(DB_NOMBRE)
        cursor = conexion.cursor()
        cursor.execute("SELECT id, fecha_hora, temperatura, humedad, presion FROM lecturas ORDER BY id DESC LIMIT 1")
        fila = cursor.fetchone()
        
        if fila:
            id_actual, fecha, temp, hum, pres = fila[0], fila[1], fila[2], fila[3], fila[4]
            
            cursor.execute("SELECT presion FROM lecturas WHERE id < ? ORDER BY id DESC LIMIT 1", (id_actual,))
            fila_anterior = cursor.fetchone()
            conexion.close()

            # Acciones condicionadas estrictamente a Temp y Hum
            ventanas = "Abiertas 🪟"
            aire = "Apagado ⚪"
            alerta_presion = "Estable (Sin avisos) 🌤️"

            if hum is not None and hum > 80.0:
                ventanas = "Cerradas (¡Lluvia por Humedad!) 🌧️"

            if temp is not None:
                if temp > 27.0:
                    aire = "Encendido en Modo Frío ❄️"
                elif temp < 18.0:
                    aire = "Encendido en Modo Calefacción ☀️"

            # Advertencia informativa de presión (no altera ventanas ni aire)
            if pres is not None and fila_anterior and fila_anterior[0] is not None:
                diferencia = pres - fila_anterior[0]
                if diferencia < -3.0:
                    alerta_presion = "¡Aviso! Caída brusca de presión (Tormenta en camino) ⚡"
                elif diferencia > 3.0:
                    alerta_presion = "Aviso: Presión en alza (Buen tiempo) ☀️"

            return {
                "temperatura": temp if temp is not None else "--",
                "humedad": hum if hum is not None else "--",
                "presion": pres if pres is not None else "--",
                "ventanas": ventanas,
                "aire": aire,
                "alerta_presion": alerta_presion,
                "fecha": fecha
            }
    except Exception as e:
        print(f"Error al leer base de datos en web: {e}")

    return estado_por_defecto


@app.route("/")
def home():
    grafico_existe = os.path.exists("static/reporte_clima.png")
    estado_casa = obtener_ultimo_estado()
    return render_template("index.html", grafico_existe=grafico_existe, estado=estado_casa)


@app.route("/ejecutar_sidd")
def ejecutar_sidd():
    try:
        import SIDD
        SIDD.inicializar_base_datos()
        SIDD.registrar_clima()
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for("home"))


@app.route("/generar_grafico")
def generar_grafico():
    try:
        import Graficos
        Graficos.generar_reporte_grafico()
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
