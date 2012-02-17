#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012, Polar Mobile.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name Polar Mobile nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL POLAR MOBILE BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Used to process the http request.
from itty import post, run_itty, get

# Regex constants used to match URLs.
API = r'/(?P<api>\w+)'
VERSION = r'/(?P<version>v[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,})'
FORMAT = r'/(?P<format>\w+)'
PRODUCT_CODE = r'/(?P<product_code>\w+)'

@get(API + VERSION + FORMAT + r'/auth' + PRODUCT_CODE)
def auth(request, api, version, format, product_code):
    '''
    Attempt an authentication for a product using supplied credentials. If
    successful, a session key is obtained that can be used for requests to
    protected resources/content. The base URL scheme for this entry point is:

    /:api/:version/:format/auth/:productcode

    In this particular case, the api is "paywallproxy" and the version is
    v1.0.0. Currently, the only supported format is "json". The URL for
    this entry point therefore looks like:

    /paywallproxy/v1.0.0/json/auth/:productcode

    '''
    return '%s, %s, %s, %s' % (api, version, format, product_code)

run_itty(host='0.0.0.0',port=8080)
