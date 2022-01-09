from django.forms import ModelForm
from .models import Tasks


class TasksForm(ModelForm):
    class Meta:
        model = Tasks
        fields = ['title', 'description', 'important',]