import sys

f = open("airlines.txt")
List = []

for l in f:
    List.append(l)

Dict = {}
for l in List:
    splittedlines = l.strip().split(",")
    Dict[splittedlines[0]] = splittedlines[1:]


def find_connection(Dict, StartingPoint, FinalPoint, Connection=[]):
    Connection = Connection + [StartingPoint]
    if StartingPoint == FinalPoint:
        return Connection
    for node in Dict[StartingPoint]:
        if node not in Connection:
            newconnection = find_connection(Dict, node, FinalPoint, Connection)
            if newconnection:
                return newconnection


From = sys.argv[1]
To = sys.argv[2]
if find_connection(Dict, From, To) != None:
    print(find_connection(Dict, From, To))
else:
    print("no way")