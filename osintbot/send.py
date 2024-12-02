import osintbot.db as db

db = db.Database()

async def message(ctx, message, file=None):
    author = ctx.author
    author_id = ctx.author.id
    guild = ctx.guild
    guild_id = ctx.guild.id
    global_response_mode = db.db_get_global_config(guild_id, "tbl_global_response_mode")
    user_response_mode = db.db_get_user_config(author_id, guild_id, "tbl_user_response_mode")
    if global_response_mode == "off":
        if user_response_mode == "dm":
            await ctx.author.send(message, file=file)
        if user_response_mode == "mm":
            await ctx.send("{}".format(ctx.author.mention) + "\n" + message, file=file)
    else:
        if global_response_mode == "dm":
            await ctx.author.send(message, file=file)
        if global_response_mode == "mm":
            await ctx.send("{}".format(ctx.author.mention) + "\n" + message, file=file)