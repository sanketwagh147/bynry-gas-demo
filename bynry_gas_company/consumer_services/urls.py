from django.urls import include, path

from . import views


urlpatterns = [
    path("", views.consumer_home, name="consumer_home")
]
