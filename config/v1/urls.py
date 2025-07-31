from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("notifications/", include("notifications.urls")),
    path("eld/", include("eld.urls")),

] 