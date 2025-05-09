from django import forms
from .models import CashFlow, Status, Type, Category, SubCategory
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class StatusForm(forms.ModelForm):
    """Форма для создания/редактирования статусов"""
    class Meta:
        model = Status
        fields = ['name']  # Используем только поле name
        error_messages = {
            'name': {
                'unique': _('Статус с таким названием уже существует'),
            },
        }

    def clean_name(self):
        """Валидация уникальности названия статуса (без учета регистра)"""
        name = self.cleaned_data['name']
        # Проверяем существование статуса с таким же именем, исключая текущий объект (если он есть)
        if Status.objects.filter(name__iexact=name).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise ValidationError(_('Статус с таким названием уже существует'))
        return name

class TypeForm(forms.ModelForm):
    """Форма для работы с типами операций"""
    class Meta:
        model = Type
        fields = ['name']
        error_messages = {
            'name': {
                'unique': _('Тип с таким названием уже существует'),
            },
        }

    def clean_name(self):
        """Проверка уникальности названия типа"""
        name = self.cleaned_data['name']
        if Type.objects.filter(name__iexact=name).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise ValidationError(_('Тип с таким названием уже существует'))
        return name

class CategoryForm(forms.ModelForm):
    """Форма для категорий"""
    class Meta:
        model = Category
        fields = ['name']  # Только поле названия (без привязки к типу)
        error_messages = {
            'name': {
                'unique': _('Категория с таким названием уже существует'),
            },
        }

    def clean_name(self):
        """Валидация уникальности названия категории"""
        name = self.cleaned_data['name']
        if Category.objects.filter(name__iexact=name).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise ValidationError(_('Категория с таким названием уже существует'))
        return name

class SubCategoryForm(forms.ModelForm):
    """Форма для подкатегорий с привязкой к категории"""
    class Meta:
        model = SubCategory
        fields = ['name', 'category']  # Название и родительская категория
        error_messages = {
            'name': {
                'unique': _('Подкатегория с таким названием уже существует в выбранной категории'),
            },
        }

    def clean(self):
        """Проверка уникальности пары название+категория"""
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        category = cleaned_data.get('category')
        
        if name and category:
            # Ищем подкатегории с таким же именем в выбранной категории
            qs = SubCategory.objects.filter(
                name__iexact=name,
                category=category
            )
            # Исключаем текущую запись при редактировании
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
                
            if qs.exists():
                raise ValidationError(
                    {'name': _('Подкатегория с таким названием уже существует в выбранной категории')}
                )
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        """Инициализация формы с возможностью передачи списка категорий"""
        categories = kwargs.pop('categories', None)
        super().__init__(*args, **kwargs)
        
        # Настраиваем queryset для выбора категорий
        if categories:
            self.fields['category'].queryset = categories
        else:
            self.fields['category'].queryset = Category.objects.none()
            
        # Настройка поля категории
        self.fields['category'].empty_label = "Выберите категорию"
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        
        
class CashFlowForm(forms.ModelForm):
    """Основная форма для операций денежного потока"""
    class Meta:
        model = CashFlow
        fields = ['date', 'status', 'type', 'category', 'subcategory', 'amount', 'comment']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',  # Используем HTML5 date input
                    'class': 'form-control',
                    'value': date.today().strftime('%Y-%m-%d')  # Значение по умолчанию - сегодня
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-select',
                    'placeholder': 'Выберите статус'
                }
            ),
            'type': forms.Select(
                attrs={
                    'class': 'form-select',
                    'placeholder': 'Выберите тип операции'
                }
            ),
            'category': forms.Select(
                attrs={
                    'class': 'form-select',
                    'placeholder': 'Выберите категорию'
                }
            ),
            'subcategory': forms.Select(
                attrs={
                    'class': 'form-select',
                    'placeholder': 'Выберите подкатегорию',
                    'disabled': True  # Поле будет разблокировано после выбора категории
                }
            ),
            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите сумму в рублях'
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Необязательный комментарий'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы с динамической загрузкой подкатегорий"""
        super().__init__(*args, **kwargs)
        
        # Изначально подкатегории не загружены
        self.fields['subcategory'].queryset = SubCategory.objects.none()
        
        # Если форма отправляется (POST запрос)
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                # Загружаем подкатегории для выбранной категории
                self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id)
                self.fields['subcategory'].widget.attrs['disabled'] = False
            except (ValueError, TypeError):
                pass  # Игнорируем ошибки преобразования
        # Если форма редактирует существующую запись
        elif self.instance.pk:
            self.fields['subcategory'].queryset = self.instance.category.subcategory_set.all()
            self.fields['subcategory'].widget.attrs['disabled'] = False