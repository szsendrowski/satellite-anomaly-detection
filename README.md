# Helio Alert Notifications System (HANS)

## Wprowadzenie
HANS to zestaw narzędzi do analizy środowiska kosmicznego w pobliżu Ziemi. Repozytorium
zawiera trzy moduły badawcze oraz aplikację Streamlit prezentującą wyniki w formie
interaktywnego interfejsu. Każdy moduł koncentruje się na innym aspekcie pogody
kosmicznej:

* **DTM / SWAMI (module1)** – generowanie globalnych map gęstości atmosfery na
  podstawie elementów orbitalnych TLE z wykorzystaniem modelu SWAMI (DTM2020).
* **CME & geomagnetyzm (module2)** – obliczanie natężenia ziemskiego pola
  magnetycznego na podstawie współczynników IGRF i trajektorii satelity ISS.
* **Koronalne wyrzuty masy (module3)** – pobieranie kolejnych obrazów z koronografu
  LASCO oraz analiza różnicowa obrazów w celu monitorowania aktywności Słońca.

Dodatkowo w katalogu `modules/notification` znajdują się skrypty pomocnicze do
powiadamiania o zdarzeniach kosmicznych (np. wysyłanie wiadomości e-mail lub SMS).

## Struktura repozytorium
```
.
├── GUI/                # aplikacja Streamlit z podstronami dla każdego modułu
├── data/               # dane wejściowe (TLE, współczynniki IGRF, itp.)
├── modules/
│   ├── module1/        # narzędzia do obliczeń DTM/SWAMI
│   ├── module2/        # narzędzia do analiz magnetosferycznych
│   ├── module3/        # skrypty do pobierania i przetwarzania danych koronograficznych
│   └── notification/   # integracje powiadomień
├── output/             # domyślne miejsce zapisu wyników i wykresów
└── tmp/                # katalog tymczasowy wymagany przez SWAMI
```

## Wymagania

### Podstawowe pakiety Python
* Python 3.9+ (zalecany 64-bit)
* `numpy`, `scipy`, `pandas`
* `matplotlib`, `cartopy`, `tqdm`
* `skyfield`, `swami`
* `streamlit`
* (opcjonalnie) `sunpy`, `astropy` – wymagane do modułu koronograficznego

Przykładowa instalacja w środowisku wirtualnym:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r GUI/requirements.txt
pip install swami tqdm cartopy sunpy
```

### SWAMI / DTM2020
Model SWAMI (DTM2020) wymaga zewnętrznego pliku wykonywalnego `swami.x` dostępnego
na systemach Windows. W pliku `modules/module1/module1.py` należy zaktualizować
ścieżki:

* `swami.SWAMI_EXE` – lokalizacja programu `swami.x`
* zmienna środowiskowa `PATH` – ścieżka do bibliotek MSYS2 wymaganych przez SWAMI
* `TMPDIR` – folder tymczasowy, domyślnie `tmp/`

### Dane wejściowe
* `data/LEO_data.tle` – katalog elementów orbitalnych TLE wykorzystywanych w module 1.
* `modules/module2/igrf14coeffs.txt` oraz `modules/module2/TLE_ISS.txt` – współczynniki
  IGRF i TLE Międzynarodowej Stacji Kosmicznej.
* Moduł 3 pobiera dane bezpośrednio z serwerów `sunpy` (potrzebne połączenie z siecią).

## Uruchamianie modułów

### Moduł 1 – Atmosfera termiczna (DTM/SWAMI)
```bash
python modules/module1/module1.py
```
Skrypt wybiera najlepiej dopasowane TLE z zakresu LEO (70–120 min okresu), oblicza
trajektorię satelity i generuje globalną mapę gęstości atmosfery zapisaną w katalogu
`output/` oraz wyświetlaną na ekranie.

### Moduł 2 – Pole magnetyczne Ziemi
```bash
python modules/module2/module2.py
```
Skrypt interpoluje współczynniki IGRF dla wskazanego roku, wyznacza natężenie pola
magnetycznego na siatce 5°×5° na wysokości 408 km oraz symuluje przebieg natężenia na
trajektorii ISS. Wynikowy wykres oraz plik CSV z danymi (`ISS_trajectory_magnetic_field.csv`)
zostają zapisane w katalogu modułu.

### Moduł 3 – Analiza koronografu LASCO
Moduł składa się z funkcji pomocniczych w `coronadata.py` i `coronaDiff.py`. Aby pobrać
kolejne obrazy LASCO i przygotować mapy różnicowe, uruchom odpowiedni skrypt lub
zaimportuj funkcje w notatniku Jupyter. Przykład:
```python
from modules.module3.coronadata import fetch_two_sequential_maps
map1, map2 = fetch_two_sequential_maps()
```
Następnie można wykorzystać `coronaDiff.py` do wyznaczenia różnic i filtracji szumu.

## Aplikacja Streamlit
Aplikacja w katalogu `GUI/` zapewnia graficzny dostęp do wyników modułów. Po
zainstalowaniu zależności uruchom:
```bash
cd GUI
streamlit run GUI_App.py
```
Podstrony w katalogu `GUI/pages/` odpowiadają kolejno modułom DTM, CME i MF.

## Dane wyjściowe i logi
* Obrazy, mapy oraz wykresy zapisywane są w katalogu `output/` (lub wewnątrz katalogów
  modułów, jeśli skrypt wskazuje inaczej).
* Logi pracy modeli SWAMI zapisywane są w `tmp/` – upewnij się, że katalog istnieje i
  użytkownik ma prawa zapisu.

## Rozszerzanie projektu
* Dodaj nowe moduły w `modules/` i zarejestruj je jako nowe podstrony Streamlit.
* Wykorzystaj katalog `modules/notification/` do integracji z usługami powiadamiania
  (np. Twilio, SMTP).
* Rozbuduj pliki TLE i współczynniki modeli, aby monitorować inne satelity i wysokości.

## Licencja
Projekt udostępniany jest na licencji MIT (szczegóły w pliku `LICENSE`).
