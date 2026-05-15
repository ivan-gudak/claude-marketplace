# Caching Directive
All resources are uncached by default since resources are generally mutable. For some special APIs this may be different (e.g., static App resources like images). Such APIs **must** carefully specify and document the cache-directives that are accepted and returned.

# ETag
ETag header **may** be used by an API. In this case it **must** follow the common ETag behavior as specified in [RFC 7232](https://datatracker.ietf.org/doc/html/rfc7232#section-2.3).

# DTO Inheritance
DTO (Data Transfer Objects) Inheritance **should** be avoided; this makes the API easier to understand. Model Composition using _allOf_ **should** be avoided as well since it is not supported by the Dynatrace Java code generators.

# HATEOAS
We do not support HATEOAS, integration into Hypermedia is not our main goal. See [Resource Context](../rest-api-guidelines/Common%20Schemas.md#resource-context-info) for more details.

# HAL
We do not support HAL, integration into Hypermedia is not our main goal.

# SSE – Server-Side Events
[Server-Side Events](https://en.wikipedia.org/wiki/Server-sent_events) to clients **should not** be used on public APIs. E.g., for [long running operations](../rest-api-guidelines/Long%20Running%20Operations.md) an asynchronous polling mechanism is defined. A polling mechanism from the client to the server **should** be preferred. On reserved and internal APIs, it **may** be used if there are good reasons to it.

# Websockets
[Websockets](https://de.wikipedia.org/wiki/WebSocket) **should not** be used on public APIs. On reserved and internal APIs, it **may** be used if there are good reasons to it.
 
# Probing
Probing (sometimes also called a "dry run") **should not** be used unless explicitly necessary. 
Probing means that an API e.g. provides an additional query parameter for certain endpoints to tell the API that the request should not be executed but instead only the parameters, permissions and other restrictions should be checked, and the response should tell the caller that a request with the same parameters would succeed or fail. This is often used by UI code to determine if certain UI widgets like buttons should be enabled or disabled proactively. 

We do not want to build our REST APIs specifically for UI usage. 

Instead of probing you can use one of these alternatives:

- _Allowed Operations_ in the [Resource Context](../rest-api-guidelines/Common%20Schemas.md#resource-context-info)
- Generic _Effective Permissions_ endpoint in PMS - see [developer portal](https://developer.dynatracelabs.com/develop/security/query-user-permissions/) and [PMS Backstage](https://backstage.internal.dynatrace.com/docs/dt-platform/component/management-service/effective-permission/) for details.
- Specialized _Effective Permissions_ endpoint in Settings - see [developer portal](https://developer.dynatracelabs.com/develop/sdks/client-classic-environment-v2/#resolveeffectivepermissions) for details.