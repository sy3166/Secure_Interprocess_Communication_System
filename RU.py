import socket
import ssl
import threading
import time

from sending_file_to_DU import *
from recieving_file_from_DU import *
from Check_Skipping import *
from ACK_Client import *
from Update_Software_RU import *
from Check_for_ssl import *
from Getting_all_commands import *

PendingVersion = ""
state = "NULL"
connected = True
Dict = dict({'HELLO': 'SOFTWARE_INVENTORY', 'SOFTWARE_INVENTORY': 'COMMUNICATION', 'COMMUNICATION': 'COMMUNICATION'})
commands=[]

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

def Do_Action(message,client_socket):
    version=receive_file(message,client_socket)
    semaphore.acquire()
    send_file(message, client_socket)
    semaphore.release()
    time.sleep(0.1)
    return version

def talk(client_socket):
    global state
    global connected
    state = 'HELLO'
  
    while connected:
        try:
            message = receivedata(client_socket)
            
            flag = To_skip(message, client_socket)
            
            semaphore.acquire()
            response = Ack_client(message, state, client_socket, flag)
            semaphore.release()
            time.sleep(0.1)
       
            if flag:
                continue

            elif message == "CLOSE" or response == 'Closing' or message == 'exit':
                state = 'NULL'
                connected = False
                break

            elif response == 'Error':
                continue

            elif response == 'RESETTING':
                state = 'HELLO'
                continue

            elif response == 'Changing_state':
                state = 'SOFTWARE_INVENTORY'
                continue
            
            incoming_version=Do_Action(message,client_socket)
            SOFTWARE_PRESENT=False
            
            if message == 'SOFTWARE_INVENTORY':
                CurrentVersion=find_RU_version()
                if incoming_version!=CurrentVersion:SOFTWARE_PRESENT=True

            if message == 'SOFTWARE_INVENTORY':
                if SOFTWARE_PRESENT:
                    state = 'SOFTWARE_DOWNLOAD'
                    PendingVersion = incoming_version
                else:
                    state = 'COMMUNICATION'
            elif message == 'SOFTWARE_DOWNLOAD':
                state = 'SOFTWARE_INSTALL'
            elif message == 'SOFTWARE_INSTALL':
                update_version(PendingVersion)
                state = 'COMMUNICATION'
            else:
                state = Dict[state]
           
        except Exception as e:
            print(f"Error: {e}")
            break

    client_socket.close()

def alarm(client_socket):
    global state
    global connected
    while connected:
        time.sleep(6)
        if state=='NULL' or state=='HELLO':continue
        try:
            semaphore.acquire()
            if connected:
                message="<message>Alarm</message>"     
                client_socket.sendall(message.encode())
            semaphore.release()
            time.sleep(1)
        except Exception as e:
            print(f'Error: {e}')

def RU_talk(client_socket):
    global state
    global connected
    global commands
    while connected:
        time.sleep(5)
        if len(commands)==0:continue
        message=commands.pop(0)
        if not message:continue
        try:
            semaphore.acquire()
            message="<message>" + message + "</message>"
            if connected:
                client_socket.sendall(message.encode())
            semaphore.release()
            time.sleep(1)
        except Exception as e:
            print(f'Error: {e}')

def accept_connections(server_socket):
    global connected
    global state
    global commands
    while True:
        connected = True
        state = "NULL"
        commands = retrieve_all_commands("RU_talk.txt")
        print('Waiting for client')
        client_socket, addr = server_socket.accept()
        print(f"New connection from: {addr}")
        try:
            flag = is_ssl(1)
            if flag == '1':
                client_socket = ssl_context.wrap_socket(client_socket, server_side=True)
                
            t1 = threading.Thread(target=alarm, args=(client_socket,))
            t2 = threading.Thread(target=talk, args=(client_socket,))
            t3=  threading.Thread(target=RU_talk, args=(client_socket,))

            t1.start()
            t2.start()
            t3.start()
# 
            t1.join()
            t2.join()
            t3.join()

        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            client_socket.close()

def main():
    global ssl_context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="certificate.crt", keyfile="private.key")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print('Server listening on port 9999')

    accept_connections(server)

if __name__ == "__main__":
    main()