from django import forms
from .models import User, Prediction
from django.contrib.auth.forms import UserCreationForm


class UserCreateForm(UserCreationForm):
    telegram = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'telegram', 'send_to_telegram', 'send_to_email', 'oddsportal_username',
                  'oddsportal_password', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        print(self.fields)
        self.fields['oddsportal_username'].widget.attrs['class'] = 'form-control'
        self.fields['oddsportal_password'].widget.attrs['class'] = 'form-control'
        self.fields['send_to_telegram'].widget.attrs['class'] = 'form-check-label'
        self.fields['send_to_email'].widget.attrs['class'] = 'form-check-label'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['telegram'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['class'] = 'form-control'


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('telegram', 'send_to_telegram', 'send_to_email', 'oddsportal_username',
            'oddsportal_password'
        )
    
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['oddsportal_username'].widget.attrs['class'] = 'form-control'
        self.fields['oddsportal_password'].widget.attrs['class'] = 'form-control'
        self.fields['send_to_telegram'].widget.attrs['class'] = 'form-check-label'
        self.fields['send_to_email'].widget.attrs['class'] = 'form-check-label'
        self.fields['telegram'].widget.attrs['class'] = 'form-control'


class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ['bet_amount', 'bet_coefficient']

    def __init__(self, *args, **kwargs):
        max_amount = kwargs.pop("max_amount")
        min_amount = kwargs.pop("min_amount")
        super(PredictionForm, self).__init__(*args, **kwargs)
        self.fields['bet_amount'].widget.attrs['min'] = min_amount
        self.fields['bet_amount'].widget.attrs['max'] = max_amount
        self.fields['bet_amount'].widget.attrs['class'] = 'form-control'
        self.fields['bet_coefficient'].widget.attrs['class'] = 'form-control'
        self.fields['bet_amount'].initial = min_amount
        self.fields['bet_coefficient'].widget.attrs['min'] = 1.00
        self.fields['bet_coefficient'].initial = 1.00
