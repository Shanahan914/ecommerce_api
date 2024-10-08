from stripe import StripeClient, Event 
from decouple import config
from django.http import HttpResponse
import json
from .models import Payment 

STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')

client = StripeClient('STRIPE_SECRET_KEY')

# list customers
def list_customers():
    try:
        return client.customers.list()
    except Exception as e:
        print('stripe error when retrieving list of customers:', e)
        return None


# retrieve single customer
def retrieve_customer(id):
    try:
        return client.customers.retrieve(id)
    except Exception as e:
        print('stripe error when retrieving customer:', e)
        return None


# raise payment intent
def create_payment_intent(amount, currency):
    try:
        return client.payment_intents.create(amount=amount, currency=currency)
    except Exception as e:
        print('stripe error when raising payment intent:', e)
        return None


# confrim payment intent
def confirm_payment_intent(intent_id):
    try:
        client.payment_intents.confirm(intent_id)
    except Exception as e:
        print('stripe error when confirming payment intent:', e)
        return None


#retrieve_payment_intent
def retrieve_payment_intent(intent_id):
    try:
        client.payment_intents.retrieve(intent_id)
    except Exception as e:
        print('stripe error when retrieving payment intent:', e)
        return None
    

#webhook handler
#TODO read about logging and then add. 
def handle_webhook(payload):
    event = None
    try:
        event = Event.construct_from(
        json.loads(payload), STRIPE_SECRET_KEY
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        Payment.objects.filter(stripe_intent_id = payment_intent.id).update(status=payment_intent.status)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        Payment.objects.filter(stripe_intent_id = payment_intent.id).update(status=payment_intent.status)
    else:
        print('Unhanded event type:', event['type'])
        
    return HttpResponse(status=200)
