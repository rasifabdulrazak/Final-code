from .views import *
import os
from Eshopee.settings import TWILIOACCOUNTSID,TWILIOAUTHTOKEN,TWILIOSERVICE
from twilio.rest import Client
from django.conf import settings
from decouple import config
from django.views.decorators.cache import never_cache
num = ''
otp = ''


# .............sending otp..............
def send_otp(number):
    global num
    num = number
    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID'] = TWILIOACCOUNTSID
        auth_token = os.environ['TWILIO_AUTH_TOKEN'] = TWILIOAUTHTOKEN
        client = Client(account_sid, auth_token)
        verification = client.verify \
            .services(TWILIOSERVICE) \
            .verifications \
            .create(to=num, channel='sms')
        return True
    except:
        return False


# ............verifying otp.............
def verify_otp(otp, request):
    account_sid = os.environ['TWILIO_ACCOUNT_SID'] = TWILIOACCOUNTSID
    auth_token = os.environ['TWILIO_AUTH_TOKEN'] = TWILIOAUTHTOKEN
    client = Client(account_sid, auth_token)
    verification_check = client.verify \
        .services(TWILIOSERVICE) \
        .verification_checks \
        .create(to="+91"+request.session['num'], code=otp)
    return verification_check.status

def verify_the_otp(otp):
    account_sid = os.environ['TWILIO_ACCOUNT_SID'] = TWILIOACCOUNTSID
    auth_token = os.environ['TWILIO_AUTH_TOKEN'] = TWILIOAUTHTOKEN
    client = Client(account_sid, auth_token)
    verification_check = client.verify \
        .services(TWILIOSERVICE) \
        .verification_checks \
        .create(to=num, code=otp)
    return verification_check.status