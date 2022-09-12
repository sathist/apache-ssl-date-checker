#!/usr/bin/python
from pymongo import MongoClient
import subprocess as sp
import paramiko
import time
from datetime import datetime
import os

now = datetime.now()
start_time = now.strftime("%Y-%m-%d %H:%M:%S")
delay = 60
time_out = time.time() + delay

# Mongo DB Connection
try:
    # user = "username"
    # password = "Password"
    # db_connection = MongoClient("mongodb://{user}:{password}@{host}:{port}")
    db_connection = MongoClient('10.0.0.70', 27017)

except:
    print("Could not connect in to MongoDB")

# Database connection name and DB name
db_name = db_connection.sslfordomains 
collection = db_name.sslexpires
collection.drop() # Need to be change update query

# Insert last run date & time
runDate_collection = db_name.lastRunDates
runDate_collection.insert_one({"date" : start_time})

# Domain IP/URL in Array List
hostName = ["192.168.0.2", "192.168.0.3", "192.168.0.4"]

try:

    for IP in hostName:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #Login to the apache hosted server
        ssh.connect(IP, username="user", password="abcd", allow_agent=False)
        #Get Apache site enabled domain names
        stdin, stdout, stderr = ssh.exec_command("a2query -s | awk '{print $1}'")
        time.sleep(0.1)
        for domains in iter(stdout.readline, ""):
            #sslcheck = sp.getoutput("sslexp --output json --url " + domains )
            response = os.system("ping -c 2 " + domains)
            if response == 0:
                #sslcheck = sp.getoutput("ssl-cert-check -b -s " + domains) 
                sslcheck = sp.getoutput("ssl-cert-check -b -s " + domains)
                split_list = sslcheck.split()

                if split_list[1] == "Expiring":
                    domain_name = domains
                    domain_name_list = domain_name[:-1]
                    expire = split_list[5]
                    last_date_of_month = split_list[2]
                    last_date_of_day = split_list[3]
                    last_date_of_year = split_list[4]
                    last_date = last_date_of_day + " " + last_date_of_month + " " + last_date_of_year
                    ssl_data = {"domain" : domain_name_list, "expire" : int(expire), "last_date" : last_date  }
                    collection.insert_one(ssl_data)
                    print (ssl_data)

                elif split_list[1] == "Valid":
                    domain_name = domains
                    domain_name_list = domain_name[:-1]
                    expire = split_list[5]
                    last_date_of_month = split_list[2]
                    last_date_of_day = split_list[3]
                    last_date_of_year = split_list[4]
                    last_date = last_date_of_day + " " + last_date_of_month + " " + last_date_of_year
                    ssl_data = {"domain" : domain_name_list, "expire" : int(expire), "last_date" : last_date  }
                    collection.insert_one(ssl_data)

                else:
                    domain_name_list = split_list[0]
                    not_domain_name_list = domain_name_list[-4]
                    print (not_domain_name_list)
            else:
                print ('\x1b[1;31;40m' + "Unable to reach - " + domains + '\x1b[0m')
    ssh.close()

except paramiko.AuthenticationException:
       print("\n Incorrect username or password! \n")

except paramiko.ssh_exception.NoValidConnectionsError:
       print("\n Unable to login to your server! Kindly check server IP... n")
