import socket
import struct


def send_msg(sock, msg):
    """ Prefix each message with a 4-byte length (network byte order)

    Args:
        sock: the socket to send over
        msg: bytes to send

    Returns:
        void
    """
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    """ Unpacks message lengtion and stores it as an int

    Args:
        sock: the socket data is sent over

    Returns:
        void
        None if given blank sock
    """
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    """ Helper function to recv n bytes or return None if EOF is hit 
    Args:
        sock: socket to expect data from
        n: length of data

    Returns:
        void
        None on EOF 
    """

    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
