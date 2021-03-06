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


from functools import reduce
from glob import glob
from operator import getitem
from os import path

from pyrogram.types import CallbackQuery
from ujson import load

from alita import ENABLED_LOCALES as enabled_locales
from alita.db import lang_db as db


def getFromDict(dict_data, list_data):
    """Get data from list of keys."""
    return reduce(getitem, list_data, dict_data)


def cache_localizations(files):
    """Get all translated strings from files."""
    ldict = {lang: {} for lang in enabled_locales}
    for file in files:
        lang_name = file.split(path.sep)[1]
        lang_data = load(open(file, encoding="utf-8"))
        ldict[lang_name.replace(".json", "")] = lang_data
    return ldict


# Get all translation files
lang_files = []
for locale in enabled_locales:
    lang_files += glob(path.join("locales", f"{locale}.json"))
lang_dict = cache_localizations(lang_files)


def tlang(m, user_msg):
    """Main function for getting the string of preferred language."""

    m_args = user_msg.split(".")  # Split in a list

    # Get Chat
    if isinstance(m, CallbackQuery):
        m = m.message

    # Get Chat
    chat = m.chat

    # Get language of user from database, default = 'en' (English)
    lang = db.get_lang(chat.id, chat.type) or "en"

    # Get lang
    m_args.insert(0, lang)

    # Raise exception if lang_code not found
    if lang not in enabled_locales:
        raise Exception("Unknown Language Code found!")

    return getFromDict(lang_dict, m_args)
