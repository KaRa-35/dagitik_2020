from multiprocessing import Process, Queue, Lock, current_process
import sys

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


def divert(data, l):
    # bu fonksiyon dosyadan alınan verileri l sayıda karakter içeren parçalara böler

    parts = []
    part = []
    lines = data.readlines()
    for line in lines:
        a = 0
        while a < len(line):
            part.append(line[a])
            if len(part) == l:
                parts.append(part)
                part = []
            a += 1
    parts.append(part)
    return parts


def worker(work_queue, done_queue, s):
    # Bu fonsiyon verilen parçaları teker teker yeni dosyaya yazar
    code = ""
    for part in iter(work_queue.get, "STOP"):
        for x in part:
            code += cipher(x, s)
        done_queue.put(code)
        newdata = open("crypted_fork_14_6_40.txt", "a")
        newdata.write(code)
        code = ""
        newdata.close()
    return True


def main():
    s = int(input("Anahtarı giriniz : "))
    n = input("Kaç parçalı olacağını giriniz : ")
    l = int(input("Şifreleme uzunluğunu giriniz : "))

    data = open("input.txt", "r+")

    workers = int(n)
    work_queue = Queue()
    done_queue = Queue()
    processes = []

    for part in divert(data, l):
        work_queue.put(part)

    print(1)
    for w in range(workers):
        p = Process(target=worker, args=(work_queue, done_queue, s))
        p.start()
        processes.append(p)
        work_queue.put("STOP")
    done_queue.put("STOP")

if __name__ == "__main__":
    main()
    print("Şifreleme Bitti")

    #Program burda bitmiyor. Processler hala devam ettiği için. ve bi çözüm bulamadım.
