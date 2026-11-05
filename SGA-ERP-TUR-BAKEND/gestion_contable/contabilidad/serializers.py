from rest_framework import serializers
from django.apps import apps

Account = apps.get_model('core_erp', 'Account')

class PlanCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'code', 'name', 'type', 'parent_account', 'initial_balance', 'is_active', 'ifrs_mapping']
        read_only_fields = ['id']

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('El código de la cuenta debe contener solo dígitos.')

        allowed_lengths = [1, 2, 4, 6, 8, 10]
        if len(value) not in allowed_lengths:
             raise serializers.ValidationError('La longitud del código debe ser 1 (Clase), 2 (Grupo), 4 (Cuenta), 6 (Subcuenta) o mayor para auxiliares.')

        return value

    def validate(self, data):
        code = data.get('code')
        request = self.context.get('request')
        tenant_id = getattr(request, 'tenant_id', None) if request else None
        if not tenant_id and request and 'HTTP_X_TENANT_ID' in request.META:
            tenant_id = request.META['HTTP_X_TENANT_ID']

        # Determinar el tipo basado en el primer dígito (Clase)
        clase = code[0]
        type_map = {
            '1': 'ASSET',
            '2': 'LIABILITY',
            '3': 'EQUITY',
            '4': 'REVENUE',
            '5': 'EXPENSE',
            '6': 'COST_OF_SALES',
            '7': 'PRODUCTION_COST',
            '8': 'DEBTOR_ORDER',
            '9': 'CREDITOR_ORDER',
        }
        data['type'] = type_map.get(clase)

        # Lógica de auto-asignación de padre si no se provee
        if not data.get('parent_account') and len(code) > 1:
            parent_code = None
            if len(code) == 2: # Grupo -> Padre es Clase
                parent_code = code[0]
            elif len(code) == 4: # Cuenta -> Padre es Grupo
                parent_code = code[:2]
            elif len(code) == 6: # Subcuenta -> Padre es Cuenta
                parent_code = code[:4]
            elif len(code) > 6: # Auxiliar -> Padre es Subcuenta o nivel anterior
                parent_code = code[:-2]

            if parent_code:
                try:
                    parent = Account.plain_objects.get(code=parent_code, tenant_id=tenant_id)
                    data['parent_account'] = parent
                except Account.DoesNotExist:
                    # Opcionalmente podrías lanzar error aquí si quieres jerarquía estricta
                    pass

        return data

    def create(self, validated_data):
        # El tenant_id es pasado por el viewset en perform_create
        # o recuperado del request inyectado por el middleware
        request = self.context.get('request')
        tenant_id = validated_data.get('tenant_id')

        if not tenant_id and 'tenant' in validated_data:
            tenant_id = validated_data['tenant'].id

        if not tenant_id and request:
            tenant_id = getattr(request, 'tenant_id', None)
            if not tenant_id and 'HTTP_X_TENANT_ID' in request.META:
                tenant_id = request.META['HTTP_X_TENANT_ID']
            if tenant_id:
                validated_data['tenant_id'] = tenant_id

        # Asegurar ChartOfAccounts
        if tenant_id and 'chart_of_accounts' not in validated_data:
            ChartOfAccounts = apps.get_model('core_erp', 'ChartOfAccounts')
            # Usar plain_objects para evitar el filtrado automático del TenantManager durante la creación/búsqueda
            chart = ChartOfAccounts.plain_objects.filter(tenant_id=tenant_id).first()

            if not chart:
                Tenant = apps.get_model('core_erp', 'Tenant')
                try:
                    tenant_obj = Tenant.plain_objects.get(pk=tenant_id)
                    chart = ChartOfAccounts.plain_objects.create(
                        tenant=tenant_obj,
                        name=f"Plan de Cuentas - {tenant_obj.name}"
                    )
                except Exception:
                    pass

            if chart:
                validated_data['chart_of_accounts'] = chart
                # Asegurar que el objeto tenant esté presente si tenemos el chart
                if 'tenant' not in validated_data:
                    validated_data['tenant'] = chart.tenant

        return super().create(validated_data)
