def Ack_client(message,state,client_socket,flag):
    response="NOERROR"
    if not (message=='HELLO' or message=='SOFTWARE_INVENTORY' or message=='SOFTWARE_DOWNLOAD' or message=='CLOSE' or message=='exit' or message == 'SOFTWARE_INSTALL' or message=='get-config' or message=='edit-config' or message=='create-subscription') :response='Error'
    elif flag:response="Skipped"
    
    elif message=='CLOSE':response='Closing'
    elif message=='HELLO' and state!='HELLO':response='RESETTING'
    elif state!='COMMUNICATION' and message!=state: response='Error'
    elif state=='COMMUNICATION' and message=='SOFTWARE_INVENTORY':response='Changing_state'
    elif state=='COMMUNICATION' and (message=='SOFTWARE_DOWNLOAD' or message == 'SOFTWARE_INSTALL'):response='Error'
    
    msg='<message>' + response + '</message>'
    client_socket.sendall(msg.encode())
    return response
