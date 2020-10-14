import sys

entries = []
class addEntry:
    def _init_(self, name, surname, age):
        self.name = name
        self.surname = surname
        self.age = age

N = int(input("kaç kisi"))
for i in range(N):
    input = input("bilgileri giriniz")
    entries.append(addEntry(input[0:input.find(" ")], input[input.find(" "):input.find(" ", input.find(" "))],
                            input[input.find(" ", input.find(" "))]))


if (len(sys.argv) <2):

    sys.exit ()

