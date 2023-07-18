import time,socket,datetime,json, threading


# Set the to be loaded slots. 
# Has to be full paths or else it won't start on boot! 
play_1 = "dict_export_test_v1.json"
play_2 = "SLOT_2.json"
path_settings = "settings.json"    





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



#Set console color for easier UDP income reading
CRED = '\033[91m'
CEND = '\033[0m'



#load composition 1
def composition_load_pir():
    global play_1, recording_pir,rec_dict_pir, last_time_pir
    print(f"{datetime.datetime.now().time()}: opening {play_1}")
    try:
        f = open(play_1, "rb")
    except:
        print("The FIRST SLOT does not contain a file.")
    else:
        one_char = f.read(1) # read first character to check if it contains data 
        if one_char:
            f.seek(-1, 1)   # go back one character to make sure json.loads still understand the format
            recording_pir = json.loads(f.read())
            rec_dict_pir = {entry["id"]:entry["time"] for entry in recording_pir}
            print(rec_dict_pir) 
            last_time_pir = list(recording_pir)[-1]["time"]
            f.close()
            print(f"{datetime.datetime.now().time()}: {play_1} is {last_time_pir} seconds long")
        elif not one_char:
            print("The FIRST SLOT does not contain any data.")
composition_load_pir()
