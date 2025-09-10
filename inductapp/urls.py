from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main pages
    path('ranklist/', views.ranklist_view, name='ranklist'),
    path('train/<int:train_id>/', views.train_detail_view, name='train_detail'),
    path('upload/', views.upload_view, name='upload'),
    
    # API endpoints
    path('api/import/', views.api_import_data, name='api_import'),
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/extract_certificate/', views.api_extract_certificate, name='api_extract_certificate'),
    path('api/report/', views.api_generate_report, name='api_report'),
]