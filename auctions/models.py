from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    categoryName = models.CharField(max_length=50)

    def __str__(self):
        return self.categoryName


class Listing(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    imageUrl = models.CharField(max_length=3000)
    price = models.FloatField()
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=False, null=False, related_name="user"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="category",
    )
    watchlist = models.ManyToManyField(
        User, blank=True, null=True, related_name="watchlist"
    )
    winner = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=False, null=True, related_name="winner"
    )

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=False, null=False, related_name="author"
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.PROTECT, blank=False, null=False, related_name="listing"
    )
    comment = models.CharField(max_length=3000)

    def __str__(self):
        return f"Comment: {self.comment}, author: {self.author}"

class Bid(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=False, null=False, related_name="bidUser"
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.PROTECT, blank=False, null=False, related_name="bidListing"
    )
    bid = models.FloatField()