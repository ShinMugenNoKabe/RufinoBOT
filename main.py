import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv, remove
from pytube import YouTube, StreamQuery
from pytube.exceptions import PytubeError

load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="//", intents=intents)

bot.queue = []

@bot.event
async def on_ready():
    ...
    #await ctx.send("Bot started")
    
    
@bot.command(name="join", help="Tells the bot to join the voice channel")
async def join(ctx):
    channel = ctx.message.channel

    if not ctx.message.author.voice:
        await send_embed(channel, description="You did not join a voice channel", color=discord.Color.red())
        return False
    
    channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    
    if voice_client and voice_client.is_connected():
        return voice_client
    
    return await channel.connect()


@bot.command(name="play", help="Tells the bot to play a Youtube video")
async def play(ctx, url):
    channel = ctx.message.channel

    try:
        yt = YouTube(url=url)
        streams = yt.streams
        audio = streams.get_audio_only(subtype="webm")
        video_name = audio.title
        
        voice_client = await join(ctx)
        
        if not voice_client:
            return
                
        audio_name = audio.download()
        
        if audio_name in bot.queue:
            await send_embed(channel, description="The song is already in queue", color=discord.Color.red())
            return
        
        bot.queue.append(audio_name)
        
        if voice_client.is_playing():
            await send_embed(channel, description=f"Added song to the queue: **{video_name}**",
                             title="YouTube", url=url, color=discord.Color.green())
            
            return
        
        await play_queue(url, video_name, voice_client, channel)
        #remove(audio_to_play)
            
        #embed = discord.Embed(
        #    description="The queue has been cleared",
        #    color=discord.Color.green())
        
        #await channel.send(embed=embed)
    except PytubeError:
        await send_embed(channel, description="Invalid URL", color=discord.Color.red())
        

@bot.command(name="stop", help="Stops the song")
async def stop(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.channel
    
    #if not voice_client or voice_client.is_paused():
    if not voice_client:
        channel = ctx.message.channel
        await send_embed(channel, description="The bot is not playing anything", color=discord.Color.red())
        return
    
    voice_client.stop()
    await send_embed(channel, description="The bot has stopped", color=discord.Color.blue())
        
        
@bot.command(name="pause", help="This command pauses the song")
async def pause(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    channel = ctx.message.channel
    
    if not voice_client:
        await send_embed(channel, description="The bot is not playing anything", color=discord.Color.red())
        return
    elif voice_client.is_paused():
        await send_embed(channel, description="The bot is already paused", color=discord.Color.red())
        return
    
    voice_client.pause()
    await send_embed(channel, description="The bot has paused. Use **//resume** to start playing again", color=discord.Color.blue())
        
        
@bot.command(name="resume", help="Resumes the song")
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    channel = ctx.message.channel
    
    if not voice_client:
        await send_embed(channel, description="The bot is not in a voice channel", color=discord.Color.red())
        return
    elif voice_client and voice_client.is_playing():
        await send_embed(channel, description="The bot is already playing a song", color=discord.Color.red())
        return
    
    voice_client.resume()


async def play_queue(url, video_name, voice_client, channel):
    audio_to_play = bot.queue[0]
    
    await send_embed(channel, description=f"Playing song **{video_name}**",
                     title="YouTube", url=url, color=discord.Color.blue())
    
    voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=audio_to_play))
    #remove(audio_to_play)
    
    bot.queue.remove(audio_to_play)
    
    if bot.queue:
        bot.queue = bot.queue
        play_queue(url, video_name, voice_client, channel)
    
    
async def send_embed(channel, **kwargs):
    description = kwargs.get("description", None)
    title = kwargs.get("title", None)
    url = kwargs.get("url", None)
    color = kwargs.get("color", None)
    
    embed = discord.Embed(
        title=title,
        url=url,
        description=description,
        color=color)
    
    await channel.send(embed=embed)
    
bot.run(TOKEN)
