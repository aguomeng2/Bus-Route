import requests
import folium
import pandas as pd

def get_directions_response(lat1, long1, lat2, long2, mode=''):
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    key = "37f8744c21mshe0c9edb9569e7b4p1b5071jsn4d9229f4aa0b"
    host = "route-and-directions.p.rapidapi.com"
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
    querystring = {"waypoints": f"{str(lat1)},{str(long1)}|{str(lat2)},{str(long2)}", "mode": mode}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


def create_map(responses, lat_lons):
    m = folium.Map()
    df = pd.DataFrame()
    # add markers for the places we visit
    for point in lat_lons:
        folium.Marker(point).add_to(m)
    # loop over the responses and plot the lines of the route
    for response in responses:
        mls = response.json()['features'][0]['geometry']['coordinates']
        points = [(i[1], i[0]) for i in mls[0]]

        # add the lines
        folium.PolyLine(points, weight=5, opacity=1).add_to(m)
        temp = pd.DataFrame(mls[0]).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
        df = pd.concat([df, temp])
    # create optimal zoom
    sw = df[['Lat', 'Lon']].min().values.tolist()
    sw = [sw[0] - 0.0005, sw[1] - 0.0005]
    ne = df[['Lat', 'Lon']].max().values.tolist()
    ne = [ne[0] + 0.0005, ne[1] + 0.0005]
    m.fit_bounds([sw, ne])
    return m
