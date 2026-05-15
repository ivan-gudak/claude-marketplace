# Execution Context

All APIs in the Analytics Platform need to accept several forms of execution context when being called. Some contexts are specific for APIs; other contexts **must** be universally supported. All execution contexts **must** be provided as [request headers](../rest-api-guidelines/Conventions.md#headers).

All execution context request headers **must** be preserved. Even if an API does not use an existing context request header it **must** forward this request header when executing requests to other services (other services **may** require the execution context).

Context request headers are not considered a direct part of the API of a service (thus they are not shown in the API Swagger UI), but rather implicit meta-information defined by the Dynatrace environments to set the context in which an API call is executed. Customers typically have no or limited control over the context information added to individual requests.

## Tenant Context
All [public APIs](../rest-api-guidelines/General%20Structure.md#public-apis) **must** support the tenant context in the `Dt-Tenant` header. The header **must** contain the tenant uuid as a plaintext string. This header is always set by the API Gateway (extracted from the public DNS name) and **must** also be set when an API is called internally within the K8s cluster. [Internal APIs](../rest-api-guidelines/General%20Structure.md#internal-apis) and [operational APIs](../rest-api-guidelines/General%20Structure.md#operational-apis) **might** be global by nature and therefore **may not** support the tenant context. 

#### Example
```
GET /platform/app-registry/v1/apps
Dt-Tenant: abc12445
```

**Caution**: The presence of this header does not mean that access to the tenant is already authorized (e.g. by the API Gateway). Each service **must** authorize access to the tenant on its own. So, if a request contains this header, its semantics is: “I want to execute this request in this tenant”.

## Authentication Context
Authentication **must** be supported in the form of JWT Bearer Tokens in the `Authorization` header as defined in [RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519). The header **must** contain the JWT token as base 64-encoded bearer string. This header is always set by the API Gateway (negotiated with SSO) and **must** also be set when an API is called internally within the K8s cluster. 

Transport via query parameter or cookie **should not** be supported. See [Authentication](../rest-api-guidelines/Authentication.md) for additional details.

#### Example
```
GET /platform/app-registry/v1/apps
Dt-Tenant: abc12445
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Application Context
Within the [Application Framework](https://dynatrace.sharepoint.com/sites/Platform/SitePages/Dynatrace-platform-architecture.aspx#application-platform) part of the Analytics Platform an additional context **may** be supported: the _application context_ - essentially the application id of the App which accesses the API. If the Application Context is supported by an API it **must** be represented in the form of the `Dt-App-Context` header which contains the App Id as a plaintext string.

If the header is set by the caller but an API does not use it the header **should** be ignored. An API **may** choose to log the header as part of e.g., its audit logging.

#### Example
```
GET /platform/app-registry/v1/apps
Dt-Tenant: abc12445
Dt-App-Context: com.dynatrace.appshell
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
APIs that work directly with Apps, like e.g. the App Registry which handles Apps as resources **should** access Apps using the application id as path parameter.

## Application Version
In addition to the Application Context an App Framework API **may** also support the App version in the form of the `Dt-App-Version` header which contains the App's version as [semVer](https://semver.org/) string in the format \<major>.\<minor>.\<patch>-\<optional suffix>. The Application Version header **requires** the [Application Context header](#application-context) to be present as well.

If the header is set by the caller but an API does not use it the header **should** be ignored. An API **may** choose to log the header as part of e.g., its audit logging.

#### Example
```
GET /platform/app-registry/v1/apps
Dt-Tenant: abc12445
Dt-App-Context: com.dynatrace.appshell
Dt-App-Version: 1.0.1-dev.20231010T102528+04997783
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Function Context
If a request comes from an App function (from within the Dynatrace serverless environments), the request contains the Function Context header to exactly describe the App function that is executing the request. This can e.g. be used for billing calculation or enabling certain functionality based on the calling function.

An API **may** support the Function Context in the form of the `Dt-Function-Context` header which contains the function name in plaintext. The Function Context header always comes in combination with the [Application Context header](#application-context).

#### Example
```
GET /platform/app-registry/v1/apps 
Dt-Tenant: abc12445 
Dt-App-Context: com.dynatrace.appshell
Dt-Function-Context: my-cool-function
Dt-App-Version: 1.0.1-dev.20231010T102528+04997783
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Gateway Context
All requests coming from the outside of the platform K8s cluster must pass through an API Gateway. Since there are two types of API Gateways (_public_ and _private_) it is sometimes necessary for services to be able to distinguish between the two sources. Therefore, the API Gateways put their type in the `Dt-Apigateway` header (either use "public" or "private"). This header is mostly used for consistency checks with other headers (mainly the [internal-service-context header](#internal-service-context)) and log deduplication. It **should not** be used for business logic decisions.

#### Example
```
GET /platform/app-registry/v1/apps 
Dt-Tenant: abc12445 
Dt-Apigateway: public
Dt-App-Context: com.dynatrace.appshell
Dt-Function-Context: my-cool-function
Dt-App-Version: 1.0.1-dev.20231010T102528+04997783
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Origin IP Address
The API Gateway adds the `Dt-Origin-Address` header. It contains the spoof-proof IP address of the client performing the request.
The value **must** be used for [audit events](https://bitbucket.lab.dynatrace.org/projects/DEUS/repos/semantic-dictionary/browse/doc/model/dt-system-events/audit_event.md) of origin type "REST" instead of e.g. the `X-Forwarded-For` header.

#### Example
```
GET /platform/app-registry/v1/apps
Dt-Tenant: abc12445
Dt-Origin-Address: 83.164.160.102
```

## Language
UI users can select the language to use for UI display (Apps, App Shell, etc.). This is stored as a user-specific setting. 

Some APIs **may** support the language in the form of the `Dt-Language` header which contains the single selected language as an [ISO-629-1](https://en.wikipedia.org/wiki/ISO_639-1) string. The list of supported languages is very limited though. The default is "en" if the header is missing, invalid or set to an unsupported language code.

#### Example
```
GET /platform/app-registry/v1/apps 
Dt-Tenant: abc12445 
Dt-App-Context: com.dynatrace.appshell
Dt-Language: ja
Dt-App-Version: 1.0.1-dev.20231010T102528+04997783
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
#### Note
The [Accept-Language](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language) header is considered a browser-local header and **must not** be used in the backend.

## Local Dev Mode
The Dynatrace App Toolkit supports App developers during local App development by giving access to tenant APIs. While developers are working on an App locally all API requests are marked with special development headers to allow the platform to distinguish Apps that are currently being developed from officially installed Apps. This allows to work on a new version of an already installed App without interference (especially when doing installations of new App Settings schemas).

## Dt-Dev-App-Id & Dt-Dev-Context
In case of a locally developed App all requests from that App set the request headers in that way:

- [Dt-App-Context](#application-context) is set to the constant "local-dev-mode".
- `Dt-Dev-App-Id` header is set to the actual App Id as specified in the [App Context](#application-context) section.
- `Dt-Dev-Context` header is set to the actual App Id as specified in the [App Context](#application-context) section. This header **may** be subject to extension.

## Internal Service Context
Some APIs **may** support context information indicating which internal service exactly is the client executing a request. This information **may** be used for special handling of such requests. E.g. Grail Query Engine uses the concept called "resource pools" to differently prioritize certain service queries from public customer queries.

The context is transported in the form of the `Dt-Internal-Service-Context` header which **must** contain a string uniquely identifying the calling service in this format:
```
dt.<service-name>.<use-case-name>
```
#### Example
```
GET /platform/storage/query/v1/query:execute 
Dt-Tenant: abc12445 
Dt-Language: ja
Dt-Internal-Service-Context: dt.lima.lima-usage-stream
```
The public API Gateways filter this header, thus ensuring that it cannot be abused by customers or attackers. Internal API Gateways will let it pass though.

#### Note
The supported values for the header must be communicated between the service teams and client teams.

## Workflow Context
Workflows are an integral part of the Dynatrace platform and a frequent trigger for REST API calls. Technically,  the workflow executes an App function or ad-hoc code that calls the platform API. In this case the workflow id is provided in the `Dt-Workflow` header in plain text. The meta information is mostly used for self-monitoring and auditing purposes but **may** also be used for special billing calculations in the future.

#### Example
```
GET /platform/storage/query/v1/query:execute 
Dt-Tenant: abc12445
Dt-Workflow: 38234ae1-478e-4035-a66c-6f4e0ee5c05f
```

## Document Context
Documents (most notably Dashboards and Notebooks) are a common source of requests since they may contain executable ad-hoc code. For self-monitoring and debugging purposes the document id is provided in the Dt-Document header in plain text. The meta information must not be used for business logic decisions since it can be spoofed by external callers.

#### Example
```
GET /platform/storage/query/v1/query:execute
Dt-Tenant: abc12445
Dt-Document: 38234ae1-478e-4035-a66c-6f4e0ee5c05f
```

# Response Context
All responses of platform API calls **must** contain a hint to the response source. The Dynatrace platform uses an API gateway in front of all platform services which acts as the gatekeeper to the services. This means it may respond on its own when a service is called (e.g. if a user is not authorized or request throttling is preventing the call). Clients may decide to act differently if a response comes from the called service directly or the API gateway in front of the service.

## Response Source
The response source is transported with the `Dynatrace-Response-Source` response header. The API Gateway ensures that this header is always set. It can have 2 different values:

- "API Gateway" - if the response was generated on the API Gateway. This happens if an explicit API Gateway API is called or the API Gateway intercepted the request (e.g. if authorization failed or throttling prevented the request)
- "Service" - if the response was generated on the called platform service.

Services **must not** set this header on their own, they can read it though.