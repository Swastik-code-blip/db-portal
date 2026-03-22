from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('resign/', views.resignation_page, name='resignation_page'),
    path('report-hardware/', views.hardware_report_page, name='hardware_report'),
    path('hw-approval/', views.hardware_approval_submit, name='hw_approval_submit'),

    path('hardware/', views.hardware_list, name='hardware_list'),
    path('hardware/add/', views.hardware_add, name='hardware_add'),
    path('hardware/export/', views.export_hardware_excel, name='export_hardware'),
    path('hardware/import/', views.import_hardware_excel, name='import_hardware'),
    path('hardware/template/', views.export_template_excel, name='export_template'),
    path('hardware/types/', views.hardware_types_manage, name='hardware_types'),
    path('hardware/search/', views.hardware_search_api, name='hardware_search_api'),
    path('hardware/<int:pk>/', views.hardware_detail, name='hardware_detail'),
    path('hardware/<int:pk>/edit/', views.hardware_edit, name='hardware_edit'),
    path('hardware/<int:pk>/status/', views.hardware_status_change, name='hardware_status_change'),
    path('hardware/<int:pk>/trash/', views.hardware_send_to_trash, name='hardware_send_to_trash'),

    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/import/', views.employee_bulk_import, name='employee_bulk_import'),
    path('employees/sync/', views.employee_master_sync, name='employee_master_sync'),
    path('employees/template/', views.export_employee_template, name='employee_template'),
    path('employees/export-left/', views.export_fired_resigned_csv, name='export_left_employees'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/action/', views.employee_action, name='employee_action'),

    path('resignations/', views.resignation_list, name='resignation_list'),
    path('resignations/<int:pk>/', views.resignation_review, name='resignation_review'),

    path('transfers/', views.transfer_request_create, name='transfer_create'),
    path('transfers/<int:pk>/review/', views.transfer_review, name='transfer_review'),

    path('approvals/', views.approvals_dashboard, name='approvals_dashboard'),
    path('approvals/hw/<int:pk>/', views.hardware_approval_review, name='hw_approval_review'),

    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),

    path('trash/', views.trash_list, name='trash_list'),
    path('trash/add/', views.trash_add, name='trash_add'),
    path('trash/<int:pk>/sold/', views.trash_mark_sold, name='trash_mark_sold'),

    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/toggle/', views.user_toggle, name='user_toggle'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/role/', views.user_role_change, name='user_role_change'),
    path('users/<int:pk>/location/', views.user_location_change, name='user_location_change'),

    path('commands/', views.commands_list, name='commands_list'),
    path('commands/add/', views.command_add, name='command_add'),
    path('commands/<int:pk>/download/', views.command_download, name='command_download'),

    path('api/search/', views.employee_search_api, name='employee_search_api'),
    path('api/stats/', views.stats_api, name='stats_api'),
    path('api/auto-fetch/', views.auto_fetch_api, name='auto_fetch_api'),
    path('messages/', views.messages_list, name='messages_list'),
    path('api/messages/unread/', views.messages_unread_count, name='messages_unread'),
]
