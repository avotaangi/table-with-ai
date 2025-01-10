import json
import os
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import QueryLog
from gigachat.models import Chat, Messages, MessagesRole
from gigachat import GigaChat
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def parse_table_to_json(table_str):
    """Конвертирует строковую таблицу в JSON."""
    data = [row.split('|')[1:-1] for row in table_str.splitlines() if '|' in row and '-' not in row]
    if not data:
        raise None
    headers = data.pop(0)
    return [dict(zip(headers, row)) for row in data]


def query_list(request):
    """Список всех запросов."""
    queries = QueryLog.objects.all()
    return render(request, 'table/query_list.html', {'queries': queries})


def query_create(request):
    """Создание нового запроса."""
    if request.method == 'POST':
        query_text = request.POST.get('query_text')
        payload = Chat(
            messages=[
                Messages(
                    role=MessagesRole.SYSTEM,
                    content="Ты бот, который составляет таблицы на основе текстовых запросов"
                )
            ],
            temperature=0.7,
        )
        # Отправляем запрос в GigaChat
        with GigaChat(credentials=os.getenv("ACCESS_TOKEN"), verify_ssl_certs=False) as giga:
            payload.messages.append(Messages(role=MessagesRole.USER, content=query_text))
            response = giga.chat(payload)
            payload.messages.append(response.choices[0].message)
            response_text = response.choices[0].message.content
        logger.debug(f"GigaChat response: {response_text}")
        # Конвертируем данные таблицы в JSON
        table_data = parse_table_to_json(response_text)
        # Сохраняем в базе
        query = QueryLog.objects.create(
            query_text=query_text,
            response_data=response_text,
            table_data=table_data
        )
        return redirect('query_result', pk=query.pk)
    return render(request, 'table/query_create.html')


def query_result(request, pk):
    """Просмотр результата запроса."""
    query = get_object_or_404(QueryLog, pk=pk)
    return render(request, 'table/query_result.html', {'query': query})


def query_edit(request, pk):
    """Редактирование запроса."""
    query = get_object_or_404(QueryLog, pk=pk)
    if request.method == 'POST':
        query_text = request.POST.get('query_text')
        payload = Chat(
            messages=[
                Messages(
                    role=MessagesRole.SYSTEM,
                    content="Ты бот, который составляет таблицы на основе текстовых запросов"
                )
            ],
            temperature=0.7,
        )
        # Отправляем запрос в GigaChat
        with GigaChat(credentials=os.getenv("ACCESS_TOKEN"), verify_ssl_certs=False) as giga:
            payload.messages.append(Messages(role=MessagesRole.USER, content=query_text))
            response = giga.chat(payload)
            payload.messages.append(response.choices[0].message)
            response_text = response.choices[0].message.content
        # Конвертируем данные таблицы в JSON
        table_data = parse_table_to_json(response_text)
        # Обновляем данные в QueryLog
        query.query_text = query_text
        query.response_data = response_text
        query.table_data = table_data
        query.save()
        return redirect('query_result', pk=query.pk)
    return render(request, 'table/query_edit.html', {'query': query})


@csrf_exempt
def query_save(request, pk):
    """Сохранение изменений в таблице."""
    query = get_object_or_404(QueryLog, pk=pk)
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            table_data = body.get('table_data', [])
            logger.debug(f"Received table_data: {table_data}")

            if not table_data or len(table_data) < 2:
                logger.error("Некорректные данные таблицы.")
                return JsonResponse({'status': 'failed', 'message': 'Некорректные данные таблицы'}, status=400)

            headers = table_data[0]
            rows = table_data[1:]
            query.table_data = [dict(zip(headers, row)) for row in rows if len(row) == len(headers)]
            query.save()
            logger.info("Таблица успешно сохранена.")
            return JsonResponse({'status': 'success'})
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.exception("Ошибка при обработке данных таблицы.")
            return JsonResponse({'status': 'failed', 'message': 'Ошибка при обработке данных таблицы'}, status=400)
    logger.warning("Метод не поддерживается.")
    return JsonResponse({'status': 'failed', 'message': 'Метод не поддерживается'}, status=405)

def query_download(request, pk, file_format):
    """Скачивание таблицы в формате XLSX или CSV."""
    query = get_object_or_404(QueryLog, pk=pk)
    df = pd.DataFrame(query.table_data)
    response = HttpResponse(content_type=f'text/{file_format}')
    if file_format == 'csv':
        response['Content-Disposition'] = f'attachment; filename="query_{pk}.csv"'
        df.to_csv(response, index=False)
    elif file_format == 'xlsx':
        response['Content-Disposition'] = f'attachment; filename="query_{pk}.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
    return response

def query_delete(request, pk):
    """Удаление таблицы."""
    query = get_object_or_404(QueryLog, pk=pk)
    if request.method == 'POST':
        query.delete()
        return redirect('query_list')
    return JsonResponse({'status': 'failed', 'message': 'Метод не поддерживается'}, status=405)