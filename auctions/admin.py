from django.contrib import admin

from .models import Bid, Category, Comment, Listing, User, Watchitem


class BidInline(admin.TabularInline):
    model = Bid
    extra = 1


class CommentsInline(admin.TabularInline):
    model = Comment
    extra = 1


class ListingInline(admin.TabularInline):
    model = Listing
    extra = 1


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('listing', 'user', 'date')


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    fieldsets = [
        ('Info', {'fields': ['username', 'first_name', 'last_name', 'email']}),
    ]
    inlines = [BidInline, CommentsInline]


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'id', 'seller', 'create_date')
    filter_horizontal = ('categories',)
    fieldsets = [
        (None,  {'fields': ['picture']}),
        ('Data Information',  {'fields': ['short_name', 'description', 'create_date', 'close_date', 'closed']}),
        (None,  {'fields': ['starting_bid', 'seller', 'buyer', 'higher_bid', 'categories']}),
    ]
    inlines = [BidInline, CommentsInline]


# Register your models here.
admin.site.register(Category)
admin.site.register(Watchitem)
