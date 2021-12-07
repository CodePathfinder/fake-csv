from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("schema", views.SchemaCreate.as_view(), name="schema"),
    path("datasets/<int:schema_id>", views.Datasets.as_view(), name="datasets"),    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
]  

