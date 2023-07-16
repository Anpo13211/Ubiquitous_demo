from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path('', views.index, name="index"),
    path('start_new/', views.start_new, name='start_new'),
    path('continue/<int:session_id>/', views.continue_session, name='continue_session'),
    path('delete_session/<int:session_id>/', views.delete_session, name = 'delete_session'), 
]
