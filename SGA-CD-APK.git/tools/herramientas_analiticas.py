import matplotlib.pyplot as plt
import pandas as pd
import uuid
import os

def generar_grafico_asistencia(query: str) -> str:
    """
    Genera un gráfico de barras basado en una consulta de lenguaje natural sobre la asistencia.
    Por ahora, utiliza datos de ejemplo.
    Devuelve la ruta local al archivo de imagen guardado.
    """
    print(f"--- 📊 Herramienta de Gráficos: Generando gráfico para la consulta: '{query}' ---")

    # --- 1. Datos de Ejemplo (en un futuro, esto vendría de una consulta a la BD) ---
    data = {
        'Mes': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo'],
        'Asistencia (%)': [85, 88, 92, 90, 95]
    }
    df = pd.DataFrame(data)

    # --- 2. Generación del Gráfico con Matplotlib ---
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(df['Mes'], df['Asistencia (%)'], color='#4CAF50')

    ax.set_title('Asistencia Mensual General', fontsize=16, fontweight='bold')
    ax.set_ylabel('Asistencia (%)', fontsize=12)
    ax.set_ylim(0, 100)
    ax.tick_params(axis='x', rotation=45)

    # Añadir etiquetas de valor encima de las barras
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f'{yval}%', ha='center', va='bottom')

    plt.tight_layout()

    # --- 3. Guardar el Gráfico en un Archivo ---
    charts_dir = "app/static/charts"
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)

    filename = f"chart_{uuid.uuid4()}.png"
    filepath = os.path.join(charts_dir, filename)

    plt.savefig(filepath)
    plt.close(fig) # Cerrar la figura para liberar memoria

    print(f"--- 📊 Gráfico guardado en: {filepath} ---")

    # --- 4. Devolver la ruta accesible por la web ---
    web_path = f"/static/charts/{filename}"
    return web_path
