import socket
import struct

from .ORGBDevice import ORGBDevice
from .consts import ORGBPkt

class OpenRGB:
    # define these constants.
    magic = bytes('ORGB', 'ascii')
    header_fmt = '4sIII'
    header_size = struct.calcsize(header_fmt)

    def __init__(self, host, port, client_string='python client'):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
        self.client_name(client_string)

    # Network stuff
    def client_name(self, name=None):
        if name is not None:
            self.client_string = name
        self._send_message(
            ORGBPkt.SET_CLIENT_NAME,
            bytes(self.client_string, 'ascii')
        )

    def controller_count(self):
        self._send_message(ORGBPkt.REQUEST_CONTROLLER_COUNT)
        msg = self._recv_message()
        _, count = msg
        count = struct.unpack('I', count)[0]
        return count

    def controller_data(self, device_id=0):
        self._send_message(
            ORGBPkt.REQUEST_CONTROLLER_DATA,
            device_id=device_id
        )
        msg = self._recv_message()
        return ORGBDevice(msg[1])

    # RGB controllers

    # not implemented
    def resize_zone(self, device_id=0):
        pass
    def set_custom_mode(self, device_id=0):
        pass
    def set_update_mode(self, device_id=0):
        pass

    # LED Control
    def update_leds(self, color_collection, device_id=0):
        c_buf = struct.pack('H', len(color_collection))
        for i in color_collection:
            c_buf += struct.pack('BBBx', i[0], i[1], i[2])
        # Add an accurate 
        real = struct.pack('I', len(c_buf)) + c_buf
        self._send_message(
            ORGBPkt.RGBCONTROLLER_UPDATELEDS,
            data=real,
            device_id=device_id
        )
    def update_zone_leds(self, device_id=0):
        self._send_message(
            ORGBPkt.RGBCONTROLLER_UPDATEZONELEDS,
            device_id=device_id
        )
    def update_single_led(self, led, color, device_id=0):
        msg = struct.pack('iBBBx', led, color[0], color[1], color[2])
        self._send_message(
            ORGBPkt.RGBCONTROLLER_UPDATESINGLELED,
            data=msg,
            device_id=device_id
        )

    # protocol helpers
    def _make_header(self, dev_idx, pkt_type, pkt_size):
        return struct.pack(
            self.header_fmt,
            self.magic,
            dev_idx,
            pkt_type,
            pkt_size
        )

    def _send_message(self, cmd, data=b'', device_id=0):
        header = self._make_header(
            device_id,
            cmd.value,
            len(data)
        )
        packet = header + data
        self.s.send(packet)

    def _recv_message(self):
        # validate the header:
        magic, dev_idx, pkt_type, pkt_size = struct.unpack(
            self.header_fmt, self.s.recv(self.header_size)
        )
        if magic != self.magic:
            raise Exception('Invalid packet received')

        # try to read it all in.
        buf = b''
        if pkt_size > 0:
            left = pkt_size
            while left > 0:
                buf += self.s.recv(left)
                left = pkt_size - len(buf)

        return (
            (dev_idx, pkt_type),
            buf
        )
