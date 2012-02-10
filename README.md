# Polar Mobile Publisher Paywall: Sample Server # 

This project is a simple sample web server for the Polar Mobile Paywall API.

 * Server only accessible through HTTPS
 * Under no circumstances should an HTTP server be run.

## Contents ##

 * __Overview__: An overview of the system as a whole.
 * __Definitions__: Definitions of bolded terms used throughout this document.

## Overview #

This section gives a broad overview of the paywall system as a whole. See
the definitions section for definitions of bolded terms.

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

