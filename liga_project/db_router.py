class DatabaseRouter:
    auth_apps = {
        'auth',
        'admin',
        'contenttypes',
        'sessions',
        'authtoken',
    }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.auth_apps:
            return 'auth_db'

        if model._meta.app_label == 'league' and model._meta.model_name == 'userprofile':
            return 'auth_db'

        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.auth_apps:
            return 'auth_db'

        if model._meta.app_label == 'league' and model._meta.model_name == 'userprofile':
            return 'auth_db'

        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.auth_apps:
            return db == 'auth_db'

        if app_label == 'league' and model_name == 'userprofile':
            return db == 'auth_db'

        if app_label == 'league':
            return db == 'default'

        return db == 'default'