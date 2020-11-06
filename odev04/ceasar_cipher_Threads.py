import threading
import queue
import time


class Thread(threading.Thread):
    def __init__(self, id, name, q):
        threading.Thread.__init__(self)
        self.threadID = id
        self.name = name
        self.q = q

    def run(self):
        process_data(self.q, newdata)


def process_data(q, newdata):
    # threadlerin yeni dosyaya yazma işlemi yapılır
    while True:
        queueLock.acquire()
        if not q.empty():
            data = q.get()
            if data == "Quit":
                break
            newdata.write(data)
            queueLock.release()
        else:
            queueLock.release()


def divert(data, l):
    # bu fonksiyon dosyadan alınan verileri l sayıda karakter içeren parçalara böler
    parts = []
    part = ""
    lines = data.readlines()
    for line in lines:
        a = 0
        while a < len(line):
            part += line[a]
            if len(part) == l:
                parts.append(cipher(part, s))
                part = ""
            a += 1
    parts.append(part)
    return parts


def cipher(text, s):
    # Bu fonsiyon verilen stringi istenen s değeriyle şifreliyerek geri gönderiyor
    # Şifrelemek için mode = 1 Şifreyi çözmek için mode = -1 kullanabiliriz

    alphabet = 'abcdefghijklmnopqrstuvwyzABCDEFGHIJKLMNOPQRSTUVWYZ'
    result = ""
    for a in text:
        index = alphabet.find(a)
        if index == -1:
            result += a
        else:
            result += alphabet[(index + len(alphabet) + s) % len(alphabet)]
    return result


s = int(input("Anahtarı giriniz : "))
n = int(input("Kaç parçalı olacağını giriniz : "))
l = int(input("Şifreleme uzunluğunu giriniz : "))

data = open("input.txt", "r+")
newdata = open("crypted_thread_18_8_48.txt", "a")

codeList = divert(data, l)

queueLock = threading.Lock()
workQueue = queue.Queue()
threads = []
threadID = 1

for _ in range(n):
    thread = Thread(threadID, str(_), workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

queueLock.acquire()
for word in codeList:
    workQueue.put(word)
queueLock.release()

while not workQueue.empty():
    pass

for _ in range(n):
    workQueue.put("Quit")

for t in threads:
    t.join()
newdata.close()
print("exit")
