from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("schema", views.SchemaCreate.as_view(), name="schema"),
    path("schema_update/<int:schema_id>", views.SchemaUpdate.as_view(), name="schema_update"),
    path("datasets/<int:schema_id>", views.Datasets.as_view(), name="datasets"),    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # API routes
    path("status_check/<str:mtk>", views.status_check, name="status_check"),
    path("delete_schema/<int:schema_id>", views.delete_schema, name="delete_schema"),
]  

