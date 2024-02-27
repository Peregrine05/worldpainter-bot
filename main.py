import os

import discord
import discord.ext.commands
import dotenv

import discord_util


class HelpBot(discord.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.managers = list(map(int, os.getenv("MANAGERS").split(",")))
        self.command_help = {}

    def add_help(self, command_help: dict):
        self.command_help.update(command_help)

    def get_command_names(self):
        return list(self.command_help.keys())

    def build_help_message(self, command_name, command_prefix):
        command_help = self.command_help.get(command_name)
        command_type = command_help[0]
        if command_type == "slash command":
            command_prefix = "/"
        elif command_type == "user command":
            command_prefix = "@"
        command_name = command_prefix + command_name
        command_description = command_help[1]

        embed = discord.Embed(
            title=f"Help for {command_type}: `{command_name}`",
            description=command_description,
            color=discord.Color.random()
        )
        if command_help[2] is not None:
            for parameter in command_help[2]:
                param_name: str = parameter.get("name")
                param_name = param_name.center(
                    len(param_name) + 2,
                    "`"
                )
                if param_name is None:
                    continue

                field_value = ""

                input_type = parameter.get("input_type")
                if input_type is not None:
                    field_value += f"- **Input type**: {input_type}\n"

                param_description = parameter.get("description")
                if param_description is not None:
                    field_value += f"- **Description**: {param_description}\n"

                embed.add_field(
                    name=param_name,
                    value=field_value,
                    inline=False
                )

            example = command_help[3].format(command_name)
            if example is not None:
                embed.set_footer(text="Example: " + example)

        return embed


def main():
    dotenv.load_dotenv()
    token = str(os.getenv("TOKEN"))

    intents = discord.Intents.default()

    bot = HelpBot(
        command_prefix=os.getenv("COMMAND_PREFIX"),
        intents=intents,
        help_command=None
    )

    bot.load_extension("commissions")
    bot.load_extension("faq")

    @bot.slash_command(
        name="help",
        description="Get bot usage information"
    )
    async def bot_help(
            ctx: discord.ApplicationContext,
            command: discord.Option(
                str,
                name="command",
                description="Command for which to get help",
                choices=bot.get_command_names(),
                required=True
            )
    ):
        command_name = command
        embed = bot.build_help_message(command_name, os.getenv("COMMAND_PREFIX"))

        await ctx.respond(embed=embed)

    @bot.command(
        name="help"
    )
    async def prefix_help(
            ctx: discord.ext.commands.context.Context,
            *,
            message=" "
    ):
        command_prefix = os.getenv("COMMAND_PREFIX")
        if message.strip().lower() not in bot.get_command_names():
            await ctx.reply(
                "To get help for a command, run the command:\n"
                f"```{command_prefix}help command```\n"
                "Values for `command` are: " + ", ".join(
                    map(lambda x: x.center(len(x) + 2, "`"),
                        bot.get_command_names())
                )
            )
            return
        embed = bot.build_help_message(message.strip().lower(), command_prefix)
        await ctx.reply(embed=embed)

    @bot.slash_command(
        name="exit_bot",
        description="Exit the bot."
    )
    @discord_util.is_manager()
    async def exit_bot(ctx: discord.ApplicationContext):
        await ctx.respond("Exiting bot")
        await bot.close()

    bot.run(token)


if __name__ == "__main__":
    main()
