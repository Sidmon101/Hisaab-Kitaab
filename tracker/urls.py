
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='tracker/login.html',authentication_form=CustomLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('create-group/', views.create_group, name='create_group'),
    path('join-group/', views.join_group, name='join_group'),
    path('group/<int:group_id>/add-expense/', views.add_expense, name='add_expense'),
    path('expense/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('group/<int:group_id>/', views.group_dashboard, name='group_dashboard'),
    path('group/<int:group_id>/pie-charts/', views.generate_pie_charts, name='generate_pie_charts'),
    path('chat/history/<int:group_id>/', views.chat_history, name='chat_history'),

]


