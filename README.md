# OpenRGB Python Client

[OpenRGB](https://gitlab.com/CalcProgrammer1/OpenRGB) 
dropped it's server protocol into master yesterday, so
I wrote this hacky little client library to use it.

## Usage

**note** This is subject to change as the library is still early in development.
I do intend do cleaner abstractions at some point, but for now it's fairly low
level. The examples folder should contain enough code to get started, but you'll
end up having to read the source if you want to do anything more complex.

First, you need to import the library:

```
from openrgb import OpenRGB
```

Then you can connect to your SDK server instance by using instantiating the
OpenRGB object with the details needed to connect to your SDK server instance.

```
client = OpenRGB('localhost', 1337)
```

Now we can start doing interesting things! Lets go through and read all the
device details:

```
# Find out how many devices there are, and collect all their data.
devices = {}
for i in range(client.controller_count()):
    devices[i] = client.controller_data(device_id=i)
```

And if we print devices, we get (subject to change due to your hardware):

```
{0: ASUS Aura Motherboard - ORGBDeviceType.MOTHERBOARD, 1: Corsair Vengeance Pro RGB - ORGBDeviceType.DRAM, 2: Corsair Vengeance Pro RGB - ORGBDeviceType.DRAM, 3: AMD Wraith Prism - ORGBDeviceType.COOLER, 4: SteelSeries Rival 110 - ORGBDeviceType.MOUSE}
```

## Protocol

### Header

Each message (from either the client or the server) has a header of the format:

```
char[4] magic
unsigned int device_id
unsigned int packet_type
unsigned int packet_size
```

The `magic` just contains the characters 'ORGB', and is used to identify if the
packet is real.

`device_id` is used to specify which device you want to control or obtain info
from. For messages that are general and don't refer to a specific device, this
is set to 0.

`packet_type` refers to what the message is about. You can see the full list
[here](https://gitlab.com/CalcProgrammer1/OpenRGB/-/blob/master/NetworkProtocol.h)

`packet_size` is the total amount of bytes of the binary payload. Some commands
don't send anything, so this gets set to 0.
