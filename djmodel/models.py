from django.db import models
from django.conf import settings

# Create your models here.


class Zip(models.Model):
    code = models.CharField(max_length=10)


class Address(models.Model):
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=2)
    zip_code = models.OneToOneField(Zip, on_delete=models.CASCADE)


class Category(models.Model):
    title = models.CharField(max_length=50)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    title = models.CharField(max_length=150)
    content = models.TextField(max_length=5000)

