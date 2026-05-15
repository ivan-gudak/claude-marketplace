# Definition
Any request that takes too long to synchronously wait for the result is called a "long running operation". Such operations **must** be implemented in an asynchronous way.

The typical workflow from the client perspective is

- Initial _trigger_ request which starts the operation in the background and immediately returns to the caller with a unique id to use for regular polling requests at a later time.
- Periodic _polling_ requests (using the id returned by the trigger request) to check the status of the operation and eventually fetch the result.
- Optional _cancel_ request (using the id returned by the trigger request) to stop the execution prematurely.

Long running operations in Dynatrace REST APIs come in two flavors: the "Resource based" and the "RPC-like" style.

# Resource Based Operations
Some operations on resources may take a long time (10s of seconds or even minutes or hours). Typically, this happens with resource creation and/or deletion. An example in the Dynatrace Platform is the installation of a Dynatrace App in the App Registry. The installation requires several background tasks to being finished before the App is considered fully installed and ready to use. All these operations may take up to several minutes to finish.

When a (standard or custom) method on a resource is executed asynchronously the API **must** reflect that in a RESTful way:

- The trigger request **may** accept an arbitrary set of additional parameters in the request body or as query parameters.
- The trigger request **must** return HTTP 202 - Accepted.
- If the trigger request is a _Create_ method, it **must** return the id of the resource that is being created in the response body.
    - The resource id **must** be usable directly in the _Get_ method for periodic status polling.
    - The resource **must** be visible in the _List_ method even if it is not yet fully created.
    - _Create_ **should** return the resource id in the [Location](https://www.rfc-editor.org/rfc/rfc7231#section-7.1.2) header as a relative URL that can be directly used in the _Get_ method. 
- The state of the resource **must** be returned in all reading operations (_List_, _Get_) using an object named `resourceStatus`.
- `resourceStatus` **must** contain a string field named `status` which defines the current state of the resource (e.g., "installing", "deployed", "incomplete"), the possible values **must** be documented for the client to correctly identify the state of the resource.
    - `resourceStatus` **may** contain progress information in percent as 32-bit integer in the field `progress`. The initial value **should** be 0.
    - `resourceStatus` **may** contain additional detail information about the state of the resource (e.g., sub-states of involved operations).
- Certain states of a resource **may** prohibit certain methods on the resource. In this case HTTP 403 - Forbidden must be returned.
- Periodic Polling **must** be possible for the caller by executing the _Get_ method on the resource using the resource id returned by the trigger operation and interpreting the `resourceStatus` field.
- Explicit _cancel_ is typically not supported. Instead, the natural counterpart of the operation _may_ be used to cancel an operation. E.g., calling _Delete_ during the execution of the _Create_ method **may** be interpreted as a _cancel_. In most scenarios it is preferred to wait for the completion of the operation to naturally undo it later. This is typically much easier and safer to do than canceling the operation during execution. 

#### Example
```
POST /apps

HTTP/1.1 202 Accepted 
Content-Type: application/json 
{
  "id": "the-app-id"
}


GET /apps/the-app-id

HTTP/1.1 200 Ok
Content-Type: application/json 
{
  "resourceStatus" : 
  {
    "status" : "INSTALLING",
    "progress" : 10,
    "functionDeploymentStatus": "SCHEDULED",
    "filesDeploymentStatus": "SCHEDULED"
  },
  "manifest": {},
  ...
}

​​​​​​​
GET /apps/the-app-id/app-icons

HTTP/1.1 403 Forbidden 
Content-Type: application/json 
{ 
  "error": {
    "code": 403,
    "message": "App installation not completed yet."
  }
}
```

# RPC-like Operations
 
Not all operations in the Dynatrace APIs are operations on actual resources. In some cases, operations represent a function call on a general service, thus being an asynchronous RPC-like call. Examples in the Dynatrace Platform are the execution of DQL queries on the Grail database or running a DAVIS analyzer over the data model. In both cases there exists no resource (in the RESTful terms) to be worked upon but rather an expensive operation is executed on the DQL or DAVIS service.

If there is no clean way to represent such an operation as a resource-based operation, an API **may** support asynchronous RPC-like operations. 

- An RPC-like long running operation **should** be provided as a [custom method](../rest-api-guidelines/Custom%20Methods.md).
- The service **must** define a hard timeout which cannot be increased by the client (this timeout is often influenced by internal factors like e.g., AWS Lambda restrictions). This overall timeout **must** be documented.

## Trigger Request
- The trigger request body **may** contain the client timeout of the operation in seconds as field named `timeoutSeconds` (POST) or a query parameter named `timeout-seconds` (GET). This is the maximum time the client is willing to wait for the result of the operation. After the timeout has passed the service **may** cancel the operation at any time.
- Either the timeout provided by the client, or the timeout defined by the service **must** specify the TTL of the long running operation depending on which one is smaller.
- The initial request **may** accept an arbitrary set of additional parameters in the request body or as query parameters.

## Trigger Response - Async
The typical use case for a trigger request is that the first request is accepted and triggers an asynchronous background operation which can be tracked by regular polling requests of the client.

- The response **must** be HTTP 202 - Accepted.
- The response body **must** contain a field named `requestToken` to be used for polling. The token **must** be a URL-safe encoded string (e.g. [base-64-url](https://datatracker.ietf.org/doc/html/rfc4648#section-5) or plain url-encoded). The token **must** be usable as a query parameter without re-encoding it.
- The response body **must** contain the remaining TTL in seconds as field named `ttlSeconds`. This field **must** contain the remaining time of the long-running operation in seconds (i.e., the remaining time left for the operation to complete normally and provide a result).
- The response body **may** contain progress information in percent as 32-bit integer in the field named `progress`. The initial value **should** be 0.
- The response body **may** contain a `status` string field containing useful additional information.

#### Example
```
POST /query:execute

HTTP/1.1 202 Accepted
Content-Type: application/json
{
  "requestToken" : "bmQgUXVhcms",
  "ttlSeconds" : 600,
  "status" : "initializing long running operation…"
  "progress" : 0
}
```

## Trigger Response - Sync
In some cases, the trigger request might already be able to serve the result (e.g., if it was already present in some cache). In this case the API **may** already return the result immediately instead of forcing the client into the polling interval. The service **may** decide to block the trigger request for a reasonable amount of time (typically in the low single digit seconds range) to determine if it can immediately serve the response or not. This delay **must** be documented.

- The response **must** be HTTP 200 - Success.
- The response body **must** not contain the field `requestToken`.
- The response body **must** contain the result set of the request.
- If `progress` is supported, it **must** be present with value 100 (representing "100% progress").

#### Example
```
POST /query:execute

HTTP/1.1 200 OK
Content-Type: application/json
{
  "response" : {
     …
  }
  "progress" : 100
}
```

## Periodic Client Polling   
- Polling **must** use GET on the custom method representing the polling endpoint with the request token as query parameter `request-token`.
- If the operation is still running the response **must** be HTTP 200 - OK.
- If the TTL has expired the API **must** return HTTP 410 - Gone.
- The response body **must** contain the remaining TTL in seconds as field `ttlSeconds`.
- If progress is supported, the response body **must** contain progress information in percent as 32-bit integer in the field `progress`.
- The response body **may** contain a `status` string field containing useful additional information.
- The service **may** decide to block the request for a reasonable amount of time (typically in the low single digit seconds range) to determine if it can immediately serve the response or not. This delay **must** be documented.

#### Example
```
GET /query:poll?request-token=bmQgUXVhcms

HTTP/1.1 200 OK
Content-Type: application/json
{
  "ttlSeconds" : 300,
  "progress" : 50
  "status" : "calculating stuff…"
}
```

## Final Request
- If the operation succeeded the API **must** return HTTP 200 - OK.
- If the operation failed an appropriate HTTP error response from the list in [HTTP Response Codes](../rest-api-guidelines/Conventions.md#error-codes) **must** be returned.
- After the final request any further requests with the request token **must** result in 410 - Gone.
- The response body **must** contain the result set of the request.
- If `progress` is supported, it **must** be present with 100%.
- The response body **may** contain a `status` string field containing useful additional information.

#### Example
```
GET /query:poll?request-token=bmQgUXVhcms

HTTP/1.1 200 OK
Content-Type: application/json
{
  "response" : {
     …
  }
  "progress" : 100
}
```

## Cancel
Cancellation of a long running operation **may** be supported by defining a custom method `cancel`.

Since the operation is executed asynchronously in the background, `cancel` **must** be asynchronous as well.

- If the operation is still running the `cancel` request **must** return HTTP 202 - Accepted. The response body **must** be empty in this case.
- If the operation is finished the `cancel` request **must** return HTTP 200 - OK. The response body **may** contain an intermediate result if possible. If `progress` is supported, the `progress` field **must** be present in the response body. Any further requests with the request token **must** result in HTTP 410 - Gone.
- If `cancel` is requested after the operation has timed out (this can also happen while the asynchronous cancel is in progress) HTTP 410 - Gone **must** be returned.

#### Example
```
POST /query:cancel?request-token=bmQgUXVhcms

HTTP/1.1 202 Accepted
Content-Type: application/json

POST /query:cancel?request-token=bmQgUXVhcms

HTTP/1.1 202 Accepted
Content-Type: application/json

POST /query:cancel?request-token=bmQgUXVhcms

HTTP/1.1 200 OK
Content-Type: application/json
{
  "response" : {
     …
  }
  "progress" : 70
}
```