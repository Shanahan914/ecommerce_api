# E-commerce API

## Overview
This is a Django REST Framework project for an e-commerce application. It provides endpoints for user registration, authentication, product management, cart operations, and payment processing through Stripe.

It is created as a solution to the roadmap.sh e-commerce api. Details on the requirements can be found here https://roadmap.sh/projects/ecommerce-api.

As this a project solution, it still requires extra work to be production-ready. THis includes,but is not limited to, throttling, user permissions, additional functionality and unit tests. Nonetheless, I hope you can see the value in the project given these considerations. 

## Features
- User registration and login with JWT authentication
- Product listing and management
- Cart functionality for adding/removing products
- Order placement with total price calculation
- Payment processing using Stripe
- Webhook integration for payment status updates

## Models
- **CustomUser**: Extends Django's User model with additional fields.
- **Product**: Represents products available for purchase.
- **Cart**: Stores items a user intends to purchase.
- **Order**: Represents a completed purchase, including total price and status.
- **Payment**: Stores payment information related to orders.

## API Endpoints
- **User Endpoints**
  - `POST /api/register/`: Register a new user.
  - `POST /api/login/`: Obtain JWT tokens.

- **Product Endpoints**
  - `GET /api/products/`: Retrieve a list of products.

- **Cart Endpoints**
  - `GET /api/cart/<cart_id>/`: View cart details.
  - `POST /api/cart/<cart_id>/`: Add items to the cart.
 
- **Cart Item Endpoints**
  - `DELETE /api/cart_item/<cartitem_id>/`: Remove item from cart. 

- **Order Endpoints**
  - `POST /api/checkout/<order_id>/`: Create a payment intent and place an order.

- **Webhook Endpoint**
  - `POST /api/webhook/`: Handle Stripe webhook events for payment status updates.

## Testing
The project uses Django's test framework with API testing capabilities. Run tests using:
```bash
python manage.py test
```

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your `.env` file with necessary environment variables, including `STRIPE_SECRET_KEY`.
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## License
This project is licensed under the MIT License.
