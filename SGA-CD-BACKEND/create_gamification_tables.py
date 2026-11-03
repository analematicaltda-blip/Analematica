from dotenv import load_dotenv
import os

# Load environment variables from the .env file in the backend directory
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(".env file loaded.")
else:
    print("Warning: .env file not found. Using system environment variables.")


from app.db.session import engine
from models import gamification as gamification_models
from models.base import Base

def create_tables():
    print("Conectando a la base de datos y creando tablas de gamificación...")
    try:
        # The new models are GamificacionMision, GamificacionMisionProgreso,
        # GamificacionMercadoItem, and GamificacionCompraLog.
        # Base.metadata.create_all will create all tables that inherit from Base
        # and do not yet exist in the database.
        Base.metadata.create_all(bind=engine)
        print("¡Tablas creadas exitosamente (o ya existían)!")
        print("Las siguientes tablas deberían estar ahora en la base de datos:")
        for table in Base.metadata.tables.keys():
            if 'gamificacion' in table:
                print(f"- {table}")

    except Exception as e:
        print(f"Ocurrió un error al crear las tablas: {e}")

if __name__ == "__main__":
    create_tables()
