echo " "
echo "Installing Ngrok"
echo "---------------------------"

cd /home/pi
if [ -e /home/pi/ngrok_linux.zip ]
then
    rm /home/pi/ngrok_linux.zip
fi
wget -O ngrok_linux.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
if [ -e /home/pi/ngrok ]
then
    rm /home/pi/ngrok
fi
unzip ngrok_linux.zip
sudo rm ngrok_linux.zip
sudo chmod 777 /home/pi/ngrok

echo "Ngrok Download Completed"
if [ -e /home/pi/.ngrok2/ngrok.yml ]
then
    sudo rm /home/pi/.ngrok2/ngrok.yml
fi
sudo -u pi ./ngrok authtoken xxxxxxx
sudo -u pi cat >/home/pi/.ngrok2/ngrok.yml<<EOL
authtoken: xxxxxx

tunnels:
  ssh:
    proto: tcp
    addr: 22
  dashboard:
    proto: http
    addr: 8080
  vnc:
    proto: tcp
    addr: 5900
EOL
echo "Ngrok Configuration File Created"

if [ -e /etc/systemd/system/ngrok-client.service ]
then
    sudo rm /etc/systemd/system/ngrok-client.service
fi
sudo -u pi cat >/etc/systemd/system/ngrok-client.service<<EOL
[Unit]
Description=ngrok-client
After=multi-user.target

[Service]
Type=idle
ExecStart=/home/pi/ngrok start --all -config /home/pi/.ngrok2/ngrok.yml
ExecStartPost=/usr/bin/python3 /home/pi/4process-acquisition/send_ngrok_email.py
WorkingDirectory=/home/pi
Restart=always
RestartSec=20
StandardOutput=syslog
StandardError=syslog
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/home/pi/4process-acquisition/4process.env

[Install]
WantedBy=multi-user.target
EOL
echo " "
echo "Ngrok Service Created"

sudo systemctl daemon-reload
sudo systemctl enable ngrok-client
echo " "
echo "Ngrok Instalattion Completed"
echo "---------------------------"