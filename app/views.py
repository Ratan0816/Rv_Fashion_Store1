from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.views import View
from django.utils.timezone import now
from .models import Product,Customer,Order,OrderItem,Cart
from django.views.generic import ListView,CreateView,DetailView
from django.views.generic.edit import UpdateView,DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.models import Permission
from django.contrib.auth.mixins import PermissionRequiredMixin,LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import CustomerForm,ProductForm,ContactForm
import razorpay
from django.conf import settings

# Create your views here.

def homepage(request):
    return render(request, 'home.html')

def aboutpage(request):
    return render(request, 'about.html')

def contactpage(request):
    return render(request, 'contact.html')

def contact_submit_page(request):
    return render(request, 'contact_submit.html')

def privacypolicypage(request):
    return render(request, 'privacy_policy.html')

def termspage(request):
    return render(request, 'terms.html')

def faqpage(request):
    return render(request, 'faq.html')

def login(request):
    return render(request,'login.html')

@login_required
def assign_permission_to_user(request):
    try:
        # Assign "can_add_product" permission to ""
        product_user = get_object_or_404(Customer, username="shree94")
        permission = Permission.objects.get(codename="can_add_product")
        product_user.user_permissions.add(permission)

        # Assign "can_update_product" permission to ""
        product_user2 = get_object_or_404(Customer, username="sakshi2000")
        permission2 = Permission.objects.get(codename="can_update_product")
        product_user2.user_permissions.add(permission2)

        return HttpResponse("Permissions added successfully.")
    except Exception as e:
        return HttpResponse(f"Error while assigning permissions: {e}")


def CustomerCreateView(request):
    if request.method=='POST':
        customer_form=CustomerForm(request.POST)
        if customer_form.is_valid():
            customer_form.save()
            return redirect('customer_list')
    else:
        customer_form=CustomerForm()
    return render(request,'customer_create_form.html',{'customer_form':customer_form})


def search_view(request):
    query=request.GET.get('q')
    product_manager=Product.objects.search(query)
    return render(request,'search_results.html',{'query': query,'product_manager': product_manager})

class CustomerList(ListView):
    model= Customer
    template_name= 'customer_list.html'
    context_object_name= 'customers'

class CustomerDetailView(DetailView):
    model= Customer
    template_name='customer_detail_view.html'

class CustomerUpdateView(UpdateView):
    model=Customer
    template_name='customer_update_view.html'
    fields=['f_name1','l_name1','email1','phone1','address1']
    success_url=reverse_lazy('customer_list')

class CustomerDeleteView(DeleteView):
    model= Customer
    template_name='customer_delete_view.html'
    success_url=reverse_lazy('customer_list')


class ProductCreateView(CreateView):
    model=Product
    template_name= 'products_create_form.html'
    fields= ['name','category','price','quantity_in_stock','description_text','image']
    success_url= reverse_lazy('products_list')


class ProductList(ListView):
    model= Product
    template_name= 'products_list.html'
    context_object_name= 'products'


class ProductDetailView(DetailView):
    model=Product
    template_name='products_detail_view.html'
    pk_url_kwarg = 'id'

class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin,UpdateView):
    model=Product
    template_name='product_update_view.html'
    fields=['name','category','price','quantity_in_stock','description_text','image']
    success_url=reverse_lazy('products_list')

    permission_required='app.can_add_product','app.can_update_product'


class ProductDeleteView(LoginRequiredMixin,DeleteView):
    model= Product
    template_name='products_delete_view.html'
    success_url=reverse_lazy('products_list')

# the cart functionality
class AddToCartView(View):
    def post(self, request):
        if request.user.is_authenticated:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))

            product = None

            if product_id:
                product = get_object_or_404(Product, id=product_id)

            if not product:
                return JsonResponse({'error': 'No product added to cart'}, status=400)

            cart_item, created = Cart.objects.get_or_create(
                customer_id = request.user,
                product_id = product,
                defaults = {'quantity': quantity, 'date_added': now()}
            )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            return redirect('view_cart')
        return JsonResponse({'error': 'You need to log in first..!'}, status=403)

class CartView(ListView):
    model = Cart
    template_name = 'cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(customer_id=self.request.user)
        return Cart.objects.none()
    
class RemoveFromCartView(View):
    def post(self, request, cart_id):
        if request.user.is_authenticated:
            cart_item = get_object_or_404(Cart, id=cart_id, customer_id=request.user)
            cart_item.delete()
            return redirect('view_cart')
        
class CreateOrderView(View):
    def post(self, request):
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(customer_id=request.user)
            if not cart_items:
                return JsonResponse({'error': 'Cart is empty'})
            
            total_amount = 0
            for item in cart_items:
                if item.product_id:
                    total_amount += item.product_id.price * item.quantity
            
            order = Order.objects.create(
                user_id = request.user,
                order_date = now(),
                total_amount = total_amount    
            )

            for item in cart_items:
                if item.product_id:
                    OrderItem.objects.create(
                        order_id=order,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        price=item.product_id.price * item.quantity
                    )
            
            cart_items.delete()

            return redirect('order_summary', order_id=order.id)
        return JsonResponse({'error': 'You need to log in first'}, status=403)


class OrderSummaryView(View):
    template_name = 'order_summary.html'

    def get(self, request, order_id):
        if request.user.is_authenticated:
            # Fetch the order
            order = get_object_or_404(Order, id=order_id, user_id=request.user)
            
            # Fetch the related order items
            order_items = OrderItem.objects.filter(order_id=order)
            
            # Prepare context data for rendering
            context = {
                'order': order,
                'order_items': order_items,
            }
            return render(request, self.template_name, context)
        else:
            return JsonResponse({'error': 'You need to log in first.'},status=403)
        
class ProceedToPaymentView(View):
    template_name = 'proceed_to_payment.html'

    def get(self, request, order_id):
        if request.user.is_authenticated:
            order = get_object_or_404(Order, id=order_id, user_id=request.user)

            if order.payment_status != 'PENDING':
                return JsonResponse({'error': 'This order is already processed.'}, status=400)

            # Create Razorpay order
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
            razorpay_order = client.order.create({
                'amount': int(order.total_amount * 100),
                'currency': 'INR',
                'payment_capture': '1',
            })

            # Save Razorpay order ID
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            context = {
                'order': order,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_api_key': settings.RAZORPAY_API_KEY,
                'order_total': order.total_amount,
            }

            return render(request, self.template_name, context)
        else:
            return JsonResponse({'error': 'You need to log in first.'}, status=403)

    def post(self, request, order_id):
        if request.user.is_authenticated:
            order = get_object_or_404(Order, id=order_id, user_id=request.user)
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
    
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            # Debug logs
            print(f"POST Data: Order ID: {razorpay_order_id}, Payment ID: {razorpay_payment_id}, Signature: {razorpay_signature}")

            if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
                return JsonResponse({'error': 'Invalid payment details.'}, status=400)

            try:
                # Verify payment signature
                params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature,
                }
                client.utility.verify_payment_signature(params_dict)

                # Fetch and verify payment status
                payment = client.payment.fetch(razorpay_payment_id)
                if payment['status'] == 'captured':
                    order.payment_status = 'COMPLETED'
                    order.razorpay_payment_id = razorpay_payment_id
                    order.save()
                    return redirect('payment_success', order_id=order.id)
                else:
                    print(f"Payment not captured. Status: {payment['status']}")
                    order.payment_status = 'FAILED'
                    order.save()
                    return JsonResponse({'error': 'Payment not captured.'}, status=400)
            except razorpay.errors.SignatureVerificationError as e:
                pass 
        else:
            return JsonResponse({'error': 'You need to log in first.'}, status=403)

class PaymentSuccessView(View):
    template_name = 'payment_success.html'

    def post(self, request, order_id):
        if request.user.is_authenticated:
            order = get_object_or_404(Order, id=order_id, user_id=request.user)
            if order.payment_status == 'COMPLETED':
                return render(request, self.template_name, {'order': order})
        return JsonResponse({'error': 'You need to log in first.'}, status=403)       


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save contact data to the database
            return redirect('contact_submit')  # Redirect to the contact_submit page
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})