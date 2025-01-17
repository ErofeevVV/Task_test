from django.urls import path
from .views import LoginView, RegisterView, DashboardView, ProfileView, ClientsView, TicketsView, ViewTicketView, \
    LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('clients/', ClientsView.as_view(), name='clients'),
    path('tickets/', TicketsView.as_view(), name='tickets'),
    path('tickets/<int:pk>/', ViewTicketView.as_view(), name='view_ticket'),
]
