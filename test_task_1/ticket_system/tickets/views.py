from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DetailView, RedirectView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import CustomUserCreationForm, EditProfileForm, NewTicketForm, NewMessageForm
from .models import CustomUser, Ticket, Message

# Логин
class LoginView(SuccessMessageMixin, TemplateView):
    template_name = 'login.html'
    success_message = 'You have successfully logged in!'

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        return render(request, self.template_name, {'form': form})

# Регистрация
class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = '/login/'

# Выходы
class LogoutView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

# Дашборд
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == 'admin':
            context['tickets'] = Ticket.objects.all()
        else:
            context['tickets'] = Ticket.objects.filter(owner=user)
        return context

# Профиль
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['form'] = EditProfileForm(instance=user)
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        return render(request, self.template_name, {'form': form})

# Управление клиентами
class ClientsView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'clients.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

# Список тикетов
class TicketsView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            queryset = Ticket.objects.all()
        else:
            queryset = Ticket.objects.filter(owner=user)
        return queryset

# Просмотр тикета
class ViewTicketView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'view_ticket.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = Message.objects.filter(ticket=self.object)
        context['form'] = NewMessageForm()
        return context

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        form = NewMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.author = request.user
            message.save()
            if request.user.role == 'admin' and 'close_ticket' in request.POST:
                ticket.status = 'closed'
                ticket.save()
            return redirect('view_ticket', pk=ticket.pk)
        return render(request, self.template_name, {'form': form})


class LogoutView(RedirectView):
    url = reverse_lazy('login')  # Переходим обратно на страницу логина после выхода

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)