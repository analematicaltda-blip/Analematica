# import asyncio
# from django.core.management.base import BaseCommand
# from agents.corps.turismo_coronel import get_turismo_coronel_graph

# class Command(BaseCommand):
#     help = 'Ejecuta una prueba de extremo a extremo del Agente Coronel de Turismo.'

#     def handle(self, *args, **options):
#         self.stdout.write(self.style.SUCCESS("--- 🚀 INICIANDO PRUEBA DEL AGENTE CORONEL 🚀 ---"))

#         async def run_test():
#             agent_graph = get_turismo_coronel_graph()

#             # --- Caso de Prueba 1: Consulta General ---
#             self.stdout.write(self.style.HTTP_INFO("\n--- Caso 1: Consulta General sobre el municipio ---"))
#             input_data_1 = {
#                 "general_order": "Háblame de Puerto Gaitán",
#                 "app_context": {},
#                 "conversation_history": []
#             }
#             final_state_1 = await agent_graph.ainvoke(input_data_1)
#             self.stdout.write(self.style.SUCCESS("✅ Respuesta del Agente:"))
#             self.stdout.write(str(final_state_1.get('final_report', 'No hubo respuesta.')))

#             # --- Caso de Prueba 2: Pregunta Específica (Hoteles) ---
#             self.stdout.write(self.style.HTTP_INFO("\n--- Caso 2: Pregunta Específica (Hoteles) ---"))
#             input_data_2 = {
#                 "general_order": "¿Cuáles son los mejores hoteles?",
#                 "app_context": {},
#                 "conversation_history": final_state_1.get('conversation_history', [])
#             }
#             final_state_2 = await agent_graph.ainvoke(input_data_2)
#             self.stdout.write(self.style.SUCCESS("✅ Respuesta del Agente:"))
#             self.stdout.write(str(final_state_2.get('final_report', 'No hubo respuesta.')))

#             # --- Caso de Prueba 3: Acción (Actualizar datos de un hotel) ---
#             self.stdout.write(self.style.HTTP_INFO("\n--- Caso 3: Simulación de Acción (Actualizar Hotel) ---"))
#             # NOTA: En un test real, necesitaríamos un prestador de hotel en la BD de prueba.
#             # Asumiremos que existe un prestador con ID 1.
#             input_data_3 = {
#                 "general_order": "El prestador con id 1 me informa que su ocupacion nacional es de 50% y la internacional de 10%",
#                 "app_context": {},
#                 "conversation_history": final_state_2.get('conversation_history', [])
#             }
#             final_state_3 = await agent_graph.ainvoke(input_data_3)
#             self.stdout.write(self.style.SUCCESS("✅ Respuesta del Agente:"))
#             self.stdout.write(str(final_state_3.get('final_report', 'No hubo respuesta.')))


#         # Ejecutar el bucle de eventos asyncio
#         try:
#             asyncio.run(run_test())
#         except KeyboardInterrupt:
#             self.stdout.write(self.style.WARNING("\nPrueba interrumpida por el usuario."))

#         self.stdout.write(self.style.SUCCESS("\n--- ✨ PRUEBA DEL AGENTE FINALIZADA ✨ ---"))
