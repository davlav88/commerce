from sqlite3.dbapi2 import Timestamp
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Categories(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.id}, {self.name}"
    
class Auctions(models.Model):
    user = models.ForeignKey(User, related_name="listings", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    description = models.TextField()
    image = models.CharField(max_length=250)
    price = models.IntegerField()
    status = models.CharField(max_length=10, default="open")
    category = models.ForeignKey(Categories, related_name="auction_category", on_delete=models.CASCADE, default="2")
    
    def __str__(self):
        return f"{self.name} is {self.status}"
    
class Bids(models.Model):
    user = models.ForeignKey(User, related_name="user_bids", on_delete=models.CASCADE)
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="auction_bids")
    price = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Bid of {self.price}$ by {self.user}"
    
class Comments(models.Model):
    user = models.ForeignKey(User, related_name="user_comments", on_delete=models.CASCADE)
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="auction_item")
    comment = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user}: {self.comment}"
    
class Watchlist(models.Model):
    user = models.ForeignKey(User, related_name="user_watchlist", on_delete=models.CASCADE)
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="watchlist_auction")

    def __str__(self):
        return f"{self.user} watchlist: {self.item}"
    
class Winners(models.Model):
    user = models.ForeignKey(User, related_name="auctions_won", on_delete=models.CASCADE)
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="winners_auction")

    def __str__(self):
        return f"{self.user} won the {self.item} auction"
    
