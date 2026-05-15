# Custom Methods 
In most cases an API can be designed using [standard methods](../rest-api-guidelines/Standard%20Methods.md) because a method can be expressed by a noun (e.g. "execution" instead of "execute"). But sometimes functionality is better expressed using a _custom method_.



Custom methods are represented by _verbs_ and **should** use the following general format:
```
https://<root>/platform/<namespace id>/<service name>/<version>/<resources>/<resource-id>:<custom-method>
```
Using a different separator for the custom method clarifies the difference between the resource name (separated by “/”) and the method.

- Custom methods **should** only be used if a standard method and the restriction to nouns for resource names makes an API ugly or hard to understand.
- Custom methods **should** use the HTTP POST method.
- Custom methods **may** use the HTTP GET method if it makes sense for the semantics of the operation, in this case it **must not** use a request body.
- Custom methods **should not** use the HTTP PATCH method.
- The URL **must** end with a verb separated from the path by a colon.
- Method names **should** be in _kebab-case_.

Examples how to represent existing APIs from the DT Cluster in the Analytics Platform:

Note the forward slash in the existing Cluster API:
```
POST tenant.live.dynatrace.com/tenantTokenRotation/start
POST tenant.live.dynatrace.com/tenantTokenRotation/finish
POST tenant.live.dynatrace.com/tenantTokenRotation/cancel
```

These APIs can now be designed like this:
```
POST tenant.apps.dynatrace.com/platform/token-service/v1/tenant-token:start-rotation
POST tenant.apps.dynatrace.com/platform/token-service/v1/tenant-token:finish-rotation
POST tenant.apps.dynatrace.com/platform/token-service/v1/tenant-token:cancel-rotation
```