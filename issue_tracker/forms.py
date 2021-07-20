from django.http import request
from .models import *
from django.forms import ModelForm

class IssueForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request=kwargs.pop('request')

        super(IssueForm,self).__init__(*args, **kwargs)
        self.fields['project'].queryset=Project.objects.filter(member=self.request.user).prefetch_related('member')
        self.fields['creator'].queryset=User.objects.filter(id=self.request.user.id) 

    class Meta:
        model= Issue

    #If I would like to use all fileds I could use fields = __all__

        fields = ['title','creator', 'user_assigned','priority', 'project','status','description']

    
    
class IssueTagForm(ModelForm):
    class Meta:
        model= IssueTag

    #If I would like to use all fileds I could use fields = __all__

        fields ='__all__'