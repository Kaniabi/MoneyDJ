from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
	error_css_class = 'error'
	required_css_class = 'required'
