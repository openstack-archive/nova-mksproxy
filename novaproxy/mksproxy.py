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
import os
import sys

import argparse
import authd
from novaclient import client
import websockify
import logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="MKS proxy host (default '0.0.0.0')",
                        default="0.0.0.0")
    parser.add_argument("--port", help="MKS proxy port (default 6090)",
                        type=int, default=6090)
    parser.add_argument("--web", help="web location", required=True)
    parser.add_argument("--verbose", help="verbose logging",
                        action="store_true", default=False)
    parser.add_argument("--username",
                        help="OpenStack username (default $OS_USERNAME)",
                        default=os.environ.get("OS_USERNAME"))
    parser.add_argument("--password",
                        help="OpenStack password (default $OS_PASSWORD)",
                        default=os.environ.get("OS_PASSWORD"))
    parser.add_argument("--project",
                        help="OpenStack project (default $OS_PROJECT_NAME or "
                             "$OS_TENANT_NAME)",
                        default=os.environ.get("OS_PROJECT_NAME",
                                   os.environ.get("OS_TENANT_NAME")))
    parser.add_argument("--auth-url",
                        help="OpenStack auth url (default $OS_AUTH_URL)",
                        default=os.environ.get("OS_AUTH_URL"))
    # TODO add log-file
    # TODO add cert/key
    args = parser.parse_args()

    if not args.username:
        sys.stderr.write('Missing OpenStack username\n')
        sys.exit(1)
    if not args.password:
        sys.stderr.write('Missing OpenStack password\n')
        sys.exit(1)
    if not args.project:
        sys.stderr.write('Missing OpenStack project\n')
        sys.exit(1)
    if not args.auth_url:
        sys.stderr.write('Missing OpenStack auth URL\n')
        sys.exit(1)

    websockify.websocketproxy.logger_init()
    logger = logging.getLogger(websockify.WebSocketProxy.log_prefix)
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    nova_client = client.Client("2.31", args.username, args.password,
                                args.project, args.auth_url, logger=logger)

    authd.AuthdRequestHandler.set_nova_client(nova_client)

    websockify.WebSocketProxy(
        listen_host=args.host,
        listen_port=args.port,
        verbose=args.verbose,
        web=args.web,
        file_only=True,
        RequestHandlerClass=authd.AuthdRequestHandler
    ).start_server()


if __name__ == '__main__':
    main()
