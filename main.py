from discord import Intents, Client, Color, utils, FFmpegPCMAudio, Embed, Game
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv, remove
from pytube import YouTube, Playlist, StreamQuery, Search
from pytube.exceptions import PytubeError
from datetime import timedelta
from queue import Queue
import asyncio
import time

load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")

intents = Intents().all()
client = Client(intents=intents)
bot = commands.Bot(command_prefix="//", intents=intents)

bot.queue = Queue()

@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name="ME VOY A TUMBAR EN LA CARRETERA"))
    
    
@bot.command(name="join", help="Tells the bot to join the voice channel")
async def join(ctx):
    channel = ctx.message.channel

    if not ctx.message.author.voice:
        await send_embed(channel, description="You did not join a voice channel", color=Color.red())
        return False
    
    channel = ctx.message.author.voice.channel
    voice_client = utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    
    if voice_client and voice_client.is_connected():
        return voice_client
    
    try:
        return await channel.connect()
    except:
        return voice_client


@bot.command(name="play", help="Tells the bot to play a Youtube video")
async def play(ctx, url):
    channel = ctx.message.channel
    yt = None

    try:
        yt = YouTube(url=url)
        streams = yt.streams
    except PytubeError:
        await send_embed(channel, description="Invalid URL", color=Color.red())
        return
    
    await download_youtube_audio(ctx, channel, yt)
        
        
@bot.command(name="search", help="Searches a video in YouTube")
async def search(ctx):
    name = ctx.message.content.replace("//search ", "").replace("//search", "")
    channel = ctx.message.channel
    
    if not name:
        await send_embed(channel, description="Introduce a name", color=Color.red())
        return
    
    search = Search(name)
    yt = search.results[0]
    
    await download_youtube_audio(ctx, channel, yt)
    
    
async def download_youtube_audio(ctx, channel, yt):
    streams = yt.streams
    url = yt.watch_url
    
    audio = streams.get_audio_only(subtype="webm")
    video_name = audio.title
    
    voice_client = await join(ctx)
    
    if not voice_client:
        return
            
    audio_name = audio.download()
    
    #if audio_name in bot.queue:
    #    await send_embed(channel, description="The song is already in queue", color=Color.red())
    #    return
    
    #bot.queue.put(audio_name)
    
    youtube_dict = {
        "url": url,
        "video_name": video_name,
        "length": yt.length,
        "voice_client": voice_client,
        "channel": channel
    }
    
    bot.queue.put(youtube_dict)
    
    if voice_client.is_playing():
        await send_embed(channel, description=f"Added song to the queue: **{video_name}**",
                            title="YouTube", url=url, color=Color.green())
        
        return
    
    #await play_queue(bot.queue.get())
    await play_queue("No error")

@bot.command(name="stop", help="Stops the song")
async def stop(ctx):
    voice_client = utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.channel
    
    #if not voice_client or voice_client.is_paused():
    if not voice_client:
        channel = ctx.message.channel
        await send_embed(channel, description="The bot is not playing anything", color=Color.red())
        return
    
    voice_client.stop()
    await send_embed(channel, description="The bot has stopped", color=Color.blue())
        
        
@bot.command(name="pause", help="This command pauses the song")
async def pause(ctx):
    voice_client = utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.channel
    
    if not voice_client:
        await send_embed(channel, description="The bot is not playing anything", color=Color.red())
        return
    elif voice_client.is_paused():
        await send_embed(channel, description="The bot is already paused", color=Color.red())
        return
    
    voice_client.pause()
    await send_embed(channel, description="The bot has paused. Use **//resume** to start playing again", color=Color.blue())
        
        
@bot.command(name="resume", help="Resumes the song")
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    channel = ctx.message.channel
    
    if not voice_client:
        await send_embed(channel, description="The bot is not in a voice channel", color=Color.red())
        return
    elif voice_client and voice_client.is_playing():
        await send_embed(channel, description="The bot is already playing a song", color=Color.red())
        return
    
    voice_client.resume()
       
       
async def play_queue(e):
    if bot.queue.empty():
        return
    
    dict_audio_to_play = bot.queue.get()
    voice_client = dict_audio_to_play["voice_client"]
    video_name = dict_audio_to_play["video_name"]
    length = str(timedelta(seconds=dict_audio_to_play["length"]))
    
    #await send_embed(dict_audio_to_play["channel"], description=f"Playing song **{video_name}** ({length})",
    #                     title="YouTube", url=dict_audio_to_play["url"], color=Color.blue())
    
    voice_client.play(FFmpegPCMAudio(executable="ffmpeg.exe", source=f"{video_name}.webm"), after=play_queue_again)
    
def play_queue_again(e):
    asyncio.run(play_queue(e))
    
async def send_embed(channel, **kwargs):
    description = kwargs.get("description", None)
    title = kwargs.get("title", None)
    url = kwargs.get("url", None)
    color = kwargs.get("color", None)
    
    embed = Embed(
        title=title,
        url=url,
        description=description,
        color=color)
    
    await channel.send(embed=embed)
    
    
@bot.command(name="queue", help="Displays the queue")
async def show_queue(ctx):
    channel = ctx.message.channel
    
    size = bot.queue.qsize()
    iter_size = 0
    
    while not bot.queue.empty():
        item = bot.queue.get()
        print(item)
        bot.queue.put(item)
        
        iter_size += 1
        
        if iter_size == size:
            break
        
    
    
bot.run(TOKEN)
