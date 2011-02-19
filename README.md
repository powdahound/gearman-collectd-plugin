gearman-collectd-plugin
=====================

A [Gearman](http://gearman.org) plugin for [collectd](http://collectd.org) using collectd's [Python plugin](http://collectd.org/documentation/manpages/collectd-python.5.shtml).

Data captured includes:

 * Pending jobs in each queue
 * Running jobs in each queue
 * Available workers for each queu

Install
-------
 1. Place gearmand_info.py in /opt/collectd/lib/collectd/plugins/python (assuming you have collectd installed to /opt/collectd).
 2. Configure the plugin (see below).
 3. Restart collectd.

Configuration
-------------
Add the following to your collectd config.

    <LoadPlugin python>
      Globals true
    </LoadPlugin>
    
    <Plugin python>
      ModulePath "/opt/collectd/lib/collectd/plugins/python"
      Import "gearmand_info"
    
      <Module gearmand_info>
        Host "localhost"
        Port 4730
        Verbose false
      </Module>
    </Plugin>

Requirements
------------
 * collectd 4.9+
