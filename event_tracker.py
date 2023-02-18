import websocket
import socket_based
import item_manager
import threading
import os
import sys
import re
import queue
from enum import Enum
from functools import total_ordering


class SpecialType(Enum):
    NONE = 0
    IONIZED = 1
    SPECTRAL = 2


class EventType(Enum):
    THEB = item_manager.get_channel("THEB_CHANNEL")
    GLOBAL = item_manager.get_channel("GLOBAL_CHANNEL")
    BEGINNER = item_manager.get_channel("BEGINNER_CHANNEL")
    DMZETEX = item_manager.get_channel("ZETEX_DM")
    TEST = item_manager.get_channel("TEST_CHANNEL")


@total_ordering
class Rarity(Enum):
    RARE = 1
    MASTER = 2
    SURREAL = 3
    MYTHIC = 4
    EXOTIC = 5
    TRANSCENDENT = 6
    ENIGMATIC = 7
    UNFATHOMABLE = 8
    ZENITH = 9
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    

class OreEvent:
    
    def __init__(self, event):
        self.__embed = event['d']['embeds'][0]
        self.get_bases()
    
    def get_bases(self):
        title_groups = re.search(r"^\*\*(.+)\*\* has found(?: an? )?((?:spectral|ionized)?)\*\* (.+)\*\*", self.__embed['title'])
        
        self.username = title_groups.group(1)
        ore = f"{title_groups.group(2)} {title_groups.group(3)}"
        ore = ore.strip()
        self.ore = ore[0].upper() + ore[1:]
        
        self.rarity = None
        with open("color_names.json", "r") as f:
            color_names = item_manager.get_color_names()
            rarity_name = color_names[str(self.__embed['color'])]
            self.rarity = Rarity[rarity_name.upper()]
            
        match (title_groups.group(2)):
            case "ionized":
                self.special = SpecialType.IONIZED
            case "spectral":
                self.special = SpecialType.SPECTRAL
            case _:
                self.special = SpecialType.NONE
        
        self.base_rarity = int(self.__embed["fields"][0]["value"].replace('1/',''))
        
        self.blocks = int(self.__embed["fields"][1]["value"])
        
        self.pickaxe = self.__embed["fields"][2]["value"]
        
        self.event = self.__embed["fields"][3]["value"]  
    
    def get_username(self):
        return self.username
    
    def get_ore(self):
        return self.ore
    
    def get_tier(self):
        return f"**{self.rarity.name.title()}** {('(' + self.special.name.title() + ')') if self.special != SpecialType.NONE else ''} {'@everyone' if self.should_ping_everyone() else ''}"

    def should_ping_everyone(self):
        return self.rarity.value + self.special.value >= 8

    def get_base_rarity(self):
        return "1 in " + '{:,}'.format(self.base_rarity)

    def get_blocks(self):
        return '{:,}'.format(self.blocks)
        
    def get_pickaxe(self):
        return self.pickaxe
        
    def get_event(self):
        return self.event
    
    def get_event_types(self) -> list[EventType]:
        out = []
        if self.blocks < 100000:
            print("Beginner: " + self.username)
            out.append(EventType.BEGINNER)
        if self.should_ping_everyone():
            out.append(EventType.GLOBAL)
        if self.username == "winter_visage":
            print("DM: " + self.username)
            self.username = "winter_visage (<@797942648932794398> THEY FOUND SOMETHING)"
            out.append(EventType.DMZETEX)
        elif self.username in item_manager.get_theb_dict().keys():
            print("THEB: " + self.username)
            name = item_manager.get_username(self.username)
            self.username = f"{self.username} {'(' + name + ')' if name is not None else ''}"
            out.append(EventType.THEB)
        return out
    
    def format(self, type: EventType):
        try:
            username = self.get_username()
            ore = self.get_ore()
            tier = self.get_tier()
            rarity = self.get_base_rarity()
            blocks = self.get_blocks()
            pickaxe = self.get_pickaxe()
            event = self.get_event()
            
            tracker_name = ""
            match type:
                case EventType.THEB:
                    tracker_name = "THEB"
                case EventType.GLOBAL:
                    tracker_name = "GLOBAL"
                    tier.replace("@everyone", "")
                case EventType.BEGINNER:
                    tracker_name = ":beginner:"
                case EventType.DMZETEX:
                    tracker_name = "ZETEX PRIVATE"
                case EventType.TEST:
                    tracker_name = "TEST"
            return f"--------------------------------------------------\n**[{tracker_name} TRACKER]**\n**{username}** has found **{ore}**\nTier: {tier}\nBase Rarity: {rarity}\nBlocks: {blocks}\nPickaxe: {pickaxe}\nEvent: {event}\n--------------------------------------------------"
        except Exception as e:
            print(e)
        
        
class EventTracker(socket_based.SocketBased):
    
    def __init__(self, socket: websocket.WebSocket):
        super().__init__(socket)
        self.queue = queue.LifoQueue()
        self.tracks = 0
    
    def start(self):
        token = item_manager.get_auth_token()
        payload = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": 'pc'
                }
            }
        }
        self.send_json_request(payload)
        
        self.main_thread = threading.Thread(target=EventTracker.loop, args=(self,))
        self.main_thread.start()
    
    def loop(self):
        while True:
            try:
                event = self.receive_json_response()
            except Exception as err:
                # SHITTY FIX ALERT
                print(err)
                os.execl(sys.executable, 'python', "main.py")
            try:
                if int(event['d']['author']['id']) in item_manager.get_tracker_bots():
                    self.handle_event(event)
                op_code = event('op')
                if op_code == 11:
                    print('heartbeat received')
            except:
                pass

    def handle_event(self, event_data):
        self.queue.put(OreEvent(event_data))