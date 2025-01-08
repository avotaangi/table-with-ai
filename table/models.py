from django.db import models


class QueryLog(models.Model):
    # Поле для текста запроса
    query_text = models.TextField(verbose_name="Текст запроса")

    # Поле для времени запроса
    query_time = models.DateTimeField(auto_now_add=True, verbose_name="Время запроса")

    # Поле для ответа в формате строки
    response_data = models.TextField(verbose_name="Ответ (таблица в строковом формате)")

    class Meta:
        verbose_name = "Журнал запросов"
        verbose_name_plural = "Журналы запросов"
        ordering = ['-query_time']  # Сортировка по времени запроса в порядке убывания

    def __str__(self):
        return f"Запрос: {self.query_text[:50]}... | Время: {self.query_time}"
