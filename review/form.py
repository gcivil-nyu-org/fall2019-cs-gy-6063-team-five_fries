from django import forms


class ReviewForm(form.Form):
    content = forms.TextField(label='review_content')