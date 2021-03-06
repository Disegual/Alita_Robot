# Copyright (C) 2020 - 2021 Divkix. All rights reserved. Source code available under the AGPL.
#
# This file is part of Alita_Robot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from pyrogram import filters
from pyrogram.errors import UserIsBlocked
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from alita import HELP_COMMANDS, LOGGER, OWNER_ID, PREFIX_HANDLER, VERSION
from alita.bot_class import Alita
from alita.tr_engine import tlang
from alita.utils.redis_helper import get_key


async def gen_cmds_kb():
    cmds = sorted(list(HELP_COMMANDS.keys()))
    kb = []

    while cmds:
        if cmds:
            cmd = cmds[0]
            a = [
                InlineKeyboardButton(
                    f"{cmd.capitalize()}",
                    callback_data=f"get_mod.{cmd.lower()}",
                ),
            ]
            cmds.pop(0)
        if cmds:
            cmd = cmds[0]
            a.append(
                InlineKeyboardButton(
                    f"{cmd.capitalize()}",
                    callback_data=f"get_mod.{cmd.lower()}",
                ),
            )
            cmds.pop(0)
        if cmds:
            cmd = cmds[0]
            a.append(
                InlineKeyboardButton(
                    f"{cmd.capitalize()}",
                    callback_data=f"get_mod.{cmd.lower()}",
                ),
            )
            cmds.pop(0)
        kb.append(a)
    return kb


async def gen_start_kb(q):

    me = await get_key("BOT_USERNAME")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    f"📚 {tlang(q, 'start.commands_btn')}",
                    callback_data="commands",
                ),
            ]
            + [
                InlineKeyboardButton(
                    f"ℹ️ {tlang(q, 'start.infos_btn')}",
                    callback_data="infos",
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🌐 {tlang(q, 'start.language_btn')}",
                    callback_data="chlang",
                ),
            ]
            + [
                InlineKeyboardButton(
                    f"➕ {tlang(q, 'start.add_chat_btn')}",
                    url=f"https://t.me/{me}?startgroup=new",
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🗃️ {tlang(q, 'start.source_code')}",
                    url="https://github.com/Divkix/Alita_Robot",
                ),
            ],
        ],
    )
    return keyboard


@Alita.on_message(
    filters.command("start", PREFIX_HANDLER) & (filters.group | filters.private),
)
async def start(_, m: Message):

    if m.chat.type == "private":
        try:
            await m.reply_text(
                tlang(m, "start.private"),
                reply_markup=(await gen_start_kb(m)),
                reply_to_message_id=m.message_id,
            )
        except UserIsBlocked:
            LOGGER.warning(f"Bot blocked by {m.from_user.id}")
    else:
        await m.reply_text(tlang(m, "start.group"), reply_to_message_id=m.message_id)
    return


@Alita.on_callback_query(filters.regex("^start_back$"))
async def start_back(_, q: CallbackQuery):

    await q.message.edit_text(
        tlang(q, "start.private"),
        reply_markup=(await gen_start_kb(q.message)),
    )
    await q.answer()
    return


@Alita.on_callback_query(filters.regex("^commands$"))
async def commands_menu(_, q: CallbackQuery):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *(await gen_cmds_kb()),
            [
                InlineKeyboardButton(
                    f"« {tlang(q, 'general.back_btn')}",
                    callback_data="start_back",
                ),
            ],
        ],
    )
    await q.message.edit_text(
        tlang(q, "general.commands_available"),
        reply_markup=keyboard,
    )
    await q.answer()
    return


@Alita.on_message(filters.command("help", PREFIX_HANDLER))
async def commands_pvt(_, m: Message):

    me = await get_key("BOT_USERNAME")

    if (m.text.split()) != 1:
        help_option = (m.text.split(None, 1)[1]).lower()
        if help_option in sorted([i.lower() for i in list(HELP_COMMANDS.keys())]):
            help_msg = HELP_COMMANDS[help_option]
        if m.chat.type == "private":
            await m.reply_text(help_msg)
        else:
            await m.reply_text(
                tlang(m, "start.public_help").format(help_option=help_option),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Help",
                                url=f"t.me/{me}?start={help_option}",
                            ),
                        ],
                    ],
                ),
            )
        return
    if m.chat.type == "private":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                *gen_cmds_kb(),
                [
                    InlineKeyboardButton(
                        f"« {tlang(m, 'general.back_btn')}",
                        callback_data="start_back",
                    ),
                ],
            ],
        )
        msg = tlang(m, "general.commands_available")
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Help",
                        url=f"t.me/{me}?start=help",
                    ),
                ],
            ],
        )
        msg = tlang(m, "start.pm_for_help")

    await m.reply_text(
        msg,
        reply_markup=keyboard,
    )

    return


@Alita.on_callback_query(filters.regex("^get_mod."))
async def get_module_info(_, q: CallbackQuery):

    module = q.data.split(".")[1]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    "« " + tlang(q, "general.back_btn"),
                    callback_data="commands",
                ),
            ],
        ],
    )
    await q.message.edit_text(
        HELP_COMMANDS[module],
        parse_mode="markdown",
        reply_markup=keyboard,
    )
    await q.answer()
    return


@Alita.on_callback_query(filters.regex("^infos$"))
async def infos(c: Alita, q: CallbackQuery):

    _owner = await c.get_users(OWNER_ID)
    res = tlang(q, "start.info_page").format(
        Owner=(
            f"{_owner.first_name} + {_owner.last_name}"
            if _owner.last_name
            else _owner.first_name
        ),
        ID=OWNER_ID,
        version=VERSION,
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    f"« {tlang(q, 'general.back_btn')}",
                    callback_data="start_back",
                ),
            ],
        ],
    )
    await q.message.edit_text(
        res,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
    await q.answer()
    return
