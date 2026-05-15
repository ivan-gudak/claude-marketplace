# Introduction
These are the general Dynatrace design guidelines for all **REST APIs** in the _Dynatrace Analytics Platform_ (short: Analytics Platform). This includes internal and external APIs of services. The guidelines do not apply to other types of APIs that might be used in the Platform like e.g., gRPC.

The goal of these guidelines is to ensure that all APIs provided in the Analytics Platform are consistent, easy to understand and follow a common understanding of [REST](https://en.wikipedia.org/wiki/Representational_state_transfer)ful HTTP/1.1 ([rfc7230](https://tools.ietf.org/html/rfc7230)) APIs.

The guideline document starts with the most important rules and will likely be extended and/or adapted over time as seen fit. 

# Contacts
If you have questions or proposals for changes or extensions of this guide, please contact Florian Aigner or Stefan Chiettini

# Conventions
This document uses a set of key words to indicate requirement levels as defined in [rfc2119](https://www.ietf.org/rfc/rfc2119.txt):
| Keywords                     | Definition                                                                                                            |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| MUST, SHALL, REQUIRED	       | The definition is a mandatory requirement, violation is considered a mistake                                          |
| MUST NOT, SHALL NOT	       | The definition is prohibited, violation is considered a mistake                                                       |
| SHOULD, RECOMMENDED	       | The definition is not mandatory but should be carefully understood and weighted before choosing a different approach  |
| SHOULD NOT, NOT RECOMMENDED  | The definition is not prohibited but should be carefully understood and weighted before choosing a different approach |
| MAY, OPTIONAL	               | The definition is truly optional                                                                                      |

These key words are written in **bold** font.

Names of parameters, fields, objects, etc. are written in `code` font.

# Setting The Stage
The Analytics Platform runs on K8s using a service mesh (Istio). Each service offering an API is represented as a service running on a K8s Pod (further in the guide called a "K8s service"). The service mesh takes care of internal communication and network security. External access from the Internet to the service APIs is handled by an _API Gateway_ which takes care of routing, filtering and IAM authentication.

For more information on the general structure see [Platform Architecture](https://dynatrace.sharepoint.com/sites/Platform/SitePages/Architecture.aspx).

## REST APIs and DQL
The Analytics Platform is tightly coupled with the Hypergraph database [Grail](https://dynatrace.sharepoint.com/sites/Platform/SitePages/DEUS.aspx). All mass data like metrics or logs is not accessed via dedicated REST APIs but via the _Dynatrace Query Language_ ([DQL](https://dynatrace.sharepoint.com/sites/Platform/SitePages/Get-started-with-DQL.aspx)) which is natively built into the database. Therefore, a lot of REST APIs well known on the existing Dynatrace Clusters are not available on the Analytics Platform - this includes special APIs for metrics, logs, problems, events, etc.

## Resource-oriented Design
The general principle defines _resources_ that can be created and manipulated via _methods_. In the API resources are represented as _nouns_ and methods as _verbs_. Using the HTTP protocol, the resources map to the URL path and operations (called _methods_ in this guide) map to standard HTTP methods (POST, GET, PUT, PATCH, DELETE).

Most resources are organized in _resource collections_ (e.g., list of users).

The **recommended** protocol is HTTP/2 due to better performance and less network bandwidth usage.

The **recommended** content type of payloads is JSON which is an industry standard on the internet. In certain high performance scenarios alternative protocols like _protobuf_ **may** be used.

The **required** [encoding](https://datatracker.ietf.org/doc/html/rfc7493#section-2.1) is UTF-8 (unless technically necessary to support different encodings).