from django.contrib.auth.decorators import user_passes_test

def group_required(*group_names):
   """Requires user membership in at least one of the groups passed in."""

   def in_groups(u):
       if u.is_authenticated:
           if bool(u.groups.filter(name__in=group_names)):
               return True
       return False
   return user_passes_test(in_groups)

def group_excluded(*group_names):
   """Requires user to not be members of groups passed in."""

   def in_groups(u):
       if u.is_authenticated:
           if bool(u.groups.filter(name__in=group_names)):
               return False
       return True
   return user_passes_test(in_groups)
