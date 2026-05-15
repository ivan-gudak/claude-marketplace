# General Mapping Rules
The standard mapping rules apply to [public APIs](../rest-api-guidelines/General%20Structure.md#public-apis) and [reserved APIs](../rest-api-guidelines/General%20Structure.md#reserved-apis). The fact that an API is hidden (i.e. reserved) has no impact on the IAM naming. In many cases the same permissions can be used in reserved APIs as in public APIs.

The general rule is that the [REST](https://en.wikipedia.org/wiki/Representational_state_transfer)ful API URL + method **must** be mapped to the appropriate IAM counterpart. Which resources get individual permissions depends on the logic of the service hosting these resources.

The following table describes the **required** mapping:

| REST URL                                                               | IAM Part                      |
| ---------------------------------------------------------------------- | ----------------------------- |
| [Service name](../rest-api-guidelines/General%20Structure.md#public-apis) | IAM service name              |
| API Resource                                                           | IAM resource                  |
| [API Standard Method](../rest-api-guidelines/Standard%20Methods.md)      | Predefined IAM action         |
| [API Custom Method](../rest-api-guidelines/Custom%20Methods.md)	         | IAM action                    |
 
## Standard Method Mapping
[API Standard Methods](../rest-api-guidelines/Standard%20Methods.md) **must** be mapped to the appropriate predefined IAM action:

| Standard Method                                                        | IAM Action    |
| ---------------------------------------------------------------------- | ------------- |
| [List and Get](../rest-api-guidelines/Standard%20Methods.md#list)           | `read`        |
| [Create and Update](../rest-api-guidelines/Standard%20Methods.md#create)    | `write`       |
| [Delete](../rest-api-guidelines/Standard%20Methods.md#delete)               | `delete`      |

![Standard Method Mapping](../permission-guidelines/img/standard%20method%20mapping.png)

#### Examples
| API Endpoint                                                        | IAM Permission                   |
| ------------------------------------------------------------------- | -------------------------------- |
| DELETE /platform/app-registry/v1/apps                               | `app-registry:apps:delete`       |
| GET /platform/app-registry/v1/app-icons                             | `app-registry:app-icons:read`    |
| POST /platform/document-store/v1/documents                          | `document-store:documents:write` |
| GET /platform-reserved/platform-management/v1/effective-permissions | `platform-management:effective-permissions:read` |

## Custom Method Mapping
[REST Custom Method](../rest-api-guidelines/Custom%20Methods.md) names are directly used as IAM action name.

![Custom Method Mapping](../permission-guidelines/img/custom%20method%20mapping.png)

#### Examples
| API Endpoint                                           | IAM Permission                   |
| ------------------------------------------------------ | -------------------------------- |
| POST /platform/automation/v2/workflows:execute         | `automation:workflows:execute`   |
| POST /platform-reserved/tokenservice/v1/tokens:rotate  | `tokenservice:tokens:rotate`     |

## Mapping Nested Resources
APIs **may** use nested resources with different sub-resources. In some cases, it **may** also be necessary to define separate permissions on parent resources and sub-resources. A permission for a sub-resource **should** use the sub-resource name if it is expressive enough without including the parent resource. If the sub-resource name is very generic or ambiguous it **must** be [qualified](#qualifying-ambiguous-or-generic-resources) using the parent resource name.

#### Example

Imagine a `problem-service` which manages problems and allows users to comment on problems. The API looks like this:
```
GET /platform/problem-service/problems                             - list all problems
GET /platform/problem-service/problems/<problem-id>                - read one problem
PUT /platform/problem-service/problems/<problem-id>                - update one problem
POST /problem/problem-service/problems/<problem-id>/comments       - add a comment to a problem
```

The service team can define these permissions:
```
problem-service:problems:read                                      - list or read
problem-service:problems:write                                     - update problem or add comment
```

With this set of permissions all actions are authenticated on the level of the parent resource `problems`. This means that the service has to use `problem-service:problems:write` for the check whether a user is allowed to write a comment or not. The issue with this approach is that any user who can add a comment can also update the problem which might not be desired.

In order to separate the permission for commenting, a separate permission for the sub-resource `comments` is required:
```
problem-service:problems:read
problem-service:problems:write
problem-service:comments:write
```
Now it is possible to separately assign commenting permissions to users who do not have permissions to update problems.

Note that the sub-resource `comments` is used without the parent resource `problems`. In the context of the `problem-service` the term `comment` is unique and therefore can be used without the parent resource.

## Qualifying Ambiguous or Generic Resources
Sometimes a sub-resource name only has clear meaning in the context of the parent resource or even is ambiguous because the same sub-resource name is also used in a different resource of the API. In these cases, the sub-resource name **must** be qualified by prepending the parent resource name separated with a dot ("."). Dynamic parts of the resource path (like e.g. ids) **must** be skipped.

#### Example (generic sub-resource)

| API Endpoint                                           | IAM Permission                     |
| ------------------------------------------------------ | ---------------------------------- |
| GET /platform/app-registry/v1/apps                     | `app-registry:apps:read`           |
| GET /platform/app-registry/v1/app-icons                | `app-registry:app-icons:read`      |
| GET /platform/app-registry/v1/apps/{app-id}/metadata   | `app-registry:apps.metadata:write` |

Technically it would be sufficient to use `app-registry:metadata:write` instead of `app-registry:apps.metadata:write` since the API contains only one `metadata` sub-resource, but such a permission is not self-explanatory and hard to relate without proper documentation. Qualifying the sub-resource with the parent resource `apps`clarifies the permission context.

#### Example (ambiguous sub-resource)

| API Endpoint                                             | IAM Permission                          |
| -------------------------------------------------------- | --------------------------------------- |
| GET /platform/app-registry/v1/apps                       | `app-registry:apps:read`                |
| GET /platform/app-registry/v1/app-icons                  | `app-registry:app-icons:read`           |
| GET /platform/app-registry/v1/apps/{app-id}/metadata     | `app-registry:apps.metadata:write`      |
| GET /platform/app-registry/v1/pp-icons/{app-id}/metadata | `app-registry:app-icons.metadata:write` |

In this example the API contains sub-resources `metadata` in two different resource contexts. `metadata` **must** be qualified to make the permissions unique.