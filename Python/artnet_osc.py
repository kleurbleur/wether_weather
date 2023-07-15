
import asyncio
from pyartnet import ArtNetNode

async def main():
    # Run this code in your async function
    node = ArtNetNode('192.168.178.9', 6454)

    # Create universe 0
    universe = node.add_universe(0)

    # Add a channel to the universe which consists of 3 values
    # Default size of a value is 8Bit (0..255) so this would fill
    # the DMX values 1..3 of the universe
    channel = universe.add_channel(start=80, width=1, byte_size=2)

    # Fade channel to 255,0,0 in 5s
    # The fade will automatically run in the background
    channel.add_fade([32768], 0)

    # this can be used to wait till the fade is complete
    await channel

asyncio.run(main())