import discord
from discord.ext import commands

import random as rand
from PIL import Image
import requests
from io import BytesIO

from utils.config import Config
from utils.image import Picture
from strings import *


def from_str_to_bool(st):
    st = st.lower()
    if st in ['false', '0']:
        return False
    elif st in ['true', '1']:
        return True
    else:
        return


def decod(token):
    return token[::-1]


class Bot(commands.Bot):
    def __init__(self):
        self.prefix = 'b'
        self.name = 'ABot'
        self.config = Config()
        self.debug = self.config.getConfigVar('debug')
        self.token = decod(self.config.getConfigVar('token'))
        super().__init__(command_prefix=f"{self.prefix} ", pm_help=False)

        self.msg_calc_module = self.config.getConfigVar('msg_calc_module')
        self.expression_limit = self.config.getConfigVar('expression_limit')
        self.link_banner_module = self.config.getConfigVar('link_banner_module')
        self.links_blacklist = self.config.getConfigVar('links_blacklist')
        self.image_module = self.config.getConfigVar('image_module')

    async def on_ready(self):
        print(bot_start % self.user)
        num = 0
        for guild in self.guilds:
            num += 1
            print(
                bot_ready % self.user,
                f'    {num}){guild.name}(ID: {guild.id})')

    async def on_member_join(self, member):
        print(member_join % (member, member.guild.name))

    async def on_member_remove(self, member):
        print(member_leave % (member, member.guild.name))


bot = Bot()
_DEBUG = bot.debug
bot.remove_command('help')


def msg_calc(message):
    result = ''
    answer = []
    nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    operations = ['x', '/', '+', '-', '*']
    count_nums = 0
    count_operations = 0
    calc = False
    expression = ''
    for i in (message + '.'):
        if calc:
            condition_nums = i in nums
            condition_operations = i in operations
            if not (condition_nums) and not (condition_operations) and i != ' ':
                count_nums = 0
                count_operations = 0
            elif condition_nums:
                count_nums += 1
                expression += i
            elif condition_operations:
                count_operations += 1
                if i == 'x':
                    expression += '*'
                else:
                    expression += i
        if i == '!':
            calc = True
        elif count_nums == 0 and count_operations == 0 and calc == True:
            calc = False
            line = f'# {expression} = {eval(expression)}'
            if len(line) <= bot.expression_limit:
                answer.append(line)
            else:
                answer.append(expression_limit_deny % bot.expression_limit)
                break
            expression = ''
    return answer


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return

    text = message.content

    if _DEBUG:
        print(text)

    # обработка команд
    if text.startswith(f'{bot.prefix} '):
        if text.split()[1] in bot.all_commands:
            await bot.process_commands(message)
        else:
            await message.channel.send(command_error)

    # модуль бота, который считает выражения в каждом сообщении
    if bot.msg_calc_module:
        answer = msg_calc(text)
        if len(answer) != 0:
            result = ''
            for i in answer:
                for j in i:
                    if j == '*':
                        result += 'x'
                    else:
                        result += j
                result += '\n'

            await message.channel.send(result)

    # модуль бота, удаляющий "левые" ссылки
    if bot.link_banner_module:
        if message.author.id != message.channel.guild.owner_id:
            # ссылки админа не удаляются
            for link in bot.links_blacklist:
                if link in text:
                    await message.delete()


####################
# КОМАНДЫ ДЛЯ ВСЕХ #
####################


@bot.command()
async def random(ctx, *, arg):
    arg = arg.split()
    arg1 = int(arg[0])
    try:
        arg2 = int(arg[1])
    except IndexError:
        arg2 = 1
    if arg2 < arg1:
        arg1, arg2 = arg2, arg1

    num = rand.randint(arg1, arg2)
    await ctx.send(command_random % (arg1, arg2, str(num)))


@bot.command()
async def random_user(ctx):
    users = ctx.guild.members
    num = rand.randint(0, len(users))
    z = -1
    for user in users:
        z += 1
        if z == num:
            break
    await ctx.send(f'<@!{user.id}>')


@bot.command()
async def image(ctx, *, arg):
    if not bot.image_module:
        return

    arg = arg.split()
    if len(ctx.message.attachments) == 0 and len(arg) <= 1:
        return

    try:
        picture_url = arg[1]
    except IndexError:
        picture_url = ctx.message.attachments[0].url
    mode = arg[0]
    channel = ctx.message.channel
    response = requests.get(picture_url)
    picture = Picture(Image.open(BytesIO(response.content)))
    if mode == 'blacknwhite':
        picture = picture.blacknwhite()
    elif mode == 'negative':
        picture = picture.negative()
    elif mode == 'mirror':
        picture = picture.mirror()
    elif mode == 'horror':
        picture = picture.horror()
    elif mode == 'aggressive':
        picture = picture.aggressive()
    elif mode == 'pixel':
        picture = picture.pixel()
    else:
        await channel.send(image_error)

    picture.save('pic.png')
    await channel.send(file=discord.File('pic.png'))


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        colour=discord.Colour.orange()
    )

    embed.set_author(name=bot.name)
    embed.add_field(name=f'{bot.prefix} random num1 num2',
                    value=help_random)
    embed.add_field(name=f'{bot.prefix} random_user',
                    value=help_random_user)
    if bot.image_module:
        embed.add_field(name=f'{bot.prefix} image mode',
                        value=help_image)
    if bot.msg_calc_module:
        embed.add_field(name='Message calculator',
                        value=help_msg_calc % bot.expression_limit)
    embed.add_field(name=f'{bot.prefix} help',
                    value=help_)

    await ctx.send(embed=embed)


#######################
# КОМАНДЫ ДЛЯ АДМИНОВ #
#######################


@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, *, arg=4):
    num = int(arg) + 1
    if num < 0:
        return
    await ctx.message.channel.purge(limit=num)


@bot.command()
@commands.has_permissions(administrator=True)
async def msg_calc_module(ctx, *, arg):
    arg = from_str_to_bool(arg)
    if arg is None:
        return

    bot.msg_calc_module = arg
    bot.config.setConfigVar('msg_calc_module', arg)
    await ctx.send(module_set % ('**Message calculator**', arg))


@bot.command()
@commands.has_permissions(administrator=True)
async def expression_limit(ctx, arg):
    if arg == '':
        return

    num = int(arg)
    bot.expression_lim = num
    bot.config.setConfigVar('expression_limit', num)


@bot.command()
@commands.has_permissions(administrator=True)
async def link_banner_module(ctx, *, arg):
    arg = from_str_to_bool(arg)
    if arg is None:
        return

    bot.link_banner_module = arg
    bot.config.setConfigVar('link_banner_module', arg)
    await ctx.send(module_set % ('**Link banner**', arg))


@bot.command()
@commands.has_permissions(administrator=True)
async def image_module(ctx, *, arg):
    arg = from_str_to_bool(arg)
    if arg is None:
        return

    bot.image_module = arg
    bot.config.setConfigVar('image_module', arg)
    await ctx.send(module_set % ('**Image**', arg))


@bot.command()
@commands.has_permissions(administrator=True)
async def help_admin(ctx):
    embed = discord.Embed(
        colour=discord.Colour.orange()
    )

    embed.set_author(name=f'{bot.name} admin')
    embed.add_field(name=f'{bot.prefix} clear num',
                    value=help_admin_clear)
    embed.add_field(name=f'{bot.prefix} link_banner_module bool',
                    value=help_admin_link_banner_module % bot.link_banner_module)
    embed.add_field(name=f'{bot.prefix} msg_calc_module bool',
                    value=help_admin_msg_calc_module % bot.msg_calc_module)
    embed.add_field(name=f'{bot.prefix} image_module bool',
                    value=help_admin_image_module % bot.image_module)
    embed.add_field(name=f'{bot.prefix} help_admin',
                    value=help_admin_)

    await ctx.send(embed=embed)


bot.run(bot.token)
