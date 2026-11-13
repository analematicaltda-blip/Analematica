from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('wallet', '0004_device_trust_and_independent_enrollment')]
    operations = [
        migrations.AddField(model_name='wallettransferintent',name='consent_by_id',field=models.PositiveBigIntegerField(null=True)),
        migrations.AddField(model_name='wallettransferintent',name='consent_digest',field=models.CharField(max_length=64,blank=True)),
        migrations.AddField(model_name='wallettransferintent',name='consent_at',field=models.DateTimeField(null=True)),
        migrations.AddField(model_name='wallettransferintent',name='purpose',field=models.JSONField(default=dict,blank=True)),
        migrations.AddField(model_name='wallettransferintent',name='renewed_from',field=models.OneToOneField(null=True,on_delete=django.db.models.deletion.PROTECT,related_name='renewal',to='wallet.wallettransferintent')),
        migrations.AlterField(model_name='wallettransferintent',name='state',field=models.CharField(max_length=12,default='PENDING',choices=[('PENDING','Pending'),('REVIEWED','Reviewed'),('EXECUTED','Executed'),('CANCELLED','Cancelled')])),
    ]
