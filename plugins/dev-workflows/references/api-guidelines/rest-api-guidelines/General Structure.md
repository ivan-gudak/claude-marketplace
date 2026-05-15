# General Structure
The Dynatrace Analytics Platform consists of a collection of services that interact with each other. 
The smallest building block is a _physical K8s service_ which provides APIs containing several REST endpoints. For details see [General Concepts](https://dynatrace.sharepoint.com/sites/Platform/SitePages/General-Concepts.aspx).

- K8s services **may** expose some of their APIs publicly on the API Gateway. An exposed API is referred to as a _public service_ (or _platform service_) on the API Gateway.
- Some K8s services **may** expose APIs on the API Gateway which are intended to be only used by Dynatrace Apps but not customer Apps. Those APIs are referred to as _reserved service_. 
- K8s services **may** contain purely internal APIs intended for other K8s services to use.
- K8s service **may** contain operational APIs used by Ops or DevOps employees for e.g. debugging purposes. Such APIs are exposed on the API gateway within the corporate network only for e.g. DevOps Apps.

## K8s Services and APIs
K8s services **should** group APIs into a predefined set of _API-Types_:

|API-Type	    |API Properties                                                                           |
|---------------|-----------------------------------------------------------------------------------------|
|/public/	    | <ul><li>Always publicly exposed by the API Gateway</li><li>Used by customers and inside of the Dynatrace Platform by other services</li><li>REST APIs only</li></ul>                                              |
|/reserved/	    | <ul><li>Always exposed by the API Gateway (reachable from the internet)</li><li>Not documented or advertised to customers (e.g., hidden in Swagger UI)</li><li>Used only by Dynatrace Apps (not customer Apps)</li><li>REST APIs and Websockets are allowed</li></ul> |
|/internal/	    | <ul><li>Never publicly exposed by the API Gateway</li><li>Mainly used only by other services in the Analytics Platform</li><li>Exception: APIs exposed on the internal path of the API Gateway used by e.g. DT Clusters or central services</li><li>REST APIs and Websockets are allowed</li></ul> |
|/operations/	| <ul><li>Never publicly exposed by the API Gateway</li><li>Non-functional features like statistics, debug APIs, test APIs, etc. used by DT infrastructure services like CDH, CI, DT Operator, CWS, etc.</li><li>Often used by Debug Apps or DevOps Apps for ACE or Dev Teams</li><li>REST APIs only</li></ul> |

If a K8s service hosts more than one API within one API-Type, it **must** separate these APIs using an _API-identifier_. The API-identifier may be omitted if the service provides only one API. K8s service APIs must be [versioned](../rest-api-guidelines/API%20Versioning.md).

Service URLs inside of the Analytics Platform K8s Cluster **should** follow this URL structure:
```
"http://<k8s-service-name>.<k8s-namespace>/<api-type>/[<api-identifier>/]<version>/<api resources>"
```

### Examples
```
app-registry.app-gateway/public/v1/apps                           -- no api-identifier
app-registry.app-gateway/public/app-registry-api/v1/apps          -- alternative using an api-identifier

persistence-service.storage/public/query-api/v1/query:execute     -- 1 K8s service with 2 APIs
persistence-service.storage/public/query-api/v1/query:validate
persistence-service.storage/public/entity-model-api/v2/models
ingest-service.storage/public/log-ingest/v2/logs                  -- 2nd service in k8s namespace "storage"
ingest-service.storage/public/metric-ingest/v1/metrics
```

## Public APIs 
All services are directly accessible only within the Analytics Platform K8s Cluster. External access from the Internet is always passing through the API Gateway. Therefore, each externally exposed K8s service needs to be mapped to a path entry in the publicly exposed URL. If a service uses API-identifiers they will be mapped as a public service name in the path. If the API identifier is omitted the K8s service name will be mapped as a public service name. 

The API Gateway ensures that all public service APIs are represented under the main namespace _platform_: 
```
https://<root>/platform/<public service name>/<version>/<api resources>
```
![Public API Mapping](../rest-api-guidelines/img/public%20api%20mapping.png)

### Examples
#### API on the K8s Service:
```
app-registry.app-gateway/public/v1/apps​                               -- no api-identifier 
app-registry.app-gateway/public/app-registry-api/v1/apps              -- alternative using an api-identifier 
```

#### Public API on the API Gateway:
```
/platform/swagger-ui/index.html                                       -- general swagger ui

/platform/app-registry/v1/apps                                        -- mapped either from api-identifier or service name
/platform/app-registry/v1/openapi.yaml                                -- swagger spec (Open API 3.x) per service
```

### Public Service Namespaces
In most cases the default URL structure is sufficient to map K8s services to public services. But in some rare corner cases this approach may not be sufficient. Especially when multiple K8s services contribute to a single logical representation on the API Gateway it **may** be necessary to group several public services into a _service namespace_ which is mapped to the k8s namespace of the services. This allows to still maintain individual services versions instead of forcing one public service version on both K8s services. K8s services contributing to one service namespace **should** be kept in one K8s namespace with the same name.

General Structure:
```
<root>/platform/<service namespace>/<public service name>/<version>/<api resources>
```

### Examples
The most important use case is Grail data access which is covered by 2 K8s services ("persistence-service" and "ingest-service"):

```
persistence-service.storage/public/query-api/v1/query:execute           -- 1 K8s service with 2 APIs
persistence-service.storage/public/query-api/v1/query:validate
persistence-service.storage/public/entity-model-api/v2/models

ingest-service.storage/public/log-ingest/v2/logs                        -- 2nd service in k8s namespace "storage"
ingest-service.storage/public/metric-ingest/v1/metrics
```

On the API Gateway those 2 services are grouped into the namespace "storage":

```
/platform/storage/queries/v1/query:execute
/platform/storage/queries/v1/query:validate
/platform/storage/entity-model/v1/models

/platform/storage/log-ingest/v2/logs
/platform/storage/metric-ingest/v1/metrics
```

Service namespaces are also useful when it comes to defining [IAM permissions](https://dynatrace.sharepoint.com/sites/Platform/SitePages/IAM-Permission-Guidelines.aspx) on the the whole namespace (e.g. "storage:metrics:read" or "storage:metrics:write").

## Reserved APIs
The API Gateway ensures that all _reserved_ service APIs are represented under the main namespace _platform-reserved_:
```
https://<root>/platform-reserved/<reserved service name>/<version>/<api resources>
```
![Reserved API Mapping](../rest-api-guidelines/img/reserved%20api%20mapping.png)

Reserved APIs are technically public, since they are reachable from the internet. But they are logically treated differently from public APIs:
- Hidden in the Swagger UI in PROD
- Not documented in the developer portal
- Intended to be used only by Dynatrace Apps, not customer Apps
- Have relaxed backward compatibility requirements since they are not used by customers

### Examples
#### API on the K8s Service:
```
app-registry.app-gateway/reserved/v1/apps​                             -- no api-identifier 
app-registry.app-gateway/reserved/app-registry-api/v1/apps            -- alternative using an api-identifier 
```

#### Reserved API on the API Gateway:
```
/platform-reserved/swagger-ui/index.html                              –- swagger ui (DEV and HARD only)

/platform-reserved/app-registry/v1/apps                               -- mapped either from api-identifier or service name
/platform-reserved/app-registry/v1/openapi.yaml                       -- swagger spec (Open API 3.x) per service (DEV and HARD only)
```
## Internal APIs

K8s services **may** provide APIs not supposed to be publicly exposed on the API Gateway. On the K8s service such APIs **must** be grouped in the _internal_ API-Type.

On the API Gateway internal APIs **must not** be published to customers but **may** be exposed to Dynatrace clients outside of the Analytics Platform K8s Cluster. Internal APIs **must** be [versioned](../rest-api-guidelines/API%20Versioning.md).
 
The API Gateway **may** expose some internal service APIs under the main namespace platform-internal:
```
<root>/platform-internal/<service name>/<api type>/<api-identifier>/<version>/<api resources>"
```
Note that the _platform-internal_ path is only accessible from within the corporate network and requires special permissions.

### Examples
```
function-proxy.app-gateway/public/function-executor/v2/executions
function-proxy.app-gateway/internal/function-executor/v1/async-executions   -- available in the platform for other services

platform-management.platform-core/internal/v1/tenants
```

One API is "exposed" internally on the API gateway:
```
platform-internal/platform-management/internal/v1/tenants                   -- available for e.g. CloudControl
```

## Operational APIs
K8s services **may** provide APIs that serve an operational purpose like a “Debug API” or APIs used by Dynatrace deployment or monitoring components. On the K8s service such APIs **must** be grouped in the _operations_ API-Type.

On the API Gateway operational APIs **must not** be published to customers. Operational APIs are inherently internal and are accessed via a separate route for security reasons (details will come later). Operational APIs **must** be [versioned](../rest-api-guidelines/API%20Versioning.md).
The API Gateway ensures that all operational service APIs are represented under the main namespace platform-internal: 
```
<root>/platform-internal/<service name>/<api type>/<api-identifier>/<version>/<api resources>
```
![Operations API Mapping](../rest-api-guidelines/img/operations%20api%20mapping.png)
Note that the _platform-internal_ path is only accessible from within the corporate network and requires internal Ops/DevOps permissions.
 
### Examples
```
app-registry.app-gateway/operations/devops/v1
app-registry.app-gateway/operations/ops/v3
app-registry.app-gateway/operations/test/v2
```

"exposed" internally on the API gateway:
```
platform-internal/app-registry/operations/devops/v1
platform-internal/app-registry/operations/ops/v3
platform-internal/app-registry/operations/test/v2
```

Recommended API-identifiers for operational APIs are:

| API-identifier   | Purpose	                                                                           | Examples                    |
| ---------------- |-------------------------------------------------------------------------------------- | --------------------------- |
| devops           | Dev-Ops API usually only used by the developers of the service mainly for debugging and proactive monitoring purposes.	| Enable a debug flag|
| ops              | Mainly used by ACE, Support or Sales Engineers. Typically these APIs represent a less detailed and less intrusive feature set as devops APIs.	| <ul><li>Trigger a thread dump</li><li> Rotate or revoke a secret </li></ul> |
| deployment       | Deployment endpoints used during service rollout or other maintenance tasks.	       | Trigger a post-update migration step |
| statistics       | Expose statistics data to Dynatrace backend systems like the CDH.                     |                             |
| test             | APIs only used by tests (e.g. by the CWS).	                                           |                             |
