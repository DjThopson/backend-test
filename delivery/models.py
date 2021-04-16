import datetime
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ManyToManyField
from .tasks import send_notification_shopper


class Shopper(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    idSlack = models.CharField(max_length=20, blank=False, default='', unique=True)

    #Datos de control
    userAdd = models.ForeignKey(User, on_delete=CASCADE)
    dateAdd = models.DateField(auto_now_add=True)

    # Se da formato
    def __str__(self):
        return '%s UUID:  %s' % (self.name, self.id)

class MealPlate(models.Model):
    name = models.CharField('Name', max_length=100, blank=False, editable=True, default='')
    description = models.CharField('Description', max_length=250, blank=True, editable=True)
    price = models.FloatField("Price", default=0.0)
    available = models.BooleanField(default=True)
 
    # Datos de control
    userAdd = models.ForeignKey(User, on_delete=models.CASCADE)
    dateAdd = models.DateField(auto_now_add=True) 
    
    # Se da formato
    def __str__(self):
        return self.name

class Option(models.Model):
    name = models.CharField('Name', max_length=100, blank=False, editable=True, default='')
    description = models.CharField('Description', max_length=250, blank=True, editable=True)
    dishes = ManyToManyField(MealPlate)
    available = models.BooleanField(default=True)

    # Datos de control
    userAdd = models.ForeignKey(User, on_delete=models.CASCADE)
    dateAdd = models.DateField(auto_now_add=True) 

    # Se da formato
    def __str__(self):
        return '%s-%s' % (self.name, self.pk)

class DailyMenu(models.Model):
    dateDelivery = models.DateField(auto_now_add=True)
    name = models.CharField('Name', max_length=100, blank=False, editable=True, default='')
    description = models.CharField('Description', max_length=250, blank=True, editable=True)
    available = models.BooleanField(default=True)
    options = models.ManyToManyField(Option)

    # Se sobreescribe el método de guardado
    def save(self, *args, **kwargs):
        
        # Se obtiene la fecha actual
        today = datetime.date.today()
        
        # Se valída si el menú almacenado es el menú del día
        if self.dateAdd == today:
            
            # Si el menú guardado es el menú del día, se notifica a los compradores a través de la tarea 
            send_notification_shopper(Shopper.objects.all())
        # Se corre el guardado nativo    
        super(DailyMenu, self).save(*args, **kwargs)

    #Datos de control
    userAdd = models.ForeignKey(User, on_delete=models.CASCADE)
    dateAdd = models.DateField(auto_now_add=True) 

class Order(models.Model):
    shopper  = models.ForeignKey(Shopper, on_delete=CASCADE)
    option = models.ForeignKey(Option, on_delete=CASCADE)
    specifications = models.TextField(blank=True)
    deleted = models.BooleanField(default=False, editable=False)

    #Datos de control
    dateAdd = models.DateTimeField(auto_now_add=True)
    
    # Se da formato
    def __str__(self):
        return 'Order-%s' % (self.pk)



    
        


