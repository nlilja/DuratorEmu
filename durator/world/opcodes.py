from enum import Enum


class OpCode(Enum):

    CMSG_CHAR_CREATE = 0x036
    CMSG_CHAR_ENUM   = 0x037
    CMSG_CHAR_DELETE = 0x038
    SMSG_CHAR_CREATE = 0x03A
    SMSG_CHAR_ENUM   = 0x03B
    SMSG_CHAR_DELETE = 0x03C

    CMSG_PLAYER_LOGIN     = 0x03D
    SMSG_NEW_WORLD        = 0x03E
    SMSG_TRANSFER_PENDING = 0x03F
    SMSG_TRANSFER_ABORTED = 0x040
    
    MSG_MOVE_WORLDPORT_ACK = 0x0DC

    CMSG_PING = 0x1DC
    SMSG_PONG = 0x1DD

    SMSG_AUTH_CHALLENGE = 0x1EC
    CMSG_AUTH_SESSION   = 0x1ED
    SMSG_AUTH_RESPONSE  = 0x1EE

    SMSG_LOGIN_VERIFY_WORLD = 0x236
