import folium
import pandas as pd
import sklearn
import requests
import os
from dotenv import load_dotenv
import urllib.parse
import networkx as nx
import osmnx as ox
import math

from road_name_lookup import load_geojson, get_road_info, twd97_to_wgs84, wgs84_to_twd97

# 加載 .env 文件
load_dotenv()

# 獲取 Google API Key
api_key = os.getenv('apikey')

geojson_data = None
accidents = []

def init():
    global geojson_data
    global accidents

    # 加載 GeoJSON 資料
    geojson_data = load_geojson('SIDEWALK_1_202406_TWD97.geojson')

    # 加載事故資料
    accident_data = pd.read_csv('accident_data.csv')
    accident_df = pd.DataFrame(accident_data)
    accident_df = accident_df[accident_df['發生地點'].notnull()]

    for i in range(len(accident_df)):
        lat = accident_df['緯度']
        lng = accident_df['經度']
        accidents.append((lat[i], lng[i]))

# 地名轉換經緯度
def get_coordinates(place):
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={place}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        # results = data['results']
        # if len(results) > 1:
        #     print("找到多個選項，請選擇一個：")
        #     for i, result in enumerate(results[:5], 1):  # 顯示前五個選項
        #         print(f"{i}. {result['formatted_address']}")
        #     choice = int(input("請輸入選項編號：")) - 1
        #     location = results[choice]['geometry']['location']
        # else:
        #     location = results[0]['geometry']['location']

        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        # print("無法找到該位置，請重新輸入。")
        print("Can't find the location, please try again.")
        return None

# 使用 Google Maps Directions API 獲取步行路線
def get_directions(start_coords, end_coords, avoid_coords=None):
    avoid_str = ''
    if avoid_coords:
        avoid_str = '|'.join([f'{lat},{lng}' for lat, lng in avoid_coords])
        url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start_coords[0]},{start_coords[1]}&destination={end_coords[0]},{end_coords[1]}&waypoints=optimize:true|{avoid_str}&alternatives=true&mode=walking&key={api_key}'
    else:
        url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start_coords[0]},{start_coords[1]}&destination={end_coords[0]},{end_coords[1]}&mode=walking&key={api_key}'

    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        route = data['routes'][0]['legs'][0]['steps']
        route_coords = [(step['start_location']['lat'],
                         step['start_location']['lng']) for step in route]
        route_coords.append((route[-1]['end_location']['lat'],
                             route[-1]['end_location']['lng']))
        return route_coords
    else:
        # print("無法獲取路線，請檢查起點和終點是否正確。")
        print("Route unreachable, please check if the start and end points are correct.")
        return None

# 生成 Google Maps 路徑連結
def generate_google_maps_link(route_coords, waypoints_flag=True):
    base_url = "https://www.google.com/maps/dir/?api=1&travelmode=walking"
    waypoints = "&waypoints=" + "|".join(
        [f"{lat},{lng}" for lat, lng in route_coords[1:-1]])
    origin = f"&origin={route_coords[0][0]},{route_coords[0][1]}"
    destination = f"&destination={route_coords[-1][0]},{route_coords[-1][1]}"

    if not waypoints_flag:
        waypoints = ''

    return base_url + origin + destination + waypoints

# 使用 OSMnx 來獲取新的路徑
def get_directions_osmnx(start_coords, end_coords, avoid_edges):
    G = ox.graph_from_point(start_coords, dist=1000, network_type='walk')
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    for edge in avoid_edges:
        u, v, key = ox.nearest_edges(G,
                                     edge[0][1],
                                     edge[0][0],
                                     return_dist=False)
        if G.has_edge(u, v, key):
            G.remove_edge(u, v, key)

    orig_node = ox.nearest_nodes(G, start_coords[1], start_coords[0])
    dest_node = ox.nearest_nodes(G, end_coords[1], end_coords[0])
    route = nx.shortest_path(G, orig_node, dest_node, weight='travel_time')
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
    return route_coords

# 計算兩條路徑之間的差異
def get_path_difference(route1, route2):
    set1 = set(route1)
    set2 = set(route2)
    difference = set1.symmetric_difference(set2)
    return list(difference)

def simplify_coords(coords, tolerance):
    from shapely.geometry import LineString
    line = LineString(coords)
    simplified_line = line.simplify(tolerance, preserve_topology=True)
    return list(simplified_line.coords)

def calculate_distance(coord1, coord2):
    RADIUS = 6373.0

    lat1 = math.radians(abs(coord1[0]))
    lon1 = math.radians(abs(coord1[1]))
    lat2 = math.radians(abs(coord2[0]))
    lon2 = math.radians(abs(coord2[1]))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = RADIUS * c
    return distance

def generate_route(start_coords, end_coords, weight_tolerance):
    print(f'Start coordinate: {start_coords}\nEnd coordinate: {end_coords}')

    route_coords_google = get_directions(start_coords, end_coords)
    old_route_link = generate_google_maps_link(route_coords_google)
    if route_coords_google is None:
        return None

    # 創建地圖並添加 Google Maps 瓦片層
    m = folium.Map(location=[(start_coords[0] + end_coords[0]) / 2,
                            (start_coords[1] + end_coords[1]) / 2],
                zoom_start=13)

    # 添加 Google Maps 瓦片層
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
                    attr='Google',
                    name='Google Maps',
                    overlay=False,
                    control=True).add_to(m)

    # 添加舊路徑到地圖
    folium.PolyLine(route_coords_google, color='gray', weight=5,
                    opacity=0.7).add_to(m)

    # 添加起點和終點標記
    folium.Marker(start_coords, tooltip='起點').add_to(m)
    folium.Marker(end_coords, tooltip='終點').add_to(m)

    # # 加載本地 GeoJSON 資料
    # geojson_data = load_geojson('SIDEWALK_1_202406_TWD97.geojson')

    global geojson_data
    global accidents

    # 定義不可通行的路段索引
    non_walkable_indices = []

    # 顯示舊路徑經過的路和轉彎點
    old_markers = []
    for i in range(len(route_coords_google) - 1):
        # 獲取當前路段的名稱和人行道淨寬
        start_lat, start_lon = route_coords_google[i]
        end_lat, end_lon = route_coords_google[i + 1]
        start_lon, start_lat = wgs84_to_twd97(start_lon, start_lat)  # 轉換座標系
        end_lon, end_lat = wgs84_to_twd97(end_lon, end_lat)
        street_name, sidewalk_width = get_road_info(start_lat, start_lon, end_lat,
                                                    end_lon, geojson_data)
        start_lon, start_lat = twd97_to_wgs84(start_lon, start_lat)
        end_lon, end_lat = twd97_to_wgs84(end_lon, end_lat)

        # 添加經緯度資訊
        popup_text = f"起點經緯度: ({start_lat}, {start_lon})\n終點經緯度: ({end_lat}, {end_lon})\n道路名稱: {street_name}\n人行道淨寬: {sidewalk_width}"

        # 計算不良人行道權重
        bad_sidewalk_weight = 0

        # 檢查附近是否有事故發生
        for acc in accidents:
            distance = calculate_distance((start_lat, start_lon), acc)
            if distance < 0.1:
                bad_sidewalk_weight += 1

        # 如果人行道淨寬小於 1 公尺，則添加權重
        if (sidewalk_width is not None and sidewalk_width < 1):
            bad_sidewalk_weight += 5

        print(f"Bad sidewalk weight: {bad_sidewalk_weight}")

        # 如果不良人行道權重超過容許值，則添加紅色標記
        if bad_sidewalk_weight > weight_tolerance:
            folium.Marker(route_coords_google[i],
                        icon=folium.Icon(color='red'),
                        popup=popup_text).add_to(m)
            non_walkable_indices.append((i, i + 1))
        else:
            folium.Marker(route_coords_google[i],
                        icon=folium.Icon(color='green'),
                        popup=popup_text).add_to(m)
        old_markers.append((start_lat, start_lon))

    # 添加不可通行的路線
    for start, end in non_walkable_indices:
        folium.PolyLine(route_coords_google[start:end + 1],
                        color='red',
                        weight=5,
                        opacity=0.7).add_to(m)

    simplified_route_coords = route_coords_google

    if len(non_walkable_indices) > 0:
        # 重新規劃路線，避開不可通行的區域
        avoid_edges = []
        for start, end in non_walkable_indices:
            avoid_edges.append((route_coords_google[start], route_coords_google[end]))

        new_route_coords_osmnx = get_directions_osmnx(start_coords, end_coords, avoid_edges)
        if new_route_coords_osmnx is None:
            return None

        # 添加新的路徑到地圖
        ## folium.PolyLine(new_route_coords_osmnx, color='blue', weight=5,
        ##                 opacity=0.7).add_to(m)

        path_difference = get_path_difference(route_coords_google,
                                            new_route_coords_osmnx)

        # 簡化新的路徑
        simplified_route_coords = simplify_coords(new_route_coords_osmnx,
                                                tolerance=0.0005)

    # 繪製簡化後的路徑
    folium.PolyLine(simplified_route_coords, color='blue', weight=5,
                    opacity=0.7).add_to(m)

    # 生成並列印 Google Maps 路徑連結
    original_route_link = generate_google_maps_link(route_coords_google, False)
    old_route_link = generate_google_maps_link(route_coords_google)
    new_route_link = generate_google_maps_link(simplified_route_coords)
    print(f"\nOriginal route: {original_route_link}\n")
    print(f"Old route: {old_route_link}\n")
    print(f"New route: {new_route_link}")

    # 保存地圖到 HTML 文件
    m.save("route_map.html")
    print("The route is saved in route_map.html")

    return new_route_link

def _test():
    # 使用 get_coordinates 獲取起點和終點的經緯度
    start_place = input("請輸入起點位置：")
    start_coords = get_coordinates(start_place)
    if start_coords is None:
        print("無法獲取起點經緯度，程式終止。")
        return

    end_place = input("請輸入終點位置：")
    end_coords = get_coordinates(end_place)
    if end_coords is None:
        print("無法獲取終點經緯度，程式終止。")
        return

    weight_tolerance = int(input("請輸入不良人行道權重容許值 (1-10)："))
    if (weight_tolerance < 1 or weight_tolerance > 10):
        print("輸入值無效，程式終止。")
        return

    generate_route(start_coords, end_coords, weight_tolerance)
