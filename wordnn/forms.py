
from django import forms
 
class AddForm(forms.Form):
    word = forms.CharField(required=False)
    n = forms.IntegerField(initial=20)
    