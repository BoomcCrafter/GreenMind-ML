import serial
import time
import pandas as pd
import joblib

model = joblib.load("model_lr_60s_final.joblib")

temperatura_zadana = float(input("Podaj temperature zadana: [C]: "))

print("Temperatura zadana: ", temperatura_zadana)
print("Model zaladowany!")

arduino = serial.Serial("/dev/ttyUSB0", 9600, timeout=2)

poprzednia_dol = None
poprzednia_gora = None
start = None

Kp = 50
Ki = 10
Kd = 2

suma_uchybu = 0.0  
poprzedni_czas_min = None
roznica_czasu = 0.0
poprzednia_temp = None

parametry = []


while True:
    dane = arduino.readline().decode("utf-8").strip()

    if not dane:
        continue

    wartosci = dane.split(",")
    print(wartosci)

    if len(wartosci) != 4:
        continue

    try:
        temp_dol = float(wartosci[0])
        temp_gora = float(wartosci[1])
        wentylator = int(wartosci[2])
        pwm = int(wartosci[3])

    except ValueError:
        continue

    temp_srednia = (temp_dol + temp_gora) /2

    if start is None:
        start = time.monotonic()

    czas_start_min = (time.monotonic() - start) / 60

    if poprzednia_dol is None and poprzednia_gora is None:
        poprzednia_gora = temp_gora
        poprzednia_dol = temp_dol
        continue

    roznica_temp_diff_gora = temp_gora - poprzednia_gora
    roznica_temp_diff_dol = temp_dol - poprzednia_dol

    poprzednia_gora = temp_gora
    poprzednia_dol = temp_dol

    blad = temperatura_zadana - temp_srednia

    roznica_temp = abs(temp_dol - temp_gora)


    df = pd.DataFrame([{
    "temp_dol": temp_dol,
    "temp_gora": temp_gora,
    "pwm": pwm,
    "wentylator": wentylator,
    "czas_start_min": czas_start_min,
    "roznica_temp": roznica_temp,
    "roznica_temp_diff_gora": roznica_temp_diff_gora,
    "roznica_temp_diff_dol": roznica_temp_diff_dol,
    "temp_srednia": temp_srednia
    }])

    df = df[model.feature_names_in_]
    prognoza = model.predict(df)[0]

    blad_ml = temperatura_zadana - prognoza

    print("Temperatura zadana: ", temperatura_zadana)
    print("Temperatura aktualna: ", temp_srednia)
    print("Blad: ", blad)
    print("Czas liczony w minutach: ", czas_start_min)

    if poprzedni_czas_min is None:
        roznica_czasu = 0.0
    else:
        roznica_czasu = czas_start_min - poprzedni_czas_min

    poprzedni_czas_min = czas_start_min
    suma_uchybu = suma_uchybu + blad * roznica_czasu

    if poprzednia_temp is None or roznica_czasu <= 0:
        D = 0.0
    else:
        roznica_temp_d = temp_srednia - poprzednia_temp
        D = -Kd * (roznica_temp_d / roznica_czasu)

    temp_graniczna = temperatura_zadana * 1.05

    if temp_srednia >= temp_graniczna:
        wentylator = 1
    else:
        wentylator = 0

    poprzednia_temp = temp_srednia

    I = Ki * suma_uchybu
    P = Kp * blad




    pwm_proponowany = P + I + D

    if pwm_proponowany > 255:
        pwm_proponowany = 255
    if pwm_proponowany <0:
        pwm_proponowany = 0    

    pwm_proponowany = int(pwm_proponowany)

    komenda = f"{pwm_proponowany},{wentylator}\n"

    arduino.write(komenda.encode("utf-8"))

    print("Wartosc czlonu P: ", P)
    print("Wartosc czlonu I: ", I)
    print("Wartosc czlonu D: ", D)
    print("Proponowany PWM: ", pwm_proponowany)
    print("Wyslano do arduino: ", komenda.strip())
    print("------------------------------------------")
    print()

    parametry.append({
        "czas_min" : czas_start_min,
        "temp_zadana" : temperatura_zadana,
        "temp_dol" : temp_dol,
        "temp_gora" : temp_gora,
        "temp_srednia" : temp_srednia,
        "blad" : blad,
        "blad_ml" : blad_ml,
        "P" : P,
        "I" : I,
        "D" : D,
        "pwm_nadany" : pwm_proponowany,
        "wentylator" : wentylator,
        "prognoza_ml" : prognoza,
        "Kp" : Kp,
        "Ki" : Ki,
        "Kd" : Kd
        })
    
