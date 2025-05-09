from django.apps import AppConfig

class CashFlowConfig(AppConfig):
    """
    Конфигурация приложения 'cash_flow' (Управление денежными потоками).
    
    Наследуется от базового класса AppConfig Django для настройки параметров приложения.
    """

    # Тип поля для автоматического создания первичных ключей
    # BigAutoField - 64-битное целое число (рекомендуется для новых проектов)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Имя приложения в формате Python path (как указано в INSTALLED_APPS)
    name = 'cash_flow'