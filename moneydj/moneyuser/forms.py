from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class RegisterForm(UserCreationForm):
	error_css_class = 'error'
	required_css_class = 'required'

class LoginForm(AuthenticationForm):
	error_css_class = 'error'
	required_css_class = 'required'
