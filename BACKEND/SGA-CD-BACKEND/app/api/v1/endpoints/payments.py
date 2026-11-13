from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from app.services.payment_gateway_adapter import payment_gateway

router = APIRouter()

PLANES_CATALOGO = [
    {
        "id": "plan_estudiante",
        "nombre": "Plan Estudiante Atleta/Artista",
        "precio": 50000,
        "moneda": "COP",
        "periodo": "Mensual",
        "beneficios": ["Acceso a entrenamientos y talleres", "Seguimiento de rendimiento", "Perfil deportivo verificado"]
    },
    {
        "id": "plan_docente",
        "nombre": "Plan Docente / Entrenador",
        "precio": 120000,
        "moneda": "COP",
        "periodo": "Mensual",
        "beneficios": ["Gestion de hasta 50 alumnos", "Planificador de clases IA", "Reportes biometricos"]
    },
    {
        "id": "plan_institucional",
        "nombre": "Plan Institucional / Club",
        "precio": 450000,
        "moneda": "COP",
        "periodo": "Mensual",
        "beneficios": ["Multi-sede ilimitado", "Ejercito de Agentes IA completo", "Pasarela de pagos personalizada"]
    }
]

class CheckoutRequest(BaseModel):
    plan_id: str
    nombre_cliente: str
    email_cliente: str
    telefono_cliente: str

@router.get("/plans")
def obtener_planes():
    return {"status": "success", "data": PLANES_CATALOGO}

@router.post("/checkout")
def crear_checkout_pago(pedido: CheckoutRequest):
    # The former anonymous route had no durable intent and reused references.
    # Keep its catalogue readable, but direct writes to the company-owned flow.
    raise HTTPException(status_code=409,detail={"code":"PERSISTED_PAYMENT_INTENT_REQUIRED","workflow":"commercial-unified/crm/payment-commands"},headers={"Cache-Control":"no-store"})

@router.get("/config")
def obtener_configuracion_pasarela():
    return {
        "pasarela_activa": "BOLD",
        "estado": "COBROS_POR_CUALIFICAR",
        "reembolsos": "BLOQUEADOS_HASTA_VERIFICAR_CONTRATO_Y_ACUSES",
        "monedas_soportadas": ["COP"]
    }