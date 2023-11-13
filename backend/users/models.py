from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import validate_email, RegexValidator


class CustomUser(AbstractUser):

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        validators=[RegexValidator(r'^[\w.@+-]+\Z')],
        unique=True)
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False)
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        validators=[validate_email],
        unique=True)
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}: {self.email}'


class Follow(models.Model):

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )]

    def __str__(self):
        return f'{self.user.username} -> {self.author.username}'
