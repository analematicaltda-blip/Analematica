"""Restore fields used by the CRM producer; legacy unknowns stay unknown."""
from django.db import migrations,models
class Migration(migrations.Migration):
    dependencies=[('comercial','0001_initial')]
    operations=[
        migrations.AddField(model_name='lead',name='industry',field=models.CharField(max_length=100,blank=True,default='')),
        migrations.AddField(model_name='lead',name='company_size',field=models.CharField(max_length=30,blank=True,default='')),
        migrations.AddField(model_name='opportunity',name='expected_plan',field=models.CharField(max_length=100,blank=True,default='')),
        migrations.AddField(model_name='opportunity',name='probability',field=models.PositiveSmallIntegerField(null=True,blank=True)),
        migrations.AlterField(model_name='opportunity',name='stage',field=models.CharField(max_length=20,default='prospecting',choices=[('prospecting','Prospecting'),('proposal','Proposal'),('negotiation','Negotiation'),('won','Won'),('lost','Lost')])),
    ]
