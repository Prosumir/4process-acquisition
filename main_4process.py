import lib_4process
import datetime

#----------------Configuration---------------------

modules = lib_4process.load_modules()

#DELAY TIME em segundos entre cada medida do log
delay = 20 #delay entre os logs

#-----------------------------Main Script------------------------------------

date = datetime.datetime.utcnow()

while(modules):
    print("Loading Modules")
    modules = lib_4process.load_modules()
    alarm = date + datetime.timedelta(seconds=delay)
    print("Capturing")
    for module in modules:
        if module["type"].count("cam"):
            ans = lib_4process.capture_photo(module["ip"])
            if not ans:
                print("Delete: {} - {} - {}".format(module["ip"],module["equipmentId"],module["metricType"]))
                modules.remove(module)

    print("Getting Data")
    for module in modules:
        if module["type"].count("sensor"):
            value, ret = lib_4process.get_value(module["ip"])
            if ret:
                module["value"] = value
                date = datetime.datetime.utcnow()
                module["time"] = date.strftime("%H:%M:%S")
                module["date"] = date.strftime("%Y-%m-%d")
            else:
                print("Delete: {} - {} - {}".format(module["ip"],module["equipmentId"],module["metricType"]))
                modules.remove(module)
    for module in modules:
        if module["type"].count("cam"):
            photo, error = lib_4process.get_photo(module["ip"])
            if not error:
                module["photo"] = photo
                date = datetime.datetime.utcnow()
                module["time"] = date.strftime("%H:%M:%S")
                module["date"] = date.strftime("%Y-%m-%d")
            else:
                print("Delete: {} - {} - {}".format(module["ip"],module["equipmentId"],module["metricType"]))
                modules.remove(module)

    print("Saving Data")
    lib_4process.save_data(modules)

    print("Waiting until {}".format(alarm.strftime("%d-%m-%Y_%H:%M:%S")))
    while(date < alarm):
        date = datetime.datetime.utcnow()
print("OUT")
