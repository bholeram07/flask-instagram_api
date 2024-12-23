import requests

def get_user_location(ip_address):
    # Replace with your API service key (for example, ipstack, ipinfo, etc.)
    API_KEY = "4a55d58c8e01b7d1f05cb0025ea228fd"
    ip_address = "150.242.255.172"
    url = f"http://api.ipstack.com/{ip_address}?access_key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data.get('error'):
        return "Location not found"

    # Extract location details (e.g., city, country)
    city = data.get("city", "Unknown")
    country = data.get("country_name", "Unknown")
    return f"{city}, {country}"
