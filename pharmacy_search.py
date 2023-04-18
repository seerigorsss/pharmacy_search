import math
import sys
from io import BytesIO
from PIL import Image

import requests


# Функция для вычисления расстояния между двумя объектами
def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    return distance


# python pharmacy_search.py Москва, улица Льва Толстого, 16
# python pharmacy_search.py Пресненская наб., 8, стр. 1, Москва
toponym_to_find = "".join(sys.argv[1:])

# Работа с геокодером исходного адреса
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    print("Ошибка выполнения запроса:")
    print(response.url)
    print("Http статус:", response.status_code, "(", response.reason, ")")

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
toponym_coodrinates = toponym["Point"]["pos"].split()

# Переходим к поиску ближайшей аптеки
search_api_server = "https://search-maps.yandex.ru/v1/"
address_ll = f'{toponym_coodrinates[0]},{toponym_coodrinates[1]}'

search_params = {
    "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if response:
    json_response = response.json()

    organization = json_response["features"][0]
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    org_work_time = organization["properties"]["CompanyMetaData"]["Hours"]["text"]

    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    delta = "0.005"

    map_params = {
        "l": "map",
        "pt": f'{org_point},pm2bl~{address_ll},pm2al',
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)
    print(f'\t----Название: {org_name}\n'
          f'\t----Адрес: {org_address}\n'
          f'\t----Время работы: {org_work_time}')
    Image.open(BytesIO(
        response.content)).show()
else:
    print("Ошибка выполнения запроса:")
    print(response.url)
    print("Http статус:", response.status_code, "(", response.reason, ")")
