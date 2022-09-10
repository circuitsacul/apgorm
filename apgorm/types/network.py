from __future__ import annotations

import ipaddress as ipaddr
from typing import Iterable, Union

from .base_type import SqlType


class CIDR(SqlType[Union[ipaddr.IPv4Network, ipaddr.IPv6Network]]):
    """IPv4 and IPv6 networks. 7 or 19 bytes.

    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-CIDR
    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-INET-VS-CIDR
    """

    __slots__: Iterable[str] = ()

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

    __slots__: Iterable[str] = ()

    _sql = "INET"


class MacAddr(SqlType[str]):
    """MAC addresses. 6 bytes.

    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-MACADDR
    """

    __slots__: Iterable[str] = ()

    _sql = "MACADDR"


class MacAddr8(SqlType[str]):
    """MAC address (EUI-64 format). 8 bytes.

    https://www.postgresql.org/docs/14/datatype-net-types.html#DATATYPE-MACADDR8
    """

    __slots__: Iterable[str] = ()

    _sql = "MACADDR8"
