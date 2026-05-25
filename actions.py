import requests

def trigger_function():
    requests.get("http://192.168.1.173:5000/buzz")
    print("THE CAT IS IN THE AREA")
