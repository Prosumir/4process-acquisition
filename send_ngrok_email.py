import requests
import json
import smtplib, ssl
import os

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

ok = False
while not ok:
    try:
        print("Try")
        page = requests.get("http://localhost:4040/api/tunnels", verify=False, timeout=10)
    except:
        print("Request Failure")
        ok=False
    else:
        print("Request OK\n")
        json = page.json()
        tunnels = json["tunnels"]
        names = []
        for tunnel in tunnels:
                names.append(tunnel["name"])
        if bool(tunnels) and ("ssh" in names) and ("vnc" in names):
            buffer = "Subject: Home NGROK\n\n"
            ok = True
            for tunnel in tunnels:
                buffer += tunnel["name"] + "-"
                buffer += tunnel["public_url"] + "\n"
        else:
            ok=False
            print("No Tunnels")

port = 587  # For starttls
smtp_server = "smtp.gmail.com"

print("Sending Email:\n\tFrom: " + SENDER_EMAIL + "\n\tTo: " + RECEIVER_EMAIL)
print(buffer)
context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(SENDER_EMAIL, EMAIL_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, buffer)
