import time
import requests
import psycopg2

FETCH_LIMIT = 20
URL = "https://nominatim.openstreetmap.org/reverse"
PARAMS = {
    'format': 'json',
    'lat': 'TO BE POPULATED',
    'lon': 'TO BE POPULATED',
    'zoom': '18',
    'addressdetails': '1'
}
HEADERS = {
    'UserAgent': "Katastar/1.0 (pretraga.stanova@gmail.com)"
}
TIMEOUT = 5


def get_timeout(url, headers, params, timeout=TIMEOUT):
    try:
        return requests.get(url=url, headers=headers, params=params, timeout=timeout)
    except Exception:
        return None


def get_retry(url, headers, params, retry_count=2):
    response = get_timeout(url=url, headers=headers, params=params)
    count = 0
    while not response and count < retry_count:
        time.sleep(1)
        count += 1
        response = get_timeout(url=url, headers=headers, params=params)
    return response


def obtain_address(lat, lon):
    PARAMS['lat'] = lat
    PARAMS['lon'] = lon
    response = get_retry(URL, HEADERS, PARAMS)

    if response:
        data = response.json()
        address = {
            'lat': lat,
            'lon': lon
        }
        address_data = data.get('address')
        if address_data:
            street = address_data.get('road')
            pedestrian = address_data.get('pedestrian')

            number = address_data.get('house_number')

            neighbourhood = address_data.get('neighbourhood')
            address_29 = address_data.get('address_29')
            residential = address_data.get('residential')

            city_part = address_data.get('suburb')
            city_district = address_data.get('city_district')

            address['number'] = number if number is not None else None
            address['street'] = street if street is not None else pedestrian
            address[
                'neighbourhood'] = neighbourhood if neighbourhood is not None else address_29 if address_29 is not None else residential
            address['city_part'] = city_part if city_part is not None else city_district

        return address
    elif response is None:
        raise Exception("Response was not recevied within timeout period of {} seconds. You should try again.".format(TIMEOUT))
    elif response.status_code == 429:
        raise Exception("The script was blocked due to too many requests(status code 429). You should try again later.")
    else:
        raise Exception("OSM API server returned unsuccessful response (status code {}). You should try again later.".format(response.status_code))


if __name__ == "__main__":
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="katastar_db")
        cursor = connection.cursor()
        cursor.execute("prepare neskenirane_adrese_statement as select lat, lon from adrese where skenirano <> true order by lat,lon limit $1")
        cursor.execute("prepare skenirana_adresa_statement as update adrese set ulica=$3, broj=$4, naselje=$5, deo_grada=$6, skenirano=true where lat=$1 and lon=$2")

        cursor.execute("select count(*) from adrese where skenirano <> true")
        address_cnt = cursor.fetchone()[0]
        offset, cnt = 0, 0
        while offset < address_cnt:
            cursor.execute("execute neskenirane_adrese_statement (%s)", [FETCH_LIMIT])
            latlons = cursor.fetchall()
            addresses = []
            for row in latlons:
                start_time_ms = time.time_ns() // 1000000
                lat, lon = row[0], row[1]
                address = obtain_address(lat, lon)
                addresses.append(address)
                cnt += 1
                if cnt % 5 == 0:
                    print("{}/{} addresses resolved".format(cnt, address_cnt))
                elapsed_time_ms = time.time_ns() // 1000000 - start_time_ms
                # we do not want to load nominatim api service with too many requests, so we should keep it under 1 req/s as noted at https://operations.osmfoundation.org/policies/nominatim/
                if (elapsed_time_ms < 1000):
                    time.sleep((1000 - elapsed_time_ms) / 1000)
            for address in addresses:
                cursor.execute("execute skenirana_adresa_statement (%s, %s, %s, %s, %s, %s)", (address.get('lat'), address.get('lon'), address.get('street'), address.get('number'), address.get('neighbourhood'), address.get('city_part')))
            connection.commit()
            print("Persisted last {} scanned addresses".format(FETCH_LIMIT))
            offset += FETCH_LIMIT
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
    except Exception as error:
        print("Exception occurred during run: ", error)
    finally:
        # closing database connection.
        if connection:
            if cursor:
                cursor.close()
            connection.close()
