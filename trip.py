import json
import traceback
import maps
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


def run_script(start_entry, end_entry, result_textbox):
    start = start_entry.get()
    end = end_entry.get()
    current_time = 1800 #int(datetime.now().strftime("%H%M"))
    cost_per_stop = 0.5
    cost_per_transfer = 5

    print("loading JSON")
    with open("stops.json", "r") as f:
        stops = json.load(f)
    with open("services.json", "r") as f:
        services_data = json.load(f)
    with open("routes.json", "r") as f:
        routes = json.load(f)
    with open("fares.json", "r") as f:
        fares_data = json.load(f)

    print("Initializing tables")
    stop_code_map = {stop["BusStopCode"]: stop for stop in stops}
    services = {service["ServiceNo"]: service for service in services_data}
    distances = []
    fare_values = []
    express_fares = []

    for i in range(1, len(fares_data)):
        distance = float(fares_data[i]["Distance(km)"])
        fare = float(fares_data[i]["Basic Bus"].replace('$', ''))
        express_fare = float(fares_data[i]["Express Services"].replace('$', ''))
        distances.append(distance)
        fare_values.append(fare)
        express_fares.append(express_fare)

    routes_map = {}
    for route in routes:
        try:
            first_bus = int(route["WD_FirstBus"])
            last_bus = int(route["WD_LastBus"])
        except:
            continue
        if first_bus <= last_bus:
            if not (first_bus <= current_time <= last_bus):
                continue
        if first_bus > last_bus:
            if (last_bus <= current_time <= first_bus):
                continue

        key = (route["ServiceNo"], route["Direction"])
        if key not in routes_map:
            routes_map[key] = []
        routes_map[key] += [route]

    print("Initializing Graph")
    graph = {}
    for service, path in routes_map.items():
        for route_index in range(len(path) - 1):
            key = path[route_index]["BusStopCode"]
            if key not in graph:
                graph[key] = {}
            curr_route_stop = path[route_index]
            next_route_stop = path[route_index + 1]
            curr_distance = curr_route_stop["Distance"] or 0
            next_distance = next_route_stop["Distance"] or curr_distance
            distance = next_distance - curr_distance
            assert distance >= 0, (curr_route_stop, next_route_stop)
            curr_code = curr_route_stop["BusStopCode"]
            next_code = next_route_stop["BusStopCode"]
            graph[curr_code][(next_code, service)] = distance

    print("Running BFS")

    def dijkstras(graph, start, end):
        import heapq
        seen = set()
        # maintain a queue of paths
        queue = []
        # push the first path into the queue
        heapq.heappush(queue, (0, 0, 0, [(start, None)]))
        while queue:
            # get the first path from the queue
            (curr_cost, curr_distance, curr_transfers, path) = heapq.heappop(queue)

            # get the last node from the path
            (node, curr_service) = path[-1]

            # path found
            if node == end:
                return (curr_cost, curr_distance, curr_transfers, path)

            if (node, curr_service) in seen:
                continue

            seen.add((node, curr_service))
            # enumerate all adjacent nodes, construct a new path and push it into the queue
            for (adjacent, service), distance in graph.get(node, {}).items():
                new_path = list(path)
                new_path.append((adjacent, service))
                new_distance = curr_distance + distance
                new_cost = distance + curr_cost
                new_transfers = curr_transfers
                if curr_service != service:
                    new_cost += cost_per_transfer
                    new_transfers += 1
                new_cost += cost_per_stop

                heapq.heappush(queue, (new_cost, new_distance, new_transfers, new_path))

    try:
        (cost, distance, transfers, path) = dijkstras(graph, start,
                                                      end)
        result_text = ""
        lat_lons = []
        responses = []
        express_bus = False
        for i in range(len(path)):
            code, service = path[i]
            if service is not None and len(service) == 2:
                if service[0] in services:
                    category = services[service[0]]["Category"]
                    if category == "EXPRESS":
                        express_bus = True
            result_text += f"{service} {stop_code_map[code]['Description']}\n"

            # Get the latitude and longitude of the current node
            lat1 = stop_code_map[code]['Latitude']
            long1 = stop_code_map[code]['Longitude']
            lat_lons.append((lat1, long1))
            # Get the latitude and longitude of the node after the current node
            if i < len(path) - 1:
                next_code, _ = path[i + 1]
                lat2 = stop_code_map[next_code]['Latitude']
                long2 = stop_code_map[next_code]['Longitude']

                # Run get_directions_response with lat1, long1, lat2, long2
                response = maps.get_directions_response(lat1, long1, lat2, long2, mode='drive')
                responses.append(response)
        result_text += f"{len(path)} stops\n"
        result_text += f"distance: {distance} km\n"
        result_text += f"transfers: {transfers - 1}\n"
        m = maps.create_map(responses, lat_lons)
        m.save('./route_map.html')

        # Compare the distance with the fares and retrieve the fare value
        for i in range(1, len(distances)):
            if distance <= distances[i]:
                if express_bus:
                    fare = express_fares[i]
                else:
                    fare = fare_values[i]
                result_text += f"Fare: ${fare}\n"
                break

        result_textbox.delete(1.0, tk.END)  # Clear previous results
        result_textbox.insert(tk.END, result_text)

    except Exception as e:
        error_message = f"An error occurred:\n\n{str(e)}"
        traceback_str = traceback.format_exc()
        error_message += f"\n\nTraceback:\n\n{traceback_str}"
        messagebox.showerror("Error", error_message)

