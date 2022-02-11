import os
from twilio.rest import Client
from django.views.decorators.cache import never_cache
num =''
otp =''
from .views import *


# .............sending otp..............
def send_otp(number):
    global num
    num = number
    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID'] = 'ACd645eeb7de9b137e225176640bbf9463'
        auth_token = os.environ['TWILIO_AUTH_TOKEN'] = 'bcc0377123dba01a4a718fc89436ab21'
        client = Client(account_sid, auth_token)
        verification = client.verify \
                        .services('VA3a30f2d843fecd0daac6d60b6c520e04') \
                        .verifications \
                        .create(to=num, channel='sms')
        return True
    except:
        return False


# ............verifying otp.............
def verify_otp(otp):
    account_sid = os.environ['TWILIO_ACCOUNT_SID'] = 'ACd645eeb7de9b137e225176640bbf9463'
    auth_token = os.environ['TWILIO_AUTH_TOKEN'] = 'bcc0377123dba01a4a718fc89436ab21'
    client = Client(account_sid, auth_token)
    verification_check = client.verify \
                            .services('VA3a30f2d843fecd0daac6d60b6c520e04') \
                            .verification_checks \
                            .create(to=num, code=otp)
    return verification_check.status
