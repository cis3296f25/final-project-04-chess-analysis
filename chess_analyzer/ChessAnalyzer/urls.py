from django.urls import path,include
from . import views
# app urls
urlpatterns = [
    path('', views.home, name='home')

]