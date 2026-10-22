from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watchlist_users")


class Category(models.Model):
    category_name = models.CharField(max_length=64)

    def __str__(self):
        return self.category_name


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # السعر الابتدائي أو الحالي
    image_url = models.CharField(max_length=800, blank=True, null=True) # رابط الصورة (اختياري)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="listings")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    is_active = models.BooleanField(default=True) # لتحديد ما إذا كان المزاد نشطاً أم مغلقاً

    def __str__(self):
        return f"{self.title} - ${self.price}"


class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2) # قيمة المزايدة
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.user.username} bid ${self.bid} on {self.listing.title}"


class Comment(models.Model):
    message = models.TextField() # نص التعليق
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.listing.title}"