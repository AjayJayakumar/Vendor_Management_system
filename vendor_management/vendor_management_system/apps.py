from django.apps import AppConfig


class VendorManagementSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vendor_management_system'

    def ready(self):
        import vendor_management_system.signals
