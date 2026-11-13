# Entrega de diagnóstico del bloque 1

## Archivos para revisión

- HALLAZGOS_Y_PRIORIDADES.md: diez hallazgos y tareas ordenadas, con evidencia,
  dependencias y criterios de aceptación. No autoriza eliminar componentes.
- ARQUITECTURA.md: dependencias observadas, identidades y límites del mapa.
- matriz-priorizada.csv / .json: 161 requisitos, responsables, prioridad,
  dependencia, evidencia disponible, estado y criterio de aceptación.
- inventario.json: modelos candidatos, relaciones declaradas, fragmentos de
  ruta, páginas/layouts, permisos declarados, fuentes con hash y duplicados.
- runtime-evidence.json: diez suites y152 pruebas aprobadas en entorno aislado.
- cobertura.json:153 no verificadas,7 parciales y1 defectuosa en la matriz.
- resumen.json y matriz-funcional.*: corte estático anterior a asociar pruebas;
  para priorizar usar matriz-priorizada.*, que conserva los límites de evidencia.

## Método y cobertura

Se inspeccionaron1943 archivos Python:988 institucionales,528 ERP,241 de
Analemática y186 de la dependencia central. Se detectaron583 clases candidatas
con declaraciones de modelos,848 fragmentos de ruta,285 páginas/layouts,
302 declaraciones de permisos y144 grupos de fuentes exactas duplicadas.
No son recuentos de endpoints resueltos, tablas migradas o funciones operativas.

Los requisitos históricos de INS/ERP/INT se conservan y se añaden seis del
corporativo. No se cambia estado a IMPLEMENTADA por una página, clase o botón.
La matriz no desglosa todavía todas las posibles funciones de Analemática:
ese detalle necesita casos y recorrido del dominio, no inferencias de nombres.
Los estados NO VERIFICADA no significan INEXISTENTE ni DEFECTUOSA.

Se excluyen agentes, dependencias instaladas, builds, cachés y carpetas privadas.
No se inspeccionan contenidos de bases de clientes, secretos o servicios reales.
Los paquetes de terceros y agentes requieren auditoría específica posterior.

Las pruebas incluyen mocks y esquemas temporales: no acreditan todos los
recorridos web. Una primera ejecución en sandbox agotó el tiempo del gateway;
la repetición fuera de ese aislamiento completó las diez suites. El informe
adjunto corresponde a esa ejecución aprobada, no se oculta un fallo del producto.

## Reproducir sin sobrescribir evidencia anterior

```bash
python BACKEND/INTEGRACIONES/plan-maestro/audit_block01.py --directory /tmp/nueva-auditoria
python BACKEND/INTEGRACIONES/plan-maestro/verify_local.py --output /tmp/nueva-evidencia.json
python BACKEND/INTEGRACIONES/plan-maestro/reconcile_block01.py --directory /tmp/nueva-auditoria --runtime /tmp/nueva-evidencia.json
```

Requiere las dependencias de prueba preparadas. Ningún comando inicia producción,
contacta proveedores ni crea commits. La auditoría AST informa tres defectos de
fuente y un fixture JavaScript con extensión Python intencional; no los repara
silenciosamente. La clasificación DEFECTUOSA de ANA-004 se refiere al archivo,
no a un fallo demostrado de un recorrido productivo.

## Siguiente orden recomendado

1. Mapear consumidores de los tres archivos defectuosos y reparar con pruebas.
2. Restablecer contrato de build completo de Turismo y ERP, sin elegir versiones
   arbitrarias ni alterar la identidad azul metalizado/celeste/blanco.
3. Verificar por flujo todos los permisos y límites empresariales/territoriales.
4. Auditoría institucional: directorios, atractivos, eventos, artesanos,
   planificación, documentos y reportes; después ERP desde el cliente.
5. Desarrollar lo ausente/parcial después de confirmar dependencias y evidencia.

La entrega de inventario y priorización está lista; la verificación funcional
integral del bloque sigue abierta. Ningún sistema se declara al100%.

El archivo restore-regression-extra.json conserva el resultado del ensayo de
restauración iniciado antes de priorizar el bloque1:19 tablas y79 filas iguales,
material MFA y sesiones legibles con las claves originales. Es un esquema
sintético mínimo, no un respaldo productivo ni un cierre del bloque9. Se corrigió
el cierre de conexiones de prueba para poder limpiar la base restaurada.
