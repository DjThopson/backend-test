from django import forms
import datetime
from django.db.models import fields

from .models import Shopper, Order, DailyMenu, Option, MealPlate

class ShopperForm(forms.ModelForm):

    class Meta:
        model = Shopper
        fields = ('name', 'phone')

class OrderForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ( 'shopper','option','specifications')

    def is_valid(self):
        # Validacción nativa
        valid = super(OrderForm, self).is_valid()
 
        # Si no es válido regresamos el dato
        if not valid:
            return valid

        # Verificación de horario
        currentHour = datetime.datetime.now().hour
        # Si la hora en la que se realiza la orden es superior a las 11am se debe indicar un error
        if currentHour > 11 :
            #Indica el error al form para plasmarlo en front
            self._errors['invalid_hour'] = 'Petición fuera de horario'
            return False
 
        # Todo bien, el formulario es válido
        return True


class DailyMenuForm(forms.ModelForm):
    class Meta:
        model = DailyMenu
        fields = ('name', 'description', 'options','available')
        
class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ('name', 'description', 'dishes')

class MealPlateForm(forms.ModelForm):
    class Meta:
        model = MealPlate
        fields = ('name', 'description', 'price')