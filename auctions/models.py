from sqlite3.dbapi2 import Timestamp
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auctions(models.Model):
    user = models.ForeignKey(User, related_name="listings", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    description = models.TextField()
    image = models.CharField(max_length=250)
    price = models.IntegerField()
    
    def __str__(self):
        return self.name
    
class Bids(models.Model):
    user = models.ForeignKey(User, related_name="bids", on_delete=models.CASCADE)
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="bids")
    price = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Bid of {self.price} by {self.user}"
    
class Comments(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="item")
    comment = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user}: {self.comment}"
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name="wishlist", on_delete=models.CASCADE)
    item = item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="auction")

    def __str__(self):
        return f"{self.user} wishlist: {self.item}"