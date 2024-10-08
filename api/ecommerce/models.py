from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CustomerUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Must provide an email')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user 
    
    def create_superuser(self,email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff set to True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser set to True')
        
        return self.create_user(email, password, **extra_fields)
        
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=55)
    last_name = models.CharField(max_length=55)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = CustomerUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class Cart(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_owner')
    updated = models.DateTimeField(auto_now=True)
    # 'through' allows us to fetch data from product and cartitem at the same time.
    # manytomany because multipe carts reference multiple products and vice versa
    products = models.ManyToManyField(Product, through='CartItem') 

    def __str__(self):
        return f"Cart for {self.owner}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, related_name='cart_products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} in {self.cart.owner.email}'s cart"


class Order(models.Model):
    class statusCodes(models.TextChoices):
       PENDING = "AP", _('Awaiting payment')
       PAID = "PD", _('Payment made')
       PREPARING = "PR", _('Prepearing')
       DISPATCHED = "DP", _('Dispatched')
       DELIVERED = "DL", _('Delivered')
       RETURNED = "RE", _('Returned')

    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='order_owner')
    updated = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(choices=statusCodes, default=statusCodes.PENDING)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, related_name='order_products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Payment(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_order_id')
    payment_bool = models.BooleanField(default=False)
    stripe_intent_id = models.CharField(max_length=500)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)