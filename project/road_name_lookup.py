import json
from shapely.geometry import shape, Point, LineString
import pyproj
from shapely.ops import transform


def load_geojson(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# WGS84經緯度（全球性資料，如：GPS） ＝> EPSG:4326
# TWD97經緯度（國土測繪中心發佈全國性資料）＝> EPSG:3824
# TM2（TWD97，中央經線121度）(適用臺灣本島，民國87年之後施行迄今) ＝> EPSG:3826
# TM2（TWD97，中央經線119度）(適用澎湖金門馬祖，民國87年之後施行迄今) ＝> EPSG:3825
# 哭阿我到底應該用哪一個坐標系 # 該問題應該已經解決


def twd97_to_wgs84(x, y):
    transformer = pyproj.Transformer.from_crs("EPSG:3826",
                                              "EPSG:4326",
                                              always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lon, lat


def wgs84_to_twd97(lon, lat):
    transformer = pyproj.Transformer.from_crs("EPSG:4326",
                                              "EPSG:3826",
                                              always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y


# 嘗試用容許值為 100 公尺進行處理
# 之後可能會改成找線與多邊形的交點用以提升準確度
# 註: TWD97 中的 1 就是 1 公尺
def get_road_info(start_lat,
                  start_lon,
                  end_lat,
                  end_lon,
                  geojson_data,
                  tolerance=100):
    start_point = Point(start_lon, start_lat)
    end_point = Point(end_lon, end_lat)
    line = LineString([start_point, end_point])
    closest_road_name = '未知道路'
    sidewalk_width = None

    for feature in geojson_data['features']:
        polygon = shape(feature['geometry'])
        if line.intersects(polygon):
            closest_road_name = feature['properties']['NAME']
            sidewalk_width = feature['properties']['SWW_WTH']
            break

    if closest_road_name != '未知道路':
        # print(
        #     f"TWD97位置({start_lat}, {start_lon}) 到 ({end_lat}, {end_lon}) 對應的道路名稱: {closest_road_name}, 人行道淨寬: {sidewalk_width}"
        # )
        print(f"TWD97 ({start_lat}, {start_lon}) to ({end_lat}, {end_lon}) road name: {closest_road_name}, sidewalk width: {sidewalk_width}")
    else:
        # print(
        #     f"經緯度 ({start_lat}, {start_lon}) 到 ({end_lat}, {end_lon}) 未找到對應的道路名稱"
        # )
        print(f"TWD97 ({start_lat}, {start_lon}) to ({end_lat}, {end_lon}) road name not found")

    return closest_road_name, sidewalk_width
