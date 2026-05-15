[Internal and operational APIs](../rest-api-guidelines/General%20Structure.md#internal-apis) typically are treated as resources in IAM. In most cases it is sufficient to grant permissions on API level instead on resources within the APIs. A typical use case is to grant access to the whole _devops_ API for members of the service development team.

IAM Permission Naming for internal and operational APIs:
```
<k8s service name>:<api-type>.<api-identifier>.<api resources>:<action>
```
![Internal API Mapping](../permission-guidelines/img/internal%20api%20mapping.png)

![Operational API Mapping](../permission-guidelines/img/operational%20api%20mapping.png)

IAM does not support wildcards but multiple permission levels **may** be defined manually. Typically it is enough though to define permissions on a rather high level instead of on the resource level.

#### Examples
```
app-registry:operations.devops.bundles:read        -- permission on resource collection level
app-registry:operations.devops:read                -- permission on API level, common case
app-registry:operations.ops:read                   -- permission on API level, common case
app-registry:operations:read                       -- permission on API-Type level
```