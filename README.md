[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
![GitHub](https://img.shields.io/github/license/ratibor78/cloudgate)
![GitHub contributors](https://img.shields.io/github/contributors/ratibor78/cloudgate)
![GitHub repo size](https://img.shields.io/github/repo-size/ratibor78/cloudgate)


# Cloudgate
### A program that allows you to administer OpenVPN clients from the AWS IAM console. 
#### Version 0.1

> The main idea of this program is to allow you to administer the OpenVPN clients from your AWS IAM console.

### Description

If you have your own EC2 instance with the OpenVPN server in AWS VPC for providing VPN access, this program will give you a more comfortable
way of administrating the VPN users than using an ssh console every time when you need to create or revoke a new VPN user.

Instead of this you can use your IAM console as the UI and single source of truth for the internal OpenVPN server.
Just create an IAM group with the name 'vpnallow' or with any other name you like, and then put the users that need VPN access into this group.
**Cloudgate** will create the OpenVPN configs for these users automatically and put them into the program folder on the server or load these configs
to your AWS S3 bucket. Also after you remove the user from this IAM group the OpenVPN client config will be revoked from the VPN server automatically.

> That's the main goal, to provide a single source of truth for administration VPN users in your AWS organization, so you will never forget to revoke the VPN access after deleting this user from your IAM service.

### Dependencies

1) EC2 instance in public subnet your VPC with Linux
2) OpenVPN server installed on the EC2 with [openvpn-install.sh ](https://github.com/Nyr/openvpn-install) script
3) Python3 and python3-venv packages installed

### Important
**Cloudgate** was created for using with OpenVPN server installed by **openvpn-install.sh** script from **Nyr/openvpn-install** repo, so some system path was hardcoded into the code, please mind this if you will use this program with the manually installed version of OpenVPN or installed with another version of **openvpn-install.sh** script. Maybe you'll need to change some paths inside **cloudgate.py** file. 

### Installation

1) Make sure the OpenVPN server was installed and working
2) Clone the **cloudgate** repo 
3) CD into the repo directory and then run **install.sh**
4) After the **install.sh** script will finish the installationion you will need start the service with **'systemctl start cloudgate.service'** command

Or you can install Cloudgate manually:

1) Clone the repository, create an environment and install requirements
```sh
$ cd cloudgate
$ python3 -m venv venv && source venv/bin/activate
$ pip3 install -r requirements.txt
```
2) Modify **settings.ini** file and copy service to systemd
```sh
$ cp settings.ini.bak settings.ini
$ vi settings.ini
$ vi cloudgate.service.template
$ cp cloudgate.service.template /lib/systemd/system/cloudgate.service
$ systemctl daemon-reload
$ systemctl enable cloudgate.service
$ systemctl start cloudgate.service
```
After installation go into the AWS IAM console and create the VPN allowed group for VPN users, the name of the group must be the same one that you setup in **settings.ini** file in **AWS_VPN_ALLOW_GROUP** section. 
Also create the new user with name **vpnadmin** or any you like and set the policy **IAMReadOnlyAccess** and S3 read/write inline policy for this user. Copy the Access Kye ID and Secter Access KEY from this **vpnadmin** user and put into **settings.ini** file. 

### Usage

Login into AWS IAM console and place any user into the VPN allowed group, wait for the time that was configured as the **REQUEST_INTERVAL**. After this you will find the new VPN client (username.ovpn) config file in **./client_configs** folder. Also, the new user will be added to the OpenVPN clients. If you have setup the S3 bucket name in the settings, the client config will be also placed there, so you can easily get it, without scp or ssh access to the OpenVPN server.

Remove the user from the VPN allowed group and after the **REQUEST_INTERVAL** the user will be revoked from the OpenVPN server and (username.ovpn) config will be deleted from **./client_configs** folder and S3 bucket. 

#### That's all, I hope you'll find this program useful. If you have any wishes you are welcome to contact me in any way you want. 

### Thanks
Special thanks to [Nyr](https://github.com/Nyr) for his [openvpn-install.sh](https://github.com/Nyr/openvpn-install)

### Licence

This project is under the [MIT Licence](https://raw.githubusercontent.com/Angristan/openvpn-install/master/LICENSE)

**[??? back to top](#Cloudgate)**
