import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Configuración de la base de datos de tu estación
DB_NOMBRE = "clima_estacion.db"

def obtener_datos():
    """Conecta a la base de datos y trae el historial de lecturas."""
    conexion = sqlite3.connect(DB_NOMBRE)
    cursor = conexion.cursor()
    
    # Traemos los datos ordenados cronológicamente
    cursor.execute("SELECT fecha_hora, temperatura, humedad, presion FROM lecturas ORDER BY fecha_hora ASC")
    filas = cursor.fetchall()
    conexion.close()
    
    fechas = []
    temperaturas = []
    humedades = []
    presiones = []
    
    for fila in filas:
        # Convertimos el texto de la fecha a un objeto datetime para Matplotlib
        fechas.append(datetime.strptime(fila[0], "%Y-%m-%d %H:%M:%S"))
        temperaturas.append(fila[1])
        humedades.append(fila[2])
        presiones.append(fila[3])
        
    return fechas, temperaturas, humedades, presiones

def generar_reporte_grafico():
    fechas, temps, hums, presiones = obtener_datos()
    
    if not fechas:
        print("Aviso: No hay datos guardados en la base de datos todavía.")
        return

    # Creamos la figura con 3 sub-gráficos alineados verticalmente
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle('Historial Estación Meteorológica SIDD', fontsize=16, fontweight='bold')

    # 1. Gráfico de Temperatura
    ax1.plot(fechas, temps, color='tab:red', linewidth=2, label='Temperatura')
    ax1.set_ylabel('Temp (°C)', color='tab:red', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 2. Gráfico de Humedad
    ax2.plot(fechas, hums, color='tab:blue', linewidth=2, label='Humedad')
    ax2.set_ylabel('Humedad (%)', color='tab:blue', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    ax2.grid(True, linestyle='--', alpha=0.5)

    # 3. Gráfico de Presión Atmosférica
    ax3.plot(fechas, presiones, color='tab:green', linewidth=2, label='Presión')
    ax3.set_ylabel('Presión (hPa)', color='tab:green', fontweight='bold')
    ax3.tick_params(axis='y', labelcolor='tab:green')
    ax3.grid(True, linestyle='--', alpha=0.5)

    # Formatear el eje X para que muestre las horas y fechas de forma legible
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    fig.autofmt_xdate() # Rota las fechas automáticamente para que no se superpongan
    
    plt.xlabel('Fecha y Hora (DD/MM HH:MM)', fontweight='bold')
    
    # Ajustamos el diseño y guardamos la imagen final dentro de static/
    plt.tight_layout()
    nombre_archivo = "static/reporte_clima.png"
    plt.savefig(nombre_archivo, dpi=300)
    plt.close()
    
    print(f"¡Gráfico generado con éxito! Guardado en '{nombre_archivo}'")

if __name__ == "__main__":
    generar_reporte_grafico()
