import os

import discord
import discord.ext.commands
from discord import Interaction, ApplicationContext

import discord_util
from main import HelpBot


class CommissionForm(discord.ui.Modal):
    def __init__(self, budget, bot: HelpBot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.budget = budget
        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.long,
                label="Description of commission request",
                placeholder="Describe your request.",
                max_length=4000,
            )
        )
        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.short,
                label="Size of requested map",
                placeholder="Input the size of the requested map.",
                max_length=50,
            )
        )
        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.short,
                label="Deadline",
                placeholder="When do you need your map by?",
                max_length=200,
            )
        )
        if self.budget == "_":
            self.add_item(
                discord.ui.InputText(
                    style=discord.InputTextStyle.short,
                    label="Your budget for this request",
                    placeholder="Input a numerical value greater than 10.",
                    min_length=2,
                    max_length=5,
                )
            )

    async def callback(self, interaction: Interaction):
        success = False
        try:
            budget = int(self.children[3].value)
            if budget < 10:
                raise ValueError
            budget = f"${budget}"
            success = True
        except IndexError:
            budget = self.budget
            success = True
        except ValueError:
            budget = ""
        if success:
            message = await create_commission_thread(
                self.bot,
                interaction,
                self.children[0].value,
                self.children[1].value,
                self.children[2].value,
                budget
            )
        else:
            message = ("You must enter a numerical value greater than 10 as a "
                       "budget.")
        await interaction.response.send_message(content=message,
                                                ephemeral=True)


class BudgetSelector(discord.ui.View):
    def __init__(self, bot, *items):
        super().__init__(*items)
        self.bot = bot

    @discord.ui.string_select(
        placeholder="Select your budget.",
        min_values=1,
        max_values=1,
        options=list(
            [
                discord.SelectOption(
                    label=f"${x}"
                ) for x in range(10, 110, 10)
            ] + [
                discord.SelectOption(
                    label="Custom (must be greater than $10)",
                    value="_"
                )
            ]
        )
    )
    async def callback(self, select, interaction):
        await interaction.response.send_modal(CommissionForm(
            title="Submit a commission request",
            bot=self.bot,
            budget=select.values[0]
        ))


class CommissionFormView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Submit a request",
                       custom_id="commission_request_button")
    async def callback(self, button, interaction):
        await interaction.response.send_message(
            view=BudgetSelector(bot=self.bot),
            ephemeral=True
        )


async def create_commission_thread(
        bot: HelpBot,
        ctx,
        description,
        map_size,
        deadline,
        budget
):
    channel_id = int(os.getenv("REQUESTS_CHANNEL"))
    if channel_id is None:
        return ("No forum channel has been set for posting commission "
                "requests. Set a forum channel ID in the `.env` file prior to "
                "starting the bot.")

    channel: discord.ForumChannel = bot.get_channel(channel_id)
    tags = channel.available_tags
    for tag in tags:
        value = int(tag.name.replace(
            "$",
            ""
        ).replace(
            " ",
            ""
        ).replace(
            "+",
            ""
        ).split("-")[0])
        budget_num = int(budget.replace("$", ""))
        if budget_num >= 100 and value == 100:
            apply_tag = tag
            break
        elif value <= budget_num < value + 10:
            apply_tag = tag
            break
    else:
        return ctx.respond("No tag matched the budget.", ephemeral=True)

    embed = discord.Embed(
        title=f"Commission Request",
        description=description,
        color=discord.Color.random()
    )
    embed.add_field(name="Client", value=ctx.user.mention)
    embed.add_field(name="Map size", value=map_size, inline=False)
    embed.add_field(name="Deadline", value=deadline, inline=False)
    embed.add_field(name="Budget", value=budget, inline=False)
    embed.set_footer(text="Use the /close command to close this request.")

    thread = await channel.create_thread(
        name=f"{ctx.user.name} - {map_size} - {budget}",
        reason=f"{ctx.user.name} ({ctx.user.id}) submitted a commission "
               f"request.",
        auto_archive_duration=10080,
        applied_tags=[apply_tag],
        content=ctx.user.mention,
        embed=embed
    )

    await thread.add_user(ctx.user)

    await thread.starting_message.pin()
    return f"Go to your request: {thread.jump_url}"


class Commissions(discord.ext.commands.Cog):
    help_messages = {}

    def __init__(self, bot):
        self.bot = bot

        @bot.event
        async def on_ready():
            bot.add_view(CommissionFormView(bot))

    async def cog_check(self, ctx: ApplicationContext) -> bool:
        return True

    @discord_util.add_slash_command(
        name="commission_request",
        description="Submit a *paid* commission request.",
        help_message_container=help_messages,
        params_help=[
            {
                "name": "description",
                "input_type": "string",
                "description": "Description of commission request"
            },
            {
                "name": "map_size",
                "input_type": "string",
                "description": "Size of requested map"
            },
            {
                "name": "deadline",
                "input_type": "string",
                "description": "Time before which you want the map"
            },
            {
                "name": "budget",
                "input_type": "int",
                "description": "Amount of money you are willing to spend, in "
                               "USD. The minimum acceptable value is 10."
            }
        ],
        example="{} description: Three islands with forests and rivers "
                "map_size: 2048x2048 deadline: I want this map within one "
                "month. budget: 40",
        guild_only=True
    )
    async def commission_request(
            self,
            ctx: discord.commands.context.ApplicationContext,
            description: discord.Option(
                str,
                name="description",
                description="Description of commission request",
                required=True,
                max_length=4000
            ),
            map_size: discord.Option(
                str,
                name="map_size",
                description="Size of requested map (Manual input is "
                            "supported)",
                required=True,
                autocomplete=lambda *args, **kwargs: [
                    "512x512",
                    "1024x1024",
                    "1536x1536",
                    "2048x2048",
                    "3072x3072",
                    "4096x4096",
                    "5120x5120",
                    "6144x6144",
                    "8192x8192",
                    "10240x10240",
                ],
                max_length=50
            ),
            deadline: discord.Option(
                str,
                name="deadline",
                description="Time before which you want the map",
                required=True,
                max_length=200
            ),
            budget: discord.Option(
                int,
                name="budget",
                description="Amount of money you are willing to spend, in "
                            "USD. (Manual input is supported; minimum value "
                            "of 10)",
                required=True,
                autocomplete=lambda *args, **kwargs: [
                    10,
                    20,
                    30,
                    40,
                    50,
                    60,
                    70,
                    80,
                    90,
                    100
                ],
                min_value=10,
                max_value=99999
            ),
    ):
        if budget < 10:
            message = "The minimum allowable value for `budget` is *10*."
        else:
            message = await create_commission_thread(
                self.bot,
                ctx,
                description,
                map_size,
                deadline,
                f"${budget}"
            )
        await ctx.respond(content=message, ephemeral=True)

    @discord_util.add_slash_command(
        name="create_modal_button",
        description="Send a message with a button for posting commission "
                    "requests.",
        help_message_container=help_messages,
        params_help=[
            {
                "name": "channel",
                "description": "Channel in which to post the message",
                "input_type": "Discord channel"
            }
        ],
        example="{}",
        guild_only=True
    )
    @discord.commands.default_permissions(manage_messages=True)
    async def create_modal_button(
            self,
            ctx: discord.commands.context.ApplicationContext,
            channel: discord.Option(
                discord.TextChannel,
                name="channel",
                description="Channel in which to post the message",
                required=False
            )
    ):
        if channel is None:
            channel = ctx.channel
        try:
            message = await channel.send(content="Use the button to prepare "
                                                 "and submit a commission "
                                                 "request.",
                                         view=CommissionFormView(self.bot))
        except discord.Forbidden:
            await ctx.respond(
                content=f"The message could not be posted to "
                        f"{channel.mention}, likely due to insufficient "
                        f"permissions.",
                ephemeral=True
            )
            return
        await ctx.respond(f"Posted message {message.jump_url} to "
                          f"{channel.mention}.", ephemeral=True)

    @discord_util.add_slash_command(
        name="close",
        description="Close this thread",
        help_message_container=help_messages,
        example="{}",
        guild_only=True
    )
    async def close_thread(
            self,
            ctx: discord.commands.context.ApplicationContext
    ):
        if not isinstance(ctx.channel, discord.Thread):
            return await ctx.respond(content="This channel is not a thread.",
                                     ephemeral=True)

        starting_message = await ctx.channel.fetch_message(ctx.channel.id)

        if ((starting_message.content == ctx.user.mention
             and starting_message.author == ctx.me)
                or ctx.user.guild_permissions.manage_threads):
            tags = ctx.channel.parent.available_tags
            await ctx.channel.edit(
                name="[CLOSED] " + ctx.channel.name,
                applied_tags=list(filter(lambda x: x.name == "Closed", tags))
            )
            await ctx.respond("This thread has been archived.")
            await ctx.channel.archive(locked=True)
            return
        await ctx.respond("Only the thread owner and moderators may "
                          "archive this thread.",
                          ephemeral=True)


def setup(bot: HelpBot):
    cog = Commissions(bot)
    bot.add_cog(cog)
    bot.add_help(cog.help_messages)
