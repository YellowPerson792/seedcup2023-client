import json
import socket
from base import *
from req import *
from resp import *
from config import config
from ui import UI
import subprocess
from threading import Thread
from itertools import cycle
from time import sleep
from logger import logger

import sys

from anlz import Anlz

# record the context of global data
gContext = {
    "playerID": -1,
    "gameOverFlag": False,
    "prompt": (
        "Take actions!\n"
        "'w': move up\n"
        "'s': move down\n"
        "'a': move left\n"
        "'d': move right\n"
        "'blank': place bomb\n"
    ),
    "steps": ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"],
    "gameBeginFlag": False,
}


class Client(object):
    """Client obj that send/recv packet.
    """

    def __init__(self) -> None:
        self.config = config
        self.host = self.config.get("host")
        self.port = self.config.get("port")
        assert self.host and self.port, "host and port must be provided"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connected = False

    def connect(self):
        if self.socket.connect_ex((self.host, self.port)) == 0:
            logger.info(f"connect to {self.host}:{self.port}")
            self._connected = True
        else:
            logger.error(f"can not connect to {self.host}:{self.port}")
            sys.exit(-1)
        return

    def send(self, req: PacketReq):
        msg = json.dumps(req, cls=JsonEncoder).encode("utf-8")
        length = len(msg)
        self.socket.sendall(length.to_bytes(8, sys.byteorder) + msg)
        # uncomment this will show req packet
        # logger.info(f"send PacketReq, content: {msg}")
        return

    def recv(self):
        length = int.from_bytes(self.socket.recv(8), sys.byteorder)
        result = b""
        while resp := self.socket.recv(length):
            result += resp
            length -= len(resp)
            if length <= 0:
                break

        # uncomment this will show resp packet
        # logger.info(f"recv PacketResp, content: {result}")
        packet = PacketResp().from_json(result)
        return packet

    def __enter__(self):
        return self
    
    def close(self):
        logger.info("closing socket")
        self.socket.close()
        logger.info("socket closed successfully")
        self._connected = False
    
    @property
    def connected(self):
        return self._connected

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        if traceback:
            print(traceback)
            return False
        return True


def cliGetInitReq():
    """Get init request from user input."""
    return InitReq("2D26RnbFrssB0yGZ7mFz3Q==")


def recvAndRefresh(ui: UI, client: Client, anlz: Anlz):
    """Recv packet and refresh ui."""
    global gContext
    resp = client.recv()

    if resp.type == PacketType.ActionResp:
        gContext["gameBeginFlag"] = True
        gContext["playerID"] = resp.data.player_id
        ui.player_id = gContext["playerID"]

    while resp.type != PacketType.GameOver:
        subprocess.run(["clear"])        
        ui.refresh(resp.data)
        ui.display()
        anlz.codebox(resp.data) 
           
        actions = anlz.action_req_send() 
        _actions = []
        for action in actions:
            _actions.append(ActionReq(gContext["playerID"], action))
   
        actionPacket = PacketReq(PacketType.ActionReq, _actions)
        client.send(actionPacket)
        
        resp = client.recv()

    print(f"Game Over!")

    print(f"Final scores \33[1m{resp.data.scores}\33[0m")

    if gContext["playerID"] in resp.data.winner_ids:
        print("\33[1mCongratulations! You win! \33[0m")
    else:
        print(
            "\33[1mThe goddess of victory is not on your side this time, but there is still a chance next time!\33[0m"
        )

    gContext["gameOverFlag"] = True
    print("press any key to quit")



key2ActionReq = {
    'w': ActionType.MOVE_UP,
    's': ActionType.MOVE_DOWN,
    'a': ActionType.MOVE_LEFT,
    'd': ActionType.MOVE_RIGHT,
    ' ': ActionType.PLACED,
}

def termPlayAPI():
    ui = UI()
    anlz = Anlz()
    
    with Client() as client:
        client.connect()    
        
        initPacket = PacketReq(PacketType.InitReq, cliGetInitReq())
        client.send(initPacket)
        
        # IO thread to display UI
        t = Thread(target=recvAndRefresh, args=(ui, client, anlz))
        t.start()
        
        print(gContext["prompt"])
        for c in cycle(gContext["steps"]):
            if gContext["gameBeginFlag"]:
                break
            print(
                f"\r\033[0;32m{c}\033[0m \33[1mWaiting for the other player to connect...\033[0m",
                flush=True,
                end="",
            )
            sleep(0.1)

        
        while not gContext["gameOverFlag"]:
            # old_settings = termios.tcgetattr(sys.stdin)
            # tty.setcbreak(sys.stdin.fileno())
            # key = sys.stdin.read(1)
            # termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            
            # if key in key2ActionReq.keys():
            #     action = ActionReq(gContext["playerID"], key2ActionReq[key])
            # else:
            #     action = ActionReq(gContext["playerID"], ActionType.SILENT)         
            
            # print(anlz.action_req_send())           
            # action = ActionReq(gContext["playerID"], anlz.action_req_send())
            
            # subprocess.run(["clear"]) 
            # resp = client.recv()
            
            # anlz.codetest(resp.data)
            
            # print(anlz.action_req_send())           
            # action = ActionReq(gContext["playerID"], anlz.action_req_send())
   
            # actionPacket = PacketReq(PacketType.ActionReq, action)
            # client.send(actionPacket)
            
            

            if gContext["gameOverFlag"]:
                break
            
            # actionPacket = PacketReq(PacketType.ActionReq, action)
            # client.send(actionPacket)
            # sleep(0.5)
            
  

if __name__ == "__main__":
    
    termPlayAPI()
