from django.urls import include, path

from . import views


urlpatterns = [
    path("", views.consumer_home, name="consumer_home"),
    path("sign-up/", views.sign_up, name="consumer_sign_up"),
    path("login/", views.login, name="login"),
    path("requests/", views.myRequests, name="myRequests"),
    path("user_requests/", views.userRequests, name="userRequests"),
    path("customer_requests/", views.customerRequests, name="customerRequests"),
    path('create-service-request/', views.ServiceRequestView.as_view(), name='create_service_request'),
    path("logout/", views.logout, name="logout"),

]
