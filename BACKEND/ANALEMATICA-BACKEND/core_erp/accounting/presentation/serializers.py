"""Read-only compatibility representations; financial writes use reviewed commands."""
from rest_framework import serializers
from ..models import Account,JournalEntry

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model=Account
        fields=('id','code','name','type','is_active','parent_account','chart_of_accounts')
        read_only_fields=fields

class JournalEntrySerializer(serializers.ModelSerializer):
    exchange_rate=serializers.DecimalField(max_digits=18,decimal_places=6,read_only=True,coerce_to_string=True)
    class Meta:
        model=JournalEntry
        fields=('id','date','reference','description','is_posted','period','currency',
                'base_currency','exchange_rate','hash_version','system_hash')
        read_only_fields=fields
