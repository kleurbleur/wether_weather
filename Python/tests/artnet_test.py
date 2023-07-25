import asyncio
from pyartnet import ArtNetNode

class channel:
    one = None
    two = None

async def setup():
    node = ArtNetNode('127.0.0.1', 6454)

    # Create universe 0
    universe = node.add_universe(0)

    # Add a channel to the universe which consists of 3 values
    # Default size of a value is 8Bit (0..255) so this would fill
    # the DMX values 1..3 of the universe
    channel.one = universe.add_channel(start=1, width=1, byte_size=1)


async def main():
    while True:
        # Run this code in your async function

        # Fade channel to 255,0,0 in 5s
        # The fade will automatically run in the background
        channel.one.set_values([0])

        # this can be used to wait till the fade is complete
        await channel.one

asyncio.run(setup())
asyncio.run(main())