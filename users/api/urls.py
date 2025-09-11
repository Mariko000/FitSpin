from django.urls import path
from .. import views
from ..views import UserListView

app_name = 'users_api'

urlpatterns = [
    path('current-user/', views.current_user_info, name='current_user_info'),
    path('list/', UserListView.as_view(), name='user_list'),
]
