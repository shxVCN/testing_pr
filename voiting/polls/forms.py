"""
Формы приложения голосования.
"""
from django import forms
from .models import Poll, Choice


class PollCreateForm(forms.ModelForm):
    """Форма создания опроса с вариантами ответов."""
    choice1 = forms.CharField(label='Вариант 1', max_length=200, required=True)
    choice2 = forms.CharField(label='Вариант 2', max_length=200, required=True)
    choice3 = forms.CharField(label='Вариант 3', max_length=200, required=False)

    class Meta:
        model = Poll
        fields = ['question']
        labels = {'question': 'Вопрос опроса'}

    def clean(self):
        """Варианты ответов не должны повторяться."""
        data = super().clean()
        choices = []
        for name in ['choice1', 'choice2', 'choice3']:
            text = data.get(name)
            if text and (t := text.strip()):
                if t in choices:
                    self.add_error(
                        name,
                        forms.ValidationError('Варианты ответа не должны повторяться.')
                    )
                choices.append(t)
        return data

    def save(self, commit=True, user=None):
        poll = super().save(commit=False)
        if user:
            poll.created_by = user
        if commit:
            poll.save()
            seen = set()
            for field_name in ['choice1', 'choice2', 'choice3']:
                text = (self.cleaned_data.get(field_name) or '').strip()
                if text and text not in seen:
                    seen.add(text)
                    Choice.objects.create(poll=poll, text=text)
        return poll


class VoteForm(forms.Form):
    """Форма голосования."""
    choice = forms.ModelChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None
    )

    def __init__(self, *args, poll=None, **kwargs):
        super().__init__(*args, **kwargs)
        if poll:
            self.fields['choice'].queryset = poll.choices.all()
