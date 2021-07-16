from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    name=models.TextField(null=True)
    members=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank= True)
class IssueTag(models.Model):
    tag_name=models.CharField(max_length=40)

class Issue(models.Model):
    creator=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank= True)
    project=models.ForeignKey(Project,on_delete=models.SET_NULL,null=True,blank= True)
    priority=
    description=models.TextField(null=True)
    create_date=models.DateTimeField(auto_now_add=True)
    update_date=models.DateTimeField()
    tags=models.ForeignKey(IssueTag,on_delete=models.SET_NULL,null=True,blank= True)
    user_assigned=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank= True)
    type=
