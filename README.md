# Katastar
Skripta za prikupljanje informacija o kupoprodajama stanova na teritoriji Srbije.
Inicijalno skripta podržava samo Beograd.

*(za napredne korisnike) Lako je proširiti podršku i na ostale gradove. Potrebno je samo malo kopati po source kodu stranice [http://katastar.rgz.gov.rs/RegistarCenaNepokretnosti/](http://katastar.rgz.gov.rs/RegistarCenaNepokretnosti/) gde ćete naći id-eve odgovarajućih opština/katastara i uneti ih u skripte opstine.py i main.py*

## Kako se koristi?
### Ovo radite samo prvi put
Potrebno je instalirati Postgresql bazu i pgAdmin 4 tool. [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
A morate imati i python 3. [https://www.python.org/downloads/](https://www.python.org/downloads/)

Kreiranje baze je najjednostavnije odraditi kroz pgAdmin gui, importovanjem baze iz **db_create.custom** ili **db_create.sql** fajla.

Pokrenite skriptu **opstine.py** kako bi inicijalizovali bazu podacima o opštinama i katastrima.
### Ovo radite periodično, s vremena na vreme, kad vam se ćefne...
Pokrenite skriptu **main.py** sa sledećim parametrima:
**-s dd.mm.yyyy -e dd.mm.yyyy**

npr: -s 28.06.2017 -e 19.12.2017 pretražuje nekretnine prodate između Vidovdana i Nikoljdana 2017. godine.

### Opciono periodično
Ukoliko želite da imate i adrese stanova pokrenite skriptu **adrese.py** koja će za stanove u vašoj bazi pronaći i adrese [https://nominatim.openstreetmap.org/](https://nominatim.openstreetmap.org/).
Imajte u vidu da se ova skripta izvršava veoma sporo (da ne bi preopteretili Nominatim servis [https://operations.osmfoundation.org/policies/nominatim/](https://operations.osmfoundation.org/policies/nominatim/)). Na svoju odgovornost možete da probate da smanjite vreme čekanja između dva uzastopna zahteva ka Nominatimu kako bi ubrzali postupak, ali rizikujete da vam blokiraju IP adresu i onda možete samo da se slikate.

### Kako da pristupite bazi
Kroz pgAdmin alat možete da pristupite sadržaju baze ili da ga exportujete u .csv pa da gledate u excellu i izvodite tu razne neke statistike i grafikone. To kako šta, guglajte malo...
