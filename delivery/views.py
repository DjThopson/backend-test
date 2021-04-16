from django.shortcuts import render, redirect
import datetime
from .models import Order, Shopper, DailyMenu, Option
from .forms import ShopperForm, DailyMenuForm, OptionForm, MealPlateForm, OrderForm
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Función para cerrar sessión
def logoutpage(request):
    #Función nativa de Django para cerrar sesión
    logout(request)

    #Una vez cerrada la sesión se redirecciona a la página principal
    return redirect("/menu/")

# Función para iniciar sesión con métodos nativos
def loginpage(request):
    # Si el método del request es POST se validan los datos recibidos
    if request.method == 'POST':
        # Se autenticann los datos enviados en el form a través de función nativa de Django
        user = authenticate(username=request.POST['username'],password=request.POST['password'])
        
        # Si la autentificación es correcta se inicia sesión del usuario
        if user:
            username = request.POST['username']
            request.session['username'] = username
            
            # Se inicia sesión a través de función nativa de Django
            login(request, user)

            # Una vez iniciada la sesión se redirecciona a la página principal 
            return redirect("/menu/")
        else:

            # Si la autentificación es incorrecta, se renderiza la página indicando el error
            return render(request, 'login.html', {"message":"Usuario o contraseña inválidos"})
    
    # Si el usuario está autenticado se redirecciona a la página principal
    if request.user.is_authenticated:
        return redirect("/menu/")
    
    #Si el usuario no está autentificado se renderiza la página de inicio de sesión
    else: 
        return render(request, 'login.html', {})

# Función para cargar la página inicial
def main(request):

    # Se obtiene el usuario dentro del request
    user = getattr(request, 'user', None)

    #Si el usuario que accede es "Nora" se le mostrarán las órdenes/pedidos de los demás usuarios 
    if user.username == 'nora':

        #Se obtienen todas las órdenes que no estén borradas lógicamente
        orders = Order.objects.filter(deleted=False)    

        #Se genera el contexto para renderizar el front
        context = {
            'user': user, 
            'orders': orders
        } 
        return render(request, 'orders.html', context)

    #Por el contrario, si el usuario no es "Nora" se renderiza el front de acceso denegado a las órdenes
    else:
        context = {'user': user,}
        return render(request, 'access.html', context)

# Fución que carga los pedidos realizados por el usuario que se identifica a través del UUID enviado a su slack
def getMenu(request,pk):
    # Se valida si el UUID enviado existe
    if Shopper.objects.filter(pk=pk).exists() :
        
        #Si existe se obtienen los datos del comprador
        shopper = Shopper.objects.get(pk=pk)
        
        #Se obtienen las órdenes del comprador que correspondan al día actual y que no estén borradas
        orderToday = Order.objects.filter(shopper=pk, dateAdd__date=datetime.date.today(), deleted=False)
        
        #Se genera la fecha de ayer
        time_threshold = datetime.date.today() - datetime.timedelta(days=1)

        #Se obtienen las órdenes anteriores al día de hoy. Esto a manera de mostrar un historia de órdenes
        orders = Order.objects.filter(shopper=pk, deleted=False, dateAdd__lte=time_threshold)
        
        # Se genera el contexto para realizar el renderizado
        context = {
            'shopper': shopper,
            'orderToday' : orderToday,
            'orders' : orders
        }
        return render(request, 'menu.html', context)
    
    # Si el UUID enviado NO existe se renderiza el front de acceso denegado
    else:
        return render(request, 'access.html', {})

#Función que le permite solo al administrador (Nora) crear un nuevo menú para el día actual
@login_required #Requiere estar autentificado
def createMenu(request):
    #Se valida si existe algún menú para el día actual
    dailyMenu = DailyMenu.objects.filter(dateAdd=datetime.date.today())
    
    #Si existe un menú para el día actual
    if dailyMenu:
        #Se obtiene dicho menú preexistente
        dailyToday = DailyMenu.objects.get(dateAdd=datetime.date.today())

        #Se genera un formulario pasando como instancia el menú preexistente
        form = DailyMenuForm(instance=dailyToday)
        
        #Si se recibe la instrucción de creación y ya existia ell menú, solo se actualiza instanciando el menú preexistente
        if request.method == "POST":
            form = DailyMenuForm(request.POST, instance=dailyToday)
            
            #Se valida el contenido del formulario
            if form.is_valid():
                #Si es correcto se guardan los cambios
                form.save()
            
            #Se regresa a la p+agina inicial
            return redirect('/menu/')
        #Si solo es la consulta se genera el contexto para renderizar y se envía un aviso de preexistencia 
        # aunado al menú preexistente
        else:
            context = {
                'form': form,
                'message': 'Ya existe un menu para el día de hoy, puedes modificarlo aquí',
                'menu':dailyMenu
                }
            return render(request, 'create_menu.html', context)
    
    #Si no existe menú preexistente y se recibe la instrucción de creación
    elif request.method == "POST":
        #Se genera formulario con los datos recibidos
        form = DailyMenuForm(request.POST)
        
        #Se valida que el formulario tenga los datos correctos
        if form.is_valid():
            
            #Si los datos son correctos se guarda el formulario
            post = form.save(commit=False)
            post.userAdd = request.user
            post.dateAdd = datetime.date.today()
            post.save()
            
            #Se redirecciona a la página principal
            return redirect('/menu/', pk=post.pk)
    #Si no existe un menú preexistente y no se recibe instrucción de crear uno se 
    # regresa el formulario corerspondiente a la creacion            
    else:
        #se genera el formulario de creación
        form = DailyMenuForm()
        #Se renderiza el formulario
        return render(request, 'create_menu.html', {'form': form})

#Función que permite crear opciones para los menus
@login_required #Requiere estar autentificado
def createOptions(request):
    #Si se recibe la instrucción de creación
    if request.method == "POST":
        #Se genera el formulario con los datos recibidos
        form = OptionForm(request.POST)
        if form.is_valid():
            #Si los datos son válidos se guarda el nuevo objeto
            post = form.save(commit=False)
            post.userAdd = request.user
            post.dateAdd = datetime.date.today() 
            post.save()
            return redirect('/menu/', pk=post.pk)
    else:
        #Si no se recibe instrucción de crear uno se 
        # regresa el formulario corerspondiente a la creacion      
        form = OptionForm()
    return render(request, 'create_option.html', {'form': form})

#Función que permite crear platillos para las opciones
@login_required #Requiere estar autentificado
def createDishes(request):
    #Si se recibe la instrucción de creación
    if request.method == "POST":
        #Se genera el formulario con los datos recibidos
        form = MealPlateForm(request.POST)
        if form.is_valid():
            #Si los datos son válidos se guarda el nuevo objeto
            post = form.save(commit=False)
            post.userAdd = request.user
            post.dateAdd = datetime.date.today()
            post.save()
            return redirect('/menu/', pk=post.pk)
    else:
        #Si no se recibe instrucción de crear uno se 
        # regresa el formulario corerspondiente a la creacion
        form = MealPlateForm()
    return render(request, 'create_meal_plate.html', {'form': form})

#Función que permite crear órdenes
def createOrder(request,pk):
    #Se obtiene el comprador dado el UUID enviado como pk
    shopper = Shopper.objects.get(pk=pk)
    
    #Se busca el menu para el día actual
    dailyMenu = DailyMenu.objects.filter(dateAdd=datetime.date.today()).values('id')
    
    #Si no existe un menú para el día actual se debe inidicar un error
    if not dailyMenu:
        return render(request, 'access.html')

    #Se obtienen las opciones asociadas al menú del día actual
    options = Option.objects.filter(dailymenu__id__in=dailyMenu)

    #Se inicializa un fomrulario con el comprador envíado por URI
    form = OrderForm(initial={'shopper':shopper})

    #Si se recibe la instrucción de creación
    if request.method == "POST":
        #Se crea un formulario con los datos recibidos
        formPost = OrderForm(request.POST)
        if formPost.is_valid():
            #Si el formulario es válido se guarda el nuevo objeto
            post = formPost.save(commit=False)
            post.dateAdd = datetime.date.today()
            post.save()
            return redirect('/menu/'+pk)
        else:
            #Se crea un formulario con los datos recibidos
            context = {'form':formPost, 'options': options}
            return render(request, 'create_order.html', context)
    else:
        #Si no se recibe instrucción de crear uno se 
        # regresa el formulario corerspondiente a la creacion
        context = {'form':form, 'options': options}
    return render(request, 'create_order.html', context)

#Función que permite editar una orden.
#No se usa para este momento
@login_required #Requiere estar autentificado
def editOrder(request,pk):
    order = Order.objects.get(id=pk)
    return render(request, 'access.html', {})

#Función que permite eliminar una órden por id
@login_required #Requiere estar autentificado
def dropOrder(request,pk):
    #Se obtiene la orden dado el pk
    order = Order.objects.get(id=pk, deleted=False)
    if request.method == "POST":
        #Se borra lógicamente
        order.deleted = True
        order.save()
        return redirect('/menu/')

    context = {'order':order}
    return render(request, 'delete_order.html', context)

#Función que permite crear un comprador
@login_required #Requiere estar autentificado
def createShopper(request):
    #Si se recibe una petición de creación
    if request.method == "POST":
        #Se crea un formulario con los datos recibidos
        form = ShopperForm(request.POST)
        if form.is_valid():
            #Si el formulario es válido se guarda el nuevo objeto
            post = form.save(commit=False)
            post.userAdd = request.user
            post.dateAdd = datetime.date.today()
            post.save()
            return redirect('/menu/', pk=post.pk)
    else:
        #Si no se recibe instrucción de crear uno se 
        # regresa el formulario corerspondiente a la creacion
        form = ShopperForm()
    return render(request, 'create_shopper.html', {'form': form})

