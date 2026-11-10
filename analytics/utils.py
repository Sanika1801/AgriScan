import os
import requests

def get_disease_risk_alert(lat=28.61, lon=77.20): # Default to New Delhi coords
    """
    Fetches weather and calculates fungal disease risk.
    High risk if humidity > 80% and temp is between 15-30C.
    """
    try:
        # Free API, no key required
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        temp = data['current']['temperature_2m']
        humidity = data['current']['relative_humidity_2m']
        
        risk_level = "Low"
        disease_name = "No immediate threat"
        advice = "Weather conditions are stable."
        
        if humidity > 80 and 15 <= temp <= 30:
            risk_level = "High"
            disease_name = "Fungal Infection Risk (Late Blight / Powdery Mildew)"
            advice = "High humidity detected. Apply preventative copper-based fungicide."
        elif humidity > 65 and temp > 30:
            risk_level = "Moderate"
            disease_name = "Bacterial Spot Risk"
            advice = "Warm and somewhat humid. Monitor leaves closely."
            
        return {
            "temp": temp,
            "humidity": humidity,
            "risk_level": risk_level,
            "disease_name": disease_name,
            "advice": advice
        }
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

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