import asyncio
import datetime

import discord
from discord.ext import tasks
from yt_dlp import YoutubeDL

import breadcord

NEW_BIRD = "https://www.youtube.com/watch?v=0LwcvjNJTuM"


class NewBird(breadcord.module.ModuleCog):
    def __init__(self, module_id: str):
        super().__init__(module_id)
        self.channel_id = int(self.settings.channel_id.value)
        self.song_path = self.module.storage_path / "free_bird.mp3"

        self.new_years_bird.start()

    async def cog_load(self) -> None:
        if self.song_path.is_file():
            return

        with YoutubeDL(dict(
            format="bestaudio/best",
            outtmpl=(self.module.storage_path / "free_bird.%(ext)s").as_posix(),
            postprocessors=[{
                "key": "FFmpegExtractAudio",
                "preferredcodec": self.song_path.suffix[1:],
            }],
        )) as ydl:
            ydl.download([NEW_BIRD])

    # Run at 23:55:05 local time every day
    @tasks.loop(seconds=1)
    async def new_years_bird(self) -> None:
        # Check if it's new years eve
        now = datetime.datetime.now()
        if not (now.month == 12 and now.day == 31):
            return
        # Check if it's 23:55:05
        if now.time() < datetime.time(hour=23, minute=55, second=5):
            return

        channel: discord.VoiceChannel = self.bot.get_channel(self.channel_id)
        if not isinstance(channel, discord.VoiceChannel):
            return

        voice = await channel.connect()
        audio = discord.FFmpegPCMAudio(self.song_path.as_posix())
        voice.play(audio)
        while voice.is_playing():
            await asyncio.sleep(1)
        await voice.disconnect()


async def setup(bot: breadcord.Bot, module: breadcord.module.Module) -> None:
    await bot.add_cog(NewBird(module.id))
