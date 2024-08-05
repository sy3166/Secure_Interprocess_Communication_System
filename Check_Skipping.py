data_folder = ""
default_file = "DefaultconfigRU.txt"
FORMAT = "utf-8"

def skip(message):
    filedata = ""
    with open(default_file, 'r') as fs:
        while True:
            data = fs.read(1024)
            if not data:
                break
            filedata += data
        fs.close()
    start = filedata.rfind('[')
    end = filedata.rfind(']')
    data = filedata[start + 1:end - 1]
    items = data.split(',')
     
    if message in items:
        return True
    else:
        return False

def To_skip(message,client_socket):
    return skip(message)