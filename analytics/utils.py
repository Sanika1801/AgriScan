import os

def send_sms(phone_number, message):
    """
    Mock SMS Sender. 
    In production, you would replace the print statement with a real API call 
    to Twilio, Fast2SMS, or Gupshup.
    """
    if not phone_number:
        print(f"⚠️ Could not send SMS: No phone number provided.")
        return False
        
    print("\n" + "="*50)
    print(f"📱 MOCK SMS SENT TO: {phone_number}")
    print(f"💬 MESSAGE: {message}")
    print("="*50 + "\n")
    
    return True

# If you get a real API key in the future, you just change the code to this:
# def send_sms(phone, message):
#     import requests
#     url = "https://www.fast2sms.com/dev/bulkV2"
#     payload = f"authorization=YOUR_API_KEY&message={message}&language=english&route=q&numbers={phone}"
#     headers = {'content-type': "application/x-www-form-urlencoded"}
#     requests.request("POST", url, data=payload, headers=headers)