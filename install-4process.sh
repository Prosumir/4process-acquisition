sudo apt-get update -y
sudo apt-get full-upgrade -y

echo " "
echo "Installing Python 3 and pip3"
echo "---------------------------"
sudo apt-get install python3-dev -y
sudo apt install python3-pip -y

echo " "
echo "Installing libraries dependencies"
echo "---------------------------"
sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test -y
sudo apt-get install -y python3-opencv

echo " "
echo "Installing Python libraries"
echo "---------------------------"
sudo -u pi pip3 install numpy -U
sudo pip3 install opencv-python
sudo -u pi pip3 -U requests
sudo -u pi pip3 --force-reinstall -U requests
sudo -u pi pip3 install datetime
#sudo -u pi pip3 install opencv-contrib-python
sudo -u pi pip3 install boto3
sudo -u pi pip3 install pika

echo " "
echo "Cleanning Installation"
echo "---------------------------"
sudo apt autoremove -y

echo " "
echo "Creating 4Process Services"
echo "---------------------------"

sudo rm /etc/systemd/systemd/4process*

echo "Acquisition Service"
sudo -u pi cat >/etc/systemd/system/4process-acquisition.service<<EOL
[Unit]
Description= servico de aquisicao de dados dos sensores
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/pi/4process-acquisition/main_4process.py
WorkingDirectory=/home/pi/4process-acquisition
User=pi
Restart=always
RestartSec=20
StartLimitInterval=0
StandardOutput=syslog
StandardError=syslog
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/home/pi/4process-acquisition/4process.env

[Install]
WantedBy=multi-user.target
EOL

echo "Client Service"
sudo -u pi cat >/etc/systemd/system/4process-client.service<<EOL
[Unit]
Description= servico de envio dos dados adquiridos para o servidor
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/pi/4process-acquisition/client_4process.py
WorkingDirectory=/home/pi/4process-acquisition
User=pi
Restart=always
RestartSec=60
StartLimitInterval=0
StandardOutput=syslog
StandardError=syslog
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/home/pi/4process-acquisition/4process.env

[Install]
WantedBy=multi-user.target
EOL

sudo chmod 644 /etc/systemd/system/4process-acquisition.service
sudo chmod 644 /etc/systemd/system/4process-client.service

echo " "
echo "Configuring Journal"
echo "---------------------------"

sudo mkdir -p /var/log/journal
sudo echo "Storage=auto" >> /etc/systemd/journald.conf
sudo echo "SystemKeepFree=2G" >> /etc/systemd/journald.conf
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald

sudo journalctl --vacuum-time "1 month"

sudo systemctl daemon-reload
sudo systemctl enable 4process-client
sudo systemctl enable 4process-acquisition
echo "End of installation process"
