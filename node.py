import sys
import time
from BullyNode import BullyNode
from BullyAlgo import *
import os

N=6  # Manually setting no of nodes
id = sys.argv[1]
print('Node '+id)
node = BullyNode("127.0.0.1", 8000+int(id), id = id, connections = N)
node.start()
time.sleep(5)

for i in range(N):
    if i != id:
        node.connect_with_node('127.0.0.1', 8000+i)

while True:
    print()
    print()
    print("1) Start Leader Election \n2) Check Prev leader\n3) Terminate Master\n4) Broadcast \n5) Print all nodes \n6) Check Keys")
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
        pk = open("pk"+str(node.id)+".pem","wb")
        pk.write(node.keys["public_key"])
        pk.close()
    # Broadcasting public keys to all other nodes connected with us
        key_msg = {"event":"Public Key Broadcast","message":open("pk"+str(node.id)+".pem").read()}
        node.send_to_nodes(key_msg)
        os.remove("pk"+str(node.id)+".pem")
    if choice==5:
        print(node.all_nodes)
    if choice==6:
        print("Connected Keys:")
        print(node.connected_keys)