import time,datetime,json,asyncio
from pyartnet import ArtNetNode
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher

#osc settings
IP = "127.0.0.1"
OSC_PORT = 1337

#Set console color for easier OSC logging
CRED = '\033[91m'
CEND = '\033[0m'


print(f"Listening on port {OSC_PORT} for OSC messages from the recorder software.") 
print("Commands are 'REC filename.json', 'EDIT', 'SHOW', 'STOP' and 'EXIT'.")
print("Sending values when in EDIT mode works if inverters are connected and programmed on 0 - 3.3V input.")    

class dmx:
    ch1 = 0
    ch2 = 0
    ch3 = 0
    ch4 = 0
    ch5 = 0
    ch6 = 0
class screen:
    hue = 0
    saturation = 0
    brightness = 0


def value_handler(address, *args)    :
    dmx.ch1 = args[0]
    dmx.ch2 = args[1]
    dmx.ch3 = args[2]
    dmx.ch4 = args[3]
    dmx.ch5 = args[4]
    dmx.ch6 = args[5]
    screen.hue = args[6]
    screen.saturation = args[7]
    screen.brightness = args[8]





# Declare variables 
playing = False
pir_sensor = False
pir_sensor_active = False
standard_mode = False
stop_thread_slow = False
stop_thread_pir = False
interaction_stop = False
edit_stop = False
play_mode = 0
play_mode_active = False

def network_udp():
    global sock, addr, UDP_OUT_PORT
    global play_mode, play_mode_active, pir_sensor_active
    global path_settings
    global stop_thread_pir, stop_thread_slow, interaction_stop, standard_mode
    global pi
    if pi:
        global inv_1, inv_2
    data = '' # empty var for incoming data
    rec = 0
    while True:
        data_raw, addr = sock.recvfrom(1024)
        data = data_raw.decode()    # My test message is encoded
        if DEBUG == 3 or DEBUG == 4:
            print(f"{CRED}{datetime.datetime.now().time()} UDP MESSAGE: {data}{CEND}")    
        if data:                                                        # only do something when there's data
            if data.startswith("status"):
                show_mode = "play_mode " + str(play_mode)
                sock.sendto((bytes(show_mode, "utf-8")), (addr[0], UDP_OUT_PORT))
            if data.startswith("SHOW"): 
                status = "status SHOW"
                sock.sendto((bytes(status, "utf-8")), (addr[0], UDP_OUT_PORT))    
                try:
                    file_settings = open(path_settings, 'w')
                    file_settings.write(data)    
                    file_settings.close()                    
                except:
                    print("settings file cannot be opened or written.")
                standard_mode = False
                stop_thread_pir = False
                stop_thread_slow = False                
                interaction_stop = False
                play_mode_active = False
                pir_sensor_active = False                
                play_mode = 2
                print("play_mode udp", play_mode)
            if data.startswith("EDIT"):
                status = "status EDIT"
                sock.sendto((bytes(status, "utf-8")), (addr[0], UDP_OUT_PORT))                    
                try:
                    file_settings = open(path_settings, 'w')
                    file_settings.write(data)    
                    file_settings.close()                    
                except:
                    print("settings file cannot be opened or written.")
                stop_thread_slow = True
                stop_thread_pir = True
                interaction_stop = True
                play_mode_active = False
                pir_sensor_active = False
                play_mode = 1 
                print("play_mode udp", play_mode)
            if play_mode == 1:
                decode_list = data.split()                              # byte decode the incoming list and split in two
                if decode_list[0].startswith("REC") and rec == 0:                    # if the first part of the list starts with "rec"
                    status = "status REC"
                    sock.sendto((bytes(status, "utf-8")), (addr[0], UDP_OUT_PORT))                        
                    print(decode_list[0],decode_list[1])                    # for debug purposes
                    y = []                                                  # the list that is used to store everything, empty or start it when this is called
                    if pi:
                        loc_file = "/home/kb/Desktop/zoro/python/zoro_18/" + decode_list[1]
                    else:
                        loc_file = decode_list[1]
                    t0 = time.time()                                        # start the timer
                    f = open(loc_file, 'w+')                           # open or new file with the chosen file in the Recorder Software
                    rec = 1
                    sock.sendto(bytes("REC", "utf-8"), (addr[0], UDP_OUT_PORT))
                elif decode_list[0].startswith("VALUES"):   # if the first part of the list starts with "VALUES"
                    if pi:
                        inv_1.value = int(decode_list[1])
                        inv_2.value = int(decode_list[2])
                    if rec:
                        t1 = time.time() - t0
                        x = {                                                   # build a dict with the info from UDP
                            "time": round(t1, 3),
                            "values":[
                                    int(decode_list[1]),
                                    int(decode_list[2]),
                                    int(decode_list[3]),
                                    int(decode_list[4]),
                                    int(decode_list[5]),
                                    int(decode_list[6]),
                                    int(decode_list[7]),
                                    int(decode_list[8]),
                                    int(decode_list[9])                                                                                         
                                ]           
                            }
                        y.append(x)                                         # append the dict to the list 
                elif decode_list[0].startswith("ST_RC"):                 # if the list starts with "ST_RC"
                    print("RECEIVED STOP RECORDING ORDER")
                    rec = 0
                    try:    
                        json_dump = json.dumps(y, sort_keys=True, ensure_ascii=False) #transfer the list of dicts into a json format
                        f.write(json_dump)                                      # write it to the file opened in "rec"
                        f.close()                                               # close the file  
                        print("done writing file")                              
                        sock.sendto(bytes("load_mode 1", "utf-8"), (addr[0], UDP_OUT_PORT))
                        del y                                                   # double check to delete to free up memory
                        # composition_load_slow() 
                        sock.sendto(bytes("load_mode 0", "utf-8"), (addr[0], UDP_OUT_PORT))
                    except:
                        print("The recording has not started yet. Try again.")
                    sock.sendto(bytes("STOPPED RECORDING", "utf-8"), (addr[0], UDP_OUT_PORT))
                    status = "status REC_DONE"
                    sock.sendto((bytes(status, "utf-8")), (addr[0], UDP_OUT_PORT))                        
                elif decode_list[0].startswith("STOP"):                 # if the list starts with "STOP"
                    status = "status STOP"
                    sock.sendto((bytes(status, "utf-8")), (addr[0], UDP_OUT_PORT))                        
                    if rec:
                        rec = 0
                        try:    
                            json_dump = json.dumps(y, sort_keys=True, ensure_ascii=False) #transfer the list of dicts into a json format
                            f.write(json_dump)                                      # write it to the file opened in "rec"
                            f.close()                                               # close the file  
                            print("done writing file")                              
                            del y                                                   # double check to delete to free up memory
                        except:
                            print("The recording has not started yet. Try again.")
                            sock.sendto(bytes("STOPPED RECORDING", "utf-8"), (addr[0], UDP_OUT_PORT))
                        status = "status REC_DONE"
                        sock.sendto((bytes(status, "utf-8")), (addr[0], UDP_OUT_PORT))                        
try:
    network_udp_worker = threading.Thread(target=network_udp)
    network_udp_worker.name = 'udp_recorder network'
    network_udp_worker.start()
except:
    print (f"{datetime.datetime.now().time()}: Error: unable to start network_udp_worker thread. Exit.")
    quit()
