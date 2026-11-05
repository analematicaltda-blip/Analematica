import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.config import Settings

# Create a settings instance, explicitly providing the path to the .env file
# This is necessary because this script is run from the root of the repo,
# not from within the backend directory where the .env file is located.
settings = Settings(_env_file="SGA-CD-FASTAPI-BACKEND/.env")

# --- Configuration ---
# List of documentation files to ingest. Paths are relative to the repository root.
DOC_PATHS = [
    "SGA-CD-FASTAPI-BACKEND/ROLES_Y_PERMISOS.md",
    "SGA-CD-WEB.git/INFORME_TECNICO.md",
    "SGA-CD-APK.git/docs/user_manual.md",
    "SGA-CD-APP.git/docs/ecosystem.md"
]

# Path where the final vector store will be saved.
VECTOR_STORE_PATH = "SGA-CD-FASTAPI-BACKEND/app/agents/knowledge_base/faiss_index_sales"

def load_documents():
    """Loads documents from the specified paths."""
    docs = []
    for path in DOC_PATHS:
        if not os.path.exists(path):
            print(f"Advertencia: El archivo no se encontró y será omitido: {path}")
            continue

        print(f"Cargando documento: {path}")
        if path.endswith(".md"):
            loader = UnstructuredMarkdownLoader(path)
        else:
            loader = UnstructuredFileLoader(path)

        docs.extend(loader.load())
    return docs

def main():
    """
    Main function to create and save the vector store.

    To run this script:
    1. Make sure you are in the root directory of the repository.
    2. Ensure your .env file in SGA-CD-FASTAPI-BACKEND has a valid OPENAI_API_KEY.
    3. Run the script: python run_ingest.py
    """
    print("Iniciando la creación de la base de conocimiento para el agente de ventas...")

    # --- Pre-flight check for API Key ---
    if not settings.OPENAI_API_KEY or "your_openai_api_key_here" in settings.OPENAI_API_KEY or len(settings.OPENAI_API_KEY) < 20:
        print("\n" + "="*80)
        print("ERROR: Clave de API de OpenAI no válida o no configurada.")
        print("Por favor, edite el archivo 'SGA-CD-FASTAPI-BACKEND/.env' y añada una clave de API de OpenAI válida.")
        print("Puede obtener una clave en: https://platform.openai.com/account/api-keys")
        print("Una vez configurada la clave, vuelva a ejecutar este script: python run_ingest.py")
        print("="*80 + "\n")
        return

    # 1. Load documents
    documents = load_documents()
    if not documents:
        print("No se encontraron documentos para procesar. Abortando.")
        return

    # 2. Split documents into chunks
    print("Dividiendo documentos en fragmentos...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    print(f"Se crearon {len(texts)} fragmentos de texto.")

    # 3. Create embeddings
    print("Creando embeddings con OpenAI...")
    if not settings.OPENAI_API_KEY:
        print("Error: La clave de API de OpenAI no está configurada. Por favor, añádala al archivo .env.")
        return
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

    # 4. Create FAISS vector store and save it
    print("Creando y guardando el almacén de vectores FAISS...")
    try:
        vector_store = FAISS.from_documents(texts, embeddings)
        vector_store.save_local(VECTOR_STORE_PATH)
        print(f"¡Éxito! La base de conocimiento ha sido guardada en: {VECTOR_STORE_PATH}")
    except Exception as e:
        print(f"Ocurrió un error al crear el almacén de vectores: {e}")

if __name__ == "__main__":
    main()
