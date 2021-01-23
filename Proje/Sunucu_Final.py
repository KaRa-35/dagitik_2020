import socket
import threading
import queue
import time
import sys

User_Dict  = {}
rooms = {}

class WriteThread(threading.Thread):
    def _init_(self,name,csoc,cAddr,threadQueue,logQueue,condition):
        threading.Thread._init_(self)
        self.name = name                   #thread adı
        self.csoc = csoc
        self.cAddr = cAddr
        self.threadQueue = threadQueue           #threadler arası mesaj iletişiminde kullanılacak
        self.logQueue = logQueue                 #logger thread ile iletişim
        self.condition = condition


    def run(self):
        self.logQueue.put("Starting " + self.name)
        while self.condition:
            queue_message = self.threadQueue.get()
            cmd = queue_message.split(" ",10)
            # kuyruktaki komut BYE ise condition false oluyor ve soket kapatılıyor
            if cmd[0].strip() == "PIN":  #Baglantı testi
                self.csoc.send(("PON").encode())
                self.condition = False
            elif cmd[0].strip() == "BYE":
                self.csoc.send(queue_message.encode())
                self.condition = False
            # sunucudan gelen ÖZEL mesaja sunucuya TEYİT mesajı gönderme
            elif cmd[0].strip() == "PRV":
                self.csoc.send(queue_message.encode())
                print("OKP")
            # sunucudan gelen Genel mesaja sunucuya TEYİT gönderme
            elif cmd[0].strip() == "GNL":
                self.csoc.send(queue_message.encode())
                print("OKG")
            else:
                self.csoc.send(queue_message.encode())

        self.logQueue.put("Exiting " + self.name)
        self.csoc.close()

class ReadThread(threading.Thread):
    def _init_(self,name,csoc,cAddr,threadQueue,logQueue,User_Dict,condition,rooms):
        threading.Thread._init_(self)
        self.name = name
        self.csoc = csoc
        self.cAddr = cAddr
        self.threadQueue = threadQueue
        self.logQueue = logQueue
        self.User_Dict = User_Dict
        self.nickname = ""
        self.condition = condition
        self.rooms = rooms

    def parser(self,d):
        data = d.strip()
        cmd = d.split(" ",10)
        cmd[0] = cmd[0].strip()
   

        if cmd[0] == "CRE":
            cmd[1] = cmd[1].strip()
            cmd[2] = cmd[2].strip()
            try:
                nick = cmd[1]
                password = cmd[2]
                if not nick in  self.User_Dict.keys():
                    if len(password) > 4:
                        self.User_Dict[nick] = {
                            'password':password,
                            'adminShip':[],
                            'memberShip':[],
                        }
                        print(self.User_Dict.get(nick))
                        # Yeni kullanıcı kaydı
                        response = "SUC " + nick +"\n"
                        # durumun log dosyasına yazılması için log kuyruğuna kaydolan kullanıcıyı yazma
                        self.logQueue.put(nick + password +" kaydoldu")
                        return response
                    else:# Kötü kalitede şifre belirlenirse
                        response = "BAD " + nick +"\n"
                        return response 
                else:#Boyle bir kullanıcı varsa hata mesajı döndür
                    response = "ALR" + nick +"\n"
                    return response 
                                   
            except:#eğer komut yanlış bir biçimde kullanıldıysa
                response = "LRR\n"
                return response
        elif cmd[0] == "NIC": # Baglantı testi
            cmd[1] = cmd[1].strip()
            cmd[2] = cmd[2].strip()
            nick = cmd[1]
            password = cmd[2]
            if nick in self.User_Dict.keys():
                print(self.User_Dict[nick][password])
                if password == self.User_Dict.get(nick).password:
                    self.nickname = nick
                    response = "WEL " + self.nickname +"\n"
                    return response
                else:
                    response = "NON " + nick +"\n"
                    return response
        elif cmd[0] == "ENT":
            cmd[1] = cmd[1].strip()
            cmd[2] = cmd[2].strip()
            rnick = cmd[1]
            members = cmd[2].split(":",10)
            self.rooms[rnick]={
                'members':members,
                'blockedusers':[]
            }
            print(self.rooms)
            response = "LIS " + rnick +"\n"
            return response

        elif cmd[0] == "TIN": # Baglantı testi
            response = "TON\n"
            return response

        elif cmd[0] == "QUI":
            if not self.User_Dict.get(self.nickname):#login olan bir kullanıcı yok ise
                response = "BYE\n"
                # buradaki self.condition değerini false yaparak readthread'in run fonksiyonundaki while dan çıkılacak
                self.condition = False
                return response
            else: #login olan bir kullanıcı var ise
                response = "BYE " + self.nickname + "\n"
                self.logQueue.put(self.nickname+" çıktı")
                self.condition = False
                return response

        elif cmd[0] == "GLS":
            nicknames = ""
            for key in self.User_Dict.keys():
                nicknames = key + ":" + nicknames
            response = "LST " + nicknames + "\n"

        elif cmd[0] == "GNL":
            try:
                message = cmd[1]
                queue_message = "GNL " + self.nickname +":"+message
                for key in self.User_Dict.keys():
                        self.User_Dict[key]["threadQueue"].put(queue_message)
                response = "OKG\n"

            except:
                response = "ERR\n"
                return response

        elif cmd[0] == "PRV":
            try:
                to_nick = cmd[1].split(":")[0]
                message = cmd[1].split(":")[1]
                #böyle bir kullanıcı yoksa
                if not to_nick in self.User_Dict.keys():
                    response = "NOP" + nick +"\n"
                #kullanıcı mevcutsa
                else:
                    queue_message = "PRV " + self.nickname + ":" + message
                    #mesajı mesaj gönderilen kullanıcının kuyruğuna yazma
                    self.User_Dict[to_nick]["threadQueue"].put(queue_message)
                    response = "OKP\n"
            except:
                response = "ERR\n"
                return response

    def run(self):
        self.logQueue.put("Starting " + self.name)
        while self.condition:
            data = self.csoc.recv(1024)
            decoded_data = data.decode("UTF-8")
            queue_message = self.parser(decoded_data)
            self.threadQueue.put(queue_message)
        self.logQueue.put("Exiting " + self.name)

class Room:
        def broadcast(self, from_player, msg):
            msg = from_player.name.encode() + b":" + msg
            for player in self.players:
                self.csoc.send(msg)

class LogThread(threading.Thread):
    def _init_(self,logQueue):
        threading.Thread._init_(self)
        self.logQueue = logQueue

    def run(self):
        with open("LogFile.txt", "w+") as logFile:
            while True:
                if not self.logQueue.empty():
                    log = time.ctime() + " : " + self.logQueue.get() + "\n"
                    logFile.write(log)
                    logFile.flush()

def main():
    s = socket.socket()
    host = "127.0.0.1"
    port = int(sys.argv[1])
    s.bind((host, port))
    s.listen()
    counter = 0
    Log_Queue = queue.Queue()  # bütün threadlerin ortak kullanacağı log kuyruğu
    yeniLogThread = LogThread(Log_Queue)
    yeniLogThread.start()

    while True:
        c, addr = s.accept()
        T_Queue = queue.Queue()
        condition = True
        yeniWthread = WriteThread("WriteThread-%s" % {counter}, c, addr, T_Queue, Log_Queue,condition)
        yeniWthread.start()
        yeniRthread = ReadThread("ReadThread-%s" % {counter}, c, addr, T_Queue, Log_Queue,User_Dict,condition,rooms)
        yeniRthread.start()
        counter=+1
    s.close()
if _name_ == "_main_":
    main()