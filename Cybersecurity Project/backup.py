from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import shutil
import os
import re
from datetime import datetime

gauth = GoogleAuth()   
gauth.LocalWebserverAuth()        
drive = GoogleDrive(gauth)

while True:
    print("Backup Menu")
    print("1. Backup Wazuh Server Files")
    print("2. Recover Wazuh Server Files from Google Drive")
    print("3. Recover Wazuh Server Files from local archive")
    print("9. Exit")
    option = input("Option: ")

    if option == "1":
        dt_string = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        wazuh_dir = "/var/ossec"
        print("Backing up files")
        backup_zip = shutil.make_archive(f"Wazuh Backup {dt_string}", 'zip', wazuh_dir)
        if os.path.exists("/var/backups/Wazuh"):
            shutil.move(backup_zip,f"/var/backups/Wazuh/Wazuh Backup {dt_string}")
            print("Backup created in /var/backups/Wazuh")
        else:
            print("Creating directory Wazuh in /var/backups")
            os.mkdir("/var/backups/Wazuh")
            shutil.move(backup_zip,f"/var/backups/Wazuh/Wazuh Backup {dt_string}")
            print("Backup created in /var/backups/Wazuh")
        upload_file_list = [f"/var/backups/Wazuh/Wazuh Backup {dt_string}"]
        for upload_file in upload_file_list:
            gfile = drive.CreateFile({'parents': [{'id': '1Pmq17UjV7rgmYMnuu4h1_YaJQKAP6Wc3'}]})
            # Read file and set it as the content of this instance.
            gfile.SetContentFile(upload_file)
            gfile['title'] = f"Wazuh Backup {dt_string}"
            gfile.Upload() # Upload the file.
        print("Backup uploaded to Google Drive")

    elif option == "2":
        file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format('1Pmq17UjV7rgmYMnuu4h1_YaJQKAP6Wc3')}).GetList()
        choosefilelist = []
        index = 1
        while True:
            print("Backup files found:")
            for file1 in file_list:
                choosefilelist.append(file1['id'])
                print(f"{index}. Title: {file1['title']}, {file1['id']}")
                index += 1
            try:
                backupfile = int(input("Choose Backup File: "))
                if backupfile > len(choosefilelist):
                    print("Please select a valid file")
                else:
                    break
            except:
                print("Please select a valid file")
            index = 1
            choosefilelist = []
        
        try: 
            downloadfile = drive.CreateFile({'id': choosefilelist[backupfile-1]})
        except: 
                print("File not found in Google Drive")
        try:
            downloadfile.GetContentFile(downloadfile['title'])
        except:
            print("Error occurred while downloading archive")

        archive = f"{os.getcwd()}/{downloadfile['title']}"
        print("Downloaded archive")
        print("Stopping Wazuh services")
        try:
            os.system(f'/var/ossec/bin/wazuh-control stop')
        except:
            print("Unable to stop Wazuh services")

        print("Unpacking archive")
        try:
            shutil.unpack_archive(archive, '/var/ossec', "zip")
            print("Archive unpacked, files restored")
        
            try:
                print("Starting Wazuh services")
                os.system(f'/var/ossec/bin/wazuh-control start')
                print("Wazuh Services started")
            except:
                print("Unable to start Wazuh services, please start manually")
        except:
            print("Error occurred while unpacking archive, please ensure Wazuh services was stopped")
    
    elif option == "3":
        while True:
            archives = os.listdir("/var/backups/Wazuh")
            backuparchives = []
            archiveindex = 1
            for archive in archives:
                print(f"{archiveindex}. {archive}")
                backuparchives.append(archive)
                archiveindex +=1 
        
            try:
                selectarchive = int(input("Choose Backup File: "))
            except:
                print("Please select a valid file")
            if selectarchive > len(backuparchives):
                print("Please select a valid file")
            else:
                break
            archiveindex = 1
            backuparchives = []

        print("Stopping Wazuh services")
        try:
            os.system(f'/var/ossec/bin/wazuh-control stop')
        except:
            print("Unable to stop Wazuh services")

        print("Unpacking archive")
        try:
            shutil.unpack_archive(f"/var/backups/Wazuh/{backuparchives[selectarchive-1]}", '/var/ossec', "zip")
            print("Archive unpacked, files restored")
        except:
            print("Error occurred while unpacking archive")
        try:
            print("Starting Wazuh services")
            os.system(f'/var/ossec/bin/wazuh-control start')
            print("Wazuh Services started")
        except:
            print("Unable to start Wazuh services, please start manually")
        
        
    elif option == "9":
        break

    else: 
        continue