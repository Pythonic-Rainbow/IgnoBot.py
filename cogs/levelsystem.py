########################
#                      #
#     Level System     #
#                      #
########################

import os

import discord
from discord.ext import commands
import random
import psycopg2

mydb = None
cursor = None

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, ctx):
        dbopen()
        global mydb
        global cursor
        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        userid = ctx.author.id
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")

        # guild check and update
        cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute(f'select count(*) from guildinfo where guildid = {guildid};')
            result = cursor.fetchone()
            print(f'Guildid search result is: {result}')
            if result[0] != 0:
                cursor.execute(f"select count(*) from guildinfo where guildname = '{guildname}';")
                result = cursor.fetchone()
            elif result[0] == 0:
                cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid}, '{guildname}');")
                mydb.commit()
                if result[0] == 0:
                    cursor.execute(f"update guildinfo set guildname = '{guildname}' where guildid = {guildid};")
                    mydb.commit()
                    print(f'updated guild {guildid} with new name: {guildname}')
                else:
                    print(f'guild {guildid} with name {guildname} is already in the database')

        # user check and update
        cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute(f'select count(*) from leveling where userid = {userid};')
            result = cursor.fetchone()
            print(f'Guildid search result is: {result}')
            if result[0] != 0:
                cursor.execute(f"select count(*) from leveling where username = '{username}';")
                result = cursor.fetchone()
                if result[0] == 0:
                    cursor.execute(f"update leveling set username = '{username}' where userid = {userid};")
                    mydb.commit()
                    print(f'updated user {userid} with new name: {username}')
                else:
                    print(f'user {userid} with name {usernameraw} is already in the database')

        # search for user in the db
        cursor.execute(f'select count(*) from leveling where userid = {userid} and guildid = {guildid};')
        result = cursor.fetchone()
        print(f'userid exists = {result[0]}')

        if userid == 913424314290815007:            # user is a bot so no xp for him
            print(f'The user ({username}) is a bot! No xp for bots')
            dbclose()
            return

        if result[0] == 0:          # user is not in the db so we add him first and then give
            xptodb = 0
            leveltodb = 0
            cursor.execute(f"insert into leveling(guildid, userid, username, xpvalue, levelvalue) values({guildid}, {userid}, '{username}', 0, 0);")
            print(f'new user {username} added')
            mydb.commit()

        else:           # user is already in the the db so no changes to be made
            print(f'user {username} is already present in the db')

        # xp giving
        xprange = random.choice(range(1, 20+1))
        print(f'generated xp is = {xprange}')
        cursor.execute(f'select xpvalue from leveling where userid = {userid} and guildid = {guildid};')            # getting xp
        result = cursor.fetchone()
        print(f'result[0] is = {result[0]}')
        xpfromdb = result[0]
        print(f'xpfromdb is = {result[0]}')
        xptodb = xpfromdb + xprange
        print(f'xptodb is = {xptodb}')
        cursor.execute(f'select levelvalue from leveling where guildid = {guildid} and userid = {userid}')          # getting level
        result = cursor.fetchone()
        level = result[0]
        if level == 0:
            neededtolvl = 100
        else:
            neededtolvl = level * level * 100           # determines how much xp is needed to level up
        if xpfromdb >= neededtolvl:
            level+= 1
        cursor.execute(f'update leveling set xpvalue = {xptodb} where guildid = {guildid} and userid = {userid};')
        cursor.execute(f'update leveling set levelvalue = {level} where guildid = {guildid} and userid = {userid};')
        mydb.commit()
        dbclose()
        
    @commands.command(name = 'level', help = 'Shows your current level')
    async def level(self, ctx):
        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        userid = ctx.author.id
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")
        useravatar = ctx.author.avatar_url
        guildavatar = ctx.guild.avatar_url
        levelfromdb = cursor.execute(f'select from leveling(levelvalue) where userid = {userid} and guildid = {guildid};')
        xpfromdb = cursor.execute(f'select from leveling(xpvalue) where userid = {userid} and guildid = {guildid};')
        embed = discord.Embed(title = 'Level and XP for {}'.format(usernameraw) , url = '', description = '', color = discord.Colour.random)
        embed.add_field(name = "Text XP", value = xpfromdb, inline = True)
        embed.add_field(name = "Level", value = levelfromdb, inline = True)
        await ctx.send(embed)

# db open/close
def dbopen():
    global mydb
    global cursor
    try:
        mydb = psycopg2.connect(host = os.getenv('dbhost'), user = os.getenv('dbuser'), password = os.getenv('dbpw'), database = os.getenv('db_db'), port = os.getenv('dbport'))
        print("Connected to the database")
    except psycopg2.Error as e:
        print(f'Error connecting to the platform (mydb): {e}')

    # getting the cursor
    try:
        cursor = mydb.cursor()
    except psycopg2.Error as c:
        print(f'Error connecting to the platform (cursor): {c}')

def dbclose():
    global mydb
    global cursor
    try:
        cursor.close()
        mydb.close()
        print(f'Database closed')
    except psycopg2.Error as ce:
        print(f'Error while closing the database: {ce}')  


def setup(bot):
    bot.add_cog(LevelSystem(bot))