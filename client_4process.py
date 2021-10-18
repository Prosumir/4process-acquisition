import requests
import time
import os
import threading
import json

# Allowed files extensions for upload
ALLOWED_EXTENSIONS = set(['pdf', 'txt', 'png', 'jpg', 'csv'])

FILE_UPLOAD_ENDPOINT = os.getenv("FILE_UPLOAD_ENDPOINT")
JSON_UPLOAD_ENDPOINT = os.getenv("JSON_UPLOAD_ENDPOINT")
UPLOAD_DIR = os.getenv("UPLOAD_DIR")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def client_thread(filename,number):
    if not filename:
        return
    r = []
    msg = ""
    action = "Client"
    try:
        if filename.rsplit(".")[1].lower() == "jpg":
            r = requests.post(  FILE_UPLOAD_ENDPOINT, 
                                files={ "file" : (filename, open(UPLOAD_DIR + filename, 'rb')) },
                                timeout=30)
        if filename.rsplit(".")[1].lower() == "txt":
            file = open(UPLOAD_DIR + filename, 'r')
            data = file.read()
            json_dict = json.loads(data)
            r = requests.post(JSON_UPLOAD_ENDPOINT,json=json_dict,timeout=30)
    except requests.Timeout as e:
        error = "Category: Timeout"
        msg = "{} - {} | HttpError:{}".format(error,action,e)
    except requests.ConnectionError as e:
        error = "Category: Connection"
        msg = "{} - {} | HttpError:{}".format(error,action,e)
    except requests.exceptions.RequestException as e:
        error = "Category: Request Exception"
        msg = "{} - {} | HttpError:{}".format(error,action,e)
    except:
        error = "Category: Undefined"
        e = "Undefined Exception"
        msg = "{} - {} | HttpError:{}".format(error,action,e)
    else:
        if r.status_code == 200:
            msg = "Request succeed"
            os.remove(os.path.join(UPLOAD_DIR, filename))
        if r.status_code == 400:
            msg = "Bad request, client sent malformed / missing data"
        if r.status_code == 500:
            msg = "Internal server error"
    finally:
        print("Uploading file ({}) - {}:{}".format(number,filename,msg))
        return

while True:
    print("Scanning files from dir " + UPLOAD_DIR)
    print("Files: {}".format(len(os.listdir(UPLOAD_DIR))))
    files = os.listdir(UPLOAD_DIR)
    threads = list()
    while files:
        for i in range(5):
            file_name = files.pop() if files else ""
            if(allowed_file(file_name) and file_name):
                thread = threading.Thread(target=client_thread,args=(file_name,len(files),), daemon=True)
                threads.append(thread)
                thread.start()
        
        for thread in threads:
            thread.join()
    print("Waiting for the next round of scan")
    time.sleep(60) # Delay for 1 minute (60 seconds)
