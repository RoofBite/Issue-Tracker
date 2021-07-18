from .models import *
from django.forms import ModelForm

class IssueForm(ModelForm):
    class Meta:
        model= Issue

    #If I would like to use all fileds I could use fields = __all__

        fields = ['title','creator', 'user_assigned','priority', 'project','status','description']

class IssueTagForm(ModelForm):
    class Meta:
        model= IssueTag

    #If I would like to use all fileds I could use fields = __all__

        fields ='__all__'