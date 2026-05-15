# Backward Compatibility
![Always be backward compatible!](../rest-api-guidelines/img/backward%20compatibility.png)

The main assumption is this: all APIs are used by our customers in various ways at all times. We **must** not break any requests of any clients that already worked at some time.

Be aware that customers are not restricted to just one form of interaction with our APIs. They may:

- Access an API in a “raw” way using HTTP and Json only
- Use [Dynatrace SDKs](../rest-api-guidelines/SDKs.md) to access an API
- Use the [OpenAPI spec files](../rest-api-guidelines/OpenAPI.md) we publish as a basis for auto-generated code (using public tooling like [OpenAPI Tools](https://github.com/OpenAPITools))

# API Versioning
For a general introduction to the idea see [The Platform Lifecycle](https://dynatrace.sharepoint.com/sites/Platform/SitePages/The-Dynatrace-Platform-Lifecycle.aspx#general-api-versioning-rules-and-restrictions).

Each service **must** maintain its own individual API version, there is no general API version (like e.g., a “Platform Version”) that applies to all services. Internally a service must apply semantic versioning to the API as described by [semVer 2.0.0](https://semver.org/).

General Version Format: 
```
<major>.<minor>.<patch>
```

## Where to apply?
Public APIs **must** be versioned. They are used by customers who rely on the APIs being backward compatible.

Reserved APIs **must** be versioned. They are used by Dynatrace Apps who rely on the API being backward compatible.

Internal APIs **must** be versioned. They are used by other Dynatrace services who rely on the APIs being backward compatible.

Operations APIs **may** be versioned. If an API is only used by human Dynatrace users, versioning **may** be skipped.

## Version Updates
_Major_ version ('x.\*.\*') **must** be incremented if a breaking change is introduced (e.g., a field is removed or renamed, or an HTTP response code is changed). Any major change **must** include the whole API functionality, not just a delta. 
E.g., if API version 1.0.0 contains 3 methods _List_, _Create_, _Delete_ and the _Create_ method breaks, the new API version 2.0.0 **must** contain all 3 methods again to keep the API consistent. This avoids mixing API versions for clients and allows to easily deprecate the whole 1.0.0 version later.

_Minor_ version ('\*.x.\*') **must** be incremented if a backward compatible change is introduced to the API (e.g., a new field is added to a response, or a new query parameter is introduced). Extensions of an existing API in general are not considered a breaking change.

_Patch_ version ('\*.\*.x') **must** be incremented if anything else in the API changes which does not affect the functionality or structure of the API (e.g., additional examples or documentation in the API Spec file).

In a _hotfix_ scenario where a bug in the API _implementation_ is fixed the API version **must not** be changed.

## Breaking Changes
What are breaking changes? In short: every change on the API that leads to existing clients misbehaving (i.e. changing their behavior) or even failing entirely (i.e. not compiling anymore or failing to execute requests or parsing responses).

Examples are:

- Renamed or changed API endpoints (e.g. path changes)
- Removed API endpoints
- Renamed response fields
- Removed response fields
- Changed “required” response fields to being optional
- Changed optional request fields to being “required”
- Changed types of response fields
- Changed or removed HTTP response codes
- Renamed query parameters
- Removed query parameters

## Behavioral Changes
Sometimes an API change is not obvious and not even directly visible on the API syntax, behavioral changes **may** be considered a breaking change as well:

- Adding new entries to enumerations. Although this is technically just an extension it may lead to broken client code in strongly typed languages like Java.
- Changes in the semantics of a response field (e.g., switching an absolute timestamp to a relative timestamp or changing the resolution of a field from milliseconds to seconds).
- Skipping fields in certain scenarios.
- Changing the HTTP response code may affect the error handling on the caller side.

# API Version in the URL
Be aware that the full version (`major`.`minor`.`patch`) is not visible on the URL but on the Client SDK and the documentation of the API. The URL of the API only contains a certain part of the version depending on the release state of the API.

## URL Format for Officially Released APIs
Only the `major` version part of the version (which is the one part that defines backward compatibility of the API) **must** be included as the first part after the service name within the URI path in this form:
```
<root>/<namespace id>/<service name>/v<major version>/<service resources>
```

Prefix 'v' **must** be lower case. The `major` version string **must** be encoded as a decimal integer.

Example:
```
tenant.apps.dynatrace.com/platform/app-registry/v1/apps
```

## URL Format during Initial Development of an API
During _initial development_ of an API, `major` version '0' **must** be used. Anything **may** change at any time. Breaking changes **must** be represented by updating the `minor` version part.

As long as version '0' is used, the `minor` version **should** be included in the URL in this form:

```
<root>/<namespace id>/<service name>/v0.<minor version>/<service resources>
```
Prefix 'v' **must** be lower case. The `minor` version string **must** be encoded as a decimal integer.

Example:
```
tenant.apps.dynatrace.com/platform/app-registry/v0.2/apps          -- must not be released officially!
```

## Version Consistency

The API version **must** be consistent over all these locations in the OpenAPI document:

- The full semantic version (consisting of `major`, `minor`, `patch`) **must** be shown in the `version` field of the OpenAPI document
- The `major` version **must** be part of the `servers` `url` definition
- The `major` version **must** be part of the `x-api-gateway-url` definition

![Service Version Locations](../rest-api-guidelines/img/service%20version%20locations.png)

#### Example

```
openapi: '3.0.3'
info:
  version: '3.1.4'

servers:
  - url: '/public/my-service/v3
    x-api-gateway-url: '/platform/my-service/v3'
```

## Going GA and API previews
Any '0.\*.\*' version **should not** be released publicly, instead version 1.0.0 represented as 'v1' in the URL **must** be used to define the very first GA release of the API. 

There are exceptions to this rule in some cases though. Sometimes a preliminary API is shown to an assorted number of preview customers to gather feedback. In that phase it is allowed to expose '0.\*.\*' versions publicly. This always involves telling those preview customers that the API may change in the future and not all requirements to backward compatibility apply.​​​​​​​​​​​​​​​​​

# API Deprecation
It is always preferable to support an older service version for a long time to avoid breaking customer integrations. But eventually a platform service version will reach its end of life and Dynatrace decides to remove it. 

All Dynatrace APIs that are about to be removed **must** go through two phases - _Deprecation_ and _Sunsetting_.

- _Deprecation_ means that the service version is no longer recommended for use, even though it is still fully operational.
- _Sunsetting_ means that the service version will be shut down, meaning that at the announced time, the service version will no longer be available.

## General Rules
Only a whole service version can be removed, service versions **must** stay [backward compatible](https://dynatrace.sharepoint.com/sites/Platform/SitePages/The-Dynatrace-Platform-Lifecycle.aspx#general-api-versioning-rules-and-restrictions) during their whole lifecycle. Therefore, it is prohibited to remove any operation or single field in any service version.

### Deprecation
- A production-grade alternative service version **must** be available, unless the reason of the deprecation is to simply remove a service.
- A migration guide to the alternative service version **must** be available, unless the reason of the deprecation is to simply remove a service.
- Release notes **must** contain the deprecation information.
- In the OpenAPI document of the service version the ['deprecated' field](https://swagger.io/specification/) **must** be set on all operations of the deprecated service.
- In the OpenAPI document a link to the alternative service version **must** be provided.
- In the OpenAPI document either a migration description or a link to a migration guide **must** be provided.
- A ['deprecation' header](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-deprecation-header-02) **must** be added to all responses of the service version. The header **must** be set to 'true', sunset dates are provided by a different header.

Single fields **may** be marked as deprecated e.g., if there is a better alternative available in the same service version. The deprecated field **must** be fully supported for the sake of backward compatibility. The 'deprecation' header **must not** be set if only a field is marked as deprecated. The header is reserved for the deprecation of a whole service version.

### Sunset
- A sunset date **must** be defined early on.
- Release notes **must** contain the sunset date.
- In the OpenAPI document of the service version the sunset date **must** be shown on the service level.
- A ['sunset' header](https://www.rfc-editor.org/rfc/rfc8594.html) with the sunset date **must** be added to all responses of the service version.

# Public APIs vs. Reserved and Internal APIs
Requirements regarding backward compatibility are stronger for public APIs since they are used by customers. This means that typically a public API **must** be kept available in older versions for a long time (several months, sometimes even years). This depends on the customer usage and Dynatrace compatibility policies.

Reserved APIs **may** be sunset much quicker since the only users are Dynatrace Apps which are rolled out by Dynatrace and kept up-to-date quickly.

Internal APIS **may** also be sunset quicker since they are only used by other Dynatrace services which are rolled out by Dynatrace and kept up-to-date quickly.