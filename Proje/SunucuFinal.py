import socket
import threading
import queue
import time
import sys

User_Dict  = {}

class WriteThread(threading.Thread):
    def __init__(self,name,csoc,cAddr,threadQueue,logQueue,condition):
        threading.Thread.__init__(self)
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
            cmd = queue_message.split(" ",1)
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
            elif cmd[0] == "LIS":
                self.list_rooms(player)
            elif cmd[0].strip() == "ENT":
                same_room = False
            if len(msg.split()) >= 2: # error check
                room_name = msg.split()[1]
                if not same_room:
                    if not room_name in self.rooms: # new room:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].players.append(player)
                    self.rooms[room_name].welcome_new(player)
                    self.room_player_map[player.name] = room_name
                print("SUC")
            if player.name in self.room_player_map:  # check if in a room or not first
                self.rooms[self.room_player_map[player.name]].broadcast(player, msg.encode())
            else:
                self.csoc.send(queue_message.encode())

        self.logQueue.put("Exiting " + self.name)
        self.csoc.close()

class ReadThread(threading.Thread):
    def __init__(self,name,csoc,cAddr,threadQueue,logQueue,User_Dict,condition):
        threading.Thread.__init__(self)
        self.name = name
        self.csoc = csoc
        self.cAddr = cAddr
        self.threadQueue = threadQueue
        self.logQueue = logQueue
        self.User_Dict = User_Dict
        self.nickname = ""
        self.condition = condition

    def parser(self,d):
        data = d.strip()
        cmd = d.split(" ",1)
        cmd[0] = cmd[0].strip()

        if cmd[0] == "NIC":
            try:
                nick = cmd[1].split(":")[0]
                if not self.User_Dict.get(nick):
                    self.User_Dict[nick] = {}
                    # Yeni kullanıcı kabulu
                    response = "WEL " + nick +"\n"
                    # durumun log dosyasına yazılması için log kuyruğuna kaydolan kullanıcıyı yazma
                    self.logQueue.put(nick+" kaydoldu")
                    return response

                else:#Boyle bir kullanıcı varsa hata mesajı döndür
                    response = "REJ" + nick +"\n"
                    return response 
                                   
            except:#eğer komut yanlış bir biçimde kullanıldıysa
                response = "LRR\n"
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

class Chatroom:
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.room_player_map = {} # {playerName: roomName}

    def list_rooms(self, player):
        if len(self.rooms) == 0:
            queue_message = 'Oops, no active rooms currently. Create your own!\n' \
                + 'Use [join room_name] to create a room.\n'
            self.csoc.send(queue_message.encode())
        else:
            queue_message ='Listing current rooms...\n'
            for room in self.rooms:
                queue_message += room + ": " + str(len(self.rooms[room].players)) + " player(s)\n"
            self.csoc.send(queue_message.encode())

class Room:
    def __init__(self, name):
        self.players = [] # a list of sockets
        self.name = name

    def broadcast(self, from_player, msg):
        msg = from_player.name.encode() + b":" + msg
        for player in self.players:
            self.csoc.send(msg)


class LogThread(threading.Thread):
    def __init__(self,logQueue):
        threading.Thread.__init__(self)
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
        yeniRthread = ReadThread("ReadThread-%s" % {counter}, c, addr, T_Queue, Log_Queue,User_Dict,condition)
        yeniRthread.start()
        counter=+1
    s.close()
if __name__ == "__main__":
    main()