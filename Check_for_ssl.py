default_file = ""
FORMAT = "utf-8"
def is_ssl(f):
    if f==1:default_file="DefaultconfigRU.txt"
    else :default_file="DefaultconfigDU.txt"

    filedata=""
    with open(default_file, 'rb') as fs:
        while True:
            data = fs.read(1024).decode(FORMAT)
            if not data:
                break
            filedata+=data
        fs.close()
    flag=""
    start=0
    for ch in filedata:
        if ch=='(':
            start=1
        elif ch==')':
            start=0
            break
        elif start==1:
            flag+=ch
    return flag


    