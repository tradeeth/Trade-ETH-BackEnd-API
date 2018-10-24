# ForkDelta Backend
# https://github.com/forkdelta/backend-replacement
# Copyright (C) 2018, Arseniy Ivanov and ForkDelta Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from os import environ

HTTP_PROVIDER_URL = environ.get("HTTP_PROVIDER_URL")
WS_PROVIDER_URL = environ.get("WS_PROVIDER_URL")

ALLOWED_ORIGIN_SUFFIXES = environ.get("ALLOWED_ORIGIN_SUFFIXES",
                                      "localhost").split(",")

ED_CONTRACT_ADDR =  environ.get("CONTRACT_ADDRESS")
with open('tradeeth.sol.json') as f:
    import json
    ED_CONTRACT_ABI = json.load(f)
ED_WS_SERVERS = [
    "wss://websocket_server/socket.io/?EIO=3&transport=websocket",
]

POSTGRES_HOST = "postgres"
POSTGRES_DB = environ.get("POSTGRES_DB")
POSTGRES_USER = environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")

FRONTEND_CONFIG_FILE = "http://admin.tradeeth.io/api/config/main"
STOPPED_TOKENS = (
    "0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0",  # EOS: https://block.one/news/community-reminder-eos-token-registration-and-freeze/
    "0x7e9e431a0b8c4d532c745b1043c7fa29a48d4fba",  # eosDAC: https://twitter.com/eosdac/status/1002657571197673475?lang=en
    "0xa5fd1a791c4dfcaacc963d4f73c6ae5824149ea7",  # JNT: https://t.me/jibrel_network/129713
)
