from django import forms

from apps.musorka.models import Musorka


class CreateMusorkaForm(forms.ModelForm):

    class Meta:
        model = Musorka
        exclude = ('user', 'counter', 'status')