import datetime
import hashlib
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text
    
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text


class SimpleUser(models.Model):
    username = models.CharField(max_length=100, unique = True)
    password = models.CharField(max_length=256)

    def set_password(self, raw_password):
        # OWASP 2021 2: Cryptographic failures
        # FLAW: unsalted SHA1 hashing
        # SHA1 is considered broken and unsuitable for password storage
        self.password = hashlib.sha1(raw_password.encode()).hexdigest()

        # FIX: use Django’s secure password hashing
        # from django.contrib.auth.hashers import make_password
        # self.password = make_password(raw_password)

    def check_password(self, raw_password):
        # OWASP 2021 2: Cryptographic failures
        # FLAW: compare using weak hash
        return self.password == hashlib.sha1(raw_password.encode()).hexdigest()

        # FIX:
        # from django.contrib.auth.hashers import check_password
        # return check_password(raw_password, self.password)
