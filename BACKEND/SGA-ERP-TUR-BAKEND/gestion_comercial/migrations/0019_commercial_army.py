from django.db import migrations,models
class Migration(migrations.Migration):
    dependencies=[('gestion_comercial','0018_ads')]
    operations=[
        migrations.CreateModel(name='ArmyRecord',fields=[('id',models.CharField(max_length=36,primary_key=True,serialize=False)),('scope',models.CharField(max_length=96,db_index=True)),('provider_ref',models.CharField(max_length=36,db_index=True)),('code',models.CharField(max_length=100,db_index=True)),('revision',models.PositiveIntegerField()),('status',models.CharField(max_length=20,db_index=True)),('document',models.JSONField()),('document_digest',models.CharField(max_length=64))],options={'db_table':'erp_army_job','constraints':[models.UniqueConstraint(fields=('scope','provider_ref','code'),name='erp_army_scope_code')]}),
        migrations.CreateModel(name='ArmyEvent',fields=[('sequence',models.BigAutoField(primary_key=True,serialize=False)),('id',models.CharField(max_length=36,unique=True)),('scope',models.CharField(max_length=96,db_index=True)),('item_id',models.CharField(max_length=36,null=True,db_index=True)),('document',models.JSONField())],options={'db_table':'erp_army_event'}),
]
