import sqlite3
import os
from langchain_ollama import ChatOllama

# 1. Crear Base de Datos Local SQLite
db_file = "test_sga_local.db"
conn = sqlite3.connect(db_file)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS alumnos (id INTEGER PRIMARY KEY, nombre TEXT, grado TEXT, estado TEXT);")
cur.execute("DELETE FROM alumnos;")
cur.execute("INSERT INTO alumnos (nombre, grado, estado) VALUES ('Carlos Ramirez', '10-A', 'Matriculado');")
cur.execute("INSERT INTO alumnos (nombre, grado, estado) VALUES ('Maria Lopez', '11-B', 'Graduada');")
conn.commit()

# 2. Consultar datos locales
cur.execute("SELECT nombre, grado, estado FROM alumnos WHERE estado = 'Matriculado';")
fila = cur.fetchone()
conn.close()

contexto_db = f"Alumno: {fila[0]}, Grado: {fila[1]}, Estado: {fila[2]}"
print(f"[SQLite Local] Registro extraido: {contexto_db}")

# 3. Inyectar el dato de la base de datos local a DeepSeek-R1 en Ollama
print("[LLM Desktop] Conectando con DeepSeek-R1:8B...")
llm = ChatOllama(model="deepseek-r1:8b", base_url="http://localhost:11434", temperature=0.1)

prompt = f"""Eres el Asistente del Nodo 5 de SGA-CD. Con base exclusivamente en este registro de la base de datos local:
{contexto_db}
Responde en una sola oracion concisa: ¿Cual es el alumno activo y en que grado esta?"""

respuesta = llm.invoke(prompt)
print("\n[RESPUESTA DE DEEPSEEK USANDO LA BASE DE DATOS LOCAL]:\n" + respuesta.content.strip())

if os.path.exists(db_file):
    os.remove(db_file)
