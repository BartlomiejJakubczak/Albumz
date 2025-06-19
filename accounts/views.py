from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView as LV
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views import generic


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


@method_decorator(never_cache, name="dispatch")
class LoginView(LV):
    redirect_authenticated_user = True
