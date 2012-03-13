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

# Used to process http errors before they are send back.
from itty import error, Response

# Used to check for json encoded errors.
from publisher.utils import (JsonBadSyntax, JsonUnauthorized, JsonForbidden,
                             JsonNotFound, JsonAppError)

# Used to encode default errors, if a non-json error is encountered.
from publisher.utils import encode_error


@error(400)
def bad_syntax(request, exception):
    '''
    This function handles 400 errors. Since no other part of the itty
    framework throws 400 errors it is safe to assume that all exceptions are
    json encoded.
    '''
    # Ensure that the exception is json encoded.
    assert isinstance(exception, JsonBadSyntax) == True

    # All exceptions handled by this function are json encoded 403 errors.
    content_type = 'application/json'
    status = 404

    # The authorization token depends on the request and it needs to be
    # mirrored back to the client as per the API. Unfortunately, we can't
    # guarantee that the header is in the request, so we need to check.
    headers = []
    if 'HTTP_AUTHORIZATION' in request._environ:
        authorization = request._environ['HTTP_AUTHORIZATION']
        headers.append(('Authorization', authorization))

    # The content is json encoded by the report_error function in utils.py.
    # In order to report the error, simply cast the error as a string.
    content = unicode(exception)
    response = Response(content, headers, status, content_type)
    return response.send(request._start_response)


@error(401)
def unauthorized(request, exception):
    '''
    This function handles 401 errors. Since no other part of the itty
    framework throws 401 errors it is safe to assume that all exceptions are
    json encoded.
    '''
    # Ensure that the exception is json encoded.
    assert isinstance(exception, JsonUnauthorized) == True

    # All exceptions handled by this function are json encoded 403 errors.
    content_type = 'application/json'
    status = 401
    headers = []

    # The authorization token depends on the request and it needs to be
    # mirrored back to the client as per the API. Unfortunately, we can't
    # guarantee that the header is in the request, so we need to check.
    if 'HTTP_AUTHORIZATION' in request._environ:
        authorization = request._environ['HTTP_AUTHORIZATION']
        headers.append(('Authorization', authorization))

    # The content is json encoded by the report_error function in utils.py.
    # In order to report the error, simply cast the error as a string.
    content = unicode(exception)
    response = Response(content, headers, status, content_type)
    return response.send(request._start_response)


@error(403)
def forbidden(request, exception):
    '''
    This function handles 403 errors. Since no other part of the itty
    framework throws 403 errors with the exception of static file serving
    (which is not in use in this project), it is safe to assume that all
    exceptions are json encoded.
    '''
    # Ensure that the exception is json encoded.
    assert isinstance(exception, JsonForbidden) == True

    # All exceptions handled by this function are json encoded 403 errors.
    content_type = 'application/json'
    status = 403
    headers = []

    # The authorization token depends on the request and it needs to be
    # mirrored back to the client as per the API. Unfortunately, we can't
    # guarantee that the header is in the request, so we need to check.
    if 'HTTP_AUTHORIZATION' in request._environ:
        # Get the token and append it to the headers.
        authorization = request._environ['HTTP_AUTHORIZATION']
        headers.append(('Authorization', authorization))

    # The content is json encoded by the report_error function in utils.py.
    # In order to report the error, simply cast the error as a string.
    content = unicode(exception)
    response = Response(content, headers, status, content_type)
    return response.send(request._start_response)


@error(404)
def not_found(request, exception):
    '''
    This function handles any uncaught HTTP 404 errors. Remember that 4xx type
    HTTP errors should be accompanied by an error report. A 404 error is a
    common error for many web frameworks; particularly those that use regex to
    route requests. Returning a proper error report makes diagnosing such
    problems easier.

    If the Polar server receives a 4xx error that does not have a report, it
    will first try to decode the body of the post request using json. This
    process will fail, and the server will then store the body of the post
    request (as opposed to its error code, message and resource) and continue
    processing.

    Errors:

        NoHandler:

            Thrown when the URL could not be routed to a handler. This error
            code should be thrown when the web framework does not understand
            the request being issued. It would imply that the API that the
            Polar server expects is not implemented on the publisher.

            Code: NoHandler
            Message: An error occurred. Please contact support.
            Debug: No handler could be found for the requested resource.
            HTTP Error Code: 404
            Required: No
    '''
    # All exceptions handled by this function are json encoded 404 errors.
    content_type = 'application/json'
    status = 404
    headers = []

    # The authorization token depends on the request and it needs to be
    # mirrored back to the client as per the API. Unfortunately, we can't
    # guarantee that the header is in the request, so we need to check.
    if 'HTTP_AUTHORIZATION' in request._environ:
        # Get the token and append it to the headers.
        authorization = request._environ['HTTP_AUTHORIZATION']
        headers.append(('Authorization', authorization))

    # The content is determined below.
    content = ''

    # If the exception is json encoded, we can use the content directly.
    if isinstance(exception, JsonNotFound) == True:
        content = unicode(exception)

    # If the exception is not an AppError exception, then send a generic
    # exception, encoded as json.
    else:
        url = request.path
        code = 'NoHandler'
        message = 'An error occurred. Please contact support.'
        debug = 'No handler could be found for the requested resource.'
        content = encode_error(url, code, message, debug)

    response = Response(content, headers, status, content_type)
    return response.send(request._start_response)


@error(500)
def internal_error(request, exception):
    '''
    This function handles all 500 type errors before they are sent back to the
    requester. 5xx type HTTP errors should be accompanied by an error report.
    While it is not necessary or feasible (HTTP Proxies can generate errors,
    for example) to handle all exception types, handling the HTTP 500 exception
    explicitly lets the publisher control the debugging information exposed.

    Some web frameworks may be verbose about an http 500 error, providing
    detailed debugging information that may compromise the system. It is up to
    the publisher to ensure that these features are well controlled.

    If the Polar server receives a 5xx error that does not have a report, it
    will first try to decode the body of the post request using json. This
    process will fail, and the server will then store the body of the post
    request (as opposed to its error code, message and resource) and continue
    processing.

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        InternalError:

            Thrown when no exception object is provided (the nature of the
            exception is unknown).

            Code: InternalError
            Message: An error occurred. Please contact support.
            Message: An internal server error occurred. Please check logs.
            HTTP Error Code: 500
            Required: No
    '''
    # All exceptions handled by this function are json encoded 500 errors.
    content_type = 'application/json'
    status = 500
    headers = []

    # The authorization token depends on the request and it needs to be
    # mirrored back to the client as per the API. Unfortunately, we can't
    # guarantee that the header is in the request, so we need to check.
    if 'HTTP_AUTHORIZATION' in request._environ:
        # Get the token and append it to the headers.
        authorization = request._environ['HTTP_AUTHORIZATION']
        headers.append(('Authorization', authorization))

    # The content is determined below.
    content = ''

    # HTTP 500 exceptions may be of any type. If the type is JsonAppError then
    # the exception has been json encoded. If it is not, then we need to
    # substitute the message with a default message.
    if isinstance(exception, JsonAppError) == True:
        content = unicode(exception)

    # If the exception is not a JsonAppError exception, then send a generic
    # exception.
    else:
        url = request.path
        code = 'InternalError'
        message = 'An error occurred. Please contact support.'
        debug = 'An internal server error occurred. Please check logs.'
        content = encode_error(url, code, message, debug)

    response = Response(content, headers, status, content_type)
    return response.send(request._start_response)
