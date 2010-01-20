from django import forms

class UIDateWidget(forms.DateInput):
    def __init__(self, attrs={}, format=None):
        super(UIDateWidget, self).__init__(attrs={'class': 'uiDateField', 'size': '10'}, format=format)