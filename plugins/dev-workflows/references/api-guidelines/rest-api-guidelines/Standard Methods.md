# Standard Methods
Most REST APIs can be designed by using only a small set of _standard methods_ when working with resources. These standard methods map naturally to HTTP methods which makes it easy to understand the API. It is **recommended** to prefer standard methods over the definition of [custom methods](../rest-api-guidelines/Custom%20Methods.md).

In General: All standard methods may return either [warnings](../rest-api-guidelines/Common%20Schemas.md#warnings-in-responses) or [errors](../rest-api-guidelines/Common%20Schemas.md#error-response-format) in addition to the specified response.

## Standard Method Mapping to HTTP Methods

| Standard Method	    | HTTP Method	                    | Request Body	  | Response Body                           |
| ------------------- | ------------------------------- | --------------- | --------------------------------------- |
| _List_	            | GET \<resource collection URL>  | \<empty>	      | List of resources                       |
| _Get_               | GET \<resource URL>             | \<empty>	      | Single resource                         |
| _Create_            | POST \<resource collection URL> | Single Resource |	Single Resource                         |
| _Update (Full)_     | PUT \<resource URL>             | Single Resource	| Single Resource, \<empty> or \<version> |
| _Update (Partial)_  | PATCH \<resource URL>           | Single Resource (partial)	| \<empty> or \<version>        |
| _Delete_            | DELETE \<resource URL>          | \<empty>        |	\<empty>                                |

## List
The _List_ method is the usual way to search for resources in a resource collection not covered by DQL. It **may** take additional HTTP query parameters to refine the search (e.g., [filtering](../rest-api-guidelines/Filtering%20And%20Sorting.md#list-filtering) or [sorting](../rest-api-guidelines/Filtering%20And%20Sorting.md#sorting)).

- List **must** use the HTTP GET method.
- List **must not** use a request body.
- The response body **must** contain a (possibly empty) list of resources.

#### Examples
```
GET /platform/app-registry/v1/apps
GET /platform/app-registry/v1/app-icons
```

## Get
The _Get_ method accesses a single resource and returns its content in the response body. It **may** take additional HTTP query parameters to refine the access (e.g., [field filtering](../rest-api-guidelines/Filtering%20And%20Sorting.md#field-filtering-and-partial-results))

- _Get_ **must** use the HTTP GET method.
- _Get_ **must not** use a request body.
- The response body **must** contain the resource content if successful.

#### Examples
```
GET /platform/app-registry/v1/apps/{app-id}
GET /platform/app-registry/v1/app-icons/{icon-id}
```

## Create
The _Create_ method creates a new resource within the specified resource collection. It **may** take additional HTTP query parameters to refine the creation process.

- _Create_ **must** use the HTTP POST method.
- _Create_ **may** accept a resource id to assign to the created resource to allow callers to select the id. If the resource id already exists, the method execution **must** fail.
- _Create_ **may** accept a request body with a selection of fields necessary to construct the resource. Optional fields may be supported and be filled with appropriate defaults values.
- On successful execution _Create_ **must** return HTTP 201 - Created.
- _Create_ **should** return the resource id in the [Location](https://www.rfc-editor.org/rfc/rfc7231#section-7.1.2) header as a relative URL that can be directly used in the Get method. An API **may** choose to not return the resource id at all (e.g., if the Create method is effectively a mass data ingest endpoint), this **must** be documented.
- The Response body **should** contain the created resource. An API **may** choose to not return the resource at all (e.g., if the _Create_ method is effectively a mass data ingest endpoint), this **must** be documented.

#### Examples
```
POST /platform/app-registry/v1/apps
HTTP/1.1 201 Created
Content-Type: application/json
Location: /my-app-id
{
  “app-id”: “my-app-id”,
  “version”: “2.3.4”,
  …
}
```

## Update
The _Update_ method **must** support a full update, it **may** also support partial updates using PATCH. The most common use case is to update an already existing resource with new content. _Update_ **may** take additional HTTP query parameters to refine the update (this **must** be documented).

### Full Update
- _Full Update_ **must** use the HTTP PUT method.
- _Full Update_ **may** allow the caller to provide non existing resource ids to create a new resource.
- If _Full Update_ allows to create resources, it **should** also provide a _Create_ method.
- The request body **must** contain all fields of the resource (exception: [read-only fields](../rest-api-guidelines/Design%20Patterns.md)).
    - Fields that are missing in the request body are considered to be removed (this deletes existing content of the missing field). 
- On successful execution _Full Update_ **must** return HTTP 200 - OK if it was used for updating a resource.
- On successful execution _Full Update_ **must** return HTTP 201 - Created if it was used for creating a resource.
- If _Full Update_ was used to create a new resource, it **should** return the resource id in the [Location](https://www.rfc-editor.org/rfc/rfc7231#section-7.1.2) header as a relative URL that can be directly used in the _Get_ method. 
- If _Full Update_ was used to create a new resource, the Response body **should** contain the created resource.
- If _Full Update_ was used to update a resource, the response body **must** be empty.
    - **Exception**: if the resource supports [optimistic locking](../rest-api-guidelines/Conflicts%20and%20Locking.md#optimistic-locking), the response body **must** only contain the created version in the field "version".
    - **Exception**: if the resource supports [resource modification info](../rest-api-guidelines/Common%20Schemas.md#resource-modification-info), the response body **may** contain the updated _modificationInfo_ field to reflect the change.

#### Example
```
PUT /platform/document/v1/documents/{document-id}

HTTP/1.1 200
OK
Content-Type: application/json
{  
  “version”: “2.3.4”
}
```

## Partial Update
- _Partial Update_ **must** use the HTTP PATCH method.
- A _Partial Update_ request body **must** contain the updated fields only.
    - Any fields missing in the request body are not changed by the partial update request. 
    - Fields are removed by explicitly setting them to `null` (except scalar values). 
- _JSON Patch_ ([RFC 6902](https://datatracker.ietf.org/doc/html/rfc6902)) **must not** be used.
- _Partial Update_ **must not** be used to create a new resource.
- On successful execution _Partial Update_ **must** return HTTP 200 - OK.
- The response body **must** be empty.
    - **Exception**: if the resource supports [optimistic locking](../rest-api-guidelines/Conflicts%20and%20Locking.md#optimistic-locking), the response body **must** only contain the created version in the field "version".

#### Example
```
PATCH /platform/document/v1/documents/{document-id}

HTTP/1.1 200
OK
Content-Type: application/json
{  
  “version”: “2.3.4”
}
```

### How to implement partial update
Platform services are implemented as Java Spring boot applications that use built-in Spring object mapping. Under the hood each parameter is running through a Jackson `ObjectMapper`. Unfortunately, Java pojos cannot distinguish between a missing Json field and a field that was explicitly set to null after the object mapping has taken place.

There is a way though to detect the difference: by parsing the incoming Json string manually into a Json tree and look at the result. 

In order to get a _String_ generated into the server code, we need to adjust the code generator and tell it to map the schema of the PATCH body to a String. We can do this by using the [schema mapping](https://openapi-generator.tech/docs/customization/#schema-mapping) function of the code generator.
We need to add the following line to the [build.gradle.kts](https://bitbucket.lab.dynatrace.org/projects/PFS/repos/platform-service-template/browse/template-content/service-api/build.gradle.kts#82) file of the service API:
```
schemaMappings.put("<your PATCH schema name>", "String")
```
This affects only the generation of server code, not SDK code generation.

**Caveat**: this setting maps all usages of the schema in the whole file with a string. If it is used in other endpoints of the API as well, you need to define a separate schema for the PATCH method.

#### Example
```
private static class Content {
    Content() { }

    public String a = null;
    public String b = null;
    public String c = null;
}

void test() throws IOException {
    ObjectMapper objectMapper = new ObjectMapper();

    String s = "{ \"a\": \"abc\", \"b\": null }";

    JsonParser parser = objectMapper.createParser(s);
    TreeNode treeNode = parser.readValueAsTree();

    TreeNode aNode = treeNode.get("a");
    TreeNode bNode = treeNode.get("b");
    TreeNode cNode = treeNode.get("c");
}
```
Missing fields do not have a tree node in the tree while explicit null values get a dedicated `NullNode`:

![Parser Result](../rest-api-guidelines/img/parser%20result.png)