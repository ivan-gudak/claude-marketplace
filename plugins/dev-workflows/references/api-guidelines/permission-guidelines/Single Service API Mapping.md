The simplest mapping scenario is to define a permission for a single K8s service with exactly one exposed API. Such services are exposed as single public services on the API Gateway. 
In this scenario the [general mapping](../permission-guidelines/General%20Mapping.md) rules apply with no exceptions or extensions.

![Single Service API Mapping](../permission-guidelines/img/single%20service%20api%20mapping.png)

#### Examples

| API Endpoint                                           | IAM Permission                   |
| ------------------------------------------------------ | -------------------------------- |
| GET /platform/app-registry/v1/apps | `app-registry:apps:read` |
| POST /platform/document-store/v1/documents  | `document-store:documents:write`     |
| POST /platform/automation/v2/workflows:execute         | `automation:workflows:execute`   |
