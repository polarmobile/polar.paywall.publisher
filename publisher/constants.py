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

# Regex constants used to match URLs. These constants are used by itty to
# route http requests to handlers. Their use can be found in auth.py and
# validate.py.
API = r'/(?P<api>\w+)'
VERSION = r'/(?P<version>v[0-9]{1,}\.[0-9]{1,}\.[0-9]{1,})'
FORMAT = r'/(?P<format>\w+)'
PRODUCT_CODE = r'/(?P<product_code>\w+)'

# The number of hours before a session key times out. Note that this value is
# set intentionally low so that development tests hit edge cases more
# frequently.
SESSION_TIMEOUT = 2

# The users dictionary is used by the model class to initialize its own record
# of users. When a model class instance is first created, it copies the users
# dictionary. To add new users to the system, modify the following structure.
users = {}

# Create a users for testing purposes.
users['user01'] = {}
users['user01']['valid'] = True
users['user01']['products'] = ['product01', 'product02']
users['user01']['password'] = 'test'
# Note that although we don't add any session ids here, we have to initialize
# the session id dictionary.
users['user01']['session ids'] = {}

# Create a users for testing purposes that is not valid.
users['user02'] = {}
users['user02']['valid'] = False
users['user02']['products'] = ['product01', 'product02']
users['user02']['password'] = 'test'
users['user02']['session ids'] = {}
