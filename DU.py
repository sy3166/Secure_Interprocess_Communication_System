import socket
import ssl
import threading
import time

# Placeholder imports for your specific functions
from sending_file_to_RU import *
from recieving_file_from_RU import *
from Check_for_ssl import *
from Getting_all_commands import *

connected = True
commands = []


state = "NULL"
isexit = False

# Initialize the semaphore
semaphore = threading.Semaphore(1)

FORMAT='utf-8'
def receivedata(client_socket):
    full_msg=''
    while True:
        data=client_socket.recv(1).decode(FORMAT)
        if not data:break
        full_msg+=data
        if(full_msg[-10:]=='</message>'):break

    response=''
    start=True
    for ch in full_msg:
       if ch=='>':start=False
       elif ch=='<' and start==False:break
       elif start==False: response+=ch
    
    return response

def DO_ACTION(message, client_socket):
    semaphore.acquire()
    send_file(message, client_socket)
    semaphore.release()
    time.sleep(0.1)
    response=receive_file(message,client_socket)
    return response
def check(response):
    ans=True
    if response=='Skipped' or response == 'RESETTING' or response == 'Closing' or response == 'Error' or response=='NOERROR':ans =False
    return ans

def talk(client_socket):
    global connected
    global isexit
    while connected :
        try:
            semaphore.acquire()
            
            message = ''
            if not connected: 
                break

            if len(commands) == 0:
                message = input(f"Enter message for RU (or 'CLOSE' to quit): ")
            else:
                message = commands.pop(0)

            if not message:
                continue
            
            if not connected: 
                break
            
            msg='<message>' + message + '</message>'
           
            client_socket.sendall(msg.encode())
            
            semaphore.release()
            time.sleep(0.1)
 
            response = receivedata(client_socket)

            while check(response):
                print("This is Message from RU : " + response)
                response=receivedata(client_socket)

            if response == 'Skipped':
                print('Skipped by RU')
                continue

            elif response == 'RESETTING':
                state='HELLO'
                continue

            elif message == 'CLOSE' or response == 'Closing' or message == 'exit':
                connected = False
                if message == 'exit':
                    isexit = True
                break

            elif response == 'Error':
                print('Error in commands...skipping')
                continue

            elif response == 'Changing_state':
                state='SOFTWARE_INVENTORY'
                continue

            if not connected: 
                break

            if message == 'HELLO':
                RU_version=DO_ACTION(message, client_socket)
                state = 'SOFTWARE_INVENTORY'
                
            elif state == 'SOFTWARE_INVENTORY' and message == "SOFTWARE_INVENTORY":
                RU_version=DO_ACTION(message, client_socket)
                DU_version=find_DU_version()
                
                if RU_version!=DU_version:
                    state = 'SOFTWARE_DOWNLOAD'
                else:
                    state = 'COMMUNICATION'
            
            elif state == 'SOFTWARE_DOWNLOAD' and message == "SOFTWARE_DOWNLOAD":
                RU_version=DO_ACTION(message, client_socket)
                state = 'SOFTWARE_INSTALL'
            
            elif state == 'SOFTWARE_INSTALL' and message == "SOFTWARE_INSTALL":
                RU_version=DO_ACTION(message, client_socket)
                state = 'COMMUNICATION'
            
            elif state == 'COMMUNICATION':
                DO_ACTION(message, client_socket)
        
        except Exception as e:
            print(f"Error..: {e}")
            connected = False
            break

def DU_talk():
    global commands
    global connected
    while connected and len(commands)>0:
        msg=input("Enter User Inputs ")
        if not msg:continue
        try:
            semaphore.acquire()
            commands.insert(0,msg)
            semaphore.release()
            time.sleep(1)
        except Exception as e:
            print('Failed to acquire results no user talk')

def main():
    global ssl_context
    global commands
    global connected
    global state
    global isexit
    
    isexit = False
    while not isexit:
        commands = retrieve_all_commands("commands.txt")
        connected = True
        state = "NULL"
        flag = is_ssl(0)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if flag == '1':
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_verify_locations('certificate.crt')
            client = ssl_context.wrap_socket(client, server_hostname='localhost')

        client.connect(('127.0.0.1', 9999))

        
        t1 = threading.Thread(target=talk, args=(client,))
        t2 = threading.Thread(target=DU_talk, args=())
        

        # t1.start()
        t1.start()
        t2.start()
        
        
        # t1.join()
        t1.join()
        t2.join()
      
        print("**CLOSED***")
        client.close()

if __name__ == "__main__":
    main()
