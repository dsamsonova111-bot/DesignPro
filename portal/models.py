from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Пользователь портала (с обязательным полем ФИО и уникальным Email)."""
    full_name = models.CharField('ФИО', max_length=150)
    email = models.EmailField('Email', unique=True)

    def __str__(self):
        return f'{self.username} ({self.full_name})'


class Category(models.Model):
    """Категория заявок (например, «3D-дизайн», «2D-дизайн», «Эскиз»)."""
    name = models.CharField('Название категории', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class DesignRequest(models.Model):
    """Заявка на разработку дизайна интерьера помещения."""
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    )

    title = models.CharField('Название заявки', max_length=200)
    description = models.TextField('Описание')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='requests'
    )
    photo = models.ImageField('Фото помещения или план', upload_to='rooms/')
    design_image = models.ImageField(
        'Готовый дизайн',
        upload_to='designs/',
        blank=True,
        null=True
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    comment = models.TextField('Комментарий администратора', blank=True)
    created_at = models.DateTimeField('Временная метка', auto_now_add=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='requests'
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'