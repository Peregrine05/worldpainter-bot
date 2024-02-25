import json

import discord
import discord.ext.commands

import discord_util


FAQ_ENTRIES = {}


def load_faq():
    global FAQ_ENTRIES
    try:
        with open("faq.json", "rt") as faq_file:
            FAQ_ENTRIES = json.load(faq_file)
    except FileNotFoundError:
        FAQ_ENTRIES = {}


load_faq()


class FAQ(discord.ext.commands.Cog):
    help_messages = {}

    def __init__(self, bot):
        self.bot = bot

    @discord_util.add_slash_command(
        name="faq_set",
        description="Set an FAQ entry.",
        help_message_container=help_messages,
        example="{} key: short name question: longer question answer: answer",
        params_help=[
            {
                "name": "key",
                "input_type": "String",
                "description": "The key to refer to the FAQ entry by"
            },
            {
                "name": "question",
                "input_type": "String",
                "description": "The actual FAQ"
            },
            {
                "name": "answer",
                "input_type": "String",
                "description": "The answer to the FAQ"
            }
        ],
        guild_only=True
    )
    @discord.commands.default_permissions(manage_messages=True)
    async def faq_set(
            self,
            ctx: discord.ApplicationContext,
            key: discord.Option(
                str,
                name="key",
                description="The key to refer to the FAQ entry by",
                required=True,
                max_length=128
            ),
            question: discord.Option(
                str,
                name="question",
                description="The actual FAQ",
                required=True,
                max_length=384
            ),
            answer: discord.Option(
                str,
                name="answer",
                description="The answer to the FAQ",
                required=True,
                max_length=4000
            )
    ):
        new_entry = {key: {"question": question, "answer": answer}}
        FAQ_ENTRIES.update(new_entry)
        with open("faq.json", "wt") as faq_file:
            json.dump(FAQ_ENTRIES, faq_file, indent=3)

        await ctx.respond(f"Added FAQ entry: `{key}`.")

    @discord_util.add_slash_command(
        name="faq_remove",
        description="Remove an FAQ entry.",
        help_message_container=help_messages,
        example="{} key: FAQ key",
        params_help=[
            {
                "name": "key",
                "input_type": "String",
                "description": "The key of the FAQ entry to be removed"
            }
        ],
        guild_only=True
    )
    @discord.commands.default_permissions(manage_messages=True)
    async def faq_remove(
            self,
            ctx,
            key: discord.Option(
                str,
                name="key",
                description="The key of the FAQ entry to display",
                required=True,
                max_length=128,
                autocomplete=lambda ctx: map(str, FAQ_ENTRIES.keys())
            )
    ):
        try:
            FAQ_ENTRIES.pop(key)
            with open("faq.json", "wt") as faq_file:
                json.dump(FAQ_ENTRIES, faq_file, indent=3)
        except KeyError:
            return await ctx.respond(f"No FAQ entry with key: `{key}` exists.",
                                     ephemeral=True)
        await ctx.respond(f"Removed FAQ entry: `{key}`.")

    @discord_util.add_slash_command(
        name="faq_get",
        description="Get an FAQ entry.",
        help_message_container=help_messages,
        example="{} key: FAQ key",
        params_help=[
            {
                "name": "key",
                "input_type": "String",
                "description": "The key of the FAQ entry to display"
            },
            {
                "name": "mention",
                "input_type": "Discord member",
                "description": "[optional] A Discord member to mention in the "
                               "message"
            },
            {
                "name": "plain",
                "input_type": "bool",
                "description": "[optional] Send the message without Markdown "
                               "formatting (in a code block)"
            }
        ]
    )
    async def faq_get(
            self,
            ctx: discord.ApplicationContext,
            key: discord.Option(
                str,
                name="key",
                description="The key of the FAQ entry to display",
                required=True,
                max_length=128,
                autocomplete=lambda ctx: map(str, FAQ_ENTRIES.keys())
            ),
            mention: discord.Option(
                discord.Member,
                name="mention",
                description="[optional] A Discord member to mention in the "
                            "message",
                required=False
            ),
            plain: discord.Option(
                bool,
                name="plain",
                description="[optional] Send the message without Markdown "
                            "formatting (in a code block)",
                default=False
            )
    ):
        try:
            question = FAQ_ENTRIES[key]["question"]
            answer = FAQ_ENTRIES[key]["answer"]
        except KeyError:
            return await ctx.respond(f"No FAQ entry with key: `{key}` exists.",
                                     ephemeral=True)
        if plain:
            answer = "```\n" + answer + "\n```"

        embed = discord.Embed(color=discord.Color.random(),
                              title=question,
                              description=answer)
        embed.set_footer(text=f"key: {key}")

        if mention is not None:
            content = mention.mention
        else:
            content = ""

        await ctx.respond(
            content=content,
            embed=embed
        )

    @discord_util.add_slash_command(
        name="faq_list",
        description="List the FAQ entries.",
        help_message_container=help_messages,
        example="{}",
    )
    async def faq_list(self, ctx):
        await ctx.respond(
            "FAQ entries are: "
            + ", ".join(
                map(lambda x: x.center(len(x) + 2, "`"),
                    list(FAQ_ENTRIES.keys())))
        )


def setup(bot):
    cog = FAQ(bot)
    bot.add_cog(cog)
    bot.add_help(cog.help_messages)
