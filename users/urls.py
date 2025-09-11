from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # 自分のプロフィール
    path("profile/", views.user_profile, name="user_profile"),

    # 他人のプロフィール（id指定）
    path("profile/<int:user_id>/", views.user_profile_detail, name="user_profile_detail"),

    # プロフィール編集
    path("profile/update/", views.profile_update, name="profile_update"),

    # ログイン履歴カレンダー
    path("calendar/", views.login_calendar, name="login_calendar"),

    # ユーザー一覧
    path("list/", views.user_list_page, name="user_list_page"),
]
