import socket               # Import socket module

s = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
# Create a socket object
s.connect(('localhost', 53))
str ='Hello DNS'
byte = str.encode()
s.sendall(byte)
s.close()