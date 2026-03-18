from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Hardware, Employee, HardwareProperty, TrashHardware, CommandLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (('DB Portal', {'fields': ('role', 'phone', 'department')}),)

class PropertyInline(admin.TabularInline):
    model = HardwareProperty
    extra = 1

@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):
    list_display = ('hw_id', 'hardware_type', 'brand', 'model_name', 'status', 'assigned_to')
    list_filter = ('hardware_type', 'status')
    search_fields = ('hw_id', 'brand', 'model_name', 'serial_number')
    inlines = [PropertyInline]

admin.site.register(Employee)
admin.site.register(TrashHardware)
admin.site.register(CommandLog)
