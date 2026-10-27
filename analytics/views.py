import requests
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import WeatherLog

@login_required
def weather_dashboard(request):
    api_key = settings.WEATHER_API_KEY
    city = request.GET.get('city', 'Mumbai') # Default city
    weather_data = None
    agricultural_alert = None

    if api_key and api_key != 'paste_your_api_key_here':
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url).json()

        if response.get('cod') == 200:
            temp = response['main']['temp']
            humidity = response['main']['humidity']
            rainfall = response.get('rain', {}).get('1h', 0) # Rainfall in last 1 hour
            description = response['weather'][0]['description'].title()
            wind_speed = response['wind']['speed']

            weather_data = {
                'city': response['name'],
                'temp': temp,
                'humidity': humidity,
                'description': description,
                'wind': wind_speed,
                'rainfall': rainfall
            }

            # Save to database
            WeatherLog.objects.create(
                location=response['name'],
                temperature=temp,
                humidity=humidity,
                rainfall_mm=rainfall
            )

            # Generate Agricultural Alerts based on data
            if humidity > 80:
                agricultural_alert = "⚠️ HIGH HUMIDITY WARNING: Conditions are highly favorable for fungal diseases (like Late Blight). Ensure proper air circulation in your fields."
            elif rainfall > 5:
                agricultural_alert = "🌧️ HEAVY RAIN WARNING: High risk of soil erosion and runoff. Postpone any scheduled pesticide spraying today."
            elif temp > 38:
                agricultural_alert = "🔥 HEATWAVE WARNING: Extreme heat detected. Ensure your crops are adequately irrigated to prevent heat stress."
            else:
                agricultural_alert = "✅ OPTIMAL CONDITIONS: The current weather is favorable for normal farming activities."

    return render(request, 'analytics/weather.html', {
        'weather': weather_data,
        'alert': agricultural_alert,
        'city': city
    })