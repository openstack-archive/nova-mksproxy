nova-mksproxy
=============

This is Nova console proxy for instances running on VMware.
It requires Nova to support microversion 2.31 to work.

Usage
-----
1. Start the proxy with OpenStack admin credentials::

    $ source openrc admin admin
    $ nova-mksproxy --web /opt/share/noVNC

   by default it binds to ``0.0.0.0:6090``

2. Configure Nova to enable MKS consoles::

    [mks]
    enabled = True
    mksproxy_base_url = http://<host>:<port>/vnc_auto.html

3. Use nova CLI to get a console URL::

    $ nova get-mks-console cirros

