from django.contrib import admin
from .models import Post

# Postモデルの管理画面表示をカスタマイズ
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 一覧に表示するフィールド
    list_display = ('title', 'author', 'created_at', 'updated_at')
    # フィルタリングに使用するフィールド
    list_filter = ('author', 'created_at')
    # 検索可能なフィールド
    search_fields = ('title', 'content')
    # 編集画面でのフィールドの表示順序
    fields = ('title', 'image', 'content', 'author')
    ordering = ('-created_at',)