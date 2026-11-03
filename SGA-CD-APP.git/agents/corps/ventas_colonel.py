import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, Runnable
from langchain_community.vectorstores import FAISS
from app.core.config import settings

# --- Configuration ---
VECTOR_STORE_PATH = "SGA-CD-FASTAPI-BACKEND/app/agents/knowledge_base/faiss_index_sales"

def get_sales_agent_executor():
    """
    Creates and returns the executor for the Sales Agent.
    This agent is designed to answer questions based on a vector store of project documentation.
    """
    # --- 1. Set up the LLM ---
    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o", temperature=0)

    # --- 2. Set up the Retriever from the FAISS Vector Store ---
    # Check if the vector store index file exists
    if not os.path.exists(VECTOR_STORE_PATH):
        # This is a fallback for when the user hasn't run the ingestion script yet.
        # The agent will still work but won't have the documentation knowledge.
        print("ADVERTENCIA: El índice del almacén de vectores no se encontró.")
        print("El agente de ventas funcionará sin conocimiento de la documentación.")
        print("Ejecute 'python run_ingest.py' para crear la base de conocimiento.")
        # Create a dummy retriever that does nothing
        class DummyRetriever(Runnable):
            def invoke(self, input, config=None):
                return []
        retriever = DummyRetriever()
    else:
        embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
        vector_store = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()

    # --- 3. Define the Prompt Template ---
    template = """
    Eres un asistente de ventas amigable y experto para una plataforma de software llamada SGA-CD.
    Tu objetivo es responder a las preguntas de los usuarios para ayudarles a entender el producto y animarles a registrarse.
    Utiliza la siguiente información de la documentación interna para basar tus respuestas.
    Si la información no contiene la respuesta, di amablemente que no tienes esa información.
    No inventes respuestas. Sé conciso y servicial.

    Contexto de la documentación:
    {context}

    Pregunta del usuario:
    {question}

    Respuesta del Asistente de Ventas:
    """
    prompt = ChatPromptTemplate.from_template(template)

    # --- 4. Create the RAG Chain ---
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

# --- Main Executor ---
# We create the agent executor when the module is loaded.
# This can be imported and used by the API endpoint.
sales_agent_executor = get_sales_agent_executor()
