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
import socket
import ssl

import mock
import testtools

from novaproxy import authd


class AuthdRequestHandler(testtools.TestCase):

    @mock.patch.object(socket, 'socket')
    @mock.patch.object(ssl, 'wrap_socket')
    def test_handshake(self, mock_wrap, mock_socket):
        msgs = ['220 Welcome',
                '331 Need password',
                '230 Login OK',
                '200 e6e4d191c0f9ebc6abc082d6e2eeeb5b7c90214d',
                '200 OK']

        def fake_recv(len):
            return msgs.pop(0)

        def fake_getpeercert(binary_form=True):
            return 'fake-certificate'

        sock = mock.MagicMock()
        sock.recv = fake_recv
        sock.getpeercert = fake_getpeercert
        mock_wrap.return_value = sock
        mock_socket.return_value = sock
        authd.handshake('host', 902, 'ticket', 'cfgFile',
                        'e6e4d191c0f9ebc6abc082d6e2eeeb5b7c90214d')

    @mock.patch.object(socket, 'socket')
    @mock.patch.object(ssl, 'wrap_socket')
    def test_handshake_invalid_thumbprint(self, mock_wrap, mock_socket):
        msgs = ['220 Welcome',
                '331 Need password',
                '230 Login OK',
                '200 e6e4d191c0f9ebc6abc082d6e2eeeb5b7c90214d',
                '200 OK']

        def fake_recv(len):
            return msgs.pop(0)

        def fake_getpeercert(binary_form=True):
            return 'fake-certificate'

        sock = mock.MagicMock()
        sock.recv = fake_recv
        sock.getpeercert = fake_getpeercert
        mock_wrap.return_value = sock
        mock_socket.return_value = sock
        self.assertRaises(Exception, authd.handshake, 'host', 902,
                          'ticket', 'cfgFile', 'invalid-thumbprint')

    @mock.patch.object(socket, 'socket')
    @mock.patch.object(ssl, 'wrap_socket')
    def test_handshake_invalid_2nd_thumbprint(self, mock_wrap, mock_socket):
        msgs = ['220 Welcome',
                '331 Need password',
                '230 Login OK',
                '200 invalid-2nd-thumbprint',
                '200 OK']

        def fake_recv(len):
            return msgs.pop(0)

        def fake_getpeercert(binary_form=True):
            return 'fake-certificate'

        sock = mock.MagicMock()
        sock.recv = fake_recv
        sock.getpeercert = fake_getpeercert
        mock_wrap.return_value = sock
        mock_socket.return_value = sock
        self.assertRaises(Exception, authd.handshake, 'host', 902,
              'ticket', 'cfg', 'e6e4d191c0f9ebc6abc082d6e2eeeb5b7c90214d')
