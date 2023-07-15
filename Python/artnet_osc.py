
import asyncio
from pyartnet import ArtNetNode
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher

#osc settings
ip = "127.0.0.1"
port = 1337

class dmx:
    ch1 = 0
    ch2 = 0
    ch3 = 0
    ch4 = 0
    

def filter_handler(address, *args):
    dmx.ch1 = args[0]
    print(f"{address}: {dmx.ch1}")



dispatcher = Dispatcher()
dispatcher.map("/channel", filter_handler)


async def artnet_loop():
    while True:
        # Run this code in your async function
        node = ArtNetNode('2.0.0.1', 6454)

        # Create universe 0
        universe = node.add_universe(0)

        # Add a channel to the universe which consists of 1 values (width)
        # Default size of a value is 8Bit (0..255) so this would fill
        # the DMX value 1 of the universe
        channel = universe.add_channel(start=80, width=1, byte_size=1)

        # Fade channel in 0s
        # The fade will automatically run in the background
        channel.add_fade([dmx.ch1], 0)
        print(dmx.ch1)

        # this can be used to wait till the fade is complete
        await channel
        await asyncio.sleep(0.0001)



async def init_main():
    server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    await artnet_loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint


asyncio.run(init_main())