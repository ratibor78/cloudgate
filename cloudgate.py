#####################################################################################
### Python program for administering OpenVPN users from the AWS IAM service.      ###
### Putting the IAM user into the specific group will automatically create        ###
### the OpenVPN client config file with the same name on the OpenVPN server side. ###
### This VPN client config will be active while the user is a member of that      ###
### specific group and will be paused once the user has left that IAM group       ###
### or will be completely removed if the user was deleted from the IAM service.   ###
###                                                                               ###
###       Created by Oleksii Nizhegolenko ratibor78@gmail.com (c) 2022            ###
#####################################################################################

import os
import sys
import time
import boto3
import logging
import botocore
import configparser
import logging.handlers
from os import environ as env


# Class formating log messages
class SyslogBOMFormatter(logging.Formatter):
    def format(self, record):
        result = super().format(record)
        return "ufeff" + result


# Logging handlers configuration
handler = logging.handlers.SysLogHandler('/dev/log')
formatter = SyslogBOMFormatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


# Loading variables from settings.ini file
PWD = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
CONFIG = configparser.ConfigParser()
CONFIG.read(f'{PWD}/settings.ini')
AWS_ACCESS_KEY_ID = CONFIG.get('AWS_ACCESS_KEY_ID', 'aws_access_key_id')
AWS_SECRET_ACCESS_KEY = CONFIG.get('AWS_SECRET_ACCESS_KEY', 'aws_secret_access_key')
AWS_VPN_ALLOW_GROUP = CONFIG.get('AWS_VPN_ALLOW_GROUP', 'vpn_allow_group')
REQUEST_INTERVAL = CONFIG.get('REQUEST_INTERVAL', 'request_interval')
S3_BUCKET_NAME = CONFIG.get('S3_BUCKET', 's3_bucket_name')

# Creating a connection to the AWS IAM service with boto3
client = boto3.client(
  'iam',
  aws_access_key_id=AWS_ACCESS_KEY_ID,
  aws_secret_access_key=AWS_SECRET_ACCESS_KEY
  )


# Creating a connection to the AWS S3 service with boto3
client_s3 = boto3.client(
  's3',
  aws_access_key_id=AWS_ACCESS_KEY_ID,
  aws_secret_access_key=AWS_SECRET_ACCESS_KEY
  )


# Getting the list of users that belong to specific AWS IAM group
# and comparing them with existing OpenVPN users.
def aws_iam_users(aws_vpn_allow_group, type):
    try:
        iam_users = [user['UserName'] for user in client.get_group(GroupName=aws_vpn_allow_group)['Users']]
    except botocore.exceptions.ClientError as client_error:
        logging.exception(client_error.response)
    try:
        with open('/etc/openvpn/server/easy-rsa/pki/index.txt', 'r') as file:
            vpn_users = [line.strip('\n').split()[4].split('=')[1] for line in file if 'V' in line and '/CN=server' not in line]
    except IOError as io_error:
        logging.exception(io_error)
    if type == 'create':
        result = list(set(iam_users).difference(set(vpn_users)))
    if type == 'revoke':
        result = list(set(vpn_users).difference(set(iam_users)))
    return result


# Main program body, creating or revoking the OpenVPN users configs
def main():
    while True:
        # Checking if there any new users were added to the VPN allow group,
        # so they need to be created in the OpenVPN server also
        users_create = aws_iam_users(AWS_VPN_ALLOW_GROUP, 'create')
        if users_create:
            for user in users_create:
                cmd = f'cd /etc/openvpn/server/easy-rsa/ && ./easyrsa --batch --days=3650 build-client-full "{user}" nopass > /dev/null 2>&1'
                os.system(cmd)
                with open(f'./client_configs/{user}.ovpn', 'a+') as config:
                    with open('/etc/openvpn/server/client-common.txt','r') as client_common:
                        for line in client_common:
                            config.write(line)
                    config.write('<ca>')
                    config.write('\n')
                    with open('/etc/openvpn/server/easy-rsa/pki/ca.crt', 'r') as ca_cert:
                        for line in ca_cert:
                            config.write(line)
                    config.write('</ca>')
                    config.write('\n')
                    config.write('<cert>')
                    config.write('\n')
                    with open(f'/etc/openvpn/server/easy-rsa/pki/issued/{user}.crt', 'r') as user_cert:
                        lines = user_cert.readlines()
                        for line_number, line in enumerate(lines, 1):
                            if 'BEGIN CERTIFICATE' in line:
                                strat_index = line_number - 1
                    with open(f'/etc/openvpn/server/easy-rsa/pki/issued/{user}.crt', 'r') as user_cert:
                        certificate = user_cert.readlines()[strat_index:]
                    for cert_line in certificate:
                        config.write(cert_line)
                    config.write('</cert>')
                    config.write('\n')
                    config.write('<key>')
                    config.write('\n')
                    with open(f'/etc/openvpn/server/easy-rsa/pki/private/{user}.key', 'r') as user_key:
                        for key_line in user_key:
                            config.write(key_line)
                    config.write('</key>')
                    config.write('\n')
                    config.write('<tls-crypt>')
                    config.write('\n')
                    with open('/etc/openvpn/server/tc.key', 'r') as tc_key:
                        tc_lines = tc_key.readlines()
                        for line_number, line in enumerate(tc_lines, 1):
                            if 'BEGIN OpenVPN Static key' in line:
                                strat_index = line_number -1
                    with open('/etc/openvpn/server/tc.key', 'r') as tc_key:
                        key = tc_key.readlines()[strat_index:]
                    for key_line in key:
                        config.write(key_line)
                    config.write('</tls-crypt>')
                    config.write('\n')
                if S3_BUCKET_NAME:
                    with open(f'./client_configs/{user}.ovpn', 'rb') as vpn_config:
                        try:
                            client_s3.upload_fileobj(vpn_config, f'{S3_BUCKET_NAME}', f'{user}.ovpn')
                        except botocore.exceptions.ClientError as client_error:
                            logging.exception(client_error.response)
        # Checking if any users were removed from the VPN allow group,
        # and they need to be revoked from the OpenVPN config also
        users_delete = aws_iam_users(AWS_VPN_ALLOW_GROUP, 'revoke')
        if users_delete:
            for user in users_delete:
                cmd1 = f'cd /etc/openvpn/server/easy-rsa/ && ./easyrsa --batch revoke "{user}" > /dev/null 2>&1 && ./easyrsa --batch --days=3650 gen-crl > /dev/null 2>&1'
                cmd2 = 'rm -f /etc/openvpn/server/crl.pem > /dev/null 2>&1 && cp /etc/openvpn/server/easy-rsa/pki/crl.pem /etc/openvpn/server/crl.pem > /dev/null 2>&1'
                cmd3 = 'chown nobody:"$group_name" /etc/openvpn/server/crl.pem > /dev/null 2>&1'
                os.system(cmd1)
                os.system(cmd2)
                os.system(cmd3)
                if os.path.exists(f'./client_configs/{user}.ovpn'):
                    os.remove(f'./client_configs/{user}.ovpn')
                if S3_BUCKET_NAME:
                    try:
                        client_s3.delete_object(Bucket=f'{S3_BUCKET_NAME}', Key=f'{user}.ovpn')
                    except botocore.exceptions.ClientError as client_error:
                        logging.exception(client_error.response)
        time.sleep(int(REQUEST_INTERVAL))


# Finally run this all :)
if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Exception in main()")
        sys.exit(1)
