import requests
import json

api_key = 'Fl77fEZnRu+1Vv7tnF+lnQ=='
headers = {'AccountKey': api_key}

def fetch_all(url):
    results = []
    skip = 0
    while True:
        response = requests.get(
            url,
            headers=headers,
            params={'$skip': skip}
        )
        data = response.json()
        new_results = data['value']
        if not new_results:
            break
        results += new_results
        skip += len(new_results)
    return results

if __name__ == "__main__":
    base_url = "http://datamall2.mytransport.sg/ltaodataservice"

    stops_url = f"{base_url}/BusStops"
    stops = fetch_all(stops_url)
    with open("stops.json", "w") as f:
        json.dump(stops, f)

    services_url = f"{base_url}/BusServices"
    services = fetch_all(services_url)
    with open("services.json", "w") as f:
        json.dump(services, f)

    routes_url = f"{base_url}/BusRoutes"
    routes = fetch_all(routes_url)
    with open("routes.json", "w") as f:
        json.dump(routes, f)
