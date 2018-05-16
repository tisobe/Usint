from django     import forms

class LoginForm(forms.Form):
    
    username = forms.CharField(label='User Name', max_length=50)
    password = forms.CharField(label='Passwrod', max_length=50, widget=forms.PasswordInput)
