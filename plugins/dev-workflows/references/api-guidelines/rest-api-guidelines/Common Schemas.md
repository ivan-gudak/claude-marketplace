# Successful Response Format

- HTTP content-type **should** be `application/json` as registered at [IANA](https://www.iana.org/).
- Sometimes different content-types are explicitly necessary (e.g., when dealing with blob storage APIs or documents), in these cases appropriate well-known content-types as registered at [IANA](https://www.iana.org/) **must** be used (self-defined custom types **must not** be used).
- When the response body represents a collection of items it **should** be wrapped into a response envelope, this allows to extend the response at a later point in time without breaking the interface. This is especially helpful when adding pagination functionality to collections later.
- Responses **must not** contain secrets directly, instead references into the _Platform Secret Vault_ **must** be returned.
#### Example (from the Settings API)
```
{
   "items": [
     {
        "latestSchemaVersion": "1.4.2",
        "schemaId": "builtin:anomaly.infrastructure",
        "displayName": "Anomaly Detection for Infrastructure"
     }
   ],
  "totalCount": 1
}
```

# Warnings in Responses
Sometimes a response **may** contain warning information although the request was successful. This may happen e.g., when some data in the request payload was missing and replaced with default values.

Warnings are purely optional but if a response contains warnings they **must** be returned as the first field in the response body, named `warnings`. It **must** contain an array of potential warning objects. 
Each warning object must contain a string field named `message` which contains the warning message.

#### Example
```
{
    "warnings": [
        {
            "message": "manifest version information is missing"
        },
        {
            "message": "application description is missing"
        }
    ],    
    "items": [ 
        { 
            "latestSchemaVersion": "1.4.2", 
            "schemaId": "builtin:anomaly.infrastructure", 
            "displayName": "Anomaly Detection for Infrastructure" 
        } 
    ], 
    "totalCount": 1
}
```
- Additional details about each warning **may** be added in a `details` field.
  - This section should be used to convey additional information about the warning like e.g., which query parameter exactly violated a precondition.
  - `details` **may** contain any fields to further describe the warning.

## Common "details" fields
These are commonly used fields in the details object.

- `warningRef`, which is a uuid string (see [RFC 4122](https://www.rfc-editor.org/rfc/rfc4122)) and represents a reference of the warning into e.g., the log file of the service.
- `traceId`, which is a string containing a 32-character hex integer value.
- `constraintViolations`, which is an array of `ConstraintViolation` objects.
- A `ConstraintViolation` object contains information about an input parameter (path, query or request body) that violated some validation rule of the service API and caused the warning.
  - `ConstraintViolation` **must** contain a field named `message` describing the warning.
  - `ConstraintViolation` **may** contain a separate field named `parameterLocation` which describes the general location of the violating parameter (query parameter, request body, etc.)
  - `ConstraintViolation` **may* contain a separate field named `path` which refers to the violating parameter within the `parameterLocation`.
  - `ConstraintViolation` **may** contain additional fields further describing the warning.

#### Example
```
{
    "warnings": [
        {
            "message": "version information missing"
            "details": {
                "warningRef": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
                "traceId": "99633483d17779d7c81141f50dbc2a49",
                "constraintViolations": [
                    {
                        "path": "manifest.version",
                        "message": "App version not defined in the manifest, using default of 1.0.0",
                        "parameterLocation": "PAYLOAD_BODY"
                    }
                ]
            }
        },
        {
            "message": "caffeine saturation is low"
            "details": {
                "warningRef": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
                "constraintViolations": [
                    {
                        "path": "dynatrace.employee",
                        "message": "Caffeine is getting low! Grab a cappuccino in the Dynatrace cafeteria!",
                        "parameterLocation": "DYNATRACE_OFFICE"
                    }
                ]
            }
        }
    ],
    "items": [
        {
            "latestSchemaVersion": "1.4.2",
            "schemaId": "builtin:anomaly.infrastructure",
            "displayName": "Anomaly Detection for Infrastructure"
        }
    ],
    "totalCount": 1
}
```

# Error Response Format
 
- HTTP content-type **must** be `application/json` as registered at [IANA](https://www.iana.org/).
- Error responses **must not** contain information that exposes knowledge about the underlying system.
  - No stack traces
  - No class names
  - No product names or version numbers
- Error responses must be returned in an error envelope like this:
```
{
    "error": {
        "code": <error code>,
        "message": "error message"
    }
}
```
- `code` **should** be set to the HTTP error code by default.
  - `code` **may** be set to an API-specific error code which **must** be properly documented.
- The error `message` **should** be short and precise, it **should not** contain details.
- An additional `help` field **may** be added which **must** be a URL to further information on how to deal with the error.
  - This **may** be some detailed error documentation page or a link to the Dynatrace support system, etc.
- Additional details about the error **may** be added in a `details` field.
  - This section **should** be used to convey additional information about the error like e.g., which query parameter exactly violated a precondition.
  - `details` **may** contain any fields to further describe the error

## Common "details" fields
These are commonly used fields in the `details` object:

- `errorRef`, which is a uuid string (see [RFC 4122](https://www.rfc-editor.org/rfc/rfc4122)) and represents a reference of the error into e.g., the log file of the service.
- `traceId`, which is a string containing a 32-character hex integer value.
- `errorCode`, which is a string value and represents a more detailed error information than the http response code alone.
  - The string **must** be a single word in _CamelCase_, and all possible values **must** be documented 
- `constraintViolations`, which is an array of `ConstraintViolation` objects.
- A `ConstraintViolation` contains information about an input parameter (path, query or request body) that violated some validation rule of the service API (e.g., maximum string length, non-negative numbers, etc.).
  - `ConstraintViolation` **must** contain a field named `message` describing the error.
  - `ConstraintViolation` **may** contain a separate field named `parameterLocation` which describes the general location of the violating parameter (query parameter, request body, etc.)
  - `ConstraintViolation` **may** contain a separate field named `path` which refers to the violating parameter within the `parameterLocation`.
  - `ConstraintViolation` **may** contain additional fields further describing the error.
- `missingScopes`, which **should** be set if the API returns a 403 - Forbidden response in case of missing OAuth scopes.
  - `missingScopes` **must** be an array of strings containing a complete list of missing IAM scopes necessary to successfully execute the request.
- `missingPermissions`, which **should** be set if the API returns a 403 - Forbidden response in case of missing OAuth user permissions.
  - `missingPermissions` **must** be an array of strings containing a complete list of missing IAM permissions necessary to successfully execute the request.

#### Examples
```
{
    "error": {
        "code": 400,
        "message": "Constraints violated.",
        "details": {
           "errorRef": "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
           "traceId": "99633483d17779d7c81141f50dbc2a49",
           "errorCode": "InvalidPaginationToken",
           "constraintViolations": [
              {
                  "path": "detectionRules[0].filterConfig.pattern",
                  "message": "may not be null",
                  "parameterLocation": "PAYLOAD_BODY"
              }
           ]
        }
    }
}

{
    "error": {
        "code": 403,
        "message": "missing OAuth scopes.",
        "details": {
            "missingScopes": [ "document:documents:read", "state:app-states:write" ]
        },
        "help": "https://dt-url.net/upgrade-licence"
    }
}
```

# Resource Modification Info
In many cases an API allows to create and modify resources. Such APIs **should** support a separate Json object named `modificationInfo` containing the most common information about the creation and 
modification of the resource similar to common file systems. This object **should** include:
 
- Creation timestamp (UTC time as string)
- Creation user (user id)
- Last modification timestamp (UTC time as string)
- Last modifying user (user id)
- Reason information about the last modification (string) - this field is optional

The object **must** use this naming schema:
```
"modificationInfo": {
   "createdBy": "123e4567-e89b-12d3-a456-426614174000",
   "createdTime": "2022-05-25T10:24:04.202Z",
   "lastModifiedBy": "123e4567-e89b-12d3-a456-426614174000",
   "lastModifiedTime": "2022-05-25T10:24:04.202Z",
   "lastModifiedReason": "migration to schema version 4"
}
```

- The object **must not** contain any other information. If a resource does not support modification, the "lastModified*" fields **may** be skipped.
- The object **must** use the anonymous user id, clear names **must not** be used for data privacy reasons.
- `modificationInfo` **may** be added to resources as an optional field (e.g., only available via [Field Filtering](../rest-api-guidelines/Filtering%20And%20Sorting.md#field-filtering-and-partial-results)).

#### Example
```
{
   "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
   "descriptor": {
      "name": "my secret",
      "description": "some description"
   },
   "modificationInfo": {
      "createdBy": "123e4567-e89b-12d3-a456-426614174000",
      "createdTime": "2022-05-25T10:24:04.202Z",
      "lastModifiedBy": "123e4567-e89b-12d3-a456-426614174000",
      "lastModifiedTime": "2022-05-25T10:24:04.202Z",
      "lastModifiedReason": "migration to schema version 4"
   }
}
```

# Resource Context Info
When accessing a resource via the _List_ or _Get_ method it is sometimes necessary to add additional meta information which is not part of the resource itself but retrieved 
from different sources. An example would be to add allowed operations on a resource for a UI to proactively display or hide certain widgets for more usability. 
This type of information is not considered a default part of the resource and **should** require to be explicitly requested using the [Partial Results](../rest-api-guidelines/Filtering%20And%20Sorting.md#field-filtering-and-partial-results) mechanism.

The optional field **must** be named `resourceContext` and **may** contain additional meta information about the requested resource.

#### Example
```
GET /platform/registry/v1/apps?add-fields=resourceContext

{
  "apps": [
    {
      "manifest": {
        "id": "com.dynatrace.cluster"
        "name": "Cluster Wrapper App",
      },
      ...
      "resourceContext": {
        ...
      }
    },
    {
      "manifest": {
        "id": “com.dynatrace.intentsender”
      },
      "name": "Intent Sender",
      ...
      "resourceContext": {
        ...
      }
    }
  ]
}
```

## Allowed Operations on a Resource
The most common use case for resource context information is to add operations that are allowed on the returned resource depending on the user's IAM permissions on the resource. 
Allowed operations **must** be represented as strings containing a single _lowercase_ verb in the field `operations` in `resourceContext`.

- The verb defining the operation **must** be consistent with the operation naming on the REST API level.
- The verb defining the operation **must** be consistent with the permission name assigned to the operation.
- Standard CRUD operations **should** be represented with standard operation names unless more appropriate operation names can be provided
  - "read"
  - "write"
  - "delete"
- If an operation is representing an endpoint using a [custom method](../rest-api-guidelines/Custom%20Methods.md), it **should** use the same name as the method itself.
- Operation strings **must** be documented.

#### Example
```
GET /platform/registry/v1/apps?add-fields=resourceContext

{
  "apps": [
    {
      "manifest": {
        "id": "com.dynatrace.cluster"
        "name": "Cluster Wrapper App",
      },
      ...
      "resourceContext": {
        "operations": [              -- user full permissions on the App
           "install",
           "uninstall",
           "execute"
        ]
      }
    },
    {
      "manifest": {
        "id": “com.dynatrace.intentsender”
      },
      "name": "Intent Sender",
      ...
      "resourceContext": {
        "operations": [             -- user can only use the App but not affect its lifecycle
          "execute"
        ]
      }
    }
  ]
}
```

Side Note: This approach is somewhat similar to the [HATEOAS](https://en.wikipedia.org/wiki/HATEOAS) approach but is less restrictive and also less effort to implement on the service side.

# User Context
Some resources maintain user-specific information which is not an intrinsic part of the resource itself but instead a convenience addition for human users. This information is typically only used in a UI.

#### Examples are

- A "last accessed" timestamp per user (allows to sort resources by last access when generating menus)
- A list of pinned favorites per user (allows to prefer certain resources when showing dropdown menus, etc.)

Such information **must** be separated from the resource data by using an optional field named `userContext` which contains the user-specific data.

#### Example
```
GET /platform/registry/v1/apps?add-fields=userContext

{
  "apps": [
    {
      "manifest": {
        "id": "com.dynatrace.cluster"
        "name": "Cluster Wrapper App"
      },
      ...
      "userContext": {
        "lastAccessedTime": 12345,
        "pinned": true
      }
    },
    {
      "manifest": {
        "id": "com.dynatrace.intentsender"
      },
      "name": "Intent Sender",
      ...
      "userContext": {
        "lastAccessedTime": 12345
      }
    }
  ]
}
```