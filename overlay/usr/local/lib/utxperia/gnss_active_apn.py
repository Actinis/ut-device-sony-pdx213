#!/usr/bin/python3
# SPDX-License-Identifier: MIT
"""Return an already active IPv4 internet APN, never activate a SIM or log IDs."""
import dbus,sys
def main():
    bus=dbus.SystemBus()
    manager=dbus.Interface(bus.get_object('org.ofono','/'),'org.ofono.Manager')
    contexts=[]
    for path, properties in manager.GetModems(timeout=3):
        if not properties.get('Online') or 'org.ofono.ConnectionManager' not in properties.get('Interfaces',[]):continue
        modem=dbus.Interface(bus.get_object('org.ofono',path),'org.ofono.ConnectionManager')
        for context,props in modem.GetContexts(timeout=3):
            if props.get('Active') and props.get('Type')=='internet' and props.get('Settings',{}).get('Address') and props.get('AccessPointName'):
                contexts.append(str(props['AccessPointName']))
    if len(contexts)!=1:sys.exit(1)
    print(contexts[0])

if __name__ == "__main__":
    try:
        main()
    except dbus.DBusException:
        sys.exit(1)
