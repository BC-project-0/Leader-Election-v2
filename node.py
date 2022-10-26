import sys
import time
from BullyNode import BullyNode
from BullyAlgo import *


N=6  # Manually setting no of nodes
id = sys.argv[1]
print('Node '+id)
node = BullyNode("127.0.0.1", 8000+int(id), id = id)
node.start()
time.sleep(5)

for i in range(N):
    if i != id:
        node.connect_with_node('127.0.0.1', 8000+i)


while True:
    print()
    print()
    print("1) Start Leader Election \n2) Check Prev leader\n3) Terminate Master\n4) Broadcast message\n5) Print all nodes")
    print()
    print()
    
    choice = int(input())
    if choice==1:
        temp = node.prevLeader
        init_leader_election(node)
    if choice==2:
        print("Prev Leader",end="")
        print(node.prevLeader)
    if choice==3:
        node.stop()
        break
    if choice==4:
        data = {"event":"Checking","message":("I am the Node "+str(id))}
        node.send_to_nodes(data)
    if choice==5:
        print(node.all_nodes)