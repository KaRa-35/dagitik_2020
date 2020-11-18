#!/usr/bin/env python

import socket
import random
import threading
import sys

guess = int(input("Enter an integer from 1 to 99: "))
n = random.randint(1, 99)

class readThread(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.conn = sock
    def run(self):
        while True:
            data = self.conn.recv(1024)
            print(data.decode())

class writeThread(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.conn = sock
    def run(self):
        while True:
            data = input()
            self.conn.send(data.encode())

def main():
    s = socket.socket()
    ipaddr = sys.argv[1]
    port = int(sys.argv[2])
    s.bind((ipaddr, port))

    s.listen()

    if not data :
        print("GRR")
#Duzgun sekilde veri alamadık

    while data[0:2] == "STA":
        conn, addr = s.accept()
        print("Sayi bulmaca oyununa hosgeldiniz ! :", addr)
        self.conn.send("Welcome to Codes Server!".encode())
        self.conn.send("\n".encode())    
#program başlıyor           
        if n != "guess":
        sendValue = ""
        data = self.conn.recv(1024)
        print("RDY ", data.decode())
        getValue = data.decode()

        if guess < n:
            print("LTH")
            guess = int(input("Enter an integer from 1 to 99: "))

        elif guess > n:
            print("GTH")
            guess = int(input("Enter an integer from 1 to 99: "))

        elif guess = n:
            print("WIN")

        elif getValue.strip() == "QUI":
            sendValue = "BYE"
            self.conn.send(sendValue.encode())
            self.conn.send("\n".encode())
            kosul = False
            c.close()    
#baglantı kontrolu       
        elif data[0] == "TIC" and data.__len__() ==1:
            self.conn.send("TOC\n")

        else:
            getValue = getValue.split(" ", 1)
            if getValue[0] == "GET":
                sendValue = get(getValue[1].strip())
            else:
                sendValue = "ERR"
            self.conn.send(sendValue.encode())
            self.conn.send("\n".encode())

        break
s.close()


if __name__ == "__main__":
    main()
