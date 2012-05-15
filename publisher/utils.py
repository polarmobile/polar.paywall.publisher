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

# Used to decode and encode post bodies that contain json encoded data.
# Note that in python 2.5 and 2.6 the json module is called simplejson.
# In Python 2.7 and onwards, json is used.
try:
    from json import dumps
except ImportError:
    from simplejson import dumps

# Used to generate exceptions.
from itty import RequestError, NotFound, AppError, Forbidden


class JsonBadSyntax(RequestError):
    '''
    Unfortunately the itty framework defines a minimal set of HTTP exceptions.
    To accommodate HTTP 400 errors (bad syntax), we need to inherit from the
    error base class and create a new exception. To differentiate between
    a normal exception, and an exception that is json encoded, the class name
    is prepended with json.
    '''
    status = 400


class JsonUnauthorized(RequestError):
    '''
    Unfortunately the itty framework defines a minimal set of HTTP exceptions.
    To accommodate HTTP 401 errors (unauthorized), we need to inherit from the
    error base class and create a new exception. To differentiate between
    a normal exception, and an exception that is json encoded, the class name
    is prepended with json.
    '''
    status = 401


class JsonForbidden(Forbidden):
    '''
    To differentiate between a normal exception, and an exception that has json
    encoded content, the class name is prepended with json.
    '''
    pass


class JsonNotFound(NotFound):
    '''
    To differentiate between a normal exception, and an exception that has json
    encoded content, the class name is prepended with json.
    '''
    pass


class JsonAppError(AppError):
    '''
    To differentiate between a normal exception, and an exception that has json
    encoded content, the class name is prepended with json.
    '''
    pass


def encode_error(url, code, message, debug=None):
    '''
    This utility function is called by raise_error to encode the url, code and
    message parameters. Errors are encoded using json. The body of the error is
    a json map with a key called "error" and an optional key called "debug".
    Under no circumstances should this object be passed secrets like passwords
    as they will be logged. The "error" value is another map with the following
    parameters:

     * "code"
     * "message"
     * "resource"

    "code" is a string error code that both Polar's server and the client
    can use to easily triage an error. Each entry point in this project
    contains documentation on the error codes it may return.

    "message" is a description of the error. This message is printed to the
    user.

    "resource" is the resource URL the request was attempting to access.

    The resulting json object may optionally contain a "debug" key. That key
    resolves to another map with at least a "message" key. Other keys can be
    added to aid in debugging. In this implementation, the debug parameter
    above is simply the debug message.

    This function takes the url, code and message and returns a json string
    containing the encoded values.
    '''
    result = {}
    result['error'] = {}
    result['error']['code'] = code
    result['error']['message'] = message
    result['error']['resource'] = url

    if debug:
        result['debug'] = {}
        result['debug']['message'] = debug

    # Encode the message as json and return.
    return dumps(result)


def raise_error(url, code, message, status, debug=None):
    '''
    For Client Errors (400-series) and Server Errors (500-series), an error
    report should be returned. Note that some errors will be returned to the
    client on their device. It is up to the publisher to ensure the  quality
    of the content of these messages. See the encode_error function for
    information regarding how errors are encoded.

    This function takes the url, error code, message and the status (http error
    code) and creates an exception object with the parameters encoded. It then
    raises the error. The itty framework will then catch these errors and add
    the proper header encodings. See error.py for more details.

    Currently, the only supported status codes are 400, 403, 404 and 500.
    In all cases, the traceback is hidden to prevent any details of the
    internal implementation from leaking outside the framework.
    '''
    # Encode the error as a json string.
    message = encode_error(url, code, message, debug)

    # Raise the appropriate error, based on the status. Note that the stack
    # trace is hidden to prevent any internal information from leaking.
    if status == 400:
        raise JsonBadSyntax(message, hide_traceback=True)
    elif status == 401:
        raise JsonUnauthorized(message, hide_traceback=True)
    elif status == 403:
        raise JsonForbidden(message, hide_traceback=True)
    elif status == 404:
        raise JsonNotFound(message, hide_traceback=True)
    else:
        # If the status is not supported, we use an error 500.
        raise JsonAppError(message, hide_traceback=True)


def check_base_url(url, api, version, format):
    '''
    The base url for all entry points in this API is as follows:

        /:api/:version/:format

    For this particular project, the api will always be "paywallproxy", the
    supported version is "v1.0.0" and the only supported format is "json".

    This function examines these common parameters, and raises errors if the
    parameters are incorrect.

    The errors this function returns are documented below.

    Errors:

        InvalidAPI:

            Returned when the publisher does not recognize the requested api.

            Code: InvalidAPI
            Message: An error occurred. Please contact support.
            Debug: The requested api is not implemented: <api>
            HTTP Error Code: 404

        InvalidVersion:

            Returned when the publisher does not recognize the requested
            version.

            Code: InvalidVersion
            Message: An error occurred. Please contact support.
            Debug: The requested version is not implemented: <version>
            HTTP Error Code: 404

        InvalidFormat:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidFormat
            Message: An error occurred. Please contact support.
            Debug: The requested format is not implemented: <format>
            HTTP Error Code: 404
    '''
    # All of the errors in this function share a common status and message.
    status = 404
    message = 'An error occurred. Please contact support.'

    # Check to make sure the api is correct.
    if api != 'paywallproxy':
        code = 'InvalidAPI'
        debug = 'The requested api is not implemented: ' + str(api)
        raise_error(url, code, message, status, debug)

    # Check to make sure the version is correct.
    if version != 'v1.0.0':
        code = 'InvalidVersion'
        debug = 'The requested version is not implemented: ' + str(version)
        raise_error(url, code, message, status, debug)

    # Check to make sure the format is correct.
    if format != 'json':
        code = 'InvalidFormat'
        debug = 'The requested format is not implemented: ' + str(format)
        raise_error(url, code, message, status, debug)
