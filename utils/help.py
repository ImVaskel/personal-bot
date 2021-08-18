from __future__ import annotations

from typing import TYPE_CHECKING

from .constants import Embed

if TYPE_CHECKING:
    from typing import Mapping, List, Optional, Tuple, Union

    from .bot import Bot

import discord
from discord.ext import commands, menus
from discord.ext.menus.views import ViewMenuPages

USE_HELP = "Use ``{0.prefix}help <command/module>`` for more help!"


class FormatBotHelp(menus.ListPageSource):
    def __init__(self, entries, ctx: commands.Context, *, per_page: Optional[int] = 5):
        super().__init__(entries, per_page=per_page)
        self.ctx = ctx

    async def format_page(
        self, menu: ViewMenuPages, entries: List[commands.Cog, List[commands.Command]]
    ):
        embed = Embed(title=f"Help!", description=USE_HELP.format(self.ctx))

        for cog, _commands in entries:
            embed.add_field(
                name=f"{cog.qualified_name}",
                value=f"{' '.join(f'``{cmd}``' for cmd in _commands) or 'No commands'}",
                inline=False,
            )

        if self.get_max_pages() > 1:
            embed.set_footer(text=f"Page {menu.current_page+1}/{self.get_max_pages()}")

        return embed


class FormatHelp(menus.ListPageSource):
    """A listpagesource that generates for both cog and commands, since they are roughly the same"""

    def __init__(
        self,
        entries,
        ctx: commands.Context,
        *,
        per_page: Optional[int] = 5,
        group: Union[commands.Cog, commands.Group],
    ):
        super().__init__(entries, per_page=per_page)
        self.ctx = ctx
        self.group = group

    async def format_page(
        self, menu: menus.Menu, entries: List[commands.Command]
    ) -> Embed:
        embed = Embed(
            title=f"Help for {self.group.qualified_name}!",
            description=USE_HELP.format(self.ctx) + "\n\n" + f"{self.group.help}",
        )

        for command in entries:
            name = f"{command} {command.signature}"
            value = command.help or "No help"

            if isinstance(command, commands.Group):
                value = f"[Group] {value}"

            embed.add_field(name=name, value=value, inline=False)

        if self.get_max_pages() > 1:
            embed.set_footer(text=f"Page {menu.current_page+1}/{self.get_max_pages()}")

        return embed


class HelpCommand(commands.HelpCommand):
    ctx: commands.Context

    async def filter_commands(self, commands, *, sort=False, key=None):
        if await self.context.bot.is_owner(self.context.author):
            return commands

        return await super().filter_commands(commands, sort=sort, key=key)

    async def send_bot_help(
        self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]
    ):
        filtered: List[Tuple[commands.Cog, List[commands.Command]]] = []

        for k, v in mapping.items():
            _filtered = await self.filter_commands(v)

            if _filtered and k:
                filtered.append((k, _filtered))

        if not filtered:
            return await self.get_destination().send("You cannot use any commands!")

        await ViewMenuPages(FormatBotHelp(filtered, self.context)).start(self.context)

    async def send_group_help(self, group: commands.Group):
        filtered = await self.filter_commands(list(group.commands))

        if not filtered:
            return await self.send_command_help(group)

        await ViewMenuPages(
            source=FormatHelp(filtered, self.context, group=group)
        ).start(self.context)

    async def send_cog_help(self, cog: commands.Cog):
        filtered = await self.filter_commands(cog.get_commands())

        if not filtered:
            return await self.get_destination().send(
                "You cannot use any commands in this module!"
            )

        await ViewMenuPages(source=FormatHelp(filtered, self.context, group=cog)).start(
            self.context
        )

    async def send_command_help(self, command: commands.Command):
        embed = Embed(
            title=f"Help for {command}!", description=USE_HELP.format(self.context)
        )

        embed.add_field(
            name="Help", value=command.help or "No help given", inline=False
        )

        embed.add_field(name="Can run", value=await command.can_run(self.context))

        embed.add_field(name="Signature", value=command.signature or "No parameters")

        embed.add_field(
            name="Aliases",
            value=" ".join(f"``{a}``" for a in command.aliases) or "None",
        )

        await self.get_destination().send(embed=embed)


def setup(bot: Bot):
    bot.help_command = HelpCommand()


def teardown(bot: Bot):
    bot.help_command = commands.DefaultHelpCommand()
