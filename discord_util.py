import discord
import discord.ext.commands

from typing import List


def add_slash_command(
        *,
        groups: List[discord.SlashCommandGroup] = None,
        display_name=None,
        params_help=None,
        example=None,
        help_message_container: dict,
        **kwargs
):
    if display_name is not None:
        name = display_name
    else:
        name = kwargs.get("name")
    if name is not None:
        if groups is not None:
            for group in reversed(groups):
                name = group.name + " " + name
        type_ = "slash command"
        description = kwargs.get("description")
        help_message_container.update(
            {name: (type_, description, params_help, example)}
        )
    if groups is not None:
        return groups[-1].command(**kwargs)
    return discord.slash_command(**kwargs)


def add_prefixed_command(
        *,
        display_name=None,
        params_help=None,
        example=None,
        help_message_container: dict,
        **kwargs
):
    if display_name is not None:
        name = display_name
    else:
        name = kwargs.get("name")
    if name is not None:
        type_ = "prefixed command"
        description = kwargs.get("description")
        help_message_container.update(
            {name: (type_, description, params_help, example)}
        )
    return discord.ext.commands.command(**kwargs)


def add_user_command(
        *,
        display_name=None,
        params_help=None,
        example=None,
        help_message_container: dict,
        **kwargs
):
    if display_name is not None:
        name = display_name
    else:
        name = kwargs.get("name")
    if name is not None:
        type_ = "user command"
        description = kwargs.get("description")
        help_message_container.update(
            {name: (type_, description, params_help, example)}
        )
    return discord.user_command(**kwargs)


def is_manager():
    async def predicate(ctx: discord.ext.commands.Context):
        return ctx.author.id in ctx.bot.managers
    return discord.ext.commands.check(predicate)

