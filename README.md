# cmk-teamspeak
Check_MK agent check for Teamspeak3 virtual server instances


## Setup
On your checkmk server:
 1. copy `agent_based/teamspeak.py` to `local/lib/python3/cmk/base/plugins/agent_based/teamspeak.py`

 On your teamspeak server:
  1. download Teamspeak3 agent plugin (from releases) to `/usr/lib/check_mk_agent/plugins/Teamspeak3`
  2. Create configuration (at `/etc/check_mk/teamspeak3.cfg`), see `teamspeak3.cfg.example` for details.

Then run service discovery.
