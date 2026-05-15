# Introduction
All APIs **must** be documented by the implementing service using an [OpenAPI document](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#openapi-document). This applies to public APIs as well as operational APIs. 
The OpenAPI document **must** be interactively browsable using a [Swagger UI](https://swagger.io/tools/swagger-ui/) hosted on the API Gateway. Each API version **must** be represented by a separate document. Internal APIs **may** be documented as well if they are e.g., used by services outside of the platform but within the company's VPN. Examples would be statistic APIs called by the Cluster Data Hub or internal integration APIs with Cloud Control or SPINE.

# Template File

[OpenAPI Spec Template File](../rest-api-guidelines/template/openapi-template.yaml)

# Format
- The OpenAPI document **must** be exposed in the [YAML](https://yaml.org/) format and [OpenAPI version 3.0.x](https://spec.openapis.org/) with the name _openapi.yaml_. 
- OpenAPI versions older than 3 **must not** be used. 
- When the file is served by the service the `Content-Type` header **must** be set to `application/openapi+yaml`.

# Location on the K8s Service
The OpenAPI document must be located on the API version root of the K8s service like this:
```
<k8s-service-name>.<k8s-namespace>/<api-type>/[<api-identifier>/]<version>/openapi.yaml
```
This structure corresponds to the API structure shown in the [General Structure](../rest-api-guidelines/General%20Structure.md) section. 

#### Examples
```
-- Public API (no api-identifier)
app-registry.app-gateway/public/v1/apps
app-registry.app-gateway/public/v1/app-icons
app-registry.app-gateway/public/v1/openapi.yaml

-- Public API (using api-identifier)
app-registry.app-gateway/public/app-registry-api/v1/apps
app-registry.app-gateway/public/app-registry-api/v1/app-icons
app-registry.app-gateway/public/app-registry-api/v1/openapi.yaml

-- Reserved API (no api-identifier) 
app-registry.app-gateway/reserved/v1/hidden-apps
app-registry.app-gateway/reserved/v1/openapi.yaml 

– Reserved API (using api-identifier) 
app-registry.app-gateway/reserved/app-registry-api/v1/hidden-apps
app-registry.app-gateway/reserved/app-registry-api/v1/openapi.yaml 

-- Operational API (no api-identifier)
app-registry.app-gateway/operations/v1/some-resource
app-registry.app-gateway/operations/v1/openapi.yaml

-- Operational API (using api-identifier) 
app-registry.app-gateway/operations/ops/v1/some-resource 
app-registry.app-gateway/operations/ops/v1/openapi.yaml

-- Internal API
platform-management.platform-core/internal/v1/tenants
platform-management.platform-core/internal/v1/openapi.yaml

-- 1 K8s service with 2 APIs
persistence-service.storage/public/query-api/v1/query:execute
persistence-service.storage/public/query-api/v1/query:validate
persistence-service.storage/public/query-api/v1/openapi.yaml 

persistence-service.storage/public/entity-model-api/v2/models
persistence-service.storage/public/entity-model-api/v2/openapi.yaml
```

# Location on the API Gateway
The API gateway maps the _api-type_ to the appropriate main namespace on the gateway (see [Public APIs](../rest-api-guidelines/General%20Structure.md#public-apis), [Reserved APIs](../rest-api-guidelines/General%20Structure.md#reserved-apis), [Internal APIs](../rest-api-guidelines/General%20Structure.md#internal-apis), [Operational APIs](../rest-api-guidelines/General%20Structure.md#operational-apis)).

The API Gateway provides separate Swagger UI paths for _public_, _reserved_ and _internal/operations_ APIs on the main namespaces `platform`, `platform-reserved` and `platform-internal`:

```
-- public APIs
/platform/swagger-ui/index.html

–- reserved APIs
/platform-reserved/swagger-ui/index.html

-- internal and operational APIs
/platform-internal/swagger-ui/index.html
```

Each Swagger UI shows all OpenAPI documents available in the particular main namespace, covering all services and APIs within the namespace.

#### Examples
```
-- public API without api identifier
/platform/app-registry/v1/apps
/platform/app-registry/v1/app-icons
/platform/app-registry/v1/openapi.yaml

– reserved API without api identifier
/platform-reserved/app-registry/v1/hidden-apps
/platform-reserved/app-registry/v1/openapi.yaml

-- operational API
/platform-internal/app-registry/operations/v1/some-resource
/platform-internal/app-registry/operations/v1/openapi.yaml

-- internal API
/platform-internal/platform-management/internal/v1/tenants
/platform-internal/platform-management/internal/v1/openapi.yaml
```

# OpenAPI Document Content
The OpenAPI document **may** contain any OpenAPI language construct that is supported by OpenAPI 3.0.x. If the document describes a platform service API exposed on the API Gateway it **must** contain several mandatory entries to be handled correctly on the API Gateway.

## API Gateway Path
The API path on the API Gateway is different from the path on the K8s service. The mapping is done in the API Gateway and is described under [General Structure](../rest-api-guidelines/General%20Structure.md). The document **must** contain the Dynatrace vendor extension `x-api-gateway-url` with the API Gateway mapping information in the servers section:

```
servers:
  # base url in the k8s cluster is relative, api-type = "public" | "reserved" | "internal" | "operations"
  - url: '/<api-type>[/<api-identifier>]/<api-version>'

  # base url in the API gateway is relative to the API gateway root url, api-location = "platform" | "platform-reserved" | "platform-internal"
    x-api-gateway-url: '/<api-location>[/<service namespace>]/<public service name>/<api version>'
```

This information is e.g. used by code generators to build SDKs both for usage within the platform and from outside of the platform. The API gateway will remove the `x-api-gateway-url` extension dynamically when exposing the document since it is not needed for users of the API.

## Version consistency
The API version specified in the OpenAPI document (i.e. the `version` field) **must** match the version information in the URL. Details are described [here](../rest-api-guidelines/API%20Versioning.md#api-version-in-the-url).

## Dt-Tenant Header
If the API accepts the [tenant context](../rest-api-guidelines/API%20Context%20Information.md#tenant-context) it **must** contain the  `Dt-Tenant` header:
```
components:
  parameters:
    dtTenantHeader:
      in: header
      name: Dt-Tenant
      description: Dynatrace tenant context header
      schema:
        type: string
      required: true
```
The `Dt-Tenant` header will be removed from the document when exposing it on the API Gateway since it is only used within the platform and is actually generated by the API Gateway. This header is e.g., used by code generators to build the service interface.

## Dt-App-Context Header
If the API accepts the [application context](../rest-api-guidelines/API%20Context%20Information.md#application-context) it **must** contain the `Dt-App-Context` header:
```
components:
  parameters:
    dtAppContextHeader:
      in: header
      name: Dt-App-Context
      description: Dynatrace application context context header
      schema:
        type: string
      required: true
```
The `Dt-App-Context` header will be removed from the document when exposing it on the API Gateway since it is only used within the platform and is actually generated by the API Gateway. This header is e.g. used by code generators to build the service interface.

## Authentication Context
If the API accepts the [authentication context](../rest-api-guidelines/API%20Context%20Information.md#authentication-context) it **must** contain the appropriate oauth2 flow:
```
components:
  # see https://swagger.io/docs/specification/authentication/oauth2/
  securitySchemes:
    ssoAuth:
      type: oauth2
      description: This API uses oauth2 with the 'client credentials' flow
      flows: 
        clientCredentials:
          tokenUrl: https://token.url    ## placeholder to be replaced in the API Gateway
          scopes:                        ## scope naming see https://dynatrace.sharepoint.com/sites/Platform/SitePages/IAM-Permission-Guidelines.aspx
            <service name>:<resource>:<action>: access scope        
            <service name>:<resource>:<action>: access scope
```
oauth2 client credentials flow is the only allowed security schema. See [Authentication](../rest-api-guidelines/Authentication.md) for additional details.

## Additional Guidelines
### OperationId
The `operationId` is a unique string in the OpenAPI specification that is used to identify an operation. This field is used by the Dynatrace code generators to specify the generated method names. Therefore, these rules apply to the `operationId`:
- `operationId` **must** be present on each endpoint
- The name of the `operationId` **must** start with a verb to be better suited as a method name during code generation.
- Changing `operationId` **must** be treated like a breaking change of the API since it affects the generated SDKs. Although the API itself does not change on the raw HTTP level, its representation on the SDK level (TS and Java) changes and will break client code on SDK updates

### oneOf, anyOf, allOf
Combination of schemas **should** be avoided since it is often confusing. `allOf` must not be used since it is not supported by the Dynatrace code generators. If combination of schemas is still required, `oneOf` must be used, it is the least confusing option and also supported by the code generators.
