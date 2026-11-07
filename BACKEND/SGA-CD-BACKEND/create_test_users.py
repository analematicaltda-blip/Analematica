import logging
from app.db.session import SessionLocal
from app import crud, schemas

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_users():
    """
    Creates a test user for each of the 12 official roles in the system.
    This script is idempotent; it will not create users that already exist.
    """
    db = SessionLocal()

    # We assume an Inquilino (tenant/empresa) with id=1 exists for testing.
    # In a real scenario, this might need to be created first.
    inquilino_id_for_test = 1

    users_to_create = [
        # role,             username,               email
        ("admin_general",   "admin_general",        "admin_general@sga.com"),
        ("admin_empresa",   "admin_empresa_test",   "admin_empresa@sga.com"),
        ("jefe_area",       "jefe_area_test",       "jefe_area@sga.com"),
        ("profesional_area","profesional_area_test","profesional_area@sga.com"),
        ("tecnico_area",    "tecnico_area_test",    "tecnico_area@sga.com"),
        ("coordinador",     "coordinador_test",     "coordinador@sga.com"),
        ("profesor",        "profesor_test",        "profesor@sga.com"),
        ("alumno",          "alumno_test",          "alumno@sga.com"),
        ("padre_acudiente", "padre_acudiente_test", "padre_acudiente@sga.com"),
        ("jefe_almacen",    "jefe_almacen_test",    "jefe_almacen@sga.com"),
        ("almacenista",     "almacenista_test",     "almacenista@sga.com"),
        ("jefe_escenarios", "jefe_escenarios_test", "jefe_escenarios@sga.com"),
    ]

    logger.info("--- Starting Test User Creation ---")

    for role, username, email in users_to_create:
        user = crud.user.get_user_by_username(db, username=username)
        if not user:
            user_in = schemas.UserCreate(
                email=email,
                password="password", # Using a common password for all test users
                nombre_usuario=username,
                nombre_completo=f"Test {role.replace('_', ' ').title()}",
                rol=role,
                inquilino_id=inquilino_id_for_test
            )
            try:
                crud.user.create_user(db=db, user=user_in)
                logger.info(f"User '{username}' with role '{role}' created successfully.")
            except Exception as e:
                logger.error(f"Failed to create user '{username}': {e}")
                db.rollback()
        else:
            logger.info(f"User '{username}' already exists, skipping.")

    logger.info("--- Test User Creation Process Finished ---")
    db.close()


if __name__ == "__main__":
    logger.info("Running test user creation script directly.")
    # Note: For this script to run, you need to have your .env file
    # with database credentials in the root of the project, and all
    # dependencies from requirements.txt installed.
    create_test_users()
