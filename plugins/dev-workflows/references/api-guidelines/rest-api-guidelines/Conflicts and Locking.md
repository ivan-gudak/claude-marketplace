# Introduction
When multiple users manipulate the same resource at the same time this typically leads to a conflict of interests.

Let's assume that 2 users read the same version of a resource, individually update some fields and then write back the updated resource at different times. Without any locking or 
validation in place the order of the write operations defines who finally wins and whose changes are lost. This is the "last write wins" strategy which is very simple to implement and 
understand. Sometimes this strategy is considered "good enough" but in many cases an API **may** want to prevent such conflicts by providing some form of locking mechanism on resources.

The most common locking strategies are ["optimistic locking"](https://en.wikipedia.org/wiki/Optimistic_concurrency_control) and ["pessimistic locking"](https://en.wikipedia.org/wiki/Concurrency_control).

# Optimistic Locking
If a Dynatrace API wants to control concurrency it **must** use the "optimistic locking" strategy. We generally expect low conflict rates on the Dynatrace APIs and want to avoid the risk 
of deadlocks. We also want to avoid the complexity and poor performance that typically comes with pessimistic locking approaches.

If an API provides "optimistic locking" on a resource, it **must** do it consistently and comprehensively. It is not allowed to use it only in a part of the API that maintains the resource 
(e.g., only when doing a partial update but not when doing a full update). If an API manages multiple different resources, it **should** use the same locking strategy for all resources and 
not mix different strategies.

If "optimistic locking" is used, it **must** be provided by assigning a version to the protected resource in the form of a _version_ field containing a representation of the version. 
This version field **must** always be added to the resource when it is returned in a reading operation. The version **must** be excluded from [field filtering](../rest-api-guidelines/Filtering%20And%20Sorting.md#field-filtering-and-partial-results) and **must not** be 
writeable by the client. The version field **must** only be maintained by the service offering the API.

There is no common version format, it depends on the usefulness for the service. So, it may be a simple ever-increasing counter or a hash, decimal or hash encoding may be used, etc.

#### Example
```
GET /documents/6239bf48-ce6d-4e06-8694-bd3c2b235d63

{
  "id": "6239bf48-ce6d-4e06-8694-bd3c2b235d63",
  "name": "test",
  "type": "text",
  "version": "2e9565ea",
  "owner": "441664f0-23c9-40ef-b344-18c02c23d789",
...
}
```
When a resource is protected by "optimistic locking" all writing operations **must** accept an `optimistic-locking-version` query parameter which contains the 
numeric representation of the original version that the content that is written was taken from. This allows the API to check if the current version of the resource 
is still the one that the write operation is based on and reject the request if it is not. The API **must** react with a 409 - Conflict status code in this case. 
The only situation where a missing `optimistic-locking-version` parameter is accepted on a writing operation is when no conflict can occur (e.g. when a new resource is 
created, or a resource is deleted).

#### Example
```
PUT /documents/6239bf48-ce6d-4e06-8694-bd3c2b235d63?optimistic-locking-version=2e9565ea

...

GET /documents/6239bf48-ce6d-4e06-8694-bd3c2b235d63
{ 
  "id": "6239bf48-ce6d-4e06-8694-bd3c2b235d63", 
  "name": "test", 
  "type": "text", 
  "version": "456efa90", 
  "owner": "441664f0-23c9-40ef-b344-18c02c23d789", 
... 
}
```