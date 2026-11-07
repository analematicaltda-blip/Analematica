# Acceso personal y empresarial

La billetera está destinada a cualquier persona de Colombia, sin exigir ser
prestador turístico o funcionario. El usuario registrado debe darse de alta
expresamente en su perfil personal. Los nombres históricos TURISTA/EMPLEADO en
la base no restringen esa elegibilidad.

GET/POST /api/v1/finance/wallet/accounts/profile/ consulta o realiza el alta
personal del usuario autenticado. POST no recibe titular, rol ni saldo. El alta
crea un perfil suspendido sin moneda ni fondos; no abre una cuenta financiera.

La billetera de una empresa ERP-TUR o SGA-CD requiere el administrador empresarial
verificado por un adaptador confiable del servidor. El equipo administrativo,
los permisos generales y el superusuario no conceden acceso. Cada acción vuelve
a comprobar la autoridad, incluso después de una revisión previa. La consola
Django genérica no expone los modelos financieros.

El adaptador WALLET_COMPANY_ADMIN_VERIFIER está deshabilitado por defecto.
La integración de identidad, alta pública y panel empresarial web/escritorio
requiere completar WAL-019. No se simulan esas credenciales ni se declara
terminada la integración de los paneles. La autorización financiera con dispositivo
y sus dos confirmaciones sigue siendo obligatoria; el alta no la reemplaza.
