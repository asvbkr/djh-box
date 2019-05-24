from django.db import models


# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField("date created", auto_now_add=True)

    who_max_len = 200
    who = models.TextField("who created", max_length=who_max_len)
