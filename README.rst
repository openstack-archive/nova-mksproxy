nova-mksproxy
=============

This is Nova console proxy for instances running on VMware.
It requires Nova to support microversion 2.31 to work.

Usage with Devstack
-------------------
There is a devstack plugin for ``nova-mksproxy``, so simply add this to your ``local.conf``::

    [[local|localrc]]
    enable_plugin nova-mksproxy https://github.com/openstack/nova-mksproxy

The plugin will enable MKS consoles in Nova and will start the proxy on port 6090. Use nova CLI to get a console URL::

    $ nova get-mks-console <instance_name>

