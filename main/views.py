import requests
import json
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from main.models import *
from .forms import *

# Create your views here.

def home(request):
    categ = Category.objects.all()
    
    context ={
        'categ': categ
    }
    
    return render(request,'index.html', context)

def products(request):
    products = Product.objects.all()
    p = Paginator(products,8)
    page = request.GET.get('page')
    pagin = p.get_page(page)
    
    context = {
        'pagin':pagin
    }
    
    return render(request, 'product.html', context)

def category(request, id, slug):
    carbrand = Category.objects.get(pk=id)
    caritem = Product.objects.filter(type_id=id)
    
    context = {
        'carbrand':carbrand,
        'caritem':caritem, 
    }
    
    return render(request, 'category.html', context)

def detail(request, id, slug):
    cardet = Product.objects.get(pk=id)
    
    context = {
        'cardet':cardet,
    }
    
    return render(request, 'detail.html', context)

def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'your message has been sent successfully!!!')
            return redirect('home')
        else:
            print(form.errors)
    
    context = {
        'form':form
    }
    
    return render(request, 'contact.html')  

def signout(request):
    logout(request)
    messages.success(request, 'you are now signed out')
    return redirect('signin')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST['password']
        print(f'Username: {username}, Password: {password}') 
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'login succussful!')
            return redirect('home')
        else:
            messages.error(request, 'username/password is incorrect please try again')
            return redirect('signin')
        
    return render(request, 'login.html')


def register(request):
    register = CustomerForm()
    if request.method == 'POST':
        address = request.POST['address']
        phone = request.POST['phone']
        pix = request.POST['pix']
        register = CustomerForm(request.POST)
        if register.is_valid():
            user = register.save()
            newuser = Customer(user=user)
            newuser.first_name = user.first_name
            newuser.last_name = user.last_name
            newuser.email = user.email
            newuser.phone = phone
            newuser.address = address
            newuser.pix = pix
            newuser.save()
            messages.success(request, f'dear {user.username} your account is created suuccessful' )
            return redirect('signin') 
        else:
            messages.error(request, register.errors)
    
    return render(request, 'register.html ')

@login_required(login_url='signin')
def profile(request):
    userprof = Customer.objects.get(user__username = request.user.username)
    
    context = {
        'userprof':userprof
    }
    
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def profile_update(request):
    userprof = Customer.objects.get(user__username = request.user.username)
    pform = ProfileForm(instance=request.user.customer)
    if request.method == 'POST':
        pform = ProfileForm(request.POST, request.FILES, instance=request.user.customer)
        if pform.is_valid():
            user = pform.save()
            new = user.first_name.title()
            messages.success(request, f'dear {new} your profile has been updated successfully!')
            return redirect ('profile')
        else:
            new = user.first_name.title()
            messages.error(request, f'dear {new} your profile updated generated the following error ')
            return redirect('profile_update')
    
    context = {
        'userprof':userprof,
        'pform':pform
    }
    
    
    return render(request, 'profile_update.html', context)

@login_required(login_url='signin')
def password_update(request):
    userprof = Customer.objects.get(user__username = request.user.username)
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        new = request.user.username.title()
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, f'dear {new} your password is now updated')
            return redirect('profile')
        else:
            messages.error(request, f'dear {new} there is an error trying to change your password')
            return redirect('password_update')
        
    context = {
        'userprof':userprof,
        'form':form
    }
            
    return render(request, 'password_update.html', context)

@login_required(login_url='signin')
def add_to_cart(request):
    if request.method =='POST':
        quantity = int(request.POST['quantity'])
        carid = request.POST['carid']
        main = Product.objects.get(pk=carid)
        cart = Cart.objects.filter(user__username = request.user.username, paid=False)
        print(f"Debug: Quantity - {quantity}, Car ID - {carid}")
        if cart:
            # basket = Cart.objects.filter(user__username = request.user.username, paid=False, phone=main.id, car=main, quantity=quantity).first() 
            basket = Cart.objects.filter(user__username=request.user.username, paid=False, price=main.price, car=main).first() 
            print(f"Debug: Basket - {basket}")
            if basket:
                basket.quantity += quantity
                basket.amount = main.price * basket.quantity
                basket.save()
                messages.success(request, 'one item added to cart')
                return redirect('products')
            else:
                newitem = Cart()
                newitem.user = request.user
                newitem.car = main
                newitem.quantity = quantity 
                newitem.price = main.price 
                newitem.amount = main.price * quantity 
                newitem.paid = False
                newitem.save()
                messages.success(request, 'one item added to cart')
                return redirect('products')
        
        else:
            newcart = Cart()
            newcart.user = request.user
            newcart.car = main
            newcart.quantity = quantity
            newcart.price = main.price
            newcart.amount = main.price * quantity   
            newcart.paid = False
            newcart.save()
            messages.success(request, 'one item added to cart')
            return redirect('products')   
        
    return HttpResponse("Invalid Request")

@login_required(login_url='signin')
def cart(request):
    cart = Cart.objects.filter(user__username=request.user.username, paid=False)
    for item in cart:
        item.amount = item.price * item.quantity
        item.save()
        
    subtotal = 0
    vat = 0 
    total = 0
    
    for item in cart:
        subtotal += item.price * item.quantity
        vat = 0.075 * subtotal
        total = subtotal + vat
        
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'vat': vat,
        'total': total,
    }
    
    return render(request, 'cart.html', context)

@login_required(login_url='signin')
def delete(request):
    if request.method == 'POST':
        del_item = request.POST['delid']
        Cart.objects.filter(pk=del_item).delete()
        messages.success(request, 'one item deleted')
        return redirect('cart')
    
@login_required(login_url='signin')  
def update(request):
    if request.method == 'POST':
        qty_item = request.POST['quantid']
        new_qty = request.POST['quant']
        newqty = Cart.objects.get(pk=qty_item)
        newqty.quantity = new_qty
        newqty.amount = newqty.price * newqty.quantity 
        newqty.save()
        messages.success(request, 'quantity updated')
        return redirect('cart')
    
@login_required(login_url='signin')    
def checkout(request):
    userprof = Customer.objects.get(user__username = request.user.username)
    cart = Cart.objects.filter(user__username=request.user.username, paid=False)
    for item in cart:
        item.amount = item.price * item.quantity
        item.save()
        
    subtotal = 0
    vat = 0 
    total = 0
    
    for item in cart:
        subtotal += item.price * item.quantity
        vat = 0.075 * subtotal
        total = subtotal + vat
        
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'vat': vat,
        'total': total,
        'userprof': userprof,
    }
    
    return render(request, 'checkout.html', context)

@login_required(login_url='signin')
# def pay(request):
#     if request.method == 'POST':
#         try:
#             api_key = 'sk_test_8f12355ff2f260164c9cc6e580d2a1c01e94f1bd' #secret key from paystack
#             curl = 'https://api.paystack.co/transaction/initialize' #paystack call url
#             cburl = 'http://127.0.0.1:8000/callback' #payment thankyou page
#             ref = str(uuid.uuid4()) #refrence number required by paystack as an additional order number
#             profile = Customer.objects.get(user__username=request.user.username)
#             order_no = profile.id #main order number
#             total = float(request.POST['total']) * 100 #total amount to be charged from the customer's card
#             user = User.objects.get(username=request.user.username) #query the user model for customer's model
#             email = user.email #store customer's email to send to paystack
#             first_name = request.POST['first_name'] #collect from ther template in case there is a change
#             last_name = request.POST['last_name'] #collect from ther template in case there is a change
#             phone = request.POST['phone'] #collect from ther template in case there is a change
#             add_info = request.POST['add_info'] #collect from ther template in case there is a change
            
#             #collect data to send paystack via call
#             headers = {'Authorization': f'Bearer {api_key}'}
#             data = {'reference': ref, 'amount': int(total), 'email': user.email, 'callback_url': cburl, 'order_number': order_no, 'currency': 'NGN'}
    
#             #make a call to paystack
#             r = requests.post(curl, headers=headers, json=data)
#             r.raise_for_status()  # Raise an error for 4xx or 5xx status codes
#             transback = json.loads(r.text)
#             rdurl = transback['data']['authorization_url']
            
#             account = Payment()
#             account.user = user
#             account.first_name = user.first_name
#             account.last_name = user.last_name
#             account.amount = total/100
#             account.paid = True
#             account.phone = phone
#             account.additional_info = add_info
#             account.pay_code = ref
#             account.save()
            
#             return redirect(rdurl)
        
#         except Customer.DoesNotExist:
#             messages.error(request, 'Customer profile not found')
#         except requests.RequestException as e:
#             messages.error(request, f'Error making request to Paystack: {e}')
#         except KeyError as e:
#             messages.error(request, f'Key error in Paystack response: {e}')
#         except Exception as e:
#             messages.error(request, f'An error occurred: {e}')
        
#         return redirect('checkout')

@login_required(login_url='signin')
def pay(request):
    if request.method == 'POST':
        api_key = 'sk_test_8f12355ff2f260164c9cc6e580d2a1c01e94f1bd' #secret key from paystack
        curl = 'https://api.paystack.co/transaction/initialize' #paystack call url
        cburl = 'http://127.0.0.1:8000/callback' #payment thankyou page
        ref = str(uuid.uuid4()) #refrence number required by paystack as an additional order number
        profile = Customer.objects.get(user__username = request.user.username)
        order_no = profile.id #main order number
        total = float(request.POST['total']) * 100 #total amount to be charged from the customer's card
        user = User.objects.get(username = request.user.username) #query the user model for customer's model
        email = user.email #store customer's email to send to paystack
        first_name = request.POST['first_name'] #collect from ther template incase there is a change
        last_name = request.POST['last_name'] #collect from ther template incase there is a change
        phone = request.POST['phone'] #collect from ther template incase there is a change
        add_info = request.POST['add_info'] #collect from ther template incase there is a change
        
        #collect data to send paystack via call
        headers = {'Authorization': f'Bearer {api_key}'}
        data = {'reference':ref, 'amount':int(total), 'email':user.email, 'callback_url':cburl, 'order_number':order_no, 'currency':'NGN'}

        #make a call to paystack
        try:
            r = requests.post(curl, headers=headers, json=data)
        except Exception:
            messages.error(request, 'network busy, please try again')
        else:
            transback = json.loads(r.text)
            rdurl = transback['data']['authorization_url']
            print(transback)
            
            if rdurl:
                account = Payment()
                account.user = user
                account.first_name = user.first_name
                account.last_name = user.last_name
                account.amount = total/100
                account.paid = True
                account.phone = phone
                account.additional_info = add_info
                account.pay_code = ref
                account.save()
                
             
                return redirect(rdurl)
            
    return redirect('checkout')

@login_required(login_url='signin')
def callback(request):
    userprof = Customer.objects.get(user__username = request.user.username)
    cart = Cart.objects.filter(user__username = request.user.username, paid = False)
    
    for item in cart:
        item.paid = True
        item.save()
        
        car = Product.objects.get(pk=item.car.id)
        
    context = {
        'userprof':userprof,
        'cart':cart,
        'car':car
    }
    
    return render(request, 'callback.html')

def search(request):
    if request.method =='POST':
        items = request.POST['search']
        searched = Q(Q(model__icontains=items)| Q(year__icontains=items))
        searched_item = Product.objects.filter(searched)
        
        context = {
            'items':items,
            'searched_item':searched_item
        }
        
        return render(request, 'search.html', context)
    else:
        return render(request, 'search.html')
        