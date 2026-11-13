from django.db import migrations,models
class Migration(migrations.Migration):
    dependencies=[('admin_plataforma','0011_media_library')]
    operations=[migrations.AddField(model_name='quotationasset',name='provider_ref',field=models.CharField(max_length=36,null=True,db_index=True))]
