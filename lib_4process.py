import requests
import datetime
import json
from time import sleep
import cv2
from PIL import Image,ImageFile
import io
ImageFile.LOAD_TRUNCATED_IMAGES = True

LOG_FILE = os.getenv("LOG_FILE")
MODULES_FILE = os.getenv("MODULES_FILE")
UPLOAD_DIR = os.getenv("UPLOAD_DIR")

#Timeout para os requests
timeout_connection = 20
timeout_read = 30

def logger(buffer):
    if buffer:
        log = open(LOG_FILE, "a")
        date = datetime.datetime.now()
        time = date.strftime("%d-%m-%Y_%H:%M:%S")
        log.write("{} : {}".format(time,buffer))
        log.close()

def get_value(ip):
    action = "Get Value"
    try:
        page = requests.get(ip + "/json", timeout=(timeout_connection,timeout_read))
    except requests.Timeout as e:
        error = "Category: Timeout"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        return 0, 0
    except requests.ConnectionError as e:
        error = "Category: Connection"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        return 0, 0
    except requests.exceptions.RequestException as e:
        error = "Category: Request Exception"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        return 0, 0
    except:
        error = "Category: Undefined"
        e = "Undefined Exception"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        return 0, 0
    else:
        json_file = page.json()
        if "value" in json_file:
            if "--" in json_file["value"]:
                error = "Category: Json"
                e = "Undefined Value"
                msg = "{} - {} - {} | Error:{}".format(error,ip,action,e)
                logger(msg)
                print(msg)
                json_file["value"] = "null"
        else:
            error = "Category: Json"
            e = "No Value"
            msg = "{} - {} - {} | Error:{}".format(error,ip,action,e)
            logger(msg)
            print(msg)
            json_file["value"] = "null"
        return json_file["value"], 1

def get_photo(ip):
    action = "Get Photo"
    img = []
    time = datetime.datetime.now()
    alarm = datetime.datetime.now() + datetime.timedelta(seconds = timeout_connection)
    shooting, error = wait_photo(ip)
    
    while(shooting and (time<alarm)) and not error:
        sleep(0.3)
        shooting, error = wait_photo(ip)
        time = datetime.datetime.now()
    if error:
        return img, error

    try:
        ans = requests.get(ip + "/saved-photo", stream=True, timeout=(timeout_connection,timeout_read))
    except requests.Timeout as e:
        error = "Category: Timeout"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        error = 1
    except requests.ConnectionError as e:
        error = "Category: Connection"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        error = 1
    except requests.exceptions.RequestException as e:
        error = "Category: Request Exception"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        error = 1
    except:
        e = "Undefined Exception"
        error = "Category: Undefined"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        error = 1
    else:
        t = datetime.datetime.now()
        try:
            action = "Load Photo"
            #img = Image.open(io.BytesIO(ans.content))
            img = Image.open(ans.raw)
        except OSError as e:
            error = "Category: OSError"
            msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
            logger(msg)
            print(msg)
            error = 1
        except ConnectionError as e:
            error = "Category: Connection"
            msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
            logger(msg)
            print(msg)
            error = 1
        except Exception as e:
            error = "Category: Exception"
            msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
            logger(msg)
            print(msg)
            error = 1
        except:
            e = "Undefined Exception"
            error = "Category: Undefined"
            msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
            logger(msg)
            print(msg)
            error = 1
        finally:
            t = datetime.datetime.now() - t
            print("{}: {}".format(action,t))
    time = datetime.datetime.now() - time - t
    print("Get Photo: {}".format(time))
    return img, error

def capture_photo(ip):
    action = "Capture Photo"
    ret = ""
    try:
        requests.get(ip + "/capture?flashlight=true", timeout=(timeout_connection,timeout_read))
    except requests.Timeout as e:
        error = "Category: Timeout"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        ret = 0
    except requests.ConnectionError as e:
        error = "Category: Connection"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        ret =  0
    except requests.exceptions.RequestException as e:
        error = "Category: Request Exception"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        ret =  0
    except:
        error = "Category: Undefined"
        e = "Undefined Exception"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        ret =  0
    else:
        ret =  1
    return ret

def get_photo_old(ip):
    img = []
    ret = 0
    try:
        cap = cv2.VideoCapture(ip)
    except:
        logger(ip + " - Capture Photo - ERROR01")
        print(ip + " - Capture Photo - ERROR01")
        ret = 0
    else:
        if cap.isOpened():
            ret,img = cap.read()
        else:
            logger(ip + " - Capture Photo - ERROR02")
            print(ip + " - Capture Photo - ERROR01")
            ret = 0
    finally:
        cap.release()
    return ret,img

def wait_photo(ip):
    error = 0
    action = "Wait Photo"
    try:
        capture = requests.get(ip + "/shooting", timeout=(timeout_connection,timeout_read)).text
    except requests.Timeout as e:
        error = "Category: Timeout"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        error =  1
    except requests.ConnectionError as e:
        error = "Category: Connection"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        error =  1
    except requests.exceptions.RequestException as e:
        error = "Category: Request Exception"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        error =  1
    except:
        error = "Category: Undefined"
        e = "Undefined Exception"
        msg = "{} - {} - {} | HttpError:{}".format(error,ip,action,e)
        logger(msg)
        print(msg)
        error =  1
    
    return int(capture), error

def save_data(modules):
    buff = ""
    time = ""
    brewery = ""
    for module in modules:
        if ("photo" in module) and ("time" in module):
            file_name = ""
            print(module["equipmentId"] + " - " + module["metricType"])
            img = module["photo"].copy()
            del module["photo"]
            del module["ip"]
            for key in module:
                file_name += str(module[key]) + "_"
            file_name = file_name[:-1] + ".jpg"
            img.save(UPLOAD_DIR + file_name, "JPEG")
    for module in modules:
        if ("value" in module) and ("time" in module):
            file_name = ""
            print(module["equipmentId"] + " - " + module["metricType"])
            del module["ip"]
            data = json.dumps(module)
            del module["value"]
            for key in module:
                file_name += str(module[key]) + "_"
            file_name = file_name[:-1] + ".txt"
            file = open(UPLOAD_DIR + file_name, "w")
            file.write(data)
            file.close()

def load_modules():
    #load config txt
    file = open(MODULES_FILE, "r")
    file_data = file.read().rsplit("{")[1:]
    file.close()

    modules = []
    for i,module in enumerate(file_data):
        modules.append(json.loads("{" + module))
    
    for module in modules:
        print("{} - {}".format(module["equipmentId"],module["metricType"]))
    return modules
