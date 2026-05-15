In some rare cases multiple K8s services **may** contribute to one logical public service. Such services **must** be grouped into a [service namespace](../rest-api-guidelines/General%20Structure.md#public-service-namespaces)
which is used in the IAM permission name instead of the public service name. The permission on a service namespace **must** be applied to resources in all services belonging to the service namespace. Services still can be versioned individually 
and provide the name of the service namespace in the API thus linking it to the IAM permission.

This results in this general permission name format:
```
<service namespace>:<resource>:<action>
```

![Multi Service API Mapping](../permission-guidelines/img/multi%20service%20api%20mapping.png)

#### Example

This example describes a data storage system that is capable to ingest different types of data in REST APIs in an _ingest service_ and to query the data via a separate _query service_. 
This is a simplified version of the Grail service structure for the sake of this example.

We assume to have 2 physical K8s services (_ingest_ and _query_) represented on the API Gateway like this:

1. _ingest_
```
POST /platform/storage/ingest/v1/logs
POST /platform/storage/ingest/v1/metrics
POST /platform/storage/ingest/v1/events
```
2. _query_
```
POST /platform/storage/query/v1:query
```
We want to be able to have fine grained control over who is allowed to ingest and query certain types of data (_logs_, _metrics_, _events_).

The resulting IAM permissions applied to the APIs of the 2 services are:
```
storage:logs:read
storage:logs:write

storage:metrics:read
storage:metrics:write

storage:events:read
storage:events:write
```

As you can see, the first part of the permissions is not containing the service names (_ingest_ or _query_) but the service namespace (_storage_) to keep the permission naming consistent across multiple physical services.
