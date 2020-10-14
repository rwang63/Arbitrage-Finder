import socket
import time

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(sock)

server_address = ('localhost', 10000)
for n in range(10_000):
    message = 'message {}'.format(n).encode('utf-8')
    print('sending {!r} (even if nobody is listening)'.format(message))
    sent = sock.sendto(message, server_address)  # the publisher does not do a bind
    print(sock)
    time.sleep(1.0)