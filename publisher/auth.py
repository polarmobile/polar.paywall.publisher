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
    Overview:

        Attempt an authentication for a product using supplied credentials. If
        successful, a session key is obtained that can be used for requests to
        protected resources/content. The base URL scheme for this entry point
        is:

            /:api/:version/:format/auth/:productcode

        In this particular case, the api is "paywallproxy" and the version is
        v1.0.0. Currently, the only supported format is "json". The URL for
        this entry point therefore looks like:

            /paywallproxy/v1.0.0/json/auth/:productcode

        If the product cannot be found, an "InvalidProduct" error should be
        returned. This error will be returned to the client. A full list of
        errors that this entry point returns is available below. Client errors
        are proxied to the client. Server errors remain on Polar's server.

        An auth-scheme token is expected when a call is made to this API end
        point. It must conform to RFC 2617 specifications. The *Authorization*
        header has the follwoing form:

            Authorization: PolarPaywallProxyAuthv1.0.0

    Parameters:

        There are two sets of parameters that this API entry point serves. The
        first set consists of the product code, which is specified in the URL
        and the post body, which contains formatted json. Technical details
        will follow after a description of the parameters and an example will
        follow after that.

        The product code is part of the URL. It is a publisher-assigned unique
        identifier for this product. The publisher code is required.

        The post body is a json map with two keys. The first key is "device",
        which is a json map describing the device requesting authorization.
        This key is required. The second key is "authParams", which is
        optional.

        The "device" map contains three keys. "manufacturer" is the full name
        of the device manufacturer. "model" is the device's model number and
        name. "os_version" is a string that describes the version of the
        device's operating system.

        The contents of the "authParams" map will vary based on the settings
        on the Polar server. The keys of the map is the name of the parameter
        set on the server. The values of the map is the value entered by the
        user.

        Details regarding the various parameters are described below.

        Product Code:

            A publisher-assigned unique identifier for this product.

            Availability: >= v1.0.0
            Required: Yes
            Location: URL
            Format: URL
            Type: String
            Max Length: 256

        device:

            A json map describing the device requesting authorization.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: json map
            Max Length: N/A

        manufacturer:

            The full name of the device manufacturer. Contained in the "device"
            map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

        model:

            The device's model number and name. Contained in the "device" map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

        os_version:

            The version of the device's operating system. Contained in the
            "device" map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

        authParams:

            A map of the authentication parameters and their values.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: map
            Max Length: N/A

        authParams key:

            The name of the authentication parameter. Contained in the
            "authParams" map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

        authParams value:

            The user entered value of the authentication parameter. Contained
            in the "authParams" map.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 512

    Response:

        The following parameters are returned by this API end point. The
        resposne is json encoded. It has two keys; "sessionKey" and "products".
        "sessionKey" is a key that allows the client to reauthenticate without
        the supplied authentication parameters. "products" is a list of product
        identifiers that the user has access to.

        sessionKey:

            A key that allows the client to reauthenticate without the supplied
            authentication parameters.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 512

        products:

            A list of product identifiers that the user has access to.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: list
            Max Length: N/A

        product:

            A publisher-assigned unique identifier for this product that the
            user has access to. Contained in the "products" list.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

    Example:


    Client Errors:

        This section documents errors that are returned to the client. Note
        that the publisher is free to modify the content of these messages as
        they please.

        InvalidProduct:

            Thrown when the product code indicated is invalid.

            Code: InvalidProduct
            Message: The requested article could not be found.
            HTTP Error Code: 404

    Server Errors:

    '''
    return '%s, %s, %s, %s' % (api, version, format, product_code)

run_itty(host='0.0.0.0', port=8080)