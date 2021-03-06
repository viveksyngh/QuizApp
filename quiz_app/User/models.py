from __future__ import unicode_literals

from django.db import models

# Create your models here.

class User(models.Model):
    user_id = models.CharField(max_length=255, primary_key=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=225, null=True, blank=True)
    last_name = models.CharField(max_length=255)
    email_id = models.CharField(max_length=255, unique=True)
    mobile_no = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name + ' ' + self.email_id + \
                self.mobile_no

    def serializer(self):
        user = {}
        user["first_name"] = self.first_name
        user["last_name"] = self.last_name
        user["middle_name"] = self.middle_name
        user["email_id"] = self.email_id
        user["mobile_no"] = self.mobile_no
        return user

