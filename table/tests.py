from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, Mock
import json
from .models import QueryLog

class QueryListViewTest(TestCase):
    def test_query_list_view(self):
        response = self.client.get(reverse('query_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table/query_list.html')

class QueryCreateViewTest(TestCase):
    def test_get_query_create(self):
        response = self.client.get(reverse('query_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table/query_create.html')

    def test_post_query_create(self):
        with patch('gigachat.GigaChat.chat') as mock_chat:
            mock_chat.return_value = Mock(choices=[Mock(message=Mock(content="|header1|header2|\n|data1|data2|"))])
            response = self.client.post(reverse('query_create'), {'query_text': 'Test query'})
            self.assertEqual(response.status_code, 302)
            self.assertTrue(QueryLog.objects.filter(query_text='Test query').exists())

class QueryResultViewTest(TestCase):
    def setUp(self):
        self.query = QueryLog.objects.create(query_text='Test', response_data='data', table_data=[{"key": "value"}])

    def test_query_result_view(self):
        response = self.client.get(reverse('query_result', args=[self.query.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table/query_result.html')

class QueryEditViewTest(TestCase):
    def setUp(self):
        self.query = QueryLog.objects.create(query_text='Test', response_data='data', table_data=[{"key": "value"}])

    def test_get_query_edit(self):
        response = self.client.get(reverse('query_edit', args=[self.query.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'table/query_edit.html')

    def test_post_query_edit(self):
        with patch('gigachat.GigaChat.chat') as mock_chat:
            mock_chat.return_value = Mock(choices=[Mock(message=Mock(content="|header1|header2|\n|data1|data2|"))])
            response = self.client.post(reverse('query_edit', args=[self.query.pk]), {'query_text': 'Updated query'})
            self.query.refresh_from_db()
            self.assertEqual(self.query.query_text, 'Updated query')

class QuerySaveViewTest(TestCase):
    def setUp(self):
        self.query = QueryLog.objects.create(query_text='Test', response_data='data', table_data=[{"key": "value"}])

    def test_post_query_save(self):
        response = self.client.post(
            reverse('query_save', args=[self.query.pk]),
            data=json.dumps({'table_data': [['header1', 'header2'], ['value1', 'value2']]}),
            content_type='application/json'
        )
        self.query.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.query.table_data, [{"header1": "value1", "header2": "value2"}])

class QueryDownloadViewTest(TestCase):
    def setUp(self):
        self.query = QueryLog.objects.create(query_text='Test', response_data='data', table_data=[{"header1": "value1", "header2": "value2"}])

    def test_query_download_csv(self):
        response = self.client.get(reverse('query_download', args=[self.query.pk, 'csv']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="query_{}.csv"'.format(self.query.pk))

    def test_query_download_xlsx(self):
        response = self.client.get(reverse('query_download', args=[self.query.pk, 'xlsx']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="query_{}.xlsx"'.format(self.query.pk))

class QueryDeleteViewTest(TestCase):
    def setUp(self):
        self.query = QueryLog.objects.create(query_text='Test', response_data='data', table_data=[{"key": "value"}])

    def test_query_delete(self):
        response = self.client.post(reverse('query_delete', args=[self.query.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(QueryLog.objects.filter(pk=self.query.pk).exists())