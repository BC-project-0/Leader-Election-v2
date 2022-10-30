from p2pnetwork.node import Node
import threading
import time
from BullyAlgo import *
#making changes

class BullyNode(Node):
    
    def __init__(self, host, port, id=None, callback=None, max_connections=0, connections = 0):
        super(BullyNode, self).__init__(host, port, id, callback, max_connections)
        self.connections = connections
        self.probability = 50 - ((int(id)*8.1) % 50)

    
    electionProcess = False # used to identity whether current node is contesting for leader or not
    votes = 0
    stop_leaderElection = threading.Event()

    leader = None
    prevLeader = None
    published = False
    
    def node_message(self, node, data):
        if data['event'] == "Checking":
            print(data)
        
        if self.leader == None:
            if node.id > self.id and  data['event'] == "Leader Election"  and data['message']=="I want to be the leader" :
                print("Higher node "+str(node.id)+" to be leader") #debug
                self.stop_leaderElection.set()

            if data['event'] == "Leader Election"  and data['message']=="I want to be the leader" :
                if self.electionProcess == False:
                    self.electionProcess = True
                    x = threading.Thread(target = leader_election,args=(self,node,data,))
                    x.start()
            

        # Once leader is set then other nodes's response are invalid
        if data['event'] == "Leader Elected" and data['message'] == "I am leader" :
            print("From "+str(node.id)+" : It is the leader")
            self.prevLeader = node
            self.leader = node
            self.votes = 0

        #heartbeat message printing
        if data["event"] == "Heartbeat":
            print(data["message"])

        # After block is published .. New message is sent to reset leader
        if data['event'] =="Block Published":
            print("Block Published by Leader")
            self.leader = None
            self.stop_leaderElection.clear()
            self.published = False

    def node_disconnect_with_outbound_node(self,node):
        print("Diconnecting from ->",node)
