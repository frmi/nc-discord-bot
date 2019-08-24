import os
import discord

print('Bot is starting')

TOKEN = os.environ['BOT_TOKEN']

client = discord.Client()

validRoles = {'buddies', 'officer', 'nc aalborg', 'nc andet kontor'}

def nonBuddie(member):
    return member.display_name + ' (joined ' + member.joined_at.strftime("%d-%m-%Y %H:%M:%S") + ")"

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
                continue

            buddies_found = False
            for role in member.roles:
                if role.name.lower() in validRoles:
                    buddies_found = True
                    break

            if not buddies_found:
                non_buddies.append(nonBuddie(member))
                non_buddies.sort()

        msg = 'Members found who does not have the \'Buddies\' role:\n'
        if len(non_buddies) > 0:
            msg += '\n**Non-buddies**\n```'
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