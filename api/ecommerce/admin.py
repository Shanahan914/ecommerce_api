from django.contrib import admin
from .models import *
from django.apps import apps

# Register your models here.
app = apps.get_app_config('ecommerce')
print(app)

for model_name, model in app.models.items():
    admin.site.register(model)