from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.add_book, name='add'),
    path('upload/', views.upload_file, name='upload'),
    path('files/', views.file_list, name='files'),
]