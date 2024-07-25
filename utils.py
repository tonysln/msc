#!/usr/bin/python3

import asyncio
from textual.widgets import Static



def update_static(screen, idd, text, append=False) -> None:
    """Utility function to update static screen object"""

    s = screen.query_one(f'#{idd}', Static)
    newtext = text if not append else s.renderable + text
    s.update(newtext)


def validate_config_params(log, backend, nname, npass, npass2) -> bool:
    """Validate the given params: SSID and password for an AP"""

    if not backend or not nname or not npass or len(nname) < 2 or len(nname) > 32 or len(npass) < 8 or len(npass) > 128:
        log.clear()
        log.write_line('[!] Make sure your network name is valid and password has at least 8 characters!')
        return False

    if npass != npass2:
        log.clear()
        log.write_line('[!] The passwords do not match!')
        return False

    return True


async def run_cmd_async(cmd):
    """Run the given command asynchronously and return output"""
    
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode(), stderr.decode()
