from django import forms


class ReviewForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)
    rating = forms.IntegerField(min_value=1, max_value=5)
