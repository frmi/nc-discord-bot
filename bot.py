import math
import os
import discord
import urllib.request
from datetime import datetime

print('Bot is starting')

TOKEN = os.environ['BOT_TOKEN']

client = discord.Client()

validRoles = {'buddies', 'officer', 'nc aalborg', 'nc andet kontor'}


def nonBuddie(member):
    return member.display_name + ' (joined ' + member.joined_at.strftime("%d-%m-%Y %H:%M:%S") + ")"


def read_queue_data():
    page = urllib.request.urlopen('http://dump.hanbo.dk/firemawqueue.csv')
    data = list(reversed(page.read().decode('utf-8').split('\n')[1:-1]))
    sequence_tracker = -1
    result_candidate = list()
    latest_queue_time = None

    for row in data:
        time, number_of_players, sequence = row.split(',')
        sequence = int(sequence)
        number_of_players = int(number_of_players)
        if sequence_tracker == -1:
            if sequence == 0:
                if latest_queue_time is None:
                    latest_queue_time = datetime.strptime(time, "%Y%m%d-%H:%M:%S")
                    latest_queue_size = number_of_players
                continue
            else:
                sequence_tracker = sequence
                result_candidate.append(number_of_players)
                continue
        if sequence == sequence_tracker - 1:
            result_candidate.append(number_of_players)
            sequence_tracker = sequence
            if sequence == 0:
                if latest_queue_time is None:
                    latest_queue_time = datetime.strptime(time, "%Y%m%d-%H:%M:%S")
                    latest_queue_size = number_of_players
                velocity_time = datetime.strptime(time, "%Y%m%d-%H:%M:%S")
                break
            continue
        else:
            sequence_tracker = -1
            result_candidate = list()
    return {'velocity_data':result_candidate, 'velocity_time': velocity_time, 'latest_queue_size': latest_queue_size, 'latest_queue_time': latest_queue_time}


def velocity(data):
    distances = [j - i for i, j in zip(data.get('velocity_data')[:-1], data.get('velocity_data')[1:])]
    skewed = skew_data(distances, 5)
    return {"velocity": math.fabs(sum(skewed) / len(skewed)), "velocity_time": data.get('velocity_time'),
            "latest_queue_time": data.get('latest_queue_time'), "latest_queue_size": data.get('latest_queue_size')}


def skew_data(distances, number_of_segments):
    ret = []
    dlen = len(distances)
    segment_size = math.ceil(dlen/number_of_segments)
    segments = [distances[i * segment_size:(i+1) * segment_size] for i in range(number_of_segments)]
    for i, segment in enumerate(segments, start=1):
        for element in segment:
            for _ in range(i):
                ret.append(element)
    return ret



@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if not message.content.startswith('!'):
        return

    channel = message.channel
    print('Reading message from server "' + channel.guild.name + '". Content="' + message.content + '" from author "' + message.author.name + '"')


    if channel.name not in ('person-vouching', 'queue-discussion'):
        return

    msg = ''

    if channel.name == 'queue-discussion' and message.content.startswith('!queue'):
        vc = velocity(read_queue_data())

        msg = 'At {} the queue was {} players. At {} the throughput was {} per minute. The expected queue time currently is {} minutes'.format(
            vc.get("latest_queue_time").strftime("%b %d %H:%M"), vc.get("latest_queue_size"),
            vc.get("velocity_time").strftime("%b %d %H:%M"), math.trunc(vc.get('velocity')),
            math.trunc(vc.get("latest_queue_size") / vc.get("velocity")))

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)

    if channel.name == 'person-vouching' and message.content.startswith('!nobuddies'):
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
        msg = 'Members found who does not have the \'Buddies\' role:\n```'
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