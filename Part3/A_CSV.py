import binascii
import socket
import csv


Qname_size = 0  #for saving Qname lenght
filename = "hostNames.csv"
header = ("Host Name", "IP")

def writer(header, data, filename, option):
    with open(filename, "w", newline="") as csvfile:
        if option == "write":

            movies = csv.writer(csvfile)
            movies.writerow(header)
            for x in data:
                movies.writerow(x)
        elif option == "update":
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(data)
        else:

            print("Option is not known")



def updater(filename):
    with open(filename, newline="") as file:
        readData = [row for row in csv.DictReader(file)]

    size=len(readData)
    for i in range (size):
        hostName=readData[i]['  Host Name']
        query = create_message("A", hostName)
        response = send_query(query, '1.1.1.1', 53)
        ip = decode_response(response)

        print(readData[i]['  Host Name'])

        # print(readData)
        readData[i]['IP'] = ip
        print(readData[i]['IP'])

    readHeader = readData[i].keys()
    # print(readHeader)

    writer( readHeader, readData, filename, "update")



def create_message(type, hostName):
    ID = 43690  # 16 bit identifier

    QR = 0  # query =0 , response=1
    OPCODE = 0  # standard query 4bit
    AA = 0  # authoritative answer 1bit
    TC = 0  # turncated  1bit
    RD = 1  # recursion desired  1bit
    RA = 0  # recursion available 1bit
    Z = 0  # 3 bit
    RCODE = 0  # return code 4bit

    flags = ""
    flags = str(QR)
    flags += str(OPCODE).zfill(4)
    flags += str(AA)
    flags += str(TC)
    flags += str(RD)
    flags += str(RA)
    flags += str(Z).zfill(3)
    flags += str(RCODE).zfill(4)

    flags = "{:04x}".format(int(flags, 2))

    QDCOUNT = 1  # number of question 4bit
    ANCOUNT = 0  # Number of answers 4bit
    NSCOUNT = 0  # Number of authority records 4bit
    ARCOUNT = 0  # Number of additional records  4bit

    message_tosend = ""
    message_tosend += "{:04x}".format(ID)
    message_tosend += flags
    message_tosend += "{:04x}".format(QDCOUNT)
    message_tosend += "{:04x}".format(ANCOUNT)
    message_tosend += "{:04x}".format(NSCOUNT)
    message_tosend += "{:04x}".format(ARCOUNT)

    host_split = hostName.split(".")
    qnameSize = 0
    global Qname_size
    for part in host_split:
        byteTosned = "{:02x}".format(len(part))

        host_part = binascii.hexlify(part.encode())
        message_tosend += byteTosned
        message_tosend += host_part.decode()
        qnameSize += len(byteTosned)
        qnameSize += len(host_part.decode())

    Qname_size = qnameSize

    message_tosend += "00"  # terminated with a byte of 0
    QTYPE = 1
    message_tosend += "{:04x}".format(QTYPE)

    QCLASS = 1
    message_tosend += "{:04x}".format(QCLASS)

    print("query: "+message_tosend)

    return message_tosend


def send_query(query, serverIP, port):
    query.replace(" ", "").replace("\n", "")
    server_address = (serverIP, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.sendto(binascii.unhexlify(query), server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()

    print("respone packet is : "+ binascii.hexlify(data).decode("utf-8"))
    return binascii.hexlify(data).decode("utf-8")


def decode_response(response):
    # Header and Question
    ID = response[0:4]
    # print("ID is:  " + ID)
    query_params = response[4:8]
    # print("flags : " + query_params)
    QDCOUNT = response[8:12]
    # print("QDCOUNT: " + QDCOUNT)
    ANCOUNT = response[12:16]
    # print("ANCOUNT :" + ANCOUNT)
    NSCOUNT = response[16:20]
    # print("NSCOUNT :" + NSCOUNT)
    ARCOUNT = response[20:24]
    # print("ARCOUNT :" + ARCOUNT)
    qname_end = 24 + Qname_size + 2

    QNAME = response[24:qname_end]
    # print("Qname :" +str(int(QNAME,16)))
    Qtype_start = qname_end
    QTYPE = response[Qtype_start:Qtype_start + 4]
    # print("QTYPE: " + QTYPE)
    Qclass_start = Qtype_start + 4
    QCLASS = response[Qclass_start:Qclass_start + 4]
    # print("Qclass :" + QCLASS)

    # Answer Part

    NUM_ANSWERS = max([int(ANCOUNT, 16), int(NSCOUNT, 16), int(ARCOUNT, 16)])
    if NUM_ANSWERS > 0:
     Answer_Start = Qclass_start + 4
    # print(Answer_Start)

     ANAME = response[Answer_Start:Answer_Start + 4]
    # print("ANAME : " + ANAME)
     ATYPE = response[Answer_Start + 4: Answer_Start + 8]
    # print("ATYPE :" + ATYPE)
     ACLASS = response[Answer_Start + 8: Answer_Start + 12]
    # print("ACLASS : " + ACLASS)
     TTL = int(response[Answer_Start + 12: Answer_Start + 20], 16)
     RDLENGTH = int(response[Answer_Start + 20:Answer_Start + 24], 16)

     RDDATA = response[Answer_Start + 24:Answer_Start + 24 + (RDLENGTH * 2)]

     octets = [RDDATA[i:i + 2] for i in range(0, len(RDDATA), 2)]

     ip = ""
     for x in octets:
        ip += str(int(x, 16))
        if (octets.index(x) != len(octets) - 1):
            ip += '.'
     print(ip)
     return ip
    else:
        print("No Answer Section...")


updater(filename)
#
# query = create_message("A", host_name)
# response = send_query(query, '1.1.1.1', 53)
#
# decode_response(response)
