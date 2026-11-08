import pandas as pd
import time
import serial
import joblib

model = joblib.load("model_lr_60s_final.joblib")

temp_zadana = float(input("Podaj temperature zadaną [C]: "))

print("Model zostal zaladowany!")

arduino = serial.Serial("/dev/ttyUSB0", 9600, timeout=2)

poprzednia_gora = None
poprzednia_dol = None
start = None
Kp = 50
Ki = 10

suma_uchybu = 0.0
poprzedni_czas_min = None

parametry = []

while True:
    dane = arduino.readline().decode("utf-8").strip()

    wartosci = dane.split(',')

    if len(wartosci) != 4:
        continue

    try:
        temp_dol = float(wartosci[0])
        temp_gora = float(wartosci[1])
        pwm = int(wartosci[3])
        wentylator = int(wartosci[2])
    except ValueError:
        continue

    temp_srednia = (temp_dol + temp_gora) /2

    roznica_temp = abs(temp_dol - temp_gora)

    if start is None:
        start = time.monotonic()

    czas_start_min = (time.monotonic() - start) /60    

    if poprzednia_dol is None or poprzednia_gora is None: 
        poprzednia_gora = temp_gora
        poprzednia_dol = temp_dol
        continue

    roznica_temp_diff_gora = temp_gora - poprzednia_gora
    roznica_temp_diff_dol = temp_dol - poprzednia_dol

    poprzednia_gora = temp_gora
    poprzednia_dol = temp_dol


    print("Temperatura aktualna: ", temp_srednia)
    print("Czas od rozpoczenia [min]: ", czas_start_min)


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

    blad_ml = temp_zadana - prognoza
    print("Temperatura za 60s: ", prognoza)
    print("Blad: ", blad_ml)

    P = Kp * blad_ml

    blad = temp_zadana - temp_srednia

    if poprzedni_czas_min is None:
        roznica_czasu = 0.0
    else:
        roznica_czasu = czas_start_min - poprzedni_czas_min

    suma_test = suma_uchybu + blad * roznica_czasu
    poprzedni_czas_min = czas_start_min

    I_test = Ki * suma_test

    pwm_test = P + I_test

    if 0 <= pwm_test <= 255:
        suma_uchybu = suma_test
    elif pwm_test > 255 and blad < 0:
        suma_uchybu = suma_test
    elif pwm_test < 0 and blad > 0:
        suma_uchybu = suma_test

    I = Ki * suma_uchybu

    pwm_nadany = P + I

    pwm_nadany = int(pwm_nadany)  

    if pwm_nadany >= 255:
        pwm_nadany = 255

    if pwm_nadany <= 0:
        pwm_nadany = 0

    temp_progowa = temp_zadana * 1.05

    if temp_srednia >= temp_progowa:
        wentylator = 1
    else:
        wentylator = 0

    komenda = f"{pwm_nadany},{wentylator}\n"
    arduino.write(komenda.encode('utf-8'))

    print("Wartosc czlonu P: ", P)
    print("Wartosc czlonu I: ", I)
    print("Wartosc PWM: ", pwm_nadany)
    print("--------------------------------")
    print()

    parametry.append({
        "czas_min" : czas_start_min,
        "temp_zadana" : temp_zadana,
        "temp_dol" : temp_dol,
        "temp_gora" : temp_gora,
        "temp_srednia" : temp_srednia,
        "blad" : blad,
        "blad_ml" : blad_ml,
        "P" : P,
        "I" : I,
        "D" : None,
        "pwm_nadany" : pwm_nadany,
        "wentylator" : wentylator,
        "prognoza_ml" : prognoza,
        "Kp" : Kp,
        "Ki" : Ki
    })



    


