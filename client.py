import tkinter as tk
import socket
import ssl
import threading

last_message = ""

class ChatWindow:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("----------------Chat Room--------------------")
        
        self.chat_box = tk.Text(self.parent, height=20, width=40)
        self.chat_box.pack()
        
        self.entry_box = tk.Entry(self.parent)
        self.entry_box.pack()
        
        self.send_button = tk.Button(self.parent, text="Send", command=self.send_message)
        self.send_button.pack()
        
        self.reply_button = tk.Button(self.parent, text="Reply", command=self.reply_message)
        self.reply_button.pack()

        # Load SSL/TLS certificate and key
        certfile = "server.crt"
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(certfile)

        # Connect to the server
        server_address = ('192.168.220.184', 8080)
        self.client_socket = ssl_context.wrap_socket(socket.socket(socket.AF_INET), server_hostname='localhost')
        self.client_socket.connect(server_address)

        # Start thread for receiving messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                self.chat_box.insert(tk.END, message + "\n")
                global last_message
                last_message=message
                print(message)
            except:
                break

    def send_message(self):
        message = self.entry_box.get()
        try:
            self.client_socket.send(message.encode())
            self.chat_box.insert(tk.END, "You: " + message + "\n")
            self.entry_box.delete(0, tk.END)
        except:
            self.chat_box.insert(tk.END, "Error sending message\n")
    
    def reply_message(self):
        message = self.entry_box.get()
        try:
            print(1)
            print(2)
            print(last_message)
            last_message_port = last_message.split(":")[1].split("]")[0]
            print(3)
            print(last_message_port)
            self.client_socket.send(("@" + last_message_port + " " + message).encode())
            self.chat_box.insert(tk.END, "You: " + message + "\n")
            self.entry_box.delete(0, tk.END)
        except:
            self.chat_box.insert(tk.END, "Error sending reply\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatWindow(root)
    root.mainloop()
