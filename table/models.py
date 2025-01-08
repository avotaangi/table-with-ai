from django.db import models


class QueryLog(models.Model):
    query_text = models.TextField()
    response_data = models.TextField()  # Хранит исходную таблицу в текстовом формате
    table_data = models.JSONField(default=list)  # Хранит таблицу в виде JSON
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Журнал запросов"
        verbose_name_plural = "Журналы запросов"
        ordering = ['-created_at']  # Сортировка по времени запроса в порядке убывания

    def __str__(self):
        return f"Запрос: {self.query_text[:50]}... | Время: {self.created_at}"
