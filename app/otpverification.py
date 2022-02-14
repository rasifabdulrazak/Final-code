from .views import *
import os
from twilio.rest import Client
from decouple import config
from django.views.decorators.cache import never_cache
num = ''
otp = ''


# .............sending otp..............
def send_otp(number):
    global num
    num = number
    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID'] = config('TWILIOACCOUNTSID')
        auth_token = os.environ['TWILIO_AUTH_TOKEN'] = config('TWILIOAUTHTOKEN')
        client = Client(account_sid, auth_token)
        verification = client.verify \
            .services(config('TWILIOSERVICE')) \
            .verifications \
            .create(to=num, channel='sms')
        return True
    except:
        return False


# ............verifying otp.............
def verify_otp(otp):
    account_sid = os.environ['TWILIO_ACCOUNT_SID'] = config('TWILIOACCOUNTSID')
    auth_token = os.environ['TWILIO_AUTH_TOKEN'] = config('TWILIOAUTHTOKEN')
    client = Client(account_sid, auth_token)
    verification_check = client.verify \
        .services(config('TWILIOSERVICE')) \
        .verification_checks \
        .create(to=num, code=otp)
    return verification_check.status
