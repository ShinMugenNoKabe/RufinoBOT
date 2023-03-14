import discord
from dotenv import load_dotenv
from os import getenv
from pytube import YouTube, StreamQuery
from pytube.exceptions import PytubeError
from time import sleep

load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents().all())

@client.event
async def on_ready():
    print("Bot has connected")


@client.event
async def on_message(message):
    # Prevent sending messages if the sender is another bot
    if message.author.bot:
        return

    # Prevent infinite recursion
    # if message.author.id == client.user.id:
    #    return
    
    queue = []

    voice_channel_id = message.author.voice.channel.id
    content = message.content
    
    if not content:
        return # TODO: Cambiar a r!play
    
    try:
        yt = YouTube(url=content)
        streams = yt.streams
        audio = streams.get_audio_only(subtype="webm")
        
        #queue.append(audio)
        
        #play_queue(queue)
        
        voice_channel = client.get_channel(voice_channel_id)
        
        voice_client = None
        
        audio_name = audio.download()
        
        if not voice_client or not voice_client.is_connected():
            voice_client = await voice_channel.connect()
            
        voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=audio_name))
    except PytubeError:
        print("Invalid link")


client.run(TOKEN)