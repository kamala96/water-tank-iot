from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Username',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'username', 'placeholder': 'Enter username', 'aria-label': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'id': 'password', 'placeholder': 'Enter password', 'aria-label': 'Username'}),
        label='Password')
