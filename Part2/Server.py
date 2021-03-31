import socket               # Import socket module

s = sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP       # Create a socket object
s.bind(('127.0.0.1', 53))        # Bind to the port

s.listen(5)                 # Now wait for client connection.
while True:
       data, addr = s.recvfrom(1024) # buffer size is 1024 bytes
       print("received message: %s" % data)