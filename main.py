import requests
from datetime import datetime
import smtplib
import time
import os

MY_LAT = os.environ["MY_LAT"]  # Your latitude
MY_LONG = os.environ["MY_LONG"] # Your longitude


def iss_above():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    if MY_LAT + 5 > iss_latitude > MY_LAT - 5 and MY_LONG + 5 > iss_longitude > MY_LONG - 5:
        return True


# Your position is within +5 or -5 degrees of the ISS position.

def is_night():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now = datetime.now().hour
    if 24 > time_now > sunset or 00 < time_now < sunrise:
        return True


while True:
    time.sleep(60)
    if is_night() and iss_above():
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=os.environ["user"], password=os.environ["password"])
            connection.sendmail(from_addr=os.environ["user"],
                                to_addrs=os.environ["receiver"],
                                msg=f"Subject: ISS ALERT!\n\nISS is currently flying above you!")
