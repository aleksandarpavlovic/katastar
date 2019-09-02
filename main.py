import psycopg2
import requests
import json
import datetime
import sys
import getopt

# constants
APARTMENT = 831
GARAGE = 835
# broj uzastopnih dana koji ce biti obuhvaceni jednim requestom
# koristim da bih smanjio ukupan broj requestova, umesto da idem dan za dan, idem po nedelju dana
# api katastra se cudno ponasa kada se ovaj broj poveca na 100 dana npr, tj ne vraca sve rezultate iako nije ispunio max od 250
# najbolje ostaviti ovako
DAYS_PER_REQUEST = 7
MAX_RESPONSE_SIZE = 250

# opstine za pretragu. inicijalno je ovde spisak svih katastara u beogradu.
# slobodno obrisi one opstine i katastre koji ti nisu od interesa tipa: ostruznica, beli potok i sl.
opstine = {
    'Novi Beograd': {
        'id': 70181, "katastri": {
            'Novi Beograd': 716090
        }
    },
    'Vracar': {
        'id': 70114, "katastri": {
            'Vracar': 703648
        }
    },
    'Savski Venac': {
        'id': 70220, "katastri": {
            'Savski Venac': 704008
        }
    },
    'Stari Grad': {
        'id': 70246, "katastri": {
            'Stari Grad': 704059
        }
    },
    'Zvezdara': {
        'id': 70149,
        "katastri": {
            'Veliki Mokri Lug': 703583,
            'Mali Mokri Lug': 703842,
            'Zvezdara': 703745,
            'Mirijevo': 703885
        }
    },
    'Rakovica': {
        'id': 70211,
        "katastri": {
            'Knezevac': 703796,
            'Resnik': 703940,
            'Stara Rakovica': 704032
        }
    },
    'Zemun': {
        'id': 70157,
        "katastri": {
            'Batajnica': 716014,
            'Zemun': 716065,
            'Zemun Polje': 716073,
            'Ugrinovci': 716138
        }
    },
    'Cukarica': {
        'id': 70254,
        "katastri": {
            'Velika Mostanica': 703559,
            'Zeleznik': 703702,
            'Ostruznica': 703893,
            'Rusanj': 703982,
            'Sremcica': 704024,
            'Umka': 704067,
            'Cukarica': 704083
        }
    },
    'Vozdovac': {
        'id': 70106,
        "katastri": {
            'Beli Potok': 703494,
            'Vozdovac': 703621,
            'Zuce': 703753,
            'Jajinci': 703761,
            'Kumodraz': 703800,
            'Pinosava': 703915,
            'Rakovica': 703931,
            'Ripanj': 703958
        }
    },
    'Palilula': {
        'id': 70203,
        "katastri": {
            'Besni Fok': 732176,
            'Borca': 732184,
            'Veliko Selo': 703591,
            'Visnjica': 703613,
            'Kovilovo': 732192,
            'Komareva Humka': 732206,
            'Krnjaca': 732214,
            'Lepusnica': 732222,
            'Ovca': 732249,
            'Palilula': 703907,
            'Slanci': 704016
        }
    }
}


def is_invalid_contract(contract):
    return contract['id'] is None \
           or contract['date'] is None \
           or contract['price'] is None \
           or contract['price'] <= 0 \
           or contract['area'] is None \
           or contract['area'] <= 0


# check if there is more than one apartment, or apartment + something which is not garage
def is_multi_contract(data):
    if len(data['n']) > 1:
        apt_cnt, garage_cnt, other_cnt = 0, 0, 0
        for realty in data['n']:
            if realty['vNepID'] == APARTMENT:  # stan
                apt_cnt += 1
            elif realty['vNepID'] == GARAGE:  # garaza
                garage_cnt += 1
            else:
                other_cnt += 1
        return apt_cnt > 1 or other_cnt > 0


def extract_garage_count(data):
    if len(data['n']) > 1:
        garage_cnt = 0
        for realty in data['n']:
            if realty['vNepID'] == GARAGE:  # garaza
                garage_cnt += 1
        return garage_cnt
    else:
        return 0


def extract_apartment(data):
    for realty in data['n']:
        if realty['vNepID'] == APARTMENT:
            return realty


def validate_dates(start_date, end_date):
    if end_date < start_date:
        raise Exception('End date must not be before start date!')


def is_response_max_size_exceeded(parsed_response):
    return len(parsed_response['d']['Ugovori']) == MAX_RESPONSE_SIZE


def parse_response(response):
    return json.loads(response.content.decode('UTF-8'))


def extract_contracts(response, id_katastar):
    contracts_dict = response['d']['Ugovori']
    contracts = []
    for data in contracts_dict.values():
        if is_multi_contract(data):
            continue
        apartment = extract_apartment(data)
        contract = {
            'id': data['uID'],
            'date': datetime.datetime.strptime(data['datumU'], '%d.%m.%Y'),
            'price': data['cena'] // 120 if data['cenaV'] == 'RSD' else data['cena'],
            'area': apartment['pov'],
            'id_katastar': id_katastar
        }
        if is_invalid_contract(contract):
            continue
        contract['pricem2'] = round(contract['price'] / contract['area'], 2)
        contract['garagecount'] = extract_garage_count(data)
        contract['lat'] = apartment['latlon']['Lat']
        contract['lon'] = apartment['latlon']['Lon']
        contracts.append(contract)
    return contracts


if __name__ == "__main__":
    start_date = datetime.date.today()
    end_date = start_date
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:e:", ["startdate=", "enddate="])
    except getopt.GetoptError:
        print
        'main.py -s <start date (inclusive) in format dd.mm.yyyy> -e <end date (inclusive) in format dd.mm.yyyy>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print
            'main.py -s <start date (inclusive) in format dd.mm.yyyy> -e <end date (inclusive) in format dd.mm.yyyy>'
            sys.exit()
        elif opt in ("-s", "--startdate"):
            start_date = datetime.datetime.strptime(arg, '%d.%m.%Y')
        elif opt in ("-e", "--enddate"):
            end_date = datetime.datetime.strptime(arg, '%d.%m.%Y')
    validate_dates(start_date, end_date)

    url = "http://katastar.rgz.gov.rs/RegistarCenaNepokretnosti/Default.aspx/Data"
    headers = {
        'Content-type': "application/json",
        'Host': "katastar.rgz.gov.rs",
        'Origin': "http://katastar.rgz.gov.rs",
        'Referer': "http://katastar.rgz.gov.rs/RegistarCenaNepokretnosti/"
    }
    body = {
        'DatumPocetak': 'TO BE POPULATED',
        'DatumZavrsetak': 'TO BE POPULATED',
        'OpstinaID': 'TO BE POPULATED',  # opstina
        'KoID': 'TO BE POPULATED',  # katastarska opstina
        'VrsteNepokretnosti': str(APARTMENT)  # stan
    }
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="katastar_db")
        cursor = connection.cursor()
        cursor.execute("prepare nekretnine_statement as insert into nekretnine (id, datum, cena, kvadratura, cenam2, lat, lon, garaze, katastar_id) values ($1,$2,$3,$4,$5,$6,$7,$8,$9) on conflict do nothing")

        current_date = start_date
        while current_date <= end_date:
            days_per_req = min(DAYS_PER_REQUEST, (end_date-current_date).days+1)
            print("Processing date: {} and next {} days".format(current_date.date(), days_per_req-1))
            contracts = []
            for opstina in opstine:
                id_opstina = opstine[opstina]['id']
                for id_katastar in opstine[opstina]['katastri'].values():
                    days = days_per_req
                    sdate = current_date
                    edate = current_date + datetime.timedelta(days=days-1)
                    while sdate <= edate and days >= 1:
                        body['DatumPocetak'] = sdate.strftime("%d.%m.%y")
                        body['DatumZavrsetak'] = (sdate + datetime.timedelta(days=days-1)).strftime("%d.%m.%y")
                        body['OpstinaID'] = id_opstina
                        body['KoID'] = id_katastar
                        try:
                            response = requests.post(url=url, data=json.dumps(body), headers=headers)
                            response_dict = parse_response(response)
                            if is_response_max_size_exceeded(response_dict) and days > 1:
                                print("Response for {} consecutive days returned maximum of {} contracts which means some contracts might be missing. Attempting with {} consecutive days...".format(days, MAX_RESPONSE_SIZE, days // 2))
                                days = days // 2
                            else:
                                contracts.extend(extract_contracts(response_dict, id_katastar))
                                sdate = sdate + datetime.timedelta(days=days)
                                days = (edate - sdate).days + 1
                        except Exception as error:
                            print("Exception occurred during processing of date: {}".format(current_date), error)

            for contract in contracts:
                cursor.execute("execute nekretnine_statement (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (contract['id'], contract['date'], contract['price'], contract['area'], contract['pricem2'], contract['lat'], contract['lon'], contract['garagecount'], contract['id_katastar']))
            connection.commit()
            current_date = current_date + datetime.timedelta(days=days_per_req)
    except psycopg2.Error as error:
        print("Error while connecting to PostgreSQL", error)
    except Exception as error:
        print("Exception occurred during run", error)
    finally:
        # closing database connection.
        if connection:
            if cursor:
                cursor.close()
            connection.close()
            print("Done processing dates: {} - {}".format(start_date.date(), end_date.date()))
