from django.http import request
from .models import *
from django.forms import ModelForm

class IssueFormDeveloper(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request=kwargs.pop('request')

        super(IssueFormDeveloper,self).__init__(*args, **kwargs)
        self.fields['user_assigned'].queryset=User.objects.none()
        self.fields['project'].queryset=Project.objects.filter(member=self.request.user).prefetch_related('member')
        #self.fields['creator'].queryset=User.objects.filter(id=self.request.user.id) 
        
    class Meta:
        model= Issue

    #If I would like to use all fileds I could use fields = __all__

        fields = ['title','creator', 'project', 'user_assigned','priority', 'status','description']


    
    
class IssueTagForm(ModelForm):
    class Meta:
        model= IssueTag

    #If I would like to use all fileds I could use fields = __all__

        fields ='__all__'