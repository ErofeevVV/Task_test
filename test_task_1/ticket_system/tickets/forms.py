from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Ticket, Message

# Форма регистрации
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')

# Форма редактирования профиля
class EditProfileForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

# Форма создания нового тикета
class NewTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title',)

# Форма отправки нового сообщения
class NewMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
