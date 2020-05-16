from django.db import models

# Create your models here.
class Post(models.Model):
    title=models.CharField(max_length=40)
    description=models.CharField(max_length=100)
    author=models.CharField(max_length=30)