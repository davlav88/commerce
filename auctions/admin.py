from django.contrib import admin
from .models import User, Auctions, Watchlist, Comments, Bids, Winners, Categories

# Register your models here.
admin.site.register(User)
admin.site.register(Auctions)
admin.site.register(Watchlist)
admin.site.register(Comments)
admin.site.register(Bids)
admin.site.register(Winners)
admin.site.register(Categories)