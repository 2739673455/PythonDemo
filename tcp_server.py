import socket
import threading
import time
import queue


class TCPServer:
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("127.0.0.1", port))
        self.sock.listen(3)
        self.end = False
        self.queue = queue.Queue()

    def input_thread(self):
        while True:
            if self.end:
                time.sleep(0.1)
                continue
            try:
                print("\b \b" * 100 + str(self.address[0]) + ":" + str(self.address[1]) + " << ", end="")
                message = input()
                self.queue.put(message)
            except:
                self.end = True

    def send_thread(self):
        while not self.end:
            try:
                message = self.queue.get(block=False, timeout=0.5)
                self.client.send(bytes(message + "\n", "utf-8"))
            except queue.Empty:
                continue
            except:
                self.end = True
                break

    def recv_thread(self):
        self.client.settimeout(0.5)
        while not self.end:
            try:
                message = self.client.recv(1024).decode("utf-8")
            except socket.timeout:
                continue
            except:
                self.end = True
                break
            resv_msg = "\b \b" * 100 + str(self.address[0]) + ":" + str(self.address[1]) + " >> " + message
            send_msg = str(self.address[0]) + ":" + str(self.address[1]) + " << "
            print(resv_msg + send_msg, end="")

    def start(self):
        input_thread = threading.Thread(target=self.input_thread)
        input_thread.daemon = True
        input_thread.start()
        while True:
            self.client, self.address = self.sock.accept()
            self.end = False
            print("\b \b" * 100 + self.address[0] + ":" + str(self.address[1]) + " connected ")
            print(str(self.address[0]) + ":" + str(self.address[1]) + " << ", end="")
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
            self.client.close()
            print("\b \b" * 100 + "connection close")


client = TCPServer(9999)
client.start()
