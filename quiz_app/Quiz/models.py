from __future__ import unicode_literals

from django.db import models
from User.models import User

# Create your models here.


class Question(models.Model):
    """Model to store information about a question."""

    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField(max_length=300)
    user = models.ForeignKey(User, related_name='user')
    question_url = models.URLField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return self.question_id

    def serializer(self):
        """Serializes a question with options."""
        question = {}
        question["id"] = self.question_id
        question["question"] = self.question_text
        question["url"] = self.question_url
        options = Option.objects.filter(question=self)
        option_list = []
        for option in options:
            option_list.append(option.serializer())
        question["options"] = option_list
        return question


class Option(models.Model):
    """Model to store information about options."""

    option_id = models.AutoField(primary_key=True)
    option_text = models.CharField(max_length=60)
    question = models.ForeignKey(Question, related_name='question')

    def __unicode__(self):
        return str(self.question_id) + ' ' + self.option_text

    def serializer(self):
        option = {}
        option["id"] = self.option_id
        option["option"] = self.option_text
        return option


class Vote(models.Model):
    """Model to store votes given by users"""
    vote_id = models.AutoField(primary_key=True)
    option = models.ForeignKey(Option, related_name='option')
    user = models.ForeignKey(User, related_name='user_voted')

    def __unicode__(self):
        return str(self.vote_id)
