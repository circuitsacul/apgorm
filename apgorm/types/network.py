from __future__ import annotations

import ipaddress as ipaddr
from typing import Union

from .base_type import SqlType


class CIDR(SqlType[Union[ipaddr.IPv4Network, ipaddr.IPv6Network]]):
    sql_name = "CIDR"


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
    sql_name = "INET"


class MacAddr(SqlType[str]):
    sql_name = "MACADDR"


class MacAddr8(SqlType[str]):
    sql_name = "MACADDR8"
