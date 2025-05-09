from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import CashFlow, Status, Type, Category, SubCategory
from .forms import CashFlowForm, CategoryForm, SubCategoryForm, StatusForm, TypeForm
from django.http import JsonResponse
from datetime import datetime
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages


# ======================== СПРАВОЧНИКИ ========================
class DictionaryListView(ListView):
    """Главная страница управления справочниками"""
    template_name = 'cash_flow/dictionaries.html'
    
    def get_queryset(self):
        """Не требуется queryset, так как используем get_context_data"""
        return None
    
    def get_context_data(self, **kwargs):
        """Добавляем все справочники в контекст шаблона"""
        context = super().get_context_data(**kwargs)
        context['statuses'] = Status.objects.all()
        context['types'] = Type.objects.all()
        context['categories'] = Category.objects.all()
        context['subcategories'] = SubCategory.objects.all()
        return context


# ======================== CRUD ДЛЯ СТАТУСОВ ========================
class StatusCreateView(CreateView):
    """Создание нового статуса"""
    model = Status
    form_class = StatusForm
    template_name = 'cash_flow/status_create.html'
    success_url = reverse_lazy('dictionaries')

    def form_invalid(self, form):
        """Обработка невалидной формы с выводом ошибок"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)
    
class StatusUpdateView(UpdateView):
    """Редактирование существующего статуса"""
    model = Status
    fields = ['name']  # Поля для редактирования
    template_name = 'cash_flow/status_edit.html'
    success_url = reverse_lazy('dictionaries')

class StatusDeleteView(DeleteView):
    """Удаление статуса с подтверждением"""
    model = Status
    template_name = 'cash_flow/status_delete.html'
    success_url = reverse_lazy('dictionaries')

    def get_context_data(self, **kwargs):
        """Добавляем количество связанных записей в контекст"""
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['related_records_count'] = obj.cashflow_set.count() if obj and obj.pk else 0
        return context

    def delete(self, request, *args, **kwargs):
        """Обработка удаления с выводом сообщения"""
        try:
            self.object = self.get_object()
            if not self.object.pk:
                raise ValueError("Не удалось получить объект для удаления")
                
            related_count = self.object.cashflow_set.count()
            response = super().delete(request, *args, **kwargs)
            
            messages.success(
                request,
                f'Статус "{self.object.name}" и {related_count} связанных записей успешно удалены'
            )
            return response
            
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')
            return redirect('dictionaries')


# ======================== CRUD ДЛЯ ТИПОВ ========================
class TypeCreateView(CreateView):
    """Создание нового типа операции"""
    model = Type
    form_class = TypeForm
    template_name = 'cash_flow/type_create.html'
    success_url = reverse_lazy('dictionaries')
    
    def form_invalid(self, form):
        """Обработка ошибок валидации"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)

class TypeUpdateView(UpdateView):
    """Редактирование типа операции"""
    model = Type
    fields = ['name']
    template_name = 'cash_flow/type_edit.html'
    success_url = reverse_lazy('dictionaries')

class TypeDeleteView(DeleteView):
    """Удаление типа операции"""
    model = Type
    template_name = 'cash_flow/type_delete.html'
    success_url = reverse_lazy('dictionaries')
    
    def get_context_data(self, **kwargs):
        """Добавление информации о связанных записях"""
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['related_records_count'] = obj.cashflow_set.count() if obj.pk else 0
        return context

    def delete(self, request, *args, **kwargs):
        """Обработка удаления с информированием пользователя"""
        try:
            self.object = self.get_object()
            related_count = self.object.cashflow_set.count()
            response = super().delete(request, *args, **kwargs)
            
            messages.success(
                request,
                f'Тип "{self.object.name}" и {related_count} связанных записей успешно удалены'
            )
            return response
            
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')
            return redirect('dictionaries')


# ======================== CRUD ДЛЯ КАТЕГОРИЙ ========================
class CategoryCreateView(CreateView):
    """Создание новой категории"""
    model = Category
    form_class = CategoryForm
    template_name = 'cash_flow/category_create.html'
    success_url = reverse_lazy('dictionaries')

    def form_invalid(self, form):
        """Вывод ошибок валидации формы"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)
    
class CategoryUpdateView(UpdateView):
    """Редактирование существующей категории"""
    model = Category
    form_class = CategoryForm
    template_name = 'cash_flow/category_edit.html'
    success_url = reverse_lazy('dictionaries')

    def form_valid(self, form):
        """Обработка случая, когда тип не выбран"""
        if not form.cleaned_data['type']:
            form.instance.type = None
        return super().form_valid(form)

class CategoryDeleteView(DeleteView):
    """Удаление категории с подтверждением"""
    model = Category
    template_name = 'cash_flow/category_delete.html'
    success_url = reverse_lazy('dictionaries')
    
    def get_context_data(self, **kwargs):
        """Подготовка данных о связанных объектах"""
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        
        # Считаем все связанные записи (операции + подкатегории)
        context['related_records_count'] = obj.cashflow_set.count() + obj.subcategory_set.count()
        
        # Детализация для информационного сообщения
        context['cashflow_count'] = obj.cashflow_set.count()
        context['subcategory_count'] = obj.subcategory_set.count()
        
        return context

    def delete(self, request, *args, **kwargs):
        """Обработка удаления с подробным сообщением"""
        try:
            self.object = self.get_object()
            cashflow_count = self.object.cashflow_set.count()
            subcategory_count = self.object.subcategory_set.count()
            total_count = cashflow_count + subcategory_count
            
            response = super().delete(request, *args, **kwargs)
            
            messages.success(
                request,
                f'Категория "{self.object.name}" и {total_count} связанных элементов удалены '
                f'({cashflow_count} операций, {subcategory_count} подкатегорий)'
            )
            return response
            
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')
            return redirect('dictionaries')


# ======================== CRUD ДЛЯ ПОДКАТЕГОРИЙ ========================
class SubCategoryCreateView(CreateView):
    """Создание новой подкатегории"""
    model = SubCategory
    form_class = SubCategoryForm
    template_name = 'cash_flow/subcategory_create.html'
    success_url = reverse_lazy('dictionaries')

    def form_invalid(self, form):
        """Обработка ошибок валидации"""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)
    
    def get_form_kwargs(self):
        """Добавляем список категорий для формы"""
        kwargs = super().get_form_kwargs()
        kwargs['categories'] = Category.objects.all()
        return kwargs

class SubCategoryUpdateView(UpdateView):
    """Редактирование подкатегории"""
    model = SubCategory
    form_class = SubCategoryForm
    template_name = 'cash_flow/subcategory_edit.html'
    success_url = reverse_lazy('dictionaries')

class SubCategoryDeleteView(DeleteView):
    """Удаление подкатегории"""
    model = SubCategory
    template_name = 'cash_flow/subcategory_delete.html'
    success_url = reverse_lazy('dictionaries')
    
    def get_context_data(self, **kwargs):
        """Добавление информации о связанных записях"""
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['related_records_count'] = obj.cashflow_set.count() if obj.pk else 0
        return context

    def delete(self, request, *args, **kwargs):
        """Обработка удаления с информированием пользователя"""
        try:
            self.object = self.get_object()
            related_count = self.object.cashflow_set.count()
            response = super().delete(request, *args, **kwargs)
            
            messages.success(
                request,
                f'Подкатегория "{self.object.name}" и {related_count} связанных записей успешно удалены'
            )
            return response
            
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')
            return redirect('dictionaries')


# ======================== ОПЕРАЦИИ С ДЕНЕЖНЫМИ ПОТОКАМИ ========================
class CashFlowListView(ListView):
    """Список денежных операций с фильтрацией"""
    model = CashFlow
    template_name = 'cash_flow/index.html'
    context_object_name = 'cashflows'
    paginate_by = 20
    ordering = ['-date']  # Сортировка по дате (новые сверху)
    
    def get_queryset(self):
        """Применение фильтров к списку операций"""
        queryset = super().get_queryset()
        request = self.request
        
        # Фильтрация по дате (период)
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if date_from and date_to:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(date__range=[date_from, date_to])
            except ValueError:
                pass  # Неверный формат даты - игнорируем фильтр

        # Фильтрация по статусу
        status = request.GET.get('status')
        if status and status != 'all':
            queryset = queryset.filter(status_id=status)

        # Фильтрация по типу операции
        type_id = request.GET.get('type')
        if type_id and type_id != 'all':
            queryset = queryset.filter(type_id=type_id)

        # Фильтрация по категории
        category_id = request.GET.get('category')
        if category_id and category_id != 'all':
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        """Добавление данных для фильтров в контекст"""
        context = super().get_context_data(**kwargs)
        context['statuses'] = Status.objects.all()
        context['types'] = Type.objects.all()
        context['categories'] = Category.objects.all()
        
        # Сохранение текущих параметров фильтрации
        context['current_filters'] = {
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'status': self.request.GET.get('status', 'all'),
            'type': self.request.GET.get('type', 'all'),
            'category': self.request.GET.get('category', 'all'),
        }
        return context

def create_cashflow(request):
    """Создание новой денежной операции (функциональное представление)"""
    if request.method == 'POST':
        form = CashFlowForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CashFlowForm()
    
    return render(request, 'cash_flow/create.html', {'form': form})

def edit_cashflow(request, pk):
    """Редактирование существующей операции"""
    cashflow = get_object_or_404(CashFlow, pk=pk)
    if request.method == 'POST':
        form = CashFlowForm(request.POST, instance=cashflow)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CashFlowForm(instance=cashflow)
    
    return render(request, 'cash_flow/edit.html', {'form': form})

def get_subcategories(request):
    """AJAX-запрос для получения подкатегорий по категории"""
    category_id = request.GET.get('category_id')
    if category_id:
        subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)

def delete_cashflow(request, pk):
    """Удаление денежной операции"""
    cashflow = get_object_or_404(CashFlow, pk=pk)
    if request.method == 'POST':
        cashflow.delete()
        return redirect('index')
    
    return render(request, 'cash_flow/delete.html', {'cashflow': cashflow})