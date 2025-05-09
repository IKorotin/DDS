from django.urls import path
from .views import (
    create_cashflow, edit_cashflow, delete_cashflow, get_subcategories,    
    DictionaryListView, CashFlowListView,
    StatusCreateView, StatusUpdateView, StatusDeleteView,
    TypeCreateView, TypeUpdateView, TypeDeleteView,
    CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    SubCategoryCreateView, SubCategoryUpdateView, SubCategoryDeleteView
)

# Основные URL-шаблоны приложения
urlpatterns = [
    # ==================== СПРАВОЧНИКИ ====================
    path('dictionaries/', DictionaryListView.as_view(), name='dictionaries'),
    
    # ---------- Статусы ----------
    # Создание нового статуса
    path('dictionaries/status/add/', 
         StatusCreateView.as_view(), 
         name='status_create'),
    
    # Редактирование существующего статуса
    path('dictionaries/status/<int:pk>/edit/', 
         StatusUpdateView.as_view(), 
         name='status_update'),
    
    # Удаление статуса (требует подтверждения)
    path('dictionaries/status/<int:pk>/delete/', 
         StatusDeleteView.as_view(), 
         name='status_delete'),
    
    # ---------- Типы операций ----------
    # Создание нового типа операции
    path('dictionaries/type/add/', 
         TypeCreateView.as_view(), 
         name='type_create'),
    
    # Редактирование типа
    path('dictionaries/type/<int:pk>/edit/', 
         TypeUpdateView.as_view(), 
         name='type_update'),
    
    # Удаление типа
    path('dictionaries/type/<int:pk>/delete/', 
         TypeDeleteView.as_view(), 
         name='type_delete'),
    
    # ---------- Категории ----------
    # Создание новой категории
    path('dictionaries/category/add/', 
         CategoryCreateView.as_view(), 
         name='category_create'),
    
    # Редактирование категории
    path('dictionaries/category/<int:pk>/edit/', 
         CategoryUpdateView.as_view(), 
         name='category_update'),
    
    # Удаление категории (с каскадным удалением подкатегорий)
    path('dictionaries/category/<int:pk>/delete/', 
         CategoryDeleteView.as_view(), 
         name='category_delete'),
    
    # ---------- Подкатегории ----------
    # Создание подкатегории (с выбором родительской категории)
    path('dictionaries/subcategory/add/', 
         SubCategoryCreateView.as_view(), 
         name='subcategory_create'),
    
    # Редактирование подкатегории
    path('dictionaries/subcategory/<int:pk>/edit/', 
         SubCategoryUpdateView.as_view(), 
         name='subcategory_update'),
    
    # Удаление подкатегории
    path('dictionaries/subcategory/<int:pk>/delete/', 
         SubCategoryDeleteView.as_view(), 
         name='subcategory_delete'),
    
    # ==================== ОСНОВНЫЕ СТРАНИЦЫ ====================
    # Главная страница - список денежных операций
    path('', 
         CashFlowListView.as_view(), 
         name='index'),
    
    # Создание новой денежной операции
    path('create/', 
         create_cashflow, 
         name='create'),
    
    # Редактирование существующей операции
    path('edit/<int:pk>/', 
         edit_cashflow, 
         name='edit'),
    
    # Удаление операции (требует подтверждения)
    path('delete/<int:pk>/', 
         delete_cashflow, 
         name='delete'),
    
    # ==================== API ЭНДПОИНТЫ ====================
    # AJAX-запрос для получения подкатегорий по выбранной категории
    path('api/subcategories/', 
         get_subcategories, 
         name='get_subcategories'),
]