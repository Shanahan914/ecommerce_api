#add a signal to create a cart when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Cart

@receiver(post_save, sender=CustomUser)
def create_cart_for_user(sender, instance, created, **kwargs):
    if created:
        print('signal triggered')
        try:
            Cart.objects.create(owner=instance)
        except:
            print('an error occured')