
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

int zarowka = 11;
int wentylator = 10;
int pin_tem_gora = 13;
int pin_tem_dol = 12;
int zielona = A3;
int czerwony = A2;

DHT czujnik_tem_dol(pin_tem_dol, DHT11);
DHT czujnik_tem_gora(pin_tem_gora, DHT11);
LiquidCrystal_I2C lcd(0x3F, 16, 2);

int pwm_zadany = 0;
int wentylator_zadany = 0;

int pwm_aktualny = 0;
int wentylator_aktualny = 1;

float tem_gora = 0;
float tem_dol = 0;

bool pomiar_poprawny = false;
bool awaria = false;
int licznik_bledow = 0;

unsigned long poprzedni_pomiar = 0;
const unsigned long czas_pomiaru = 5000UL;

unsigned long ostatnia_komenda = 0;
const unsigned long limit_czasu = 10000UL;
bool pierwsza_komenda = false;

const float limit_temperatury = 35.0;

String bufor_komendy = "";
bool za_dluga_komenda = false;

void setup()
{
    Serial.begin(9600);

    pinMode(zarowka, OUTPUT);
    pinMode(wentylator, OUTPUT);
    pinMode(zielona, OUTPUT);
    pinMode(czerwony, OUTPUT);

    analogWrite(zarowka, 0);
    digitalWrite(wentylator, HIGH);

    digitalWrite(zielona, LOW);
    digitalWrite(czerwony, HIGH);

    czujnik_tem_dol.begin();
    czujnik_tem_gora.begin();

    lcd.init();
    lcd.backlight();

    bufor_komendy.reserve(12);
}

void przetworzKomende(const String &komenda)
{
    int pozycja = komenda.indexOf(',');

    if (pozycja <= 0 || komenda.indexOf(',', pozycja + 1) != -1)
    {
        return;
    }

    String pwm_tekst = komenda.substring(0, pozycja);
    String wentylator_tekst = komenda.substring(pozycja + 1);

    if (pwm_tekst.length() == 0 || pwm_tekst.length() > 3 ||
        wentylator_tekst.length() != 1)
    {
        return;
    }

    for (int i = 0; i < pwm_tekst.length(); i++)
    {
        if (!isDigit(pwm_tekst[i]))
        {
            return;
        }
    }

    for (int i = 0; i < wentylator_tekst.length(); i++)
    {
        if (!isDigit(wentylator_tekst[i]))
        {
            return;
        }
    }

    int nowe_pwm = pwm_tekst.toInt();
    int nowy_wentylator = wentylator_tekst.toInt();

    if (nowe_pwm >= 0 && nowe_pwm <= 255 &&
        (nowy_wentylator == 0 || nowy_wentylator == 1))
    {
        pwm_zadany = nowe_pwm;
        wentylator_zadany = nowy_wentylator;

        ostatnia_komenda = millis();
        pierwsza_komenda = true;
    }
}

void odbierzKomende()
{
    while (Serial.available() > 0)
    {
        char znak = Serial.read();

        if (znak == '\n')
        {
            if (!za_dluga_komenda)
            {
                przetworzKomende(bufor_komendy);
            }

            bufor_komendy = "";
            za_dluga_komenda = false;
        }
        else if (znak != '\r')
        {
            if (!za_dluga_komenda && bufor_komendy.length() < 8)
            {
                bufor_komendy += znak;
            }
            else
            {
                za_dluga_komenda = true;
                bufor_komendy = "";
            }
        }
    }
}

void odczytajCzujniki()
{
    tem_gora = czujnik_tem_gora.readTemperature();
    tem_dol = czujnik_tem_dol.readTemperature();

    if (isnan(tem_gora) || isnan(tem_dol))
    {
        pomiar_poprawny = false;
        licznik_bledow++;

        if (licznik_bledow >= 3)
        {
            awaria = true;
        }

        return;
    }

    pomiar_poprawny = true;
    licznik_bledow = 0;

    if (tem_gora >= limit_temperatury ||
        tem_dol >= limit_temperatury)
    {
        awaria = true;
    }
}

void zastosujSterowanie()
{
    bool komunikacja_ok = pierwsza_komenda &&
        (millis() - ostatnia_komenda < limit_czasu);

    if (awaria || !pomiar_poprawny || !komunikacja_ok)
    {
        pwm_aktualny = 0;
        wentylator_aktualny = 1;

        digitalWrite(zielona, LOW);
        digitalWrite(czerwony, HIGH);
    }
    else
    {
        pwm_aktualny = pwm_zadany;
        wentylator_aktualny = wentylator_zadany;

        digitalWrite(zielona, HIGH);
        digitalWrite(czerwony, LOW);
    }

    analogWrite(zarowka, pwm_aktualny);
    digitalWrite(wentylator, wentylator_aktualny);
}

void wyslijPomiar()
{
    if (!pomiar_poprawny)
    {
        Serial.println("ERR,CZUJNIK");
        return;
    }

    if (awaria)
    {
        Serial.println("ERR,AWARIA");
        return;
    }

    Serial.print(tem_dol);
    Serial.print(",");
    Serial.print(tem_gora);
    Serial.print(",");
    Serial.print(wentylator_aktualny);
    Serial.print(",");
    Serial.println(pwm_aktualny);
}

void wyswietlLCD()
{
    if (awaria)
    {
        lcd.setCursor(0, 0);
        lcd.print("AWARIA          ");
        lcd.setCursor(0, 1);
        lcd.print("RESET WYMAGANY ");
        return;
    }

    if (!pomiar_poprawny)
    {
        lcd.setCursor(0, 0);
        lcd.print("BLAD CZUJNIKA   ");
        lcd.setCursor(0, 1);
        lcd.print("GRZALKA OFF     ");
        return;
    }

    lcd.setCursor(0, 0);
    lcd.print("Gora: ");
    lcd.print(tem_gora, 1);
    lcd.print(" C    ");

    lcd.setCursor(0, 1);
    lcd.print("Dol: ");
    lcd.print(tem_dol, 1);
    lcd.print(" C    ");
}

void loop()
{
    odbierzKomende();

    bool nowy_pomiar = false;

    if (millis() - poprzedni_pomiar >= czas_pomiaru)
    {
        poprzedni_pomiar = millis();
        odczytajCzujniki();
        nowy_pomiar = true;
    }

    zastosujSterowanie();

    if (nowy_pomiar)
    {
        wyslijPomiar();
        wyswietlLCD();
    }
}
