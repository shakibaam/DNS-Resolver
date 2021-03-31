import socket

UDP_IP = "208.67.222.222"
UDP_PORT = 53
MESSAGE = "google.com"

print("UDP  IP: %s" % UDP_IP)
print("UDP  port: %s" % UDP_PORT)
print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

msgFromServer = sock.recvfrom(512)
print(msgFromServer)