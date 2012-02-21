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

# Used to process unhandled http errors.
from itty import error

# Used to report errors.
from publisher.utils import report_error


@error(500)
def handle_500(request, exception):
    '''
    This function handles any uncaught HTTP 500 errors. Remember that 5xx type
    HTTP errors should be accompanied by an error report. While it is not
    necessary or feasible (HTTP Proxies can generate errors, for example) to
    handle all uncaught exceptions, handling the HTTP 500 exception explicitly
    lets the publisher control the debugging information exposed.

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

            Thrown when an uncaught exception is raised by the publisher.

            Code: InternalError
            Message: An internal server error occurred.
            HTTP Error Code: 500
    '''
    # Generate the error report.
    code = 'InternalError'
    message = 'An internal server error occurred.'
    status = 500

    # Call report_error and get the result.
    result = report_error(code, message, request, status)

    # Return the result.
    return result


@error(404)
def handle_404(request, exception):
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

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        NoHandler:

            Thrown when the URL could not be routed to a handler. This error
            code should be thrown when the web framework does not understand
            the request being issued. It would imply that the API that the
            Polar server expects is not implemented on the publisher.

            Code: NoHandler
            Message: No handler could be found for the requested resource.
            HTTP Error Code: 404
    '''
    # Generate the error report.
    code = 'NoHandler'
    message = 'No handler could be found for the requested resource.'
    status = 404

    # Call report_error and get the result.
    result = report_error(code, message, request, status)

    # Return the result.
    return result
