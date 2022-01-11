# MIT License
#
# Copyright (c) 2021 TrigonDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import ipaddress as ipaddr
from typing import Union

from .base_type import SqlType


class CIDR(SqlType[Union[ipaddr.IPv4Network, ipaddr.IPv6Network]]):
    """IPv4 and IPv6 networks. 7 or 19 bytes.

    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-CIDR
    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-INET-VS-CIDR
    """

    _sql = "CIDR"


class INET(
    SqlType[
        Union[
            ipaddr.IPv6Address,
            ipaddr.IPv6Interface,
            ipaddr.IPv4Address,
            ipaddr.IPv4Interface,
        ]
    ]
):
    """IPv4 and IPv6 hosts and networks. 7 or 19 bytes.

    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-INET
    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-INET-VS-CIDR
    """

    _sql = "INET"


class MacAddr(SqlType[str]):
    """MAC addresses. 6 bytes.

    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-MACADDR
    """

    _sql = "MACADDR"


class MacAddr8(SqlType[str]):
    """MAC address (EUI-64 format). 8 bytes.

    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-MACADDR8
    """

    _sql = "MACADDR8"
