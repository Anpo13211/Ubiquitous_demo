from django import forms

class ChatForm(forms.Form):

    sentence = forms.CharField(label='ゴルフスイングアドバイザー', widget=forms.Textarea(), required=True)