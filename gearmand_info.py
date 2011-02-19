# gearman-collectd-plugin - gearmand_info.py
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; only version 2 of the License is applicable.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Authors:
#   Garret Heaton <powdahound at gmail.com>
#
# About this plugin:
#   This plugin uses collectd's Python plugin to record Gearmand information.
#
# collectd:
#   http://collectd.org
# Gearman:
#   http://gearman.org
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml

import collectd
import socket


# Host to connect to. Override in config by specifying 'Host'.
GEARMAND_HOST = 'localhost'

# Port to connect on. Override in config by specifying 'Port'.
GEARMAND_PORT = 4730

# Verbose logging on/off. Override in config by specifying 'Verbose'.
VERBOSE_LOGGING = False


def fetch_status():
    """Connect to Gearmand server and request status"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((GEARMAND_HOST, GEARMAND_PORT))
        log_verbose('Connected to Gearmand at %s:%s' % (GEARMAND_HOST, GEARMAND_PORT))
    except socket.error, e:
        collectd.error('gearmand_info plugin: Error connecting to %s:%d - %r'
                       % (GEARMAND_HOST, GEARMAND_PORT, e))
        return None
    fp = s.makefile('r')
    log_verbose('Sending info command')
    s.sendall('status\r\n')

    status = {}
    while True:
        data = fp.readline().strip()
        log_verbose('Received data: %r' % data)
        if not data or data == '.':
            break
        function, total, running, available_workers = data.split('\t')
        status[function] = {
            'total': total,
            'running': running,
            'available_workers': available_workers}

    s.close()
    return status

def configure_callback(conf):
    """Receive configuration block"""
    global GEARMAND_HOST, GEARMAND_PORT, VERBOSE_LOGGING
    for node in conf.children:
        if node.key == 'Host':
            GEARMAND_HOST = node.values[0]
        elif node.key == 'Port':
            GEARMAND_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        else:
            collectd.warning('gearmand_info plugin: Unknown config key: %s.'
                             % node.key)
    log_verbose('Configured with host=%s, port=%s' % (GEARMAND_HOST, GEARMAND_PORT))

def dispatch_value(info, key, type, type_instance=None):
    """Read a key from info response data and dispatch a value"""
    if key not in info:
        collectd.warning('gearmand_info plugin: Info key not found: %s' % key)
        return

    if not type_instance:
        type_instance = key

    value = int(info[key])
    log_verbose('Sending value: %s=%s' % (type_instance, value))

    val = collectd.Values(plugin='gearmand')
    val.type = type
    val.type_instance = type_instance
    val.values = [value]
    val.dispatch()

def read_callback():
    log_verbose('Read callback called')
    status = fetch_status()

    if not status:
        collectd.error('gearmand_info plugin: No status received')
        return

    # function stats
    for function, info in status.items():
        dispatch_value(info, 'total', 'gauge', "func-%s-total" % function)
        dispatch_value(info, 'running', 'gauge', "func-%s-running" % function)
        dispatch_value(info, 'available_workers', 'gauge',
                       "func-%s-available_workers" % function)

def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('gearmand_info plugin [verbose]: %s' % msg)


# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(read_callback)

