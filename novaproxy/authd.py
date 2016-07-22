# Copyright (c) 2016 VMware Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import Cookie
import hashlib
import json
import os
import socket
import ssl
import urlparse

import websockify


VMAD_OK = 200
VMAD_WELCOME = 220
VMAD_LOGINOK = 230
VMAD_NEEDPASSWD = 331
VMAD_USER_CMD = "USER"
VMAD_PASS_CMD = "PASS"
VMAD_THUMB_CMD = "THUMBPRINT"
VMAD_CONNECT_CMD = "CONNECT"


def expect(sock, code):
    line = sock.recv(1024)
    recv_code, msg = line.split()[0:2]
    recv_code = int(recv_code)
    if code != recv_code:
        raise Exception('Expected %d but received %d' % (code, recv_code))
    return msg


def handshake(host, port, ticket, cfg_file, thumbprint):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    expect(sock, VMAD_WELCOME)
    sock = ssl.wrap_socket(sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    cert = sock.getpeercert(binary_form=True)
    h = hashlib.sha1()
    h.update(cert)
    if thumbprint != h.hexdigest():
        raise Exception("Server thumbprint doesn't match")
    sock.write("%s %s\r\n" % (VMAD_USER_CMD, ticket))
    expect(sock, VMAD_NEEDPASSWD)
    sock.write("%s %s\r\n" % (VMAD_PASS_CMD, ticket))
    expect(sock, VMAD_LOGINOK)
    rand = os.urandom(12)
    rand = base64.b64encode(rand)
    sock.write("%s %s\r\n" % (VMAD_THUMB_CMD, rand))
    thumbprint2 = expect(sock, VMAD_OK)
    thumbprint2 = thumbprint2.replace(':', '').lower()
    sock.write("%s %s mks\r\n" % (VMAD_CONNECT_CMD, cfg_file))
    expect(sock, VMAD_OK)
    sock2 = ssl.wrap_socket(sock)
    cert2 = sock2.getpeercert(binary_form=True)
    h = hashlib.sha1()
    h.update(cert2)
    if thumbprint2 != h.hexdigest():
        raise Exception("Second thumbprint doesn't match")
    sock2.write(rand)
    return sock2


class AuthdRequestHandler(websockify.ProxyRequestHandler):

    @classmethod
    def set_nova_client(cls, nova_client):
        cls._nova_client = nova_client

    def new_websocket_client(self):
        # The nova expected behavior is to have token
        # passed to the method GET of the request
        parse = urlparse.urlparse(self.path)
        query = parse.query
        token = urlparse.parse_qs(query).get("token", [""]).pop()
        if not token:
            # NoVNC uses it's own convention that forward token
            # from the request to a cookie header, we should check
            # also for this behavior
            hcookie = self.headers.getheader('cookie')
            if hcookie:
                cookie = Cookie.SimpleCookie()
                cookie.load(hcookie)
                if 'token' in cookie:
                    token = cookie['token'].value

        resp, body = self._nova_client.client.get(
            '/os-console-auth-tokens/%s' % token)
        # TODO check response
        connect_info = body['console']
        host = connect_info['host']
        port = connect_info['port']
        internal_access_path = connect_info['internal_access_path']
        mks_auth = json.loads(internal_access_path)
        ticket = mks_auth['ticket']
        cfg_file = mks_auth['cfgFile']
        thumbprint = mks_auth['thumbprint']

        tsock = handshake(host, port, ticket, cfg_file, thumbprint)

        # Start proxying
        try:
            self.do_proxy(tsock)
        except Exception:
            if tsock:
                tsock.shutdown(socket.SHUT_RDWR)
                tsock.close()
                self.vmsg("%(host)s:%(port)s: Target closed" %
                          {'host': host, 'port': port})
            raise
