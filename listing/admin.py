from django.contrib import admin
from listing.models import Category, Product, Review


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)