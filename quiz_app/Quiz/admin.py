from django.contrib import admin
from models import Question, Option, Vote 

# Register your models here.
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Vote)