# Pool 02 · Identidad y biometría

Estado: diseño pendiente, salvo la biometría nativa necesaria para usar las llaves
incluida en Pool 01. No hay detector de cámara falsa ni prueba de vida implementados.

El siguiente contrato debe vincular una operación de llave de hardware al desafío
único, resumen de importe/destino, solicitante y caducidad de cada autorización de
transferencia. Requiere enrolamiento/revocación de dispositivos y comprobación en
backend: una bandera local `biometric=true` nunca autoriza fondos. Mantener las dos
autorizaciones del mismo administrador y comprobar fallos/replay/cambio de importe.

La biometría del sistema valida a una persona enrolada en ese dispositivo, no su
identidad civil. Heurísticas de emulador/cámara pueden complementar, pero no
certifican que una cámara o vídeo sean auténticos en un sistema comprometido.
No crear una base propia de rostros ni afirmar KYC/prueba de vida sin evidencia.
