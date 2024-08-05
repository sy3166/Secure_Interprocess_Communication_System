import os
import random


data_folder = ""
default_file = "DefaultconfigRU.txt"
FORMAT = "utf-8"

def number_of_files(dir_path):
    return len([entry for entry in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, entry))])

def retreive_folder_name():
    filedata = ""
    with open(default_file, 'r') as fs:
        while True:
            data = fs.read(1024)
            if not data:
                break
            filedata += data
        fs.close()
    items = filedata.split('[')
    return items[0]

def update(filedata,version):
    newdata=""
    for ch in filedata:
        if(ch=='{'):break
        else :newdata+=ch
    
    newdata=newdata+'{'+version+'}'
    return newdata
     

def update_version(newversion):
    filedata=""
    with open(default_file, 'rb') as fs:
        while True:
            data = fs.read(1024).decode(FORMAT)
            if not data:
                break
            filedata+=data
        fs.close()

    update_filedata=update(filedata,newversion)
    f = open(default_file, "w")
    f.write(update_filedata)
    f.close()
