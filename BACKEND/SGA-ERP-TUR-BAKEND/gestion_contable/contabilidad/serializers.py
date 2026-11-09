"""Account metadata only: balances and company scope are never supplied by clients."""
from rest_framework import serializers
from apps.core_erp.accounting.models import Account,ChartOfAccounts,LedgerEntry

class PlanCuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Account
        fields=['id','code','name','type','parent_account','initial_balance','is_active','ifrs_mapping']
        read_only_fields=['id','type','initial_balance']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['parent_account'].queryset=Account.plain_objects.filter(tenant_id=self.context.get('accounting_tenant_id'))

    def validate_code(self,value):
        if not value.isdigit() or len(value) not in [1,2,4,6,8,10] or value[0] not in '123456789':
            raise serializers.ValidationError('Código PUC inválido.')
        return value

    def validate(self,data):
        tenant_id=self.context.get('accounting_tenant_id')
        if tenant_id is None:raise serializers.ValidationError('Empresa contable verificada requerida.')
        forbidden=set(self.initial_data)-{'code','name','parent_account','is_active','ifrs_mapping'}
        if forbidden:raise serializers.ValidationError('No se permiten campos de identidad, saldo o tipo derivados del servidor.')
        code=data.get('code',getattr(self.instance,'code',None))
        if not code:raise serializers.ValidationError('El código es obligatorio.')
        if self.instance and LedgerEntry.plain_objects.filter(account=self.instance,journal_entry__is_posted=True).exists():
            for key in ('code','parent_account'):
                if key in data and data[key]!=getattr(self.instance,key):
                    raise serializers.ValidationError('No se puede reclasificar una cuenta con movimientos contabilizados.')
        data['type']={'1':'ASSET','2':'LIABILITY','3':'EQUITY','4':'REVENUE','5':'EXPENSE','6':'COST_OF_SALES','7':'PRODUCTION_COST','8':'DEBTOR_ORDER','9':'CREDITOR_ORDER'}[code[0]]
        chart_id=getattr(self.instance,'chart_of_accounts_id',None)
        duplicate=Account.plain_objects.filter(tenant_id=tenant_id,code=code)
        if self.instance:duplicate=duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():raise serializers.ValidationError('Código de cuenta existente o ambiguo en esta empresa.')
        parent=data.get('parent_account',getattr(self.instance,'parent_account',None))
        if parent:
            if str(parent.tenant_id)!=str(tenant_id) or (chart_id and parent.chart_of_accounts_id!=chart_id):
                raise serializers.ValidationError('El padre debe pertenecer al mismo plan y empresa.')
            visited={self.instance.pk} if self.instance else set()
            cursor=parent
            while cursor:
                if cursor.pk in visited or len(visited)>100:raise serializers.ValidationError('Ciclo contable no permitido.')
                visited.add(cursor.pk)
                if str(cursor.tenant_id)!=str(tenant_id):raise serializers.ValidationError('Jerarquía de otra empresa.')
                cursor=cursor.parent_account
        return data

    def create(self,validated_data):
        company=validated_data.pop('tenant')
        charts=list(ChartOfAccounts.plain_objects.filter(tenant=company).order_by('pk')[:2])
        if len(charts)>1:raise serializers.ValidationError('Seleccione/reconcilie un único plan contable antes de crear cuentas.')
        chart=charts[0] if charts else ChartOfAccounts.plain_objects.create(tenant=company,name='Plan contable empresarial')
        parent=validated_data.get('parent_account')
        if parent and parent.chart_of_accounts_id!=chart.pk:raise serializers.ValidationError('Padre de otro plan.')
        return Account.plain_objects.create(tenant=company,chart_of_accounts=chart,**validated_data)
