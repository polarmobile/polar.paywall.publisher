# Polar Mobile Publisher Paywall: Sample Server # 

This project is a simple sample web server for the Polar Mobile Paywall API.

## Contents ##

 * __Definitions__: Definitions of bolded terms used throughout this document.
	* __Architecture__
	* __Business__
 * __Overview__: An overview of the system as a whole.
	* __Objective__
	* __Moving Parts__
	* __API__
		* __Client to Server__
		* __Server to Publisher__
 * __Sample Publisher__: An overview of this project.
    * __Minimum Requirements__
    * __Installation__
    * __Moving Parts__
    * __utils.py__
    * __errors.py__
    * __auth.py__
    * __validate.py__
    * __model.py__
    * __credentials.py__
    * __test.py__
    * __runserver.py__
    * __setup.py__
 * __Deployment__: A brief description of how the server should be deployed.
 * __Errors__: A description of error reporting.
	* __Error Reports__
		* __id__
		* __code__
		* __resource__
		* __Example__
 * __Creating Users__: How to create test users and products.

## Definitions ##

This section describes the definitions used throughout this document.

### Architecture ###

Definitions related to the systems architecture.

 * __Client__ := Client devices, like iPhones, Androids and Blackberries.
 * __Server__ := Polar Mobile's server.
 * __Publisher__ := The publishers server.

### API ###

Definitions specific to this API.

 * __Client Error__ := An error message that is proxied to the client.
 * __Server Error__ := An error message that is stored on Polar's server.

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

The basic operation is as follows. First the user logs in. The __client__ uses
those credentials to ask the __server__ for a session key. The __server__ will
then ask the __publisher__ for the key. The __publisher__ will send the key to
the __server__, who will send it back to the client.

Next, when a __client__ wants to access protected content, they will send the
key with the request, which will get proxied by the __server__ to the
__publisher__. If the client has access to the content, the __publisher__ will
return successfully and the __server__ will deliver the content to the
__client__.

### API ###

This section is an overview of the communication that happens between the
__client__ and the __server__.

#### Client to Server ####

Note that this part of the API is not implemented by the __publisher's__ server.
They are described for completeness.

 * __Listing__: Obtain a listing of all __products__.
 * __Authenticate__: Send user credentials to the __server__ and get a key back.
 * __Product Access__: Request content from the server with a key.

#### Server to Publisher ####

 * __Authenticate__: Send user credentials to the __publisher__ and get a key back.
 * __Product Access__: Request permission to serve content to the client.

## Sample Publisher ##

This project is a sample implementation of a publisher server. It is written in
Python and meant to serve as a reference for implementation. The sample is not
fully functional and takes several shortcuts during implementation; it should
under no circumstances be used in production.

This section provides an overview of the sample and the contents of the various
files used in its implementation.

### Minimum Requirements ###

In order to run this sample, your system should have Python 2.6 or greater
installed and accessible from your command prompt. You will also need the
itty package, version 0.8.0 or greater.

### Installation ###

Note that installation is not required in order to test or run this sample. In
order to run this sample, issue the following command to your command prompt:

    python runserver.py

In order to install this sample, run the following command:

    python setup.py install

### Moving Parts ###

The sample implementation contains three main moving parts:
    
    * __auth.py__ := A request handler that authorizes the user.
    * __validate.py__ := A request handler that grants the user access to a product.
    * __model.py__ := A data store used to store and fetch usernames and passwords.

All other files simply provide supporting functionality to achieve these three
main operations.

### utils.py ###

This file contains two functions; report\_error and check\_base\_url.
report\_error formats error messages in a way expected by the __Polar Server__.
check\_base\_url validates the common parts of the url for all API entry points.

### errors.py ###

This file contains default handlers for two common http errors; 500 and 404.
While it is not mandatory to implement these handlers, having them will make
deployment more secure and easier to debug.

### auth.py ###

The auth function in this file is a handler used to authenticate a user, using
their supplied authentication credentials. It also supplies two additional
functions (check\_device, and check\_auth\_params) that check the validity of
the parameters passed to the auth function.

### validate.py ###
### model.py ###

In order to simplify the design of this sample, the state of the system is
stored in memory, as opposed to a database. The server is then run in a
single process with multiple threads. The model class contains a singleton
that stores the state of the server.

### credentials.py ###
### test.py ###

A series of unit tests used during the development of this project. To run the
unit test suite, issue the following command on your terminal:

    python test.py

### runserver.py ###

A script that is used to run the sample server on port 8080. Note that this
script should only ever be used for testing purposes and not in production. To
run this script directly, issue the following command on your terminal:

    python runserver.py

### setup.py ###

Used to install the sample server. Note that it is not necessary to install the
same server in order to test with it. The runserver.py script can be called
directly as long as the stated requirements are met.

## Deployment ##

The __publisher__ server is deployed as a HTTPS web server. It should under no
circumstances be exposed as an HTTP server as it may allow a third party to
obtain login credentials.

Note that routing rules should only allow traffic between Polar's server and
the Publisher's server over HTTPS (port 443). An IDS should be placed in front
of the server to ensure that an attacker does not attempt to brute force any
passwords and keys.

## Errors ##

For Client Errors (400-series) and Server Errors (500-series), an error report
should be returned. Note that some error messages will be returned to the client
as printable text. It is up to the publisher to ensure the quality of the
content of these messages.

### Error Reports ###

Error are encoded using json. The body of the error is a json map with a single
key called "error". The "error" value is another map with the following
parameters:

 * "code"
 * "message"
 * "resource"

#### code ####

This is a string error code that both Polar's server and the client can use to
easily triage an error. Each entry point in this project contains documentation
on the error codes it may return.

#### message ####

A description of the error.

#### resource ####

The resource URI the request was attempting to access.

#### Example ####

Example Request:

    GET /paywallproxy/v1.0.0/json/auth/60c2c670ea6b3847b HTTP/1.1

Example Error Response:

    HTTP/1.1 404 NOT FOUND
    Content-Type: application/json
    Accept-Language: en
    
    {
        "error": {
            "code": "InvalidProduct",
            "message": "The specified article does not exist.",
            "resource": "/paywallproxy/v1.0.0/json/auth/60c2c670ea6b3847b"
        }
    }

## Creating Users ##

This section describes how to create test users and products. To add a new user
or set of products to the test system, modify the create\_users function in the
model class in model.py
