import socket
import ssl
import threading
import os
import random
from pathlib import Path
import re
# semaphore=threading.Semaphore(1)

data_folder = ""
default_file = "DefaultconfigRU.txt"
FORMAT = "utf-8"
HEADERSIZE=10
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

def find_RU_version():
    filedata=""
    with open(default_file, 'rb') as fs:
        while True:
            data = fs.read(1024).decode(FORMAT)
            if not data:
                break
            filedata+=data
        fs.close()
    version=""
    start=0
    for ch in filedata:
        if ch=='{':
            start=1
        elif ch=='}':
            start=0
            break
        elif start==1:
            version+=ch
    return version
def send_file(message, client_socket):

    data_folder = retreive_folder_name()
    orginal_msg=message
    message="reply_"+message
    num = random.randint(1, number_of_files(os.path.join(data_folder, message)))
    
    filename=message + '_' + str(num) + '.txt'
    text_file=os.path.join(data_folder, message, filename)

    # print('Opening file ', text_file)
    full_msg=''
    with open(text_file, 'rb') as fs:
        # print("Sending file.")
        while True:
                data = fs.read(1024)
                if not data:
                    break
                data=data.decode(FORMAT)
                full_msg+=data
        fs.close()
    
    updatemsg=full_msg
    if orginal_msg=='SOFTWARE_INVENTORY':
        #find version tag and add current version of RU into it 
        start = "<version>"
        end = "</version>"

        arr1 = [i.start() for i in re.finditer(start, full_msg)] 
        arr2 = [i.start() for i in re.finditer(end, full_msg)] 
        
        latest_RU_version=find_RU_version()
        newadd="<version>" + latest_RU_version + "</version>"

        updatemsg=full_msg[0:arr1[0]] + newadd + full_msg[arr2[0]+10:]

    total_sent = 0
    data_length = len(updatemsg)
    # print("Sending file.")
    while total_sent < data_length:
        chunk = updatemsg[total_sent:total_sent + 1024]
        client_socket.sendall(chunk.encode())
        total_sent += len(chunk)
        
    # print("Sent.")

