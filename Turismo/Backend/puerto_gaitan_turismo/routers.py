class DatabaseRouter:
    """
    Router para controlar las operaciones de base de datos en el sistema Sarita (Fase 18).
    Garantiza el aislamiento entre Wallet, Delivery y el Core.
    """
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'wallet':
            return 'wallet_db'
        if model._meta.app_label == 'delivery':
            return 'delivery_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'wallet':
            return 'wallet_db'
        if model._meta.app_label == 'delivery':
            return 'delivery_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Permitir relaciones si ambos están en la misma base de datos
        if obj1._meta.app_label == obj2._meta.app_label:
            return True

        # Excepción: Permitir relaciones con 'api' y 'companies' que están en default
        if obj1._meta.app_label in ['wallet', 'delivery'] and obj2._meta.app_label in ['api', 'companies']:
            return True
        if obj2._meta.app_label in ['wallet', 'delivery'] and obj1._meta.app_label in ['api', 'companies']:
            return True

        # Permitir relaciones generales con default
        if obj1._state.db == 'default' or obj2._state.db == 'default':
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'wallet':
            return db == 'wallet_db'
        if app_label == 'delivery':
            return db == 'delivery_db'

        # El resto va a default
        if db in ['wallet_db', 'delivery_db']:
            return False

        return db == 'default'
