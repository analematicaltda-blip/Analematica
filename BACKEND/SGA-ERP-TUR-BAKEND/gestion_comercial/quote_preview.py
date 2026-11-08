"""Non-binding price preview. No sales, tax invoices, payment or stock mutations."""
from decimal import Decimal
from uuid import UUID
from rest_framework.exceptions import ValidationError
from apps.turismo.services.company_identity import resolve_company
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product


def preview(user,data):
    if not isinstance(data,dict) or set(data)!={'provider_id','customer_id','lines'}:raise ValidationError('Solo se admiten prestador, cliente y líneas.')
    try:
        provider_id=UUID(str(data['provider_id']))
        raw_customer=data['customer_id']
        if type(raw_customer) is not int and not (isinstance(raw_customer,str) and raw_customer.isascii() and raw_customer.isdecimal()):raise ValueError()
        customer_id=int(raw_customer)
        if not 1<=customer_id<=9223372036854775807:raise ValueError()
    except (ValueError,TypeError):raise ValidationError('Identificadores inválidos.')
    link=resolve_company(user,provider_id)
    if not Cliente.objects.filter(pk=customer_id,perfil_id=provider_id).exists():raise ValidationError('Cliente no disponible en la empresa.')
    lines=data['lines']
    if not isinstance(lines,list) or not 1<=len(lines)<=50:raise ValidationError('Se requieren entre una y cincuenta líneas.')
    ids=[];quantities={}
    for line in lines:
        if not isinstance(line,dict) or set(line)!={'product_id','quantity'}:raise ValidationError('Cada línea requiere producto y cantidad; los precios se calculan en servidor.')
        try:product_id=UUID(str(line['product_id']))
        except (ValueError,TypeError):raise ValidationError('Producto inválido.')
        qty=line['quantity']
        if type(qty)is not int or not 1<=qty<=10000 or product_id in quantities:raise ValidationError('Cantidad inválida o producto duplicado.')
        ids.append(product_id);quantities[product_id]=qty
    products={p.pk:p for p in Product.objects.filter(pk__in=ids,provider_id=provider_id,is_active=True)}
    if len(products)!=len(ids):raise ValidationError('Hay productos no disponibles en la empresa.')
    subtotal=Decimal('0');result=[]
    for product_id in ids:
        p=products[product_id];price=p.base_price
        if price is None or str(price.currency)!=link.tenant.currency or not price.amount.is_finite() or price.amount<0:raise ValidationError('Moneda o tarifa requiere revisión; no se convierte moneda.')
        amount=(price.amount*quantities[product_id]).quantize(Decimal('0.01'))
        subtotal+=amount
        if subtotal>Decimal('9999999999999999.99'):raise ValidationError('Importe fuera de rango.')
        result.append({'product_id':str(product_id),'quantity':quantities[product_id],'unit_price':str(price.amount),'subtotal':str(amount)})
    return {'status':'NON_BINDING_PREVIEW','company_id':str(link.tenant_id),'currency':link.tenant.currency,'lines':result,'subtotal':str(subtotal),'taxes_calculated':False,'payable_total':None,'availability_checked':False,'stock_reserved':False,'financial_transaction_created':False}
