from django.contrib import admin
from .models import QueryLog


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'query_text', 'created_at', 'short_response')  # Заменили query_time на created_at
    search_fields = ('query_text', 'response_data')
    list_filter = ('created_at',)  # Заменили query_time на created_at
    fields = ('query_text', 'created_at', 'response_data')
    readonly_fields = ('created_at', 'response_data')  # Заменили query_time на created_at

    def short_response(self, obj):
        return obj.response_data[:50] + ('...' if len(obj.response_data) > 50 else '')

    short_response.short_description = 'Краткий ответ'
