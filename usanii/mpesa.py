# mpesa.py
from datetime import datetime
import uuid

def initiate_stk_push(phone, amount, reference="ArtGalleryPayment"):
    """Simulate STK Push for school project"""
    return {
        "ResponseCode": "0",
        "ResponseDescription": "Success",
        "MerchantRequestID": "SIM-" + str(uuid.uuid4()),
        "CheckoutRequestID": "SIM-" + str(uuid.uuid4()),
        "CustomerMessage": "Payment simulated successfully for school project"
    }