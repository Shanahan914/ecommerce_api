from .models import CustomUser, Product, Cart, CartItem, Order, OrderItem, Payment
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields  = ['email','password' ,'first_name', 'last_name', 'is_active', 'is_superuser', 'is_staff']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# for use in the cart item and order item serializers. Only serializes two fields. 
class ProductSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price']


class CartItemSerializer(serializers.ModelSerializer):
    #fetches all the data comes from the product serializer. This will appear against the 'product' field
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_detail = ProductSummarySerializer(source = 'product', read_only= True)
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity' ,'product_detail']
        #ensuring cart and product are unique together
        validators = [UniqueTogetherValidator(
            queryset= CartItem.objects.all(),
            fields = ['cart', 'product']
        )
        ]


    def create(self, validated_data):
        product = validated_data.pop('product')
        cart_item = CartItem.objects.create(product=product, **validated_data)
        return cart_item

# summary serializer for use in cart serializer. Omits 'cart' and removes other logic. 
class CartItemSummarySerializer(serializers.ModelSerializer):
    #fetches all the data comes from the product serializer. This will appear against the 'product' field
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_detail = ProductSummarySerializer(source = 'product', read_only= True)
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity' ,'product_detail']
        


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSummarySerializer(many=True, read_only = True)
    class Meta:
        model = Cart
        fields = ['id', 'owner', 'updated', 'cart_items']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        validators = [UniqueTogetherValidator(
            queryset= OrderItem.objects.all(),
            fields = ['order', 'product']
        )
        ]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only = True)

    status = serializers.ChoiceField(choices=Order.statusCodes.choices)

    class Meta:
        model = Order
        fields = ['id', 'owner', 'updated', 'total_price', 'status', 'order_items']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'