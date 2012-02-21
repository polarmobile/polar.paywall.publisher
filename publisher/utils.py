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

# Used to contain the itty response with the proper headers.
from itty import Response


def report_error(code, message, request, status):
    '''
    For Client Errors (400-series) and Server Errors (500-series), an error
    report should be returned. Note that some errors will be returned to the
    client on their device. It is up to the publisher to ensure the  quality
    of the content of these messages.

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

    This function takes the error code, message, request object and the status
    (http error code) and creates a response object with the content type
    properly set.
    '''
    # Create a hash table to store the result.
    result = {}
    result['error'] = {}

    # Store the error values. Note that the order of insertion does not
    # matter as this is a hash table.
    result['error']['code'] = code
    result['error']['message'] = message
    result['error']['resource'] = request.path

    # Convert the result into json and then package it in an itty response.
    type = 'application/json'
    return Response(dumps(result), content_type=type, status=status)


def check_base_url(request, api, version, format):
    '''
    The base url for all entry points in this API is as follows:

        /:api/:version/:format

    For this particular project, the api will always be "paywallproxy", the
    supported version is "v1.0.0" and the only supported format is "json".

    This function examines these common parameters, and raises errors if the
    the parameters are incorrect. If the parameters are correct, this function
    returns the None object.

    The errors this function returns are documented below.

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        InvalidAPI:

            Returned when the publisher does not recognize the requested api.

            Code: InvalidAPI
            Message: The requested api is not implemented: <api>
            HTTP Error Code: 404

        InvalidVersion:

            Returned when the publisher does not recognize the requested
            version.

            Code: InvalidVersion
            Message: The requested version is not implemented: <version>
            HTTP Error Code: 404

        InvalidFormat:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidFormat
            Message: The requested format is not implemented: <format>
            HTTP Error Code: 404
    '''
    # Check to make sure the api is correct.
    if api != 'paywallproxy':
        code = 'InvalidAPI'
        message = 'The requested api is not implemented: ' + str(api)
        status = 404
        return report_error(code, message, request, status)

    # Check to make sure the version is correct.
    elif version != 'v1.0.0':
        code = 'InvalidVersion'
        message = 'The requested version is not implemented: ' + str(version)
        status = 404
        return report_error(code, message, request, status)

    # Check to make sure the format is correct.
    elif format != 'json':
        code = 'InvalidFormat'
        message = 'The requested format is not implemented: ' + str(format)
        status = 404
        return report_error(code, message, request, status)

    # No errors were found, so return None.
    return None
