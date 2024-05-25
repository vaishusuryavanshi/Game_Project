from django.shortcuts import render,HttpResponse,redirect
from gameapp.forms import ProductForm,UpdateProductForm ,RegisterUserForm,LoginUserForm #for add product form
from gameapp.models import Product, Cart ,Reviews,Orders
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.db.models import Avg
from django.conf import settings
from django.core.mail import get_connection, EmailMessage
import random
import razorpay


# Create your views here.
def index(request):

    return render(request,'index.html')

def product_add(request):

    form =ProductForm(request.POST,request.FILES)

    if request.method == "POST":

        form.save()

        return redirect("/products/show")
    
    else:
        
        form = ProductForm() #we created Form variable to save info in that variable. 2nd thing we need to send that variable to addproduct.html that why we created context below


        context = {} #created empty dicti

        context ['form'] = form # created keyword ['form'] to save data from form

        return render(request,'addproduct.html',context)


def product_show(request):

    obj =Product.objects.all()

    context ={}

    context['data'] = obj
    rating ={}
    for x in obj:

        rate = Reviews.objects.filter(prod =x).aggregate(Avg('rating'))
        rating[x]=rate

    context['rate'] = rating

    print(context)
    return render(request, 'showproduct.html',context)

def product_edit(request,rid):


    obj = Product.objects.get(id = rid )


    if request.method== "POST":

        form = UpdateProductForm(request.POST, request.FILES, instance= obj)

        form.save()

        return redirect ('/products/show')

    else:
        obj = Product.objects.get(id =rid)
         
        form = UpdateProductForm(instance= obj)
    
        context ={}

    context['form'] =form

    return render(request,'editproduct.html',context)

def product_delete(request,rid):

    obj = Product.objects.filter(id= rid)

    obj.delete()

    return redirect('/products/show')

def user_register(request):

    form = RegisterUserForm(request.POST)    #all data from reg.html going save in form vari

    if request.method == "POST" and form.is_valid():

        password =form.cleaned_data['password']     #like od method(fillter) we using cleaned_data to fetch password. form.cleaned_data form- from form filter password
        password2= form.cleaned_data['password2']

        if password != password2:
            context ={}

            context['msg']= 'Password & Confirm password is not match '

            context['form'] = form

            return render (request,'registration.html',context)
        
        else:
            user = form.save(commit=True) # before saving data come from form we need to update form before save to show password in encrypt format

            user.set_password(password)
            user.save()
            context ={}

            context['msg'] = "User Registered Successfully"
            context['form'] = form

            return render(request,'registration.html',context)

    else:

         form = RegisterUserForm()

         context ={}
         context['form'] = form

         return render(request,'registration.html',context)
  

   
def user_login(request):
    
    form= LoginUserForm(request.POST)

    if request.method=="POST" and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(username= username, password= password)

        if user is not None:

            login(request,user)

            return redirect('/')



    else:
        form = LoginUserForm
    
        context = {}

        context['form'] = form

        return render(request,'login.html',context)
    
def user_logout(request):

    logout(request)

    return redirect('/')   

@login_required(login_url="/login")
def add_to_cart(request,rid):

        prod = Product.objects.get(id = rid)

        cart = Cart.objects.filter(user = request.user,prod= prod).exists()
        if cart:

            return redirect('/products/show')
        else:
            p = Product.objects.get(id=rid)

            total_price = p.price

            

            c=Cart.objects.create(user = request.user, prod = p, total_price = total_price)

            c.save()

            return redirect('/products/show')

def show_cart(request):

    c = Cart.objects.filter(user = request.user)

    total_quantity = 0


    for x in c:
        total_quantity =total_quantity + x.quantity

    t_price = 0
    final_price=0

    for x in c:

        t_price = t_price * x.quantity

        final_price = final_price + x.total_price




    context = {}

    context['data'] = c

    context['total_quantity'] = total_quantity

    context['final_price']= final_price

    return render(request, 'cart.html',context)


def remove_cart(request,rid):

    c =Cart.objects.filter(id=rid)

    c.delete()

    return redirect('/cart')  

def update_cart(request, rid, cid):

    c = Cart.objects.filter(prod =cid)

    total = c[0].prod.price * float(rid)

    c.update(quantity = rid, total_price = total)

    return redirect ('/cart')  

def blank(request):
    return render (request,'blank.html')

def add_to_order(request):

    cart = Cart.objects.filter(user = request.user)

    for x in cart:
        prod = x.prod
        quantity = x.quantity
        price = x.total_price

        order = Orders.objects.create(user=request.user, prod = prod, quantity=quantity, total_price=price)
        order.save()
    cart.delete()


        
    return render(request,'payment.html')

def show_order(request):
    
    obj = Orders.objects.filter(user = request.user)

    context = {}
    context['data'] = obj

    return render (request,"order.html",context)

def add_review(request,rid):

    p = Product.objects.get(id = rid) # featching the data

    review = Reviews.objects.filter(user= request.user, prod = p)

    if not review:


        if request.method == 'POST':
                p = Product.objects.get(id=rid)

                r = request.POST['review']

                i = request.FILES['image']

                s = request.POST['rating']   # rating saving in s

                obj = Reviews.objects.create(user = request.user,prod = p , review = r , rating = s,image =i)
                obj.save()
                return redirect('/orders')

        return render(request,'review.html')
    
    else:

        if request.method == "GET":
            p = Product.objects.get(id=rid)
            review = Reviews.objects.filter(user =request.user,prod = p)

            context = {}
            context['data'] = review
            return render(request,'editreview.html',context)
        
        else:
             p = Product.objects.get(id=rid)
             review = Reviews.objects.filter(user =request.user,prod = p)
             
             r = request.POST['review']
             i = request.FILES['image']
             s = request.POST['rating']

             review.update(review=r ,rating = s, image =i)

             return redirect('/orders')


def product_details(request,rid):
    prod = Product.objects.get(id = rid)
    review = Reviews.objects.filter(prod = prod)
    avg = Reviews.objects.filter(prod =prod).aggregate(Avg('rating'))

    avgrating = int(avg['rating__avg'])

    context = {}

    context['data'] = review

    context ['rating'] = avgrating

    return render(request,'productdetails.html',context)


def send_otp(request):
    
    
    if request.method == "GET":
        
        return render(request, 'send_otp.html')
    
    else:
        email = request.POST['email']
        
        request.session['email']= email
        
        user = User.objects.filter(email=email)
        
        if user is not None:

            otp = random.randint(1000,9999)
            
            request.session['otp']=otp
            
            with get_connection(
                host = settings.EMAIL_HOST,
                port = settings.EMAIL_PORT,
                username = settings.EMAIL_HOST_USER,
                password = settings.EMAIL_HOST_PASSWORD,
                use_tls = settings.EMAIL_USE_TLS,
            ) as connection:
                subject="OTP Verification"
                email_from= settings.EMAIL_HOST_USER
                Reception_list=[ email ]
                message= f"OTP is {otp}"
                
                EmailMessage(subject, message, email_from, Reception_list, connection= connection).send()
                
                return redirect('/verify_otp')
            
        else:
            return HttpResponse("User Not Found")
        
def verify_otp(request):
    if request.method == 'GET':
        return render(request, 'verify_otp.html')
    else:
        otp =request.session['otp']
        user_otp = request.POST['otp']
        
        otp = int(otp)
        user_otp= int(user_otp)
        
        if otp == user_otp:
            return redirect('/update_password')
        else:
            return HttpResponse('otp not same')
    
def update_password(request):
    
    if request.method == "GET":
        return render(request,'updatepassword.html')
    
    else:
        email= request.session['email']
        
        user = User.objects.get(email=email)
        
        
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            
            return redirect('/login')
        
        else:
            
            return HttpResponse('Password and Confirm Password Does not match')        
