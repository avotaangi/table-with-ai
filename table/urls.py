from django.urls import path
from . import views

urlpatterns = [
    path('', views.query_list, name='query_list'),
    path('create/', views.query_create, name='query_create'),
    path('result/<int:pk>/', views.query_result, name='query_result'),
    path('edit/<int:pk>/', views.query_edit, name='query_edit'),
    path('save/<int:pk>/', views.query_save, name='query_save'),
    path('download/<int:pk>/<str:file_format>/', views.query_download, name='query_download'),
    path('delete/<int:pk>/', views.query_delete, name='query_delete'),
]
