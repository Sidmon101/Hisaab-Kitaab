from django import forms
from .models import Group
from .models import Expense
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # You can add custom checks here if needed
        pass

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise forms.ValidationError("This username is not registered. Please sign up first.")

        return super().clean()


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        if Group.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A group with this name already exists.")
        return name


class GroupJoinForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Select a Group",
        widget=forms.Select(attrs={'class': 'form-control'})
    )



class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description']
