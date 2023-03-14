import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv, remove
from pytube import YouTube, StreamQuery
from pytube.exceptions import PytubeError

load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")

intents=discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="//", intents=intents)

bot.queue = []

@bot.event
async def on_ready():
    ...
    #await ctx.send("Bot started")
    
    
@bot.command(name="join", help="Tells the bot to join the voice channel")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
        return
    
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
        
        audio_name = audio.download()
        
        if audio_name in bot.queue:
            embed = discord.Embed(
                    description="The song is already in queue",
                    color=discord.Color.red())
                
            await channel.send(embed=embed)
            return
        
        bot.queue.append(audio_name)
        
        if voice_client.is_playing():
            embed = discord.Embed(
                title="YouTube",
                url=url,
                description=f"Added song to the queue: **{video_name}**",
                color=discord.Color.green())
            
            await channel.send(embed=embed)
            return
        
        await play_queue(url, video_name, voice_client, channel)
        #remove(audio_to_play)
            
        #embed = discord.Embed(
        #    description="The queue has been cleared",
        #    color=discord.Color.green())
        
        #await channel.send(embed=embed)
    except PytubeError:
        embed = discord.Embed(
            description="Invalid URL",
            color=discord.Color.red())
        
        await channel.send(embed=embed)
        

@bot.command(name="stop", help="Stops the song")
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        channel = ctx.message.channel
        
        embed = discord.Embed(
            description="The bot is not playing anything",
            color=discord.Color.red())
        
        await channel.send(embed=embed)


async def play_queue(url, video_name, voice_client, channel):
    audio_to_play = bot.queue[0]
            
    embed = discord.Embed(
        title="YouTube",
        url=url,
        description=f"Playing song **{video_name}**",
        color=discord.Color.blue())
    
    await channel.send(embed=embed)
    
    voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=audio_to_play))
    #remove(audio_to_play)
    
    bot.queue.remove(audio_to_play)
    
    if bot.queue:
        bot.queue = bot.queue
        play_queue(url, video_name, voice_client, channel)
    
    
bot.run(TOKEN)
