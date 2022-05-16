from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.mail import send_mail

from .forms import CreationForm, User


send_mail(
    'Тема письма',
    'Текст письма.',
    'from@example.com',  # Это поле "От кого"
    ['to@example.com'],  # Это поле "Кому" (можно указать список адресов)
    fail_silently=False,  # Сообщать об ошибках («молчать ли об ошибках?»)
)


class SignUp(CreateView):
    model = User
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
