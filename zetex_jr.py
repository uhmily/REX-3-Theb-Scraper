import discord
from discord.ext import tasks
import websocket
import os

import heartbeat
import event_tracker


class ZetexJr(discord.Bot):
    
    async def on_ready(self):
        print("Zetex Jr ready for action!")
        await self.get_channels()
        await self.start_tracking()
    
    async def get_channels(self):
        self.test_channel = self.get_channel(1075585315483439166)
    
    async def start_tracking(self):
        ws = websocket.WebSocket()
        self.hb = heartbeat.HeartBeat(ws)
        self.et = event_tracker.EventTracker(ws)
        
        self.hb.start()
        self.et.start()
        self.send_event.start()

    @tasks.loop(seconds=1.0)
    async def send_event(self):
        if self.et.queue.qsize() != 0:
            event = self.et.queue.get()
            for type in event.get_event_types():
                self.et.tracks += 1
                await self.get_channel(type.value).send(event.format(type) + f"\nTracks Without Incident: {self.et.tracks}")
                
zetex_jr = ZetexJr(command_prefix="$")

@zetex_jr.command()
async def hefuckingdied(ctx):
    ctx.send("Restarting!")
    os.system("/root/restart.sh")