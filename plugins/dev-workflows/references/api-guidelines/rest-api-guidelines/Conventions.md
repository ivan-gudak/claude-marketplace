# General Restrictions
Although there is no limit specified in [RFC 2616](https://datatracker.ietf.org/doc/html/rfc2616) or [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986), the common agreement is to limit certain aspects of HTTP based requests to ensure support of all common browsers and other services like DNS.

- Hostnames **must** be limited to 255 characters
- URLs **must** be limited to 2048 characters
- Query parameters **must** be limited to 1024 characters

# Case Sensitivity
All resource-path entries and query parameters **must** be case sensitive. This includes path parameters, query parameter names and values.

Quote from [RFC 7230]()https://www.rfc-editor.org/rfc/rfc7230#page-19: 
>_"The scheme and host are case-insensitive and normally provided in lowercase; all other components are compared in a case-sensitive manner."_

# Naming Conventions
In general, all names in an API **should** be:

- Simple
- Intuitive
- Precise
- Consistent
- International

This includes all names of services, resources, collections, parameters, and methods.

- Names **should** be American English.
- Commonly used abbreviations may be used.
    - E.g., TTL, API, …
- The same names should be used for the same concept across all APIs.
    - E.g., do not mix terms like "delete", "remove", "erase".
- Avoid name overloading. Use different names for different concepts.
- Avoid overly generic terms like "data", "info", etc.
- Well established abbreviations like "config" or "id" should be used instead of the full name (i.e. "configuration", "information").

## Service Names
Service names **must** be URL-safe strings. They are used for the internal service naming in K8s/Istio and are the default name used by the API Gateway to access the API.

- Service names **should** be _singular nouns_.
- Service names **should** be in _kebab-case_.

## Collection Names
- Collection Ids **should** be _plural nouns_.
- Collection Ids **should** be in _kebab-case_.

## Field Names
- Field names **should** be in _lowerCamelCase_ (this is the preferred casing in Java and JavaScript based environments using JSON).

## Field Values
- Enum values **should** be single words in _UPPER_SNAKE_CASE_, this also includes enums that are used in query parameters.

## Query Parameters
- Query parameter names **should** be in _kebab-case_.
- Array parameters **should** be encoded with _style=form_ and _explode=false_

#### Example for array parameter:
```
- name: my-param
  in: query
  schema:
    type: array
    items:
      type: string
  style: form
  explode: false
```
#### Result:
```
?my-param=value1,value2,value3
```
This typically comes into play when dealing with [field filtering](../rest-api-guidelines/Filtering%20And%20Sorting.mdfield-filtering-and-partial-results) or [sorting](../rest-api-guidelines/Filtering%20And%20Sorting.md#sorting).

## Headers
- Header names **should** use _uppercase separate words_ with hyphens as defined in [RFC 4229](https://tools.ietf.org/html/rfc4229). Due to the lack of standards in the internet in this field all APIs **must** accept headers case-insensitively. The "X-" prefix is deprecated and **must not** be used.

## Path Parameters
- Path parameter names are not directly visible in the API when it is used but they are shown in the Swagger UI documenting the API. Therefore, they are considered customer facing and **must** follow a common schema.
- Path parameter names **should** be _singular nouns_.
- Path parameter names **should** be in _kebab-case_.

# HTTP Response Codes
- APIs **must** use only status codes registered at [IANA](https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml).
- APIs **must not** define proprietary HTTP status codes (_9xx_ codes **must not** be used).
- APIs **should** prefer a small set of HTTP status codes, lesser-known status codes should be avoided if possible.

## Success Codes
These are the recommended success response codes to use:
| Success Status Code	 | Description                                                                                     |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| 200 - OK	             | Successful execution of the request, the result is returned in the response.                    |
| 201 - Created	         | Successful execution of the request, the response body **may** be empty in this case.           |
| 202 - Accepted	     | Request was accepted and will be executed asynchronously at a later point in time. The response body may contain a reference to check the status of the execution (see [Long Running Operations](../rest-api-guidelines/Long%20Running%20Operations.md)). In some cases (e.g. monitoring data ingest) it **may** be empty. |
| 204 - No Content	     | Successful execution of the request, no result. The response body **must** be empty in this case. |

## Redirect Codes
HTTP 3xx redirection codes **should not** be used unless an API explicitly works with content encoding `text/html`. Instead of HTTP 3xx an API **should** return HTTP 404 - not found.

If redirection is still required (e.g., within the API Gateway implementation), the HTTP 307/308 **should** be preferred over 301/302.

## Error Codes
If an error status code is returned, the response **should** contain an error envelope if possible (sometimes an error is generated by a Webserver directly). These are the recommended error response codes to use:

| Error Status Code	          | Description                                                                                                                                                                                                                                                                               |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 400 - Bad Request	          | The request syntax was corrupt. <p>This is also the default fallback code to transport an application-level error if no specific error code is available (e.g., the request was valid, but the application logic refused to execute it due to some application restriction like a quota). |
| 401 - Unauthorized          | The request was rejected because the client needs to be authenticated first.                                                                                                                                                                                                              |
| 403 - Forbidden	            | The request was rejected because the (authenticated) client did not have the necessary permissions. See [Response Format](../rest-api-guidelines/Common%20Schemas.md#error-response-format) for the required details in the error response.                                               |
| 404 - Not Found	            | The requested resource was not found (it never existed).                                                                                                                                                                                                                                  |
| 409 - Conflict	             | The write operation failed because a conflict was detected by the ["optimistic locking"](../rest-api-guidelines/Conflicts%20and%20Locking.md#optimistic-locking) strategy.                                                                                                                |
| 410 - Gone                  | The requested resource was not found although it existed some time ago.                                                                                                                                                                                                                   |
| 429 - Too Many Requests     | 	The client sent too many requests at a certain time (see [Throttling](../rest-api-guidelines/Design%20Patterns.md#rate-limiting-and-throttling)).                                                                                                                                        |
|                             |                                                                                                                                                                                                                                                                                           | 
| 500 - Internal Server Error | 	Unspecified server error (typically caused by internal problems like exceptions).                                                                                                                                                                                                        |
| 501 - Not Implemented	      | Standard or custom method is not supported by the API.                                                                                                                                                                                                                                    |
| 503 - Service Unavailable	  | Service is temporarily unavailable.                                                                                                                                                                                                                                                       |