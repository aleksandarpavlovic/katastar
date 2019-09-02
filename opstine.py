import psycopg2

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


if __name__ == "__main__":

    try:
        connection = psycopg2.connect(user="postgres",
                                      password="postgres",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="katastar_db")
        cursor = connection.cursor()
        cursor.execute("prepare opstina_statement as insert into opstine (id, ime) values ($1,$2) on conflict do nothing")
        cursor.execute("prepare katastar_statement as insert into katastri (id, ime, opstina_id) values ($1,$2,$3) on conflict do nothing")
        for opstina in opstine:
            id_opstina = opstine[opstina]['id']
            cursor.execute("execute opstina_statement (%s, %s)", (id_opstina, opstina))
            for katastar in opstine[opstina]['katastri']:
                id_katastar = opstine[opstina]['katastri'][katastar]
                cursor.execute("execute katastar_statement (%s, %s, %s)", (id_katastar, katastar, id_opstina))
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            if cursor:
                cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
