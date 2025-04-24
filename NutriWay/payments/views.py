from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from specialists.models import SubscriptionPlan
from django.core.mail import send_mail
from django.contrib.auth.models import User
import logging
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

@login_required
def start_checkout(request : HttpRequest, plan_id : int) -> HttpResponse: 
    try:
        # Retrieve the subscription plan
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        logger.error(f"Plan with ID {plan_id} does not exist")
        return HttpResponse("Invalid plan ID", status=400)


    # Create a Stripe checkout session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'sar',
                    'product_data': {
                        'name': f'{plan.duration}-Month Nutrition Plan',
                    },
                    'unit_amount': int(round(plan.price * 100)),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://localhost:8000/payments/success/?plan_id={plan.id}',
            cancel_url='http://localhost:8000/payments/cancel/',
            metadata={
                "plan_id": plan.id,
                "user_id": request.user.id
            }
        )    
    except stripe.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return HttpResponse("Error creating checkout session", status=500)

    #Redirect directly to Stripe
    return redirect(session.url)
    

@login_required
def payment_success(request : HttpRequest) -> HttpResponse:
    user = request.user
    try:
        # Retrieve the plan ID from the request query parameters
        plan_id = request.GET.get('plan_id')
        if not plan_id:
            logger.error("Plan ID is missing in the request")
            return HttpResponse("Plan ID is required", status=400)
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        logger.error(f"Plan with ID {plan_id} does not exist")
        return HttpResponse("Invalid plan ID", status=400)

    # Create payment record
    try:
        payment = Payment.objects.create(
            user=request.user,
            specialist=plan.specialist,
            subscription_plan=plan,
            amount=plan.price,
            payment_status='Paid'
        )
    except Exception as e:
        logger.error(f"Error creating payment record: {e}")
        return HttpResponse("Error creating payment record", status=500)

    # Send confirmation email
    try:
        send_mail(
            subject='NutriWay - Payment Confirmation',
            message=(
                f"Hi {user.first_name},\n\n"
                f"Your payment of {plan.price} SAR for the {plan.duration}-month plan has been received.\n"
                f"Your specialist is {plan.specialist.user.username}.\n\n"
                f"Plan Details:\n"
                f"Name: {plan.name}\n"
                f"Description: {plan.description}\n"
                f"Thank you for subscribing to NutriWay!"
                f"\n\nBest regards,\n"
                f"NutriWay Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")

    # Render the success page
    return render(request, 'payments/success.html', {
        'plan': plan,
        'amount': plan.price,
    })


def payment_cancel(request : HttpRequest) -> HttpResponse:
    # Handle payment cancellation
    return render(request, 'payments/cancel.html')
