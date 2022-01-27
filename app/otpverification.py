import os
from twilio.rest import Client
num =''
otp =''

from .views import *

# .............sending otp..............

def send_otp(number):
    global num
    num = number
    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID'] = 'AC3207c2b834a4fb5d151a073c8cd9d7ec'
        auth_token = os.environ['TWILIO_AUTH_TOKEN'] = 'db3193b8d624c6bb7607e3e6d375fe8c'
        client = Client(account_sid, auth_token)
        verification = client.verify \
                        .services('VA68685e82ab5c6aa20cf8cf3082bddce2') \
                        .verifications \
                        .create(to=num, channel='sms')
        return True
    except:
        return False

# ............verifying otp.............

def verify_otp(otp):
    account_sid = os.environ['TWILIO_ACCOUNT_SID'] = 'AC3207c2b834a4fb5d151a073c8cd9d7ec'
    auth_token = os.environ['TWILIO_AUTH_TOKEN'] = 'db3193b8d624c6bb7607e3e6d375fe8c'
    client = Client(account_sid, auth_token)

    verification_check = client.verify \
                            .services('VA68685e82ab5c6aa20cf8cf3082bddce2') \
                            .verification_checks \
                            .create(to=num, code=otp)

    
    return verification_check.status
