from django.contrib import admin
from .models import Bid, Category, Comment, Listing, User

# تسجيل النماذج لظهرورها في لوحة التحكم
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)