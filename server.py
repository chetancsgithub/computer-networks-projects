import socket
import ssl
import threading

def handle_client(client_socket, client_address):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"[{client_address[0]}:{client_address[1]}] says: {message}")
            
            # Check if the message is a private message
            if message.startswith('@'):
                # Extract the recipient's port number from the message
                recipient_port = int(message.split()[0][1:])
                
                # Find the recipient's socket object in the clients dictionary
                recipient_socket = None
                for sock, addr in clients.items():
                    if addr[1] == recipient_port:
                        recipient_socket = sock
                        break
                
                # If the recipient socket object was found, send the message only to the recipient
                if recipient_socket is not None:
                    send_message(f"[Private message from {client_address[0]}:{client_address[1]}]: {' '.join(message.split()[1:])}", recipient_socket)
                else:
                    send_message(f"Error: recipient with port {recipient_port} not found", client_socket)
            else:
                # Otherwise, broadcast the message to all clients except the sender
                broadcast(f"[{client_address[0]}:{client_address[1]}] says: {message}", client_socket)
        except:
            break

    client_socket.close()
    print(f"Connection closed: {client_address[0]}:{client_address[1]}")

def broadcast(message, sender_socket):
    for client_socket in clients.keys():
        if client_socket != sender_socket:
            send_message(message, client_socket)

def send_message(message, client_socket):
    try:
        client_socket.send(message.encode())
    except:
        # If there was an error sending the message, remove the client from the clients dictionary
        clients.pop(client_socket, None)

clients = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('192.168.220.184', 8080))
server_socket.listen()

# Load SSL/TLS certificate and key
certfile = "server.crt"
keyfile = "server.key"
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile, keyfile)

# Wrap the socket with SSL/TLS
ssl_socket = ssl_context.wrap_socket(server_socket, server_side=True)

print("Server started. Listening for connections...")

while True:
    client_socket, client_address = ssl_socket.accept()
    print(f"New connection: {client_address[0]}:{client_address[1]}")
    clients[client_socket] = (client_address[0], client_address[1])
    threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

    # Send welcome message to new client
    send_message("Welcome to the chat room!", client_socket)

    # Send notification to other clients
    broadcast(f"A new user has joined the chat: {client_address[0]}:{client_address[1]}", client_socket)

    # Send a message from the server to the new client
    send_message("This is a message from the server", client_socket)