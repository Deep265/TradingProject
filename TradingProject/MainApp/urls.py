from django.urls import path
from .views import get_csv
app_name = 'MainApp'

urlpatterns = [
    path('',get_csv,name='get_csv'),
]