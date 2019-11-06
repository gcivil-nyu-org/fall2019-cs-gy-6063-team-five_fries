from django import forms


class ReviewForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
