# Módulo de Nómina (gestion_contable/nomina)

Este módulo gestiona la información de empleados, contratos y la liquidación de nómina, incluyendo prestaciones sociales y parafiscales.

## Declaración de Deuda Técnica Arquitectónica (Fase 5.2)

**El cálculo de nómina reside temporalmente en gestion_contable/nomina.**
**La separación hacia gestion_operativa se realizará en una fase posterior, una vez cerrados los ciclos fiscales y contables.**

Esta decisión ha sido tomada conscientemente para permitir el avance del proyecto (Fase 5.2) sin realizar refactorizaciones estructurales prematuras. El diseño actual concentra la lógica de cálculo y el registro contable en este mismo módulo, actuando como un "módulo mixto transitorio".
