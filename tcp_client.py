import socket
import threading
import time


class TCPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.end = False

    def send_thread(self):
        send_msg = str(self.host) + ":" + str(self.port) + " << "
        while True:
            try:
                message = input(send_msg)
                self.sock.send(bytes(message + "\n", "utf-8"))
            except:
                self.end = True
                break

    def recv_thread(self):
        while True:
            try:
                message = self.sock.recv(1024).decode("utf-8")
                if not message:
                    self.end = True
                    break
            except:
                self.end = True
                break
            resv_msg = "\r" + str(self.host) + ":" + str(self.port) + " >> " + message
            send_msg = str(self.host) + ":" + str(self.port) + " << "
            print(resv_msg + send_msg, end="")

    def start(self):
        send_thread = threading.Thread(target=self.send_thread)
        recv_thread = threading.Thread(target=self.recv_thread)
        send_thread.daemon = True
        recv_thread.daemon = True
        send_thread.start()
        recv_thread.start()
        while not self.end:
            try:
                time.sleep(0.5)
            except:
                break
        self.sock.close()
        print("\b \b" * 100 + "connection close")


client = TCPClient("127.0.0.1", 9999)
client.start()
