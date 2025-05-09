from django.db import models

class Status(models.Model):
    """
    Модель статуса операции (например: Бизнес, Личное, Налог)
    """
    name = models.CharField(
        max_length=100, 
        unique=True,  # Гарантирует уникальность названий
        verbose_name="Название статуса"
    )
    
    def __str__(self):
        """Строковое представление объекта (используется в админке и формах)"""
        return self.name

class Type(models.Model):
    """
    Модель типа операции (например: Пополнение, Списание)
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Тип операции"
    )
    
    def __str__(self):
        return self.name

class Category(models.Model):
    """
    Модель категории операций (например: Инфраструктура, Маркетинг)
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Название категории"
    )
    
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    """
    Модель подкатегории, связанная с категорией
    (например: для категории "Маркетинг" - "Farpost", "Avito")
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Название подкатегории"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,  # Удаление подкатегорий при удалении категории
        verbose_name="Родительская категория"
    )
    
    class Meta:
        # Уникальность комбинации названия и категории
        unique_together = ('name', 'category')
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
    
    def __str__(self):
        return f"{self.name} ({self.category})"  # Формат: "Название (Категория)"

class CashFlow(models.Model):
    """
    Основная модель для учета денежных потоков (доходы/расходы)
    """
    date = models.DateField(
        verbose_name="Дата операции"
    )
    status = models.ForeignKey(
        Status, 
        on_delete=models.CASCADE,  # Удаление операций при удалении статуса
        verbose_name="Статус"
    )
    type = models.ForeignKey(
        Type, 
        on_delete=models.CASCADE,
        verbose_name="Тип операции"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    subcategory = models.ForeignKey(
        SubCategory, 
        on_delete=models.CASCADE,
        verbose_name="Подкатегория"
    )
    amount = models.DecimalField(
        max_digits=12,  # Максимум 12 цифр
        decimal_places=2,  # 2 знака после запятой
        verbose_name="Сумма"
    )
    comment = models.TextField(
        blank=True,  # Необязательное поле
        null=True,  # Может быть NULL в БД
        verbose_name="Комментарий"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,  # Устанавливается при создании
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,  # Обновляется при каждом сохранении
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Денежный поток"
        verbose_name_plural = "Денежные потоки"
        ordering = ['-date']  # Сортировка по дате (новые сверху)
    
    def __str__(self):
        """Формат: "Дата - Тип - Сумма" (например: 2023-01-15 - Пополнение - 1000.00)"""
        return f"{self.date} - {self.type} - {self.amount}"