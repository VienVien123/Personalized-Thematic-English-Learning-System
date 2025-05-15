from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(TopicListen)
admin.site.register(Section)
admin.site.register(Subtopic)
admin.site.register(AudioExercise)
admin.site.register(TopicVocab)
admin.site.register(Word)
