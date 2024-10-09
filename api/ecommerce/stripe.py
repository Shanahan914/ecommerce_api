import stripe
from decouple import config
from django.http import HttpResponse
import json
from .models import Payment 

STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
stripe.api_key = config('STRIPE_SECRET_KEY')


# raise payment intent
def create_payment_intent(amount, currency):
    try:
        return stripe.PaymentIntent.create(amount=amount, 
                                             currency=currency,
                                             payment_method_types=['card'] )
    except Exception as e:
        print('stripe error when raising payment intent:', e)
        return None
    

#webhook handler
def handle_webhook(payload):
    event = None
    try:
        event = stripe.Event.construct_from(
        json.loads(payload), STRIPE_SECRET_KEY
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse( status=400)
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        Payment.objects.filter(stripe_intent_id = payment_intent.id).update(status=payment_intent.status)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        Payment.objects.filter(stripe_intent_id = payment_intent.id).update(status=payment_intent.status)
    else:
        print('Unhanded event type:', event['type'])
        
    return HttpResponse(status=200)
