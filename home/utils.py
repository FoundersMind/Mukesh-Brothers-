import requests

def get_user_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather_code = data["current_weather"]["weathercode"]  # Code-based condition
        temperature = data["current_weather"]["temperature"]
        
        weather_category = classify_weather(weather_code)  # Convert code to category
        return {"weather": weather_category, "temperature": temperature}
    else:
        return {"error": "Failed to fetch weather data"}

def classify_weather(code):
    """Maps Open-Meteo weather codes to categories"""
    if code in [0, 1]:  # Clear or Mostly Clear
        return "Summer"
    elif code in [2, 3, 45, 48]:  # Partly Cloudy / Foggy
        return "Winter"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:  # Rainy Conditions
        return "Rainy"
    else:
        return "Unknown"
