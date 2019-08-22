import os
import discord

print('Bot is starting')

TOKEN = os.environ['BOT_TOKEN']

client = discord.Client()

validRoles = {'buddie', 'officer', 'nc aalborg', 'nc andet kontor'}

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if not message.content.startswith('!'):
        return

    channel = message.channel
    print('Reading message from server "' + channel.guild.name + '". Content="' + message.content + '" from author "' + message.author.name + '"')

    if channel.name != 'person-vouching':
        return

    msg = ''
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)

    if message.content.startswith('!nobuddies'):
        members = channel.guild.members
        non_buddies = list()
        for member in members:
            if member.bot:
                break

            buddies_found = False
            for role in member.roles:
                if role.name.lower() in validRoles:
                    buddies_found = True
                    break

            if not buddies_found:
                non_buddies.append(member.display_name)

        msg = 'Members found who does not have the \'Buddie\' role:\n```'
        if len(non_buddies) > 0:
            msg += '\n'.join(non_buddies)
        else:
            msg += 'All members are buddies'

        msg += '```'

    if msg == '':
        return

    await channel.send(msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)