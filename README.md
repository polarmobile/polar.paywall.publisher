# Polar Mobile Publisher Paywall: Sample Server # 

This project is a simple sample web server for the Polar Mobile Paywall API.


 * Server only accessible through HTTPS
 * Under no circumstances should an HTTP server be run.

## Contents ##

 * __Definitions__: Definitions of bolded terms used throughout this document.
 * __Overview__: An overview of the system as a whole.
 * __Deployment__: An overview of how the server should be deployed.
 * __Errors__: An overview of error reporting.

## Definitions ##

This document describes the definitions used throughout this document.

### Architecture ###

Definitions related to the systems architecture.

 * __Client__ := Client devices, like iPhones, Androids and Blackberries.
 * __Server__ := Polar Mobile's server.
 * __Publisher__ := The publishers server.

### Business ###

Definitions related to the business domain.

 * __Entitilement Mechanism__ := A way users can access protected content.
    * __Subscription__ := An __entitilement mechanism__ where the user pays a recurring fee.
        * __Proxy Subscription__ := __Subscriptions__ managed by the __Publisher__.
        * __Managed Subscription__ := __Subscriptions__ managed by the __Server__.
 * __Product__ := Content that is protected.
 * __Seller__ := A legal entity that provides the content.
 * __Product Association__ := Association between __Entitlement Mechanism__ and __Product__.
 * __Product Allocation__ := When a user gains access to a __Product__.

## Overview ##

This section gives a broad overview of the paywall system as a whole.

### Objective ###

The point of this API is to allow publishers to password protect their
publications.

### Moving Parts ###

 * __Client__ := Client devices, like iPhones, Androids and Blackberries.
 * __Server__ := Polar Mobile's server.
 * __Publisher__ := The publishers server.

The basic operation is as follows. First the user logs in. The __client__ uses
those credentials to ask the __server__ for a session key. The __server__ will
then ask the __publisher__ for the key. The __publisher__ will then send the
key to the server, who will send it back to the client.

Next, when a __client__ wants to access protected content, they will send the
key with the request, which will get proxied by the __server__ to the
__publisher__. If the client has access to the content, the __publisher__ will
return successfully and the __server__ will deliver the content to the
__client__.

### API ###

An overview of the communication that happens between the __client__ and the
__server__.

### Client to Server ###

 * __Listing__: Obtain a listing of all __products__.
 * __Authenticate__: Send user credentials to the __server__ and get a key back.
    * Done on a per product basis.
 * __Product Access__: Request content from the server with a key.
    * Done via a new version of our editorial APIs.

### Server to Publisher ###

 * __Authenticate__: Send user credentials to the __publisher__ and get a key back.
 * __Product Access__: Request premission to serve content to the client.

## Deployment ##

The __publisher__ server is deployed as a HTTPS web server. It should under no
circumstances be exposed as an HTTP server as it may allow a third party to
obtain login credentials.

Note that routing rules should only allow traffic between Polar's server and
the Publisher's server over HTTPS (port 443).

## Errors ##

For Client Errors (400-series) and Server Errors (500-series), an error report
should be returned. Note that some error messages will be returned to the client
as printable text. It is up to the publisher to ensure the quality of these
messages.

### Error Reports ###

Error are encoded using json. The body of the error is a json dictionary with
a single key called "error". The "error" value is another dictionary with the
following parameters.

 * "id"
 * "code"
 * "message"
 * "resource"

#### id ####

"id" is an attribute that is claculated from the other values in the message.
To calculate the "id", you need to generate an SHA1 hash of the following
values in order:

 1. HTTP Header Values
  * Note that only the headers that start with HTTP- will be used.
 1. Date and Time
 1. Resource URI
 1. Originating IP Address

The date and time fields iso formatted values in UTC. Specifically, in the
format YYYY-MM-DDTHH:MM:SS.mmmmmm. The following is an example of a date
time value:

    "2012-02-10T19:06:31.996996"

The originating IP address is the contents of the REMOTE_ADDR field in the
HTTP header. An example of the implementation of this algorithm can be found
in the error.py file under the publisher directory.

#### code ####

This is a simple error code that both Polar's server and the client can use to
easily triage an error. Each entry point contains documentation on the error
codes it may return.

#### message ####

A description of the error.

#### message ####

The resource URI the request was attempting to access.

#### Example ####

Example Request:

    GET /paywallproxy/v1.0.0/json/auth/60c2c670ea6b3847b54eb0e4b2736e93 HTTP/1.1

Example Error Response:

    HTTP/1.1 404 NOT FOUND
    Content-Type: application/json
    Accept-Language: en
    
    {
        "error": {
            "id": "9137646716eb362d6eb07d893895b6dc",
            "code": "InvalidProduct",
            "message": "The specified article does not exist.",
            "resource": "/paywallproxy/v1.0.0/json/auth/60c2c670ea6b3847b54eb0e4b2736e93"
        }
    }

