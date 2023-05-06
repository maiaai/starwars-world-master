from django.contrib import admin

from app.models import Collection


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['filename', 'collected_at']
