from django.db import models

# Create your models here.
class User(models.Model):
    id =models.CharField(verbose_name='LinkedIn Id',primary_key=True,max_length=40)
    first_name = models.CharField(verbose_name='FirstName', max_length=30)
    last_name = models.CharField(verbose_name='LastName', max_length=30)
    profile_pic_url = models.CharField( verbose_name='Profile Picture', null=True, max_length=100)

    def __str__(self):
        return self.first_name+" "+self.last_name
