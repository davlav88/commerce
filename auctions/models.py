from sqlite3.dbapi2 import Timestamp
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auctions(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to="uploads/")
    price = models.ForeignKey('Bids', related_name="bid", on_delete=models.CASCADE)
    
    def __str__(self):
        return super().__str__()
    
class Bids(models.Model):
    user = models.ForeignKey(User, related_name="bids", on_delete=models.CASCADE)
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="bids")
    price = models.IntegerField()
    Timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return super().__str__()
    
class Comments(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="item")
    comment = models.CharField(max_length=250)
    Timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return super().__str__()