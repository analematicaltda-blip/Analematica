import random
from django.apps import apps
from django.db import transaction
from faker import Faker
fake = Faker('es_CO')

NUM_PRESTADORES = {
    'hoteles': 3000,
    'restaurantes': 3000,
    'bares_discotecas': 3000,
    'guias': 3000,
    'agencias_viajes': 3000,
    'operadoras_turisticas': 3000,
    'transporte_terrestre': 3000,
    'transporte_fluvial': 3000,
    'artesanos': 3000,
    'asociaciones': 3000,
}

NUM_TURISTAS = 1_000_000

@transaction.atomic
def create_stress_data():
    CustomUser = apps.get_model('api', 'CustomUser')
    # Create prestadores
    for tipo, num in NUM_PRESTADORES.items():
        for _ in range(num):
            user = CustomUser.objects.create(
                username=f'{tipo}_{random.randint(1,999999)}',
                role='PRESTADOR',
            )
            # Create specialized profile
    # Create turistas
    for _ in range(NUM_TURISTAS):
        user = CustomUser.objects.create(role='TURISTA')
    # Simulate interactions: ventas, compras MP, nómina, gastos
    print('Stress test complete - run migrate first')

if __name__ == '__main__':
    create_stress_data()

