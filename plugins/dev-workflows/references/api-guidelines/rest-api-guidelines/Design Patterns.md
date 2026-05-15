# Handling Read-Only JSON Fields in Resources
In many cases resources will contain read-only fields when returned by the _Get_ method. APIs **should** ignore such fields if they are provided in a request body for _Create_ or _Update_ instead of returning an error. APIs also **should** accept [Full Update](../rest-api-guidelines/Standard%20Methods.md#full-update) requests (using PUT) where read-only fields are missing although this is technically a Partial Update which requires PATCH.

This is seen as a convenience improvement for customers.

# Handling Unknown JSON Fields in Resources
If a resource in a _Create_ or _Update_ request body contains unknown fields, an API **should** ignore these fields instead of returning an error.

This is seen as a convenience improvement for customers and helps dealing with rolling update scenarios where a caller might already know about new fields but the callee is not yet updated.

# Null Representation
If a field is not set it **should not** be part of the result set by default. In some cases, null represents an actual value (e.g., explicitly stating that a dimension is not present in a timeseries at a certain point in time). In this case the response **may** contain null values.

# Parameters
Parameters **must** be passed either via query parameters or the request body (headers **must not** be used except well-known ones like _Accept_ and headers used for [API context transfer](../rest-api-guidelines/API%20Context%20Information.md)). Parameter passing **should not** be mixed.

If a parameter is the same as a field in a response body, it **must** be named equally (except for the casing).

# Headers
Standard headers as registered at [IANA](https://www.iana.org/) **may** be used, the usage **must** be documented. Custom headers except the ones used for [API context transfer](../rest-api-guidelines/API%20Context%20Information.md)) **must not** be used.

#### Examples
```
Accept-Encoding
Content-Length
Content-Type
```

# Timeframes
If a method supports timeframes, it **must** accept 2 query parameters named `start-time` and `end-time` to define the requested timeframe. `start-time` **must** be smaller than `end-time`. If `end-time` is missing it **must** default to `now`.

Each parameter **should** support [absolute timestamps](../rest-api-guidelines/Common%20Datatypes.md#timestamp) and timestamps relative to the current time (i.e., "now"). If it does not support any of these representations it **must** document this. A mixture of absolute timestamps and relative timestamps **may** be supported.

Relative Timestamp Format: [now()][-|+]\<offset>

[now()](https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/functions/time-functions#now) **must** represent the current time when the request is executed. If it is missing it **must** be assumed to be the default.

`offset` **must** be a human readable representation of a time offset in the following resolution:

- "s" - Seconds
- "m" - Minutes
- "h" - Hours
- "d" - Days (1 day = 24 hours, time zones do not apply)

A combination of these offsets (e.g., "now()-1d3h30m") **should not** be supported.

`offset` **may** be omitted which means an offset of 0.

#### Examples
```
GET /problems?start-time=now()-2d&end-time=now()-1h         -- get problems from 2 days ago until one hour ago
GET /problems?start-time=-2d&end-time=now()                 -- get problems from 2 days ago until now
GET /problems?start-time=-2d&end-time=-1h                   -- get problems from 2 days ago until one hour ago
GET /problems?start-time=2021-10-10T00:00:00+01:00          -- get problems from Oct. 10th until now
GET /problems?start-time=1633523598453&end-time=now()-1h    -- get problems from Oct. 6th 12:33 until 1 hour ago
GET /maintenance?start-time=now()-2d&end-time=now()+2d      -- get the maintenance windows defined from 2 days ago until 2 days in the future
```
Reference implementation of a timeframe parser can be found here as a Java library:  https://bitbucket.lab.dynatrace.org/projects/PFS/repos/timeparsing/browse

Note: the timeframe format does not support the [time alignment operator](https://docs.dynatrace.com/docs/shortlink/dql-operators#time-alignment) from DQL.

# List Pagination
Listable collections **should** support pagination even if the expected list size is small.

***Rationale***: If an API does not support pagination from the start, supporting it later is troublesome because adding pagination breaks the API's behavior. Clients that are unaware that the API now uses pagination could incorrectly assume that they received a complete result, when in fact they only received the first page.

- _List_ **may** provide a query parameter named `page-key` which represents the cursor to the next page. If this parameter is missing, the first page **must** be returned. The content of the cursor depends on the use case. In general, it **must** contain the URL-safe base64 encoded data necessary to locate the next page (e.g., a database cursor or a reference into cache already containing the next page).
- Alternatively, _List_ **may** provide a non-negative query parameter `page` which defines the page number to fetch based on the page size. This allows to directly select any page. Default is page 1.
- _List_ **may** provide a query parameter `page-size` which defines the requested number of entries for the next page. If the parameter is missing, a default size **must** be applied which **must** be carefully documented.
- _List_ **should** specify and document a maximum supported page size.
- _List_ **must** provide a field `nextPageKey` in the response body which contains the cursor to the next page (if available). The value of this field **must** be directly usable to fill the query parameter `page-key` without further preprocessing.
- `nextPageKey` **must not** be provided when the last page of the list has been reached.
- Subsequent requests using `page-key` **must not** require any additional parameters to fulfil the paged request. All necessary parameters **must** be encoded in `page-key`.

The response **may** provide a field named `totalCount` which represents the total number of entries in the overall list (not the single page) at the point in time the request was processed. This value **may** change on subsequent calls to _List_ (e.g., resources are added or removed while fetching pages).

With the usage of `page-key` and `page` it is possible to either implement _cursor-based pagination_ or _offset-based pagination_. An API **may** implement any or both forms of pagination but **must** carefully document that.

## Cursor-based Pagination
Cursor-based pagination uses only `page-key` to stream through a list of resources. There is no way back to the previous pages and no way to skip over next pages. This form of pagination is used for APIs mainly consumed by automations, not humans.

#### Example
```
GET /documents?doc-type=dashboard&page-size=20

HTTP/1.1 200 OK
Content-Type: application/json
{
  "documents" : [
     …
  ],
  "nextPageKey" : "bmQgUXVhcms=",
  "totalCount" : 135
}

GET /documents?page-key=bmQgUXVhcms=

HTTP/1.1 200 OK
Content-Type: application/json
{
  "documents" : [
     …
  ],
  "nextPageKey" : "bmhjhTZSJDGJHVhcms=",
  "totalCount" : 135
}
```

## Offset-based Pagination
Offset-based pagination ignores the `page-key` and instead only uses `page-size` and `page` to navigate through a list of resources. The response **may** still contain the `nextPageKey` to the following page. This form of pagination is mainly used for UI representations of a list which are consumed by humans and allow to select any page directly.

#### Example
```
GET /documents?doc-type=dashboard&page-size=20 

HTTP/1.1 200 OK 
Content-Type: application/json 
{ 
  "documents" : [ … ],                               -- page 1 documents
  "nextPageKey" : "bmQgUXVhcms=",                    -- link to page 2
  "totalCount" : 135 
} 

GET /documents?doc-type=dashboard&page=3&page-size=20 

HTTP/1.1 200 OK 
Content-Type: application/json 
{ 
  "documents" : [ … ],                              -- page 3 documents
  "nextPageKey" : "bmQgUXVhcms=",                   -- link to page 4
  "totalCount" : 135 
}
```

## Mixed Pagination
A mixture of cursor and offset pagination **must not** be used since it is confusing and does not give any additional value.

# Rate Limiting and Throttling
Services **may** support a throttling mechanism based on metrics like e.g., number of open DB connections, execution time overhead, low memory, etc.

Typically, there are 3 levels of throttling that can be supported:

- Global limit: throttling because the service instance runs out of shared resources (e.g., thread-pool, DB connections, memory). This is usually easy to implement and therefore in most cases the default.
- Tenant limit: prevent a single tenant to consume all of the shared resources of a service causing other tenants to be blocked ("Tenant starvation"). The tenant context is always available via the [Dt-Tenant](../rest-api-guidelines/API%20Context%20Information.md#tenant-context) header, so this is possible to implement in most cases.
- User/Client limit: prevent a single user session to exhaust the tenant limit causing other users of the tenant to be blocked ("User starvation"). It is not always easy to get the identity of the client, so this is an optional limit in many cases.

If a service throttles a request, it

- **must** return HTTP 429 - Too Many Requests in case of user/client throttling.
- **must** return HTTP 429 - Too Many Requests in case of tenant throttling.
- **must** return HTTP 503 - Service Unavailable in case of global throttling or if the service is unable to determine the need for HTTP 429.
- **must** set the `retry-after` header with the number of seconds to wait until the next retry.
- The error response **must** include the time until the next retry in the field named `retryAfterSeconds` in seconds. It **may** include details about the violated constraint (detailed information **must not** expose sensitive information about the systems internals).

#### Example
```
{
    "error": {
        "code": 503,
        "message": "service is overloaded",
        "retryAfterSeconds": 3,
        "details": "service is busy, good luck next time!"
    }
}
```

# Bulk Operations
In some rare cases it **may** be necessary to explicitly support bulking an operation to reduce the number of requests necessary to fulfil an operation. An example would be to mass-delete documents of a user. Instead of deleting thousands of documents individually it is much more efficient to provide a list of document ids to be deleted in bulk with one single request.

In general, any operation may be bulked although bulking only makes sense in certain cases. E.g. it is not useful to support bulking for CREATE unless it is required to create many objects with the same properties (in test scenarios this may be helpful but not in production APIs).

## Bulk operation request
Bulk operations **must** be represented as [custom POST methods](../rest-api-guidelines/Custom%20Methods.md) on the resource that the operation is executed upon. Input parameters **must** be transferred via the request body (no query parameters) to allow large input lists. The request body **must** contain the bulk operation target resources as a list of resource ids in this form:

```
POST /<resource>:<bulk operation>
{
    "ids" : [
        "<id1>",
        "<id2>",
        "<id3>",
        ...
    ]
}
```

#### Examples

Example for a bulk delelte (i.e. deleting multiple objects in one request):
```
POST /documents:delete
{
    "ids" : [
        "abc",
        "def",
        "ghi"
    ]
}
```

Example for a bulk update (i.e. setting 2 fields of multiple resources to a certain value):
```
POST /documents:update
{
    "field1": "val1",
    "field2": "val2",
    "ids" : [
        "abc",
        "def",
        "ghi"
    ]
}
```

## Bulk operation response
Bulk operations **must** return a response body which contains the individual results per operation. The name of the field can be chosen freely.

Successful responses **must** be represented by the same HTTP response code used for the individual operation that is bulked. So, if the individual DELETE method returns HTTP 200, the result in a bulked DELETE **must** be HTTP 200 for successful execution as well. 

Failed operations within a bulk operation **must** be represented by the same HTTP response code used for the individual operation that is bulked. So, if the individual DELETE method returns HTTP 400, the result in a bulked DELETE **must** be HTTP 400 for that one failed execution as well. Also, the same error response body **must** be added to the bulk operation response as well.

The bulked operation itself **must** return HTTP 200 unless the bulk itself fails (e.g. due to authorization errors).

#### Example
```
POST /documents:delete
{
    "ids" : [
        "abc",
        "def"
    ]
}

{
    "results": [
        {
            "id": "abc",
            "code": 200
        },
        {
            "id": "def",
            "code": 400,
            "error": {
                "code": 0,
                "message": "string",
                "details": {
                    "errorRef": "string"
                }
            }
        }
    ]
}
```

## Response Filtering
Bulk operations **may** support a `filter` query parameter which allows to reduce the size of the result set.

Valid Filter Values:

- "all" (default if not set) - response contains successful and failed responses.
- "failed-only" - only include failed operation responses, an empty response body means that all operations in the bulk succeeded.
- "success-only" - only include successful operation responses.
- "none" - skip all results (ignores the results).

#### Example
```
POST /documents:delete?filter=success-only
{
    "ids" : [
        "abc",
        "def"
    ]
}

{
    "results": [
        {
            "id": "abc",
            "code": 200
        }
    ]
}
```