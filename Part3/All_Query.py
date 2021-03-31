import binascii
import socket

Qname_size = 0  # for saving Qname lenght


def get_type(type):
    types = [
        "ERROR",  # type 0 does not exist
        "A",
        "NS",
        "MD",
        "MF",
        "CNAME",
        "SOA",
        "MB",
        "MG",
        "MR",
        "NULL",
        "WKS",
        "PTS",
        "HINFO",
        "MINFO",
        "MX",
        "TXT"
    ]

    index = int(types.index(type))

    return "{:04x}".format(index)


# if isinstance(type, str) else types[type]

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
    QTYPE = get_type(type)
    message_tosend += QTYPE

    QCLASS = 1
    message_tosend += "{:04x}".format(QCLASS)

    print("query: " + message_tosend)

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

    print("respone packet is : " + binascii.hexlify(data).decode("utf-8"))
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

    Answer_num = max([int(ANCOUNT, 16), int(NSCOUNT, 16), int(ARCOUNT, 16)])
    if Answer_num > 0:
        for Answer in range(Answer_num):
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
            # print(RDLENGTH)
            RDDATA = response[Answer_Start + 24:Answer_Start + 24 + (RDLENGTH * 2)]
            # print(RDDATA)
            if ATYPE == get_type("A"):
                octets = [RDDATA[i:i + 2] for i in range(0, len(RDDATA), 2)]

                ip = ""
                for x in octets:
                    ip += str(int(x, 16))
                    if (octets.index(x) != len(octets) - 1):
                        ip += '.'
                print(ip)

            else:
                string = ""
                arr = parse_parts(RDDATA, 0, [])
                for x in arr:
                    bytes_object = bytes.fromhex(x)
                    string += binascii.unhexlify(x).decode('iso8859-1')

                    if (arr.index(x) != len(arr) - 1):
                        string += '.'
                print(string)

    else:
        print("No Answer Section...")



def parse_parts(message, start, parts):
    part_start = start + 2
    part_len = message[start:part_start]

    if len(part_len) == 0:
        return parts

    part_end = part_start + (int(part_len, 16) * 2)
    parts.append(message[part_start:part_end])

    if message[part_end:part_end + 2] == "00" or part_end > len(message):
        return parts
    else:
        return parse_parts(message, part_end, parts)


host_name = input("Enter your host name: ")
record_type = input("Enter your record: ")
query = create_message(record_type, host_name)
response = send_query(query, '1.1.1.1', 53)

ip = decode_response(response)
