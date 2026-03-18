from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('hardware/', views.hardware_list, name='hardware_list'),
    path('hardware/add/', views.hardware_add, name='hardware_add'),
    path('hardware/export/', views.export_hardware_excel, name='export_hardware'),
    path('hardware/import/', views.import_hardware_excel, name='import_hardware'),
    path('hardware/template/', views.export_template_excel, name='export_template'),
    path('hardware/<int:pk>/', views.hardware_detail, name='hardware_detail'),
    path('hardware/<int:pk>/edit/', views.hardware_edit, name='hardware_edit'),
    path('hardware/<int:pk>/status/', views.hardware_status_change, name='hardware_status_change'),

    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),

    path('trash/', views.trash_list, name='trash_list'),
    path('trash/add/', views.trash_add, name='trash_add'),

    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/toggle/', views.user_toggle, name='user_toggle'),
    path('users/<int:pk>/role/', views.user_role_change, name='user_role_change'),
    path('users/<int:pk>/location/', views.user_location_change, name='user_location_change'),

    path('commands/', views.commands_list, name='commands_list'),
    path('commands/add/', views.command_add, name='command_add'),
    path('commands/<int:pk>/download/', views.command_download, name='command_download'),

    path('api/search/', views.employee_search_api, name='employee_search_api'),
    path('api/stats/', views.stats_api, name='stats_api'),
    path('api/auto-fetch/', views.auto_fetch_api, name='auto_fetch_api'),
]
