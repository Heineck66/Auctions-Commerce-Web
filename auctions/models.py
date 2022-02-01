from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING, PROTECT


class User(AbstractUser):
    nickname = models.CharField(max_length=32, default='userx')

    def __str__(self):
        return f'{self.username}'


class Category(models.Model):
    category = models.CharField(max_length=62)

    def __str__(self):
        return f'{self.category}'


class Listing(models.Model):
    short_name = models.CharField(max_length=32)
    description = models.CharField(max_length=92, null=True)
    picture = models.CharField(max_length=300, null=True, blank=True)
    create_date = models.DateTimeField()
    close_date = models.DateField(null=True, blank=True)
    closed = models.BooleanField(null=False, default=False)
    starting_bid = models.FloatField()
    higher_bid = models.FloatField(null=False)
    seller = models.ForeignKey(User, on_delete=PROTECT, related_name='seller')
    buyer = models.ForeignKey(User, on_delete=PROTECT, null=True, blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='listing')

    def __str__(self):
        return f'listing: {self.short_name}'


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    isHigherBid = models.BooleanField(default=False)
    value = models.FloatField()
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=DO_NOTHING, related_name='buyer')

    def __str__(self):
        return f'user:{self.user} value:{self.value} to {self.listing.short_name} is {self.isHigherBid}'


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=DO_NOTHING, related_name='comment')
    comment = models.CharField(max_length=780)
    date = models.DateTimeField()


class Watchitem(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchitem')

    def __str__(self):
        return f'{self.listing}, user: {self.user}'
