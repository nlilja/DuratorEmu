from struct import Struct

from durator.common.crypto.session_cipher import SessionCipher
from durator.config import DEBUG
from durator.world.opcodes import OpCode
from pyshgck.format import dump_data
from pyshgck.logger import LOG


class WorldPacket(object):

    OUTGOING_SIZE_BIN   = Struct(">H")
    OUTGOING_OPCODE_BIN = Struct("<H")

    # This static packet buffer ensures that all world packets are correctly
    # received in their entirety. It is always either empty or starting with a
    # new packet.
    _PACKET_BUF = b""

    def __init__(self, data = None):
        self.opcode = None
        self.data = data or b""

    @staticmethod
    def from_socket(socket, session_cipher = None):
        """ Receive a WorldPacket through socket and return it, or None if the
        connection is closed during reception. """
        data = WorldPacket._recv_next_packet(socket, session_cipher)
        if data is None:
            return None

        opcode, opcode_value, data = WorldPacket._parse_packet_data(data)

        if DEBUG:
            if opcode is not None:
                print("<<<", opcode)
            else:
                print("<<< 0x{:X}".format(opcode_value))
            print(dump_data(data), end = "")

        packet = WorldPacket()
        packet.opcode = opcode
        packet.data = data
        return packet

    @staticmethod
    def _recv_next_packet(socket, session_cipher):
        """ Receive the next packet through socket and maybe decrypt it. """
        while True:
            # If the packet buffer is empty, receive data as long as the
            # connection is opened.
            if not WorldPacket._PACKET_BUF:
                data_part = socket.recv(1024)
                if not data_part:
                    return None
                WorldPacket._PACKET_BUF += data_part

            # Continue receiving data until we have a complete header.
            if len(WorldPacket._PACKET_BUF) < SessionCipher.DECRYPT_HEADER_SIZE:
                continue

            # If a session cipher is provided, use it to decrypt the header.
            if session_cipher is not None:
                decrypted = session_cipher.decrypt(WorldPacket._PACKET_BUF)
                WorldPacket._PACKET_BUF = decrypted

            packet_size = int.from_bytes(WorldPacket._PACKET_BUF[0:2], "big")
            WorldPacket._PACKET_BUF = WorldPacket._PACKET_BUF[2:]

            # Now that we have a packet size, wait until we have all the data
            # of this packet.
            if len(WorldPacket._PACKET_BUF) < packet_size:
                continue

            # When all the packet is in the static buffer, cut it from the
            # buffer and return it.
            data = WorldPacket._PACKET_BUF[:packet_size]
            WorldPacket._PACKET_BUF = WorldPacket._PACKET_BUF[packet_size:]
            break

        return data

    @staticmethod
    def _parse_packet_data(data):
        """ Return the OpCode (if possible, else None), the opcode value and the
        packet content. """
        opcode_bytes, data = data[:4], data[4:]
        opcode_value = int.from_bytes(opcode_bytes, "little")

        opcode = None
        try:
            opcode = OpCode(opcode_value)
        except ValueError:
            LOG.warning("Unknown opcode {:X}".format(opcode_value))

        return opcode, opcode_value, data

    def to_socket(self, session_cipher = None):
        """ Return ready-to-send bytes, possibly encrypted, from the packet. """
        opcode_bytes = self.OUTGOING_OPCODE_BIN.pack(self.opcode.value)
        packet = opcode_bytes + self.data
        size_bytes = self.OUTGOING_SIZE_BIN.pack(len(packet))
        packet = size_bytes + packet

        if session_cipher is not None:
            packet = session_cipher.encrypt(packet)

        return packet
