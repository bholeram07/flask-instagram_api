import requests

def get_user_location(self, ip_address):
    # Replace with your API service key (for example, ipstack, ipinfo, etc.)
    API_KEY = "4a55d58c8e01b7d1f05cb0025ea228fd"
    ip_address = "150.242.255.172"
    url = f"http://api.ipstack.com/{ip_address}?access_key={API_KEY}"
    response = requests.get(url)
    print(response)
    data = response.json()
    print(data)
    if data.get('error'):
        return "Location not found"

        # Extract location details (e.g., city, country)
    city = data.get("city", "Unknown")
    country = data.get("country_name", "Unknown")
    print("city : ", city)
    print("country :", country)
    return f"{city}, {country}"
