import socket

# init client
address = "127.0.0.1"
port = 5005
buffer_size = 1024
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
msg = "CONNECT"

# client is working
client.connect((address, port))
print("Successfull connected")
while msg.lower() != "close":
    print("Sending...", end="")
    client.send(msg.encode())
    print(" finished")
    data = client.recv(buffer_size)
    if data: print("Received:", data.decode())
    while data != b"ACK":
        data = client.recv(buffer_size)
        if data: print("Received:", data.decode())
    msg = input()
client.send(b"CLOSE")
print("Client is closing...")
client.close()
