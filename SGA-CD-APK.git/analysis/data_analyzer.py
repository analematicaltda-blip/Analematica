import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import os

# Ensure the directory for saving plots exists
os.makedirs("assets/plots", exist_ok=True)

def get_jefe_area_info(tenant_id: int, user_id: int, conn) -> str:
    """Helper to get the area ('Cultura' or 'Deportes') of a Jefe de Área."""
    cursor = conn.cursor()
    cursor.execute("SELECT area_responsabilidad FROM jefes_area WHERE inquilino_id = ? AND usuario_id = ?", (tenant_id, user_id))
    result = cursor.fetchone()
    return result[0] if result else None

def analyze_q1(tenant_id: int, area: str, conn) -> pd.DataFrame:
    """¿Qué profesores tienen la mayor tasa de asistencia en sus clases?"""
    query = """
        SELECT
            u.nombre_completo AS Profesor,
            CAST(COUNT(a.id) AS REAL) / COUNT(DISTINCT c.id) AS Asistencia_Promedio_Por_Clase
        FROM usuarios u
        JOIN profesores p ON u.id = p.usuario_id
        LEFT JOIN clases c ON c.instructor_id = u.id
        LEFT JOIN asistencias a ON a.clase_id = c.id
        WHERE u.inquilino_id = ? AND p.area = ?
        GROUP BY u.nombre_completo
        HAVING COUNT(DISTINCT c.id) > 0 -- Only include professors with classes
        ORDER BY Asistencia_Promedio_Por_Clase DESC;
    """
    df = pd.read_sql_query(query, conn, params=(tenant_id, area))
    return df

def analyze_q5(tenant_id: int, area: str, conn) -> str:
    """Identificar grupos (clusters) de alumnos según su nivel de participación."""
    query = """
        SELECT
            a.usuario_id,
            u.nombre_completo,
            COUNT(ast.id) as total_asistencias
        FROM alumnos a
        JOIN usuarios u ON a.usuario_id = u.id
        LEFT JOIN inscripciones i ON a.id = i.alumno_id AND i.area = ?
        LEFT JOIN asistencias ast ON i.alumno_id = ast.alumno_id AND ast.clase_id = i.clase_id
        WHERE a.inquilino_id = ?
        GROUP BY a.usuario_id, u.nombre_completo;
    """
    df = pd.read_sql_query(query, conn, params=(area, tenant_id))

    if df.empty or df['total_asistencias'].sum() == 0:
        return "No hay suficientes datos de asistencia para realizar el análisis de clusters."

    # Pre-process data
    features = df[['total_asistencias']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Find clusters
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    df['cluster'] = kmeans.fit_predict(scaled_features)

    # Create a plot
    plt.figure(figsize=(10, 6))
    for i in range(3):
        cluster_data = df[df['cluster'] == i]
        plt.scatter(cluster_data.index, cluster_data['total_asistencias'], label=f'Cluster {i} (Participación {"Baja" if i==0 else "Media" if i==1 else "Alta"})')

    plt.title('Clusters de Participación de Alumnos')
    plt.ylabel('Total de Asistencias')
    plt.xlabel('Alumnos')
    plt.legend()

    # Save the plot
    plot_path = f"assets/plots/cluster_analysis_{tenant_id}_{area}.png"
    plt.savefig(plot_path)
    plt.close() # Close the plot to free up memory

    return plot_path


# Placeholder for the main function
def analyze_question(question_key: str, tenant_id: int, user_id: int):
    """
    Main function to dispatch to the correct analysis function.
    Returns a dictionary with the result type ('table', 'image', 'text') and the data.
    """
    conn = sqlite3.connect("formacion.db")
    area = get_jefe_area_info(tenant_id, user_id, conn)

    if not area:
        conn.close()
        return {"type": "text", "data": "Error: No se pudo determinar el área para este usuario."}

    result = {"type": "text", "data": "Análisis no implementado todavía."}

    if question_key == "q1":
        df = analyze_q1(tenant_id, area, conn)
        result = {"type": "table", "data": df.to_dict('records')}
    elif question_key == "q5":
        # This function returns a path to an image or a string message
        analysis_result = analyze_q5(tenant_id, area, conn)
        if "No hay suficientes datos" in analysis_result:
            result = {"type": "text", "data": analysis_result}
        else:
            result = {"type": "image", "data": analysis_result}
    # Add other questions here later

    conn.close()
    return result
