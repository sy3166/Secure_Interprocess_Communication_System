import threading
import re
# semaphore=threading.Semaphore(1)

FORMAT='utf-8'

def data_recovery(full_msg):
    response=''
    start=True
    for ch in full_msg:
       if ch=='>':start=False
       elif ch=='<' and start==False:break
       elif start==False: response+=ch
    
    return response

def receivedata_rpc(client_socket):
    full_msg=''
    while True:
        data=client_socket.recv(1).decode(FORMAT)
        if not data:break
        full_msg+=data
        if full_msg[-6:]=='</rpc>' or full_msg[-8:]=='</hello>':break
    
    start = "<message>"
    end = "</message>"

    arr1 = [i.start() for i in re.finditer(start, full_msg)] 
    arr2 = [i.start() for i in re.finditer(end, full_msg)] 

    n=len(arr1)
    for i in range(n):
        print("This is Message from DU : " + data_recovery(full_msg[arr1[i]:arr2[i]+10]))   
    
    filedata=full_msg
    if n>0: 
        filedata=full_msg[:arr1[0]]
        for i in range(n):
            if(i<n-1):
                filedata+=full_msg[arr2[i]+10:arr1[i+1]]
            else :
                filedata+=full_msg[arr2[i]+10:]

    return filedata

   
def receive_file(message,client_socket):
    text_file = 'DU_reply.txt'
    filedata=""
    with open(text_file, "a") as fw:
        # print("Receiving..")
        filedata = receivedata_rpc(client_socket)
        # print("received data :" + filedata)
        fw.write(filedata + '\n')
        fw.close()
        # print("final Received..")
        
    if message=='SOFTWARE_INVENTORY':
        start = "<version>"
        end = "</version>"
        arr1 = [i.start() for i in re.finditer(start, filedata)] 
        arr2 = [i.start() for i in re.finditer(end, filedata)] 

        full_msg=filedata[arr1[0]:arr2[0]+10]
        response=''
        start=True
        for ch in full_msg:
            if ch=='>':start=False
            elif ch=='<' and start==False:break
            elif start==False: response+=ch
        return response
    else:return None