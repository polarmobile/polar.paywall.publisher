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

# Used to encode the resulting error into json.
from json import dumps


def report_error(code, message, resource):
    '''
    For Client Errors (400-series) and Server Errors (500-series), an error
    report should be returned. Note that some errors will be returned to the
    client as printable text. It is up to the publisher to ensure the
    quality of the content of these messages.

    Error are encoded using json. The body of the error is a json map with a
    key called "error". The "error" value is another map with the following
    parameters:

     * "code"
     * "message"
     * "resource"

    "code" is a string error code that both Polar's server and the client
    can use to easily triage an error. Each entry point in this project
    contains documentation on the error codes it may return.

    "message" is a description of the error. Note that this message should
    never contain a users password.

    "resource" is the resource URI the request was attempting to access.

    This function takes a hash table of HTTP headers and strings containing
    the remaining characters and produces a string containing the json
    encoded response.
    '''
    # Create a hash table to store the result.
    result = {}
    result['error'] = {}

    # Store the error values. Note that the order of insertion does not
    # matter as this is a hash table.
    result['error']['code'] = code
    result['error']['message'] = message
    result['error']['resource'] = resource

    # Convert the result into json and return the string.
    return dumps(result)
