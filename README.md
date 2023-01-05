[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
![GitHub](https://img.shields.io/github/license/ratibor78/cloudgate)
![GitHub contributors](https://img.shields.io/github/contributors/ratibor78/cloudgate)
![GitHub repo size](https://img.shields.io/github/repo-size/ratibor78/cloudgate)
![GitHub Repo stars](https://img.shields.io/github/stars/ratibor78/cloudgate?style=social)

# Cloudgate
### A program that allows you to administer OpenVPN clients from the AWS IAM console. 
#### Version 0.1

> The main idea of this program is to allow you to administer the OpenVPN clients from your AWS IAM console.

## Description

If you have your own EC2 instance with the OpenVPN server in AWS VPC for providing VPN access, this program will give you a more comfortable
way of administrating the VPN users than using an ssh console every time you need to create or revoke a new VPN user.

Instead this you can use your IAM console as the UI for the internal OpenVPN server, just create an IAM group with the name 'vpnallow' or
with any other name, you prefer, and then put the users that need VPN access into this group.

The Cloudgate script will create the OpenVPN configs for these users automatically and put them into the program folder or load these configs
to your AWS S3 bucket. Also after you remove the user from this IAM group the OpenVPN client config will be revoked from the VPN server automatically.

That's the main goal, to provide a single source of truth for administration VPN users, so you will never forget to revoke the VPN access after deleting this user from your IAM service.
