from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator

# Create your models here.

class Customer(AbstractUser):
    f_name1=models.CharField(max_length=10)
    l_name1=models.CharField(max_length=10)
    email1=models.CharField(max_length=30)
    phone1=models.CharField(max_length=15, null=True, blank=True)
    address1=models.CharField(max_length=40)

    def __str__(self):
        return f"{self.f_name1} {self.l_name1}"
    
class ProductManager(models.Manager):
    def search(self,query):
        if query :
            return self.get_queryset().filter(models.Q(name__exact=query)|models.Q(breed__exact=query))

class Category(models.Model):
    cat_name=models.CharField(max_length=10)
    cat_type=models.CharField(max_length=10)
    prices=models.DecimalField(max_digits=10,decimal_places=2)
    description=models.CharField(max_length=40)

class Product(models.Model):
    name=models.CharField(max_length=10)
    category=models.CharField(max_length=20)
    price=models.DecimalField(max_digits=10, decimal_places=2,
                    validators=[MaxValueValidator(10000,message=("The minimum price pet should be 10k"))])
    quantity_in_stock=models.IntegerField()
    description_text=models.CharField(max_length=40)
    image=models.ImageField(upload_to='products_images/',null=True, blank=True)     

objects= ProductManager()

class Order(models.Model):
    user_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date=models.DateTimeField()
    total_amount=models.DecimalField(max_digits=10,decimal_places=2)
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING'
    )
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
   
class OrderItem(models.Model):
    order_id=models.ForeignKey(Order,on_delete=models.CASCADE)
    cat_id=models.ForeignKey(Category,on_delete=models.CASCADE,null=True, blank=True)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE,null=True, blank=True)
    quantity=models.IntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)

class Cart(models.Model):
    customer_id=models.ForeignKey(Customer,on_delete=models.CASCADE)
    cat_id=models.ForeignKey(Category,on_delete=models.CASCADE, null=True, blank=True)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE, null=True, blank=True)
    quantity=models.IntegerField()
    date_added=models.DateTimeField()

class Payment(models.Model):
    order_id=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment_date=models.DateTimeField()
    payment_method=models.CharField(max_length=15)
    amount=models.DecimalField(max_digits=10,decimal_places=2)

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
