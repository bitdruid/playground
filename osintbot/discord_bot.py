import discord
from discord.ext import commands
import os
import time
from datetime import datetime

import osintbot.send as send
import osintkit.helper as kit_helper
import osintbot.log as log

import aiohttp.client_exceptions

from osintbot.__version__ import __version__

def main(env_instance, db_instance):

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix='/', intents=intents)
    bot.help_command = None

    document_path = "documents/"
    os.makedirs(document_path, exist_ok=True)

    about_message = \
        "This bot was created by bitdruid.\n" + \
        "Current Version is: {}\n\n".format(__version__) + \
        "https://github.com/bitdruid/osintbot"

    def create_document(filename, content):
        document = open(document_path + filename, "w")
        document.write(content)
        document.close()
        document = open(document_path + filename, "rb")
        return document

    async def output_text_result(ctx, input: str, result: str, request_name: str):
        message = f"{request_name.upper()} data for {input}:\n\n" + kit_helper.json_to_string(result, markdown=True)
        await send.message(ctx, message)

    async def output_file_result(ctx, input, result, request_name):
        if isinstance(result, dict):
            result = kit_helper.json_to_string(result)
        document = create_document(request_name + "_" + input + ".txt", result)
        await send.message(ctx, f"{request_name.upper()} data for {input}:", file=discord.File(document, filename=request_name + "_" + input + ".txt"))
        
    async def initialize():
        # check if bot-channel exists and create it if not
        ready_message = f"`{time.strftime('%d/%m/%Y %H:%M:%S')}` - `{env_instance.bot_name}` ready to serve."
        for guild in bot.guilds:
            # insert guild leader into database
            db_instance.db_insert_leader(guild.owner.id, guild.owner.name, guild.id, guild.name)
            db_instance.db_insert_global_config(guild.id, guild.name)
            for channel in guild.channels:
                if channel.name == env_instance.bot_channel:
                    await channel.send(ready_message)
                    return
            overwrites = {
                guild.owner: bot.PermissionOverwrite(read_messages=True),
                guild.me: bot.PermissionOverwrite(read_messages=True),
                guild.default_role: bot.PermissionOverwrite(read_messages=False)
            }
            channel = await guild.create_text_channel(env_instance.bot_channel, overwrites=overwrites)
            await channel.send("{}".format(guild.owner.mention) + "\n" + f"I'm {env_instance.bot_name} and created this private channel for interaction. Configure permissions for this channel as you like.\nGet started with `/help` or mention `@{env_instance.bot_name} help` in this channel.")
            await channel.send(ready_message)





    # timeout a command for guild for 10 seconds
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "This command is on cooldown to prevent flooding API by bot-IP. Try again in {:.2f}s.".format(error.retry_after))
        else:
            raise error






    # if bot joins a server or starts it checks for osint-channel and creates it if it does not exist
    @bot.event
    async def on_ready():
        await initialize()
        
    @bot.event
    async def on_guild_join(guild):
        await initialize()





    @bot.command(name='commands', aliases=['help', 'start', 'usage'], description='Shows help message')
    async def help(ctx):
        # send and mention
        commands = {}
        commands_message = ""
        for command in bot.commands:
            commands[command.name] = f"`{command.name}` - {command.description}"
        commands = dict(sorted(commands.items()))
        for command in commands:
            commands_message += commands[command] + "\n"
        message = \
            "\n\n" + \
            "__I am {} and i can help you with this:__".format(env_instance.bot_name) + \
            "\n\n" + \
            commands_message + \
            "\n" + \
            "You can also mention me to run commands.\nExample: `@{} whois example.com`".format(env_instance.bot_name)
        if env_instance.mail_user:
            message += \
                "\n\n" + \
                "Further you can write a mail to `{}` with the subject `<command> <input>` to get the result as a mail.".format(env_instance.mail_user)
        await ctx.send("{}".format(ctx.author.mention) + message)





    async def datarequest_input_check(ctx, command, input):
        if not input:
            await ctx.send("{}".format(ctx.author.mention) + "\n" + f"**Usage:**\n/{command} <ip/domain>")
            return
        if not kit_helper.validate_domain(input) and not kit_helper.validate_ip(input):
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "Invalid domain or IP address.")
            return
        return True

    async def datarequest_failed(ctx, command, input):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + f"No {command} data available for this input. Check if the domain or IP address is valid and does exist.")





    import osintkit.whois as whois
    @bot.command(name='whois', description='Shows WHOIS information for a domain', )
    async def query_whois(ctx, domain=None):
        await datarequest_input_check(ctx, "whois", domain)
        data = whois.request(domain)
        if data:
            await output_file_result(ctx, domain, data, "whois")
        else:
            await datarequest_failed(ctx, "whois", domain)





    import osintkit.iplookup as iplookup
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @bot.command(name='iplookup', description='Shows IP information for a domain or IP address')
    async def query_iplookup(ctx, input=None):
        await datarequest_input_check(ctx, "iplookup", input)
        data = iplookup.request(input)
        if data:
            await output_text_result(ctx, input, data, "iplookup")
        else:
            await datarequest_failed(ctx, "iplookup", input)






    import osintkit.geoip as geoip
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @bot.command(name='geoip', description='Shows GeoIP information for a domain or IP address')
    async def query_geoip(ctx, input=None):
        await datarequest_input_check(ctx, "geoip", input)
        data = geoip.request(input)
        if data:
            await output_text_result(ctx, input, data, "geoip")
        else:
            await datarequest_failed(ctx, "geoip", input)




    import osintkit.arecord as arecord
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @bot.command(name='arecord', description='Shows A record information for a domain or IP address')
    async def query_arecord(ctx, input=None):
        await datarequest_input_check(ctx, "arecord", input)
        data = arecord.request(input)
        if data:
            await output_text_result(ctx, input, data, "arecord")
        else:
            await datarequest_failed(ctx, "arecord", input)




    import osintbot.datarequest as datarequest
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @bot.command(name='report', description='Gives you whois, iplookup and geoip information for a domain or IP address')
    async def query_report(ctx, input=None):
        await datarequest_input_check(ctx, "report", input)
        report_data = datarequest.full_report(input)
        if report_data:
            await output_file_result(ctx, input, report_data, "report")
        else:
            await datarequest_failed(ctx, "report", input)





    import osintkit.screenshot as screenshot
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @bot.command(name='screenshot', description='Takes a screenshot of a website')
    async def query_screenshot(ctx, input=None):
        await datarequest_input_check(ctx, "screenshot", input)
        screenshot_data = screenshot.request(input, document_path)
        if screenshot_data:
            for file in screenshot_data:
                await send.message(ctx, f"Screenshot for {input}:", file=discord.File(file, filename=file))
        else:
            await datarequest_failed(ctx, "screenshot", input)





    @bot.command(name='prune', description='Prunes messages from the osint-channel')
    async def prune(ctx):
        if ctx.channel.name == env_instance.bot_channel:
            count_history = 0
            async for message in ctx.channel.history(limit=None):
                count_history += 1
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            caller = ctx.author
            # purge messages
            await ctx.channel.purge()
            # prune documents
            amount_documents = len(os.listdir(document_path))
            for file in os.listdir(document_path):
                os.remove(document_path + file)
            prune_message = await ctx.send("{}".format(ctx.author.mention) + "\n" + "Pruned history from osint-channel at `{}` by `{}`:\n".format(timestamp, caller) + "- messages: `{}`\n".format(count_history) + "- documents: `{}`".format(amount_documents))
            # pin message
            await prune_message.pin()
        else:
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "This command is only available in the osint-channel.")





    @bot.command(name='config', description='Configure bot settings for you and your server')
    async def config(ctx, command=None, key=None, value=None):
        mode = "set the bot mode for response to `dm` (direct message) or `mm` (mention message)"
        globalmode = mode + " or `off` (user can set mode by himself)"
        if not command:
            await ctx.send("{}".format(ctx.author.mention) + "\n" + \
                "**Usage:**\n/config <command> <value>:\n" + \
                "Available commands:\n" + \
                "- `mode` - " + mode + "\n" + \
                "- `show` - show the current configuration\n" + \
                "Admin commands:\n" + \
                # "- `mkadmin <@user>` - make a user admin\n" + \
                # "- `rmadmin <@user>` - remove a user from admin\n" + \
                "- `globalmode` <mode> - " + globalmode + "\n" + \
                "- `userdump` - dump the user database\n" + \
                "- `confdump` - dump the configuration database")
            return
        if command == "mode":
            if not key:
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/config mode <mode>:\n" + mode)
                return
            if key == "dm":
                db_instance.db_set_user_config(ctx.author.id, ctx.guild.id, "tbl_user_response_mode", "dm")
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be sent as direct message for user" + ctx.author.mention)
            elif key == "mm":
                db_instance.db_set_user_config(ctx.author.id, ctx.guild.id, "tbl_user_response_mode", "mm")
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be public sent as mention message for user" + ctx.author.mention)
        if command == "show":
            if db_instance.db_isleader(ctx.author.id, ctx.guild.id):
                config = db_instance.db_get_global_config(ctx.guild.id)
                config = kit_helper.json_to_string(config)
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Configuration for:\n" + config)
            else:
                config = db_instance.db_get_user_config(ctx.author.id, ctx.guild.id)
                config = kit_helper.json_to_string(config)
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Configuration for:\n" + config)
        if db_instance.db_isleader(ctx.author.id, ctx.guild.id):
            if command == "userdump":
                dump = db_instance.db_dump(ctx.guild.id, "user")
                document = create_document("dbdump" + "_" + ctx.guild.name + ".txt", dump)
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Database dump for {}:".format(ctx.guild.name), file=discord.File(document, filename="dbdump" + "_" + ctx.guild.name + ".txt"))
            if command == "confdump":
                dump = db_instance.db_dump(ctx.guild.id, "conf")
                document = create_document("confdump" + "_" + ctx.guild.name + ".txt", dump)
                await ctx.send("{}".format(ctx.author.mention) + "\n" + "Configuration dump for {}:".format(ctx.guild.name), file=discord.File(document, filename="confdump" + "_" + ctx.guild.name + ".txt"))
            if command == "globalmode":
                if not key:
                    await ctx.send("{}".format(ctx.author.mention) + "\n" + "**Usage:**\n/config globalmode <mode>:\n" + globalmode)
                    return
                if key == "dm":
                    db_instance.db_set_global_config(ctx.guild.id, ctx.author.id, "tbl_global_response_mode", "dm")
                    await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be sent as direct message.")
                elif key == "mm":
                    db_instance.db_set_global_config(ctx.guild.id, ctx.author.id, "tbl_global_response_mode", "mm")
                    await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be public sent as mention message.")
                elif key == "off":
                    db_instance.db_set_global_config(ctx.guild.id, ctx.author.id, "tbl_global_response_mode", "off")
                    await ctx.send("{}".format(ctx.author.mention) + "\n" + "Bot responses will be sent like the user specified for himself.")
        else:
            await ctx.send("{}".format(ctx.author.mention) + "\n" + "You are not the leader of this server and not allowed to use this command.")



                
            




    @bot.command(name='id', description='Shows your Discord ID')
    async def id(ctx):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + "Your Discord ID is: {}".format(ctx.author.id))





    @bot.command(name='about', description='Shows information about this bot')
    async def about(ctx):
        await ctx.send("{}".format(ctx.author.mention) + "\n" + about_message)




    # you can run commands by mentioning the bot
    @bot.event
    async def on_message(message):
        # ignore messages from bot, dms and other channels then bot-channel
        if message.author == bot.user:
            return
        if message.guild is None:
            await message.channel.send(f"Please communicate in the bot-channel.")
            return
        if message.channel.name != env_instance.bot_channel:
            return
        
        # add the user to the database
        db_instance.db_insert_user(message.author.id, message.author.name, message.guild.id, message.guild.name)
        
        if bot.user.mentioned_in(message):
            # remove mention from message
            content = message.content
            words = content.split()
            words = [words for words in words if not words.startswith("<@")]
            # check if message is not empty after removing mention and get command + arguments
            if len(words) > 0:
                command_name = words[0]
                command_arguments = words[1:]
                # check if command exists
                command = bot.get_command(command_name)
                if command:
                    # invoke command = run command
                    ctx = await bot.get_context(message)
                    try:
                        bucket = command._buckets.get_bucket(ctx)
                        retry_after = bucket.update_rate_limit()
                    except:
                        retry_after = False
                    if retry_after:
                        await ctx.send(f"{ctx.author.mention} This command is on cooldown. Try again in {retry_after:.2f} seconds.")
                    else:
                        await ctx.invoke(command, *command_arguments)
                else:
                    await message.channel.send("{}".format(message.author.mention) + "\n" + "Unknown command.")
            else:
                await message.channel.send("{}".format(message.author.mention) + "\n" + "You can use `/help` to get a list of commands.")
        await bot.process_commands(message)





    while aiohttp.client_exceptions.ClientConnectorError:
        try:
            bot.run(env_instance.bot_token)
        except aiohttp.client_exceptions.ClientConnectorError as e:
            log.exception("discord", "Could not connect to discord API. Retrying in 1 minute.", e)
            time.sleep(60)

if __name__ == "__main__":
    main()