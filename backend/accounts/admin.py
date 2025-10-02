from django.contrib import admin
from .models import CustomUser, Follow
# Register your models here.

@admin.register(CustomUser)
class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active',)

admin.site.register(Follow)