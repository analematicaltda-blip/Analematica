# SGA-CD — Reporte Final de Integridad y Verificación de Perímetro (Fase PoC-PHI3-R1)

**Fecha:** 27 de Octubre de 2026
**Rama Git:** `jules-16089663740279313638-db197fdf`
**HEAD Commit:** `ff97c4ddf48bc67d6b4a1b2f55e210491b3cf2e8`

---

## 1. Verificación de los 5 Archivos Protegidos del Perímetro

Se ejecutaron los comandos de suma de verificación MD5 sobre los 5 archivos congelados del perímetro del proyecto:

```bash
md5sum SGA-CD-WEB.git/js/views/admin_general.js
md5sum SGA-CD-FASTAPI-BACKEND/app/api/v1/endpoints/admin_general.py
md5sum SGA-CD-WEB.git/index.html
md5sum SGA-CD-WEB.git/css/vanguard.css
md5sum SGA-CD-WEB.git/css/style.css
```

### Resultados Obtenidos:

| Archivo Protegido | MD5 de Referencia Obligatorio | MD5 Calculado en Fase PoC-PHI3-R1 | Estado de Integridad |
| :--- | :--- | :--- | :--- |
| `SGA-CD-WEB.git/js/views/admin_general.js` | `52c83cfca2ba094b060661bdf259b51c` | `52c83cfca2ba094b060661bdf259b51c` | **100% INTACTO** |
| `SGA-CD-FASTAPI-BACKEND/app/api/v1/endpoints/admin_general.py` | `b396d65984216013b45fd006e4eeffe8` | `b396d65984216013b45fd006e4eeffe8` | **100% INTACTO** |
| `SGA-CD-WEB.git/index.html` | `132c63fe3220bf746fe24b8d5a8fc2a8` | `132c63fe3220bf746fe24b8d5a8fc2a8` | **100% INTACTO** |
| `SGA-CD-WEB.git/css/vanguard.css` | `256e0b2ae110280c1d94d4842bef4c8d` | `256e0b2ae110280c1d94d4842bef4c8d` | **100% INTACTO** |
| `SGA-CD-WEB.git/css/style.css` | `35e60be9613c955b76e37c036f53063c` | `35e60be9613c955b76e37c036f53063c` | **100% INTACTO** |

---

## 2. Auditoría del Estado de Git

1. **Operaciones Prohibidas**: Cero ejecuciones de `git reset`, `git clean`, `git stash`, `git checkout` o `git restore`.
2. **Archivos de Pesos del Modelo (2.62 GB)**: Verificados como no rastreados (`git status` no muestra ningún archivo binario dentro del índice).
3. **Módulos Afectados**: Las modificaciones se limitan estrictamente a la adición del laboratorio de pruebas en `SGA-CD-APK.git/ai-lab/phi-3-mini/` y a la adición no destructiva de reglas de exclusión en `.gitignore` y `SGA-CD-APK.git/.gitignore`.
