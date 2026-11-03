import asyncio
from app.agents.command_staff import JarviGeneralOrchestrator, NekoConversationalGeneral

async def run_battlefield_test():
    print("=========================================================================")
    print("   DESPLIEGUE OPERATIVO DEL ESTADO MAYOR SGA-CD: JARVI Y N.E.K.O.")
    print("=========================================================================")

    jarvi = JarviGeneralOrchestrator(db_path="/tmp/test_corps.db")
    neko = NekoConversationalGeneral(orchestrator=jarvi)

    ordenes = [
        "Crea un Reel vertical y un banner para el torneo deportivo institucional",
        "Publica el contenido en redes sociales y responde el mensaje de WhatsApp del acudiente",
        "Consulta el pipeline de ventas y registra un nuevo prospecto en el CRM"
    ]

    for i, orden in enumerate(ordenes, 1):
        print(f"\n>>> ORDEN #{i} DEL COMANDANTE: '{orden}'")
        respuesta = await neko.handle_user_command(
            command_text=orden,
            user_id="13",
            tenant_id="1",
            roles=["admin_general"]
        )
        print("\n" + respuesta)
        print("-" * 73)

if __name__ == "__main__":
    asyncio.run(run_battlefield_test())