import random
import time
from threading import Thread

flag = False

# An event triggers the init_leader_election
def init_leader_election(currNode):
    print()
    print("I want to be the leader")
    if currNode.leader == None and currNode.prevLeader!=currNode:   # Making sure same node is not leader
        data = {"event":"Leader Election","message":"I want to be the leader"}
        currNode.send_to_nodes(data)
    time.sleep(15)  # waits for 60 seconds for replies

    # If some higher node wants to be leader then stop_leaderElection is set to True
    if not currNode.stop_leaderElection.is_set():
        if currNode.votes >= 1: # might be removed 
            # Majority voted yes
            
            data = {"event":"Leader Elected","message":"I am leader"}
            currNode.send_to_nodes(data)      
            print("I am the leader")

            # proceed to publish the block
            x = Thread(target=publish_block,args=(currNode,))
            y = Thread(target=heartbeat,args= (currNode,))
            x.start()
            y.start()

    # Clean up Code
    currNode.stop_leaderElection.clear()
    currNode.votes =0    
    currNode.leader = None    
    currNode.electionProcess = False

# to choose whether the current node standing for leader should be elected or not
def leader_election(currNode,senderNode,data):
    wantToBeLeader =  bool(random.choice([True, False])) 
    if senderNode.id < currNode.id :
        if wantToBeLeader == True:
            init_leader_election(currNode)
            currNode.electionProcess = False
    
    if wantToBeLeader == False:
        decide_senderNode_leader(currNode,senderNode,data)
        currNode.electionProcess = False
    

def decide_senderNode_leader(currNode,senderNode,data):    
    choice =   bool(random.choice([True, False]))
    if choice == True:
        data = {"event":"Leader Election","message":("Accept "+str(senderNode.id))}
        currNode.send_to_nodes(data)


def heartbeat(currNode):
    while not currNode.published:
        print("heartbeat testing ...")
        data = {"event":"Heartbeat","message":"Heartbeat from leader"}
        currNode.send_to_nodes(data)
        time.sleep(3)

def publish_block(currNode):
    time.sleep(15)
    data = {"event":"Block Published","message":""}
    currNode.send_to_nodes(data)
    currNode.published = True