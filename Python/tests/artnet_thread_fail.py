from pyartnet import ArtNetNode
import time,socket,datetime,json, threading, asyncio

# Set the incoming UPD port here
UDP_PORT = 6006
# Set the outgoing UDP port here
UDP_OUT_PORT = 6007
#The address of the artnet controller
IP_ARTNET = '192.168.178.9'


# UDP setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setblocking(1)
sock.bind(('', UDP_PORT))
#Set console color for easier UDP income reading
CRED = '\033[91m'
CEND = '\033[0m'


BIT = False
END = False


def network_udp():
    global sock, addr, UDP_OUT_PORT
    global BIT, END
    global stop_thread_pir, stop_thread_slow, interaction_stop, standard_mode
    data = '' # empty var for incoming data
    rec = 0
    while True:
        data_raw, addr = sock.recvfrom(1024)
        data = data_raw.decode()    # My test message is encoded
        print(f"{CRED}{datetime.datetime.now().time()} UDP MESSAGE: {data}{CEND}")    
        if data:                                                        # only do something when there's data
            if data.startswith("BIT"):
                BIT = True
                print(f"BIT: {BIT}")
            if data.startswith("END"):     
                END = True
                print(f"END: {END}")
try:
    network_udp_worker = threading.Thread(target=network_udp)
    network_udp_worker.name = 'udp_recorder network'
    network_udp_worker.start()
except:
    print (f"{datetime.datetime.now().time()}: Error: unable to start network_udp_worker thread. Exit.")
    quit()

async def main():
    global BIT, END
    # ARTNET SETUP
    node = ArtNetNode(IP_ARTNET, 6454)
    # Create universe 0
    universe = node.add_universe(0)
    # Add a channel to the universe which consists of 3 values
    # Default size of a value is 8Bit (0..255) so this would fill
    # the DMX values 1..3 of the universe
    channel = universe.add_channel(start=80, width=1, byte_size=2)
    if BIT == True:
        print("async bit")
        channel.add_fade([10000], 0)
        await channel
    if END == True:
        print("async end")
        channel.add_fade([65535], 0)
        await channel

asyncio.run(main())