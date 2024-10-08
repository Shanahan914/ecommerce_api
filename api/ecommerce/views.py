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
# GET TODO: POST
# /order/
# class view_order(generics.ListAPIView):
#     serializer_class = OrderSerializer
#     def get_queryset(self):
#         return Order.objects.filter(owner = self.request.user)
    
class view_order(APIView):
    
    def get(self, request):
        try:
            objects = Order.objects.filter(owner = self.request.user)
            serializer = OrderSerializer(objects)
            return Response(serializer.data, staus=200)
        except Exception as e:
            return Response({"Error:", e}, status=500)
    
    def post(self, request):
        #create order
        # cart = Cart.objects.get(owner = request.user)
        print(request.user)
        return Response({"msg":"test"})


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
# NOTE so we just need
class checkout(APIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def post(self, request, pk):
        user = request.user.id 
        order_id = pk
        order = Order.objects.get(id = order_id)

        #create the stripe payment intent
        stripe_response = create_payment_intent(order.total_price, 'GBP')

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
    handle_webhook(request.body)
    # payload = request.body
    # event = None
    # try:
    #     event = stripe.Event.construct_from(
    #     json.loads(payload), stripe.api_key
    #     )
    # except ValueError as e:
    #     # Invalid payload
    #     return HttpResponse(status=400)
    # #use helper func to deal with the event
   


