from p2pnetwork.node import Node
import threading
import time
from BullyAlgo import *
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64
import os

class BullyNode(Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0, connections=0):
        super(BullyNode, self).__init__(
            host, port, id, callback, max_connections)
        self.connections = connections
        self.probability = 50 - ((int(id)*8.1) % 50)

        # key pair generation
        key = RSA.generate(1024) # keys[0] = pub key , keys[1] = pvt key
        self.keys = {"public_key":key.publickey().export_key(),"private_key":key.export_key()}
        self.connected_keys = {}


    # used to identity whether current node is contesting for leader or not
    electionProcess = False
    votes = 0
    stop_leaderElection = threading.Event()

    leader = None
    prevLeader = None
    published = False

    def node_message(self, node, data):
        def decrypt(self,data):
            data = base64.b64decode(bytes(data, 'utf8'))
            private_key = self.keys['private_key']    

            file_temp = open("temp.bin",'wb');
            file_temp.write(data)
            file_temp.close()

            file_temp = open("temp.bin","rb")

            priKey  = RSA.import_key(private_key)
            enc_session_key, nonce, tag, ciphertext = [ file_temp.read(x) for x in (priKey.size_in_bytes(), 16, 16, -1) ]

            cipher_rsa = PKCS1_OAEP.new(priKey)
            session_key = cipher_rsa.decrypt(enc_session_key)

            cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
            plain_text = cipher_aes.decrypt_and_verify(ciphertext, tag)
            file_temp.close()
            
            return plain_text.decode("utf-8")

        
        if self.leader == None:
            if node.id > self.id and data['event'] == "Leader Election" and decrypt(self,data['message']) == "I want to be the leader":
                print("Higher node "+str(node.id)+" to be leader")  # debug
                self.stop_leaderElection.set()

            if data['event'] == "Leader Election" and decrypt(self,data['message']) == "I want to be the leader":
                if self.electionProcess == False:
                    self.electionProcess = True
                    x = threading.Thread(
                        target=leader_election, args=(self, node, data,))
                    x.start()

        if data['event']=="Key Exchange Request":
            self.connected_keys[node.id] = (RSA.import_key(data["message"]))
            
            pk = open("pk"+str(self.id)+".pem","wb")
            pk.write(self.keys["public_key"])
            pk.close()
    # Broadcasting public keys to all other nodes connected with us
            key_msg = {"event":"Key Exchange Reply","message":open("pk"+str(self.id)+".pem").read()}
            self.send_to_node(node,key_msg)
            os.remove("pk"+str(self.id)+".pem")

        if data['event']=="Key Exchange Reply":
            self.connected_keys[node.id] = (RSA.import_key(data["message"]))
            return

        # Once leader is set then other nodes's response are invalid
        if data['event'] == "Leader Elected" and decrypt(self,data['message']) == "I am leader":
            print("From "+str(node.id)+" : It is the leader")
            self.prevLeader = node
            self.leader = node
            self.votes = 0
            return

        # heartbeat message printing
        if data["event"] == "Heartbeat":
            print(decrypt(self,data["message"]))
            return

        # After block is published .. New message is sent to reset leader
        if data['event'] == "Block Published":
            print("Block Published by Leader")
            self.leader = None
            self.stop_leaderElection.clear()
            self.published = False
            return

    def node_disconnect_with_outbound_node(self, node):
        print("Diconnecting from ->", node)
        return

    def send_encrypted_msg(self,event,msg):  # note to nitheesh decryption encryption works cant send bytes thru sockets as of now and sending ciphertext made with resp                                 # pub keys also works
        for node in self.all_nodes:
            session_key = get_random_bytes(16)
            pk = self.connected_keys[node.id]
            cipher_rsa = PKCS1_OAEP.new(pk)
            enc_session_key = cipher_rsa.encrypt(session_key)
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(msg.encode("utf-8"))

            file_out = open("encrypted_data.bin", "wb")
            [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
            file_out.close()

            txt = open("encrypted_data.bin","rb").read()
            # Convterting to string using base64
            b64_txt = str(base64.b64encode(txt), 'utf8')
            data = {"event":event,"message":b64_txt}
            self.send_to_node(node,data)
            # print("sent")
        return