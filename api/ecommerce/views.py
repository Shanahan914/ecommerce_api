from django.shortcuts import render
from django.db.models import Q
from .serializers import *
from .models import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .stripe import create_payment_intent, handle_webhook
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from decimal import Decimal

# Create your views here.

# register 
# POST 
# /register
# NOTE A cart is automatically created via a signal 
class register_user(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()


#add to cart
# GET & POST
# /cart/<cart_id>
class view_add_cart(APIView):
    def get(self, request, pk):
        try:
            cart = Cart.objects.get(pk = pk)
            serializer= CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": str(e)}, status=500)
    
    def post(self, request, pk):
        data = request.data.copy()
        data['cart'] = pk
        serializer = CartItemSerializer(data=data)
        if serializer.is_valid():
            print('is valid')
            serializer.save()
            return Response(serializer.data, status =  status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#remove from cart OR update it
# DELETE / PUT
# /<cart_item_id>
#TODO need to add a put method. 
class remove_from_cart(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    lookup_field = 'pk'
    queryset = CartItem.objects.all()


#view products and search
# GET
# /products
class view_products(generics.ListAPIView):
    serializer_class = ProductSerializer
    # adding search functionailty. searches title and description
    def get_queryset(self):
        queryset = Product.objects.all()
        search_query = self.request.query_params.get('search', None)
        print(search_query)
        if search_query:
            queryset = queryset.filter( 
                Q(description__icontains = search_query) | Q(name__icontains = search_query))
        return queryset


# view all orders for customer and create an order
# GET & POST
# /order/
class view_order(APIView):

    def get(self, request):
        try:
            objects = Order.objects.filter(owner = self.request.user)
            serializer = OrderSerializer(objects, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({f"Error: str{e}"}, status=500)
    
    def post(self, request):
        # CREATE CART
        # fetch cart and cartitem data
        try:
            cart = Cart.objects.get(owner = request.user)
            cartItems = CartItem.objects.filter(cart = cart)

            if not cartItems.exists():
                return Response({"msg" : "cart is empty"}, status=400)
            
            data = CartItemSerializer(cartItems, many=True).data
            total = sum([Decimal(item['quantity']) * Decimal(item['product_detail']['price']) for item in data])

        except Cart.DoesNotExist as e:
            print(f"error ; {e}")
            return Response({"msg":"cart not found"}, status=404)
        except (ValueError, TypeError) as e:
            return Response({"msg":"error when calculating total price"}, status=500)
        
        # enter data into order table
        order = Order.objects.create(owner = request.user, total_price = total)
        serializer = OrderSerializer(order)

        
        
        # CREATE ORDER ITEMS
        try:
            order_items = [
            OrderItem(
                order=order,
                product = item.product,
                quantity = item.quantity,
            )
            for item in cartItems
        ]
            OrderItem.objects.bulk_create(order_items)
        except Exception as e:
            return Response({"msg": "order raised but error raised while creating order items"}, status=500)

        # delete cart items
        try:
            cartItems.delete()
        except Exception as e:
            return Response({"msg": "order raised but error raised while deleting cart items"}, status=500)
        
        #return the order
        return Response(serializer.data, status=201)


# view single order
# GET
# /order/<order_id>
class view_single_order(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Order.objects.filter(owner = self.request.user)


# checkout - proceeds to payment for the order
# POST 
# /checkout/<order_id>
class checkout(APIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def post(self, request, pk):
        user = request.user
        print(user)
        order_id = pk
        print(order_id)
        order = Order.objects.get(id = order_id)
        print(order)

        #create the stripe payment intent
        amount = int(100 *  Decimal(order.total_price))
        print(amount)
        stripe_response = create_payment_intent(amount, 'GBP')

        #create an entry in the payment table with the response from stripe. 
        intent_id = stripe_response.id
        status = stripe_response.status
        Payment.objects.create(
            customer = user,
            order = order,
            status = status,
            stripe_intent_id = intent_id
        )
        # my mythical frontend will use this code to interact directly with the stripe api
        return Response({"client secret": stripe_response.client_secret})


#stripe webhook
# POST
# stripe/webhook/
@csrf_exempt
def webhook(request):
    return handle_webhook(request.body)

