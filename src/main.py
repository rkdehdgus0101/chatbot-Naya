import os
import asyncio
import discord, openai
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import CommandNotFound



discord_bot_key = os.getenv('DISCORD_BOT_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), help_command=None)

embed_color = 0x976bff
delete_after_time = 15
user_messages = {}


# OpenAI API
async def openai_api(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content


# Bot Ready
@bot.event
async def on_ready():
    print(str(bot.user.name) + '(' + str(bot.user.id) + ')')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="노래"))
    await bot.tree.sync()
    print('준비 완료!')


# on_message
@bot.event
async def on_message(message):
    if not message.guild or message.author.id == bot.user.id:
        return
    
    await bot.process_commands(message)


# on_command_error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


# Ping
@bot.tree.command(name="ping", description='현재 핑을 알려줘요♥️')
async def ping(interaction: discord.Interaction):
    await asyncio.sleep(2)
    embed = discord.Embed(description=str(
        bot.latency*1000) + 'ms', color=embed_color)
    await interaction.response.send_message(embed=embed, delete_after=delete_after_time)
    print('ping')


# Chat
@bot.tree.command(name='chat', description='나야와 채팅을 할 수 있습니다!')
@app_commands.describe(텍스트='나야에게 하고싶은 말을 적어주세요!')
async def chat(interaction: discord.Interaction, 텍스트: str = ""):
    if 텍스트 == "":
        embed = discord.Embed(description='text를 넣어주세요!', color=embed_color)
        await interaction.response.send_message(embed=embed, delete_after=delete_after_time)
    else:
        await interaction.response.defer()

        try:
            author_id = str(interaction.user.id)

            if author_id not in user_messages:
                user_messages[author_id] = [
                    {"role": "system",
                        "content": "You are a helpful assistant. your name is Naya"},
                ]

            user_messages[author_id].append({"role": "user", "content": 텍스트})
            assistant_response = await openai_api(user_messages[author_id])
            user_messages[author_id].append(
                {"role": "assistant", "content": assistant_response})

            embed = discord.Embed(description='**' + str(interaction.user.name) +
                                  '**: ' + 텍스트 + '\n\n**Naya**: '+str(assistant_response), color=embed_color)
            message = await interaction.followup.send(embed=embed)

            # 일정 시간 후 메시지 삭제
            await asyncio.sleep(delete_after_time * 10)
            await message.delete()
        except Exception as e:
            error_message = str(e)
            embed = discord.Embed(description='error: ' + error_message, color=embed_color)
            message = await interaction.followup.send(embed=embed)

            # 일정 시간 후 메시지 삭제
            await asyncio.sleep(delete_after_time * 10)
            await message.delete()


# reset
@bot.tree.command(name='reset', description='나야와 했던 채팅 기록을 삭제합니다!')
async def reset(interaction: discord.Interaction):
    author_id = str(interaction.user.id)
    if author_id in user_messages:
        del user_messages[author_id]
        embed = discord.Embed(
            description='대화 기록이 초기화되었습니다.', color=embed_color)
        await interaction.response.send_message(embed=embed, delete_after=delete_after_time)
    else:
        embed = discord.Embed(description='대화 기록이 없습니다.', color=embed_color)
        await interaction.response.send_message(embed=embed, delete_after=delete_after_time)


# chatlog
@bot.tree.command(name='chatlog', description='나야와 했던 채팅 기록을 보여줍니다!')
async def chatlog(interaction: discord.Interaction):
    author_id = str(interaction.user.id)
    if author_id in user_messages:
        text = ''
        for i in user_messages[author_id]:
            if i['role'] == 'user':
                text = text + '**' + interaction.user.name + \
                    '**: ' + i['content'] + '\n'
            elif i['role'] == 'assistant':
                text = text + '**Naya**: ' + \
                    i['content'] + '\n――――――――――――――――――――――――――――\n'
        embed = discord.Embed(description=text, color=embed_color)
        await interaction.response.send_message(embed=embed, delete_after=delete_after_time*10)
    else:
        embed = discord.Embed(description='대화 기록이 없어요!', color=embed_color)
        await interaction.response.send_message(embed=embed, delete_after=delete_after_time)






bot.run(discord_bot_key)