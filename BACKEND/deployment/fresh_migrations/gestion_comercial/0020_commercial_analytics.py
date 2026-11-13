from django.db import migrations,models
class Migration(migrations.Migration):
    dependencies=[('gestion_comercial','0019_commercial_army')]
    operations=[
        migrations.CreateModel(name='AnalyticsRecord',fields=[('id',models.CharField(max_length=36,primary_key=True,serialize=False)),('scope',models.CharField(max_length=96,db_index=True)),('provider_ref',models.CharField(max_length=36,db_index=True)),('code',models.CharField(max_length=100,db_index=True)),('revision',models.PositiveIntegerField()),('status',models.CharField(max_length=20,db_index=True)),('document',models.JSONField()),('document_digest',models.CharField(max_length=64))],options={'db_table':'erp_analytics_job','constraints':[models.UniqueConstraint(fields=('scope','provider_ref','code'),name='erp_analytics_scope_code')]}),
        migrations.CreateModel(name='AnalyticsEvent',fields=[('sequence',models.BigAutoField(primary_key=True,serialize=False)),('id',models.CharField(max_length=36,unique=True)),('scope',models.CharField(max_length=96,db_index=True)),('item_id',models.CharField(max_length=36,null=True,db_index=True)),('document',models.JSONField())],options={'db_table':'erp_analytics_event'}),
]
