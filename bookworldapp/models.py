from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.contrib.auth.models import User

class contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=50)
    message = models.TextField()

    def __str__(self):
        return self.name


class seller(models.Model):
    sname = models.CharField(max_length=50)
    semail = models.EmailField()
    snumber = models.CharField(max_length=50)
    sstate = models.CharField(max_length=100)

    def __str__(self):
        return self.sname


class Category(models.Model):
    title = models.CharField(max_length=300)
    primaryCategory = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class books(models.Model):
    product_id = models.AutoField
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    slug = models.SlugField()
    subcategory = models.CharField(max_length=100)
    image = models.ImageField(upload_to='img')
    price = models.IntegerField()
    oldprice = models.IntegerField()
    category = (
        ('undergraduate', 'undergraduate'),
        ('postgraduate', 'postgraduate'),
        ('stationary', 'stationary'),
    )
    category = models.CharField(max_length=100, choices=category)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    item = models.ForeignKey(books, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} of {self.item.name}'

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_item_oldprice(self):
        return self.quantity * self.item.oldprice

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_item_oldprice()

    def get_final_price(self):
        if self.item.oldprice:
            return self.get_total_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    orderitems = models.ManyToManyField(Cart)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.orderitems.all():
            total += order_item.get_final_price()
        return total

