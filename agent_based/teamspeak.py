#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  This file is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# <<<Teamspeak3>>>
# ConfigError: No
# QueryPortReachable: Yes
# AuthSuccess: Yes
# Version: 3.12.1
# Platform: Linux
# Build: 1585305527
# VirtualServer: (9987 online 0 32 0 yes 0 0)

from .agent_based_api.v1 import *
import time

RESERVED_SLOTS = 3

def parse_teamspeak3(string_table):
    parsed = {u'VirtualServer': {}}
    for line in string_table:
        if line[0][:-1] == "VirtualServer":
            data = {u'port': int(line[1][1:]),
                    u'status': line[2],
                    u'clientsonline': int(line[3]),
                    u'clientsmax': int(line[4]),
                    u'channels': int(line[5]),
                    u'autostart': line[6],
                    u'ingress': int(line[7]),
                    u'egress': int(line[8][:-1])}
            parsed[u'VirtualServer'][str(data['port'])] = data
        else:
            parsed[line[0][:-1]] = " ".join(line[1:])
    return parsed


def discover_teamspeak3(section):
    if section.get(u'Version'):
        yield Service(item = "Global")
    for port, vs in section['VirtualServer'].items():
        yield Service(item = str(port))


def check_teamspeak3(item, section):
    if section.get("ConfigError", "No").startswith("Yes"):
        yield Result(state=State.CRIT, summary=f"Config error!")
        return

    if section.get("QueryPortReachable", "No") == "No":
        yield Result(state=State.CRIT, summary=f"Server unrechable!")
        return

    if section.get("AuthSuccess", "No") == "No":
        yield Result(state=State.CRIT, summary=f"Unable to authenticate!")
        return

    if item == "Global":
        yield Result(state=State.OK, summary=f"Platform: {section['Platform']}, Version: {section['Version']} {section['Build']}")
        return


    if item not in section["VirtualServer"]:
        return

    server = section["VirtualServer"][item]

    summary = f"{server['status']} ({server['clientsonline']} clients, {server['channels']} channels), autostart {server['autostart']}" 

    state = State.OK
    if server["status"] != "online":
        state = State.CRIT
    if server['clientsonline'] >= (server["clientsmax"] - RESERVED_SLOTS):
        state = State.WARN

    now = time.time()

    value_store = get_value_store()

    yield Metric(name="if_in_octets", value=get_rate(value_store, f"teamspeak3.{item}.if_in_octets", now, server[u'ingress']))
    yield Metric(name="if_out_octets", value=get_rate(value_store, f"teamspeak3.{item}.if_out_octets", now, server[u'egress']))

    yield Metric(name="channels", value=server["channels"])

    yield Metric(name="current_users", value=server["clientsonline"], levels=(server["clientsmax"] - RESERVED_SLOTS, server["clientsmax"]), boundaries=(0.0, server["clientsmax"] + 1))

    yield Result(state=state, summary=summary)


register.agent_section(
    name = "Teamspeak3",
    parse_function = parse_teamspeak3,
)

register.check_plugin(
    name = "Teamspeak3",
    service_name = "Teamspeak3 %s",
    discovery_function = discover_teamspeak3,
    check_function = check_teamspeak3,
)
