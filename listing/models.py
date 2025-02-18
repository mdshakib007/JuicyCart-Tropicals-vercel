from django.db import models
from django.template.defaultfilters import slugify
from shop.models import Shop
from users.models import Customer

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True , blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.URLField(max_length=250, blank=True, null=True, default="https://ibb.co.com/jZhrJtTS")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    available = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)
    about = models.TextField()

    def __str__(self):
        return f"{self.name}"


class Review(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(default=0)
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.user.username} on {self.product.name}"
