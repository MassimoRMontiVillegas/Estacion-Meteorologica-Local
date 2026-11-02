import os
import subprocess
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Nos aseguramos de que la carpeta de assets estáticos exista
if not os.path.exists("static"):
    os.makedirs("static")


@app.route("/")
def home():
    # Verifica si ya se generó algún gráfico para mostrarlo en el HTML
    grafico_existe = os.path.exists("static/reporte_clima.png")
    return render_template("index.html", grafico_existe=grafico_existe)


@app.route("/ejecutar_sidd")
def ejecutar_sidd():
    """Ruta web para forzar una lectura del hardware en tiempo real."""
    try:
        import SIDD
        SIDD.inicializar_base_datos()
        SIDD.registrar_clima()
        print("Lectura manual forzada desde la web.")
    except Exception as e:
        print(f"Error al ejecutar SIDD de forma manual: {e}")
    return redirect(url_for("home"))


@app.route("/generar_grafico")
def generar_grafico():
    """Ruta web para actualizar el gráfico estadístico."""
    try:
        import Graficos
        Graficos.generar_reporte_grafico()
        print("Gráfico renderizado con éxito desde la web.")
    except Exception as e:
        print(f"Error al generar gráfico: {e}")
    return redirect(url_for("home"))


if __name__ == "__main__":
    # Escucha en el puerto 5000 para toda tu red local (0.0.0.0)
    app.run(host="0.0.0.0", port=5000, debug=True)
