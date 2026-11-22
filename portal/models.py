import os
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

def validate_room_image(file):
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError('Разрешены только форматы: jpg, jpeg, png, bmp.')

    max_size = 2 * 1024 * 1024  # 2 МБ
    if file.size > max_size:
        raise ValidationError('Максимальный размер файла — 2 МБ.')


class CustomUser(AbstractUser):
    full_name = models.CharField('ФИО', max_length=255)

    def __str__(self):
        return self.full_name or self.username


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class DesignRequest(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'Принято в работу'),
        (STATUS_COMPLETED, 'Выполнено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='design_requests',
        verbose_name='Пользователь',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='design_requests',
        verbose_name='Категория',
    )
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    photo = models.ImageField(
        'Фото помещения или план',
        upload_to='rooms/',
        validators=[validate_room_image],
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )
    comment = models.TextField('Комментарий к работе', blank=True, null=True)
    design_image = models.ImageField(
        'Изображение дизайна',
        upload_to='designs/',
        blank=True,
        null=True,
        validators=[validate_room_image],
    )
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на дизайн'
        verbose_name_plural = 'Заявки на дизайн'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'