import json

def parse_itinerary(text):
    try:
        return json.loads(text)
    except:
        return []