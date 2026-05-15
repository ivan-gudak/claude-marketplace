Sometimes a K8s service provides multiple APIs which are internally identified using an [API identifier](../rest-api-guidelines/General%20Structure.md#k8s-services-and-apis). The API identifier is typically chosen as the [public service name](../rest-api-guidelines/General%20Structure.md#public-apis) exposed on the API Gateway. In this scenario the [general mapping](../permission-guidelines/General%20Mapping.md) rules apply with no exceptions or extensions. The only difference to the [Single Service API Mapping](../permission-guidelines/Single%20Service%20API%20Mapping.md) is that the public service name that is mapped to the IAM service name originates from an API identifier instead of a K8s service name.

![Multi-API Service Mapping](../permission-guidelines/img/multi%20api%20service%20mapping.png)

#### Examples

K8s service level (multiple APIs on one service):
```
persistence-service.storage/public/query-api/v1/queries:execute
persistence-service.storage/public/query-api/v1/queries:validate
persistence-service.storage/public/entity-model-registry/v2/models
```

API Gateway Mapping and IAM Permissions:
```
POST /platform/query-service/v1/queries:execute    --> 'query-service:queries:execute'
POST /platform/query-service/v1/queries:validate   --> 'query-service:queries:validate'
PUT /platform/entity-model-registry/v2/models      --> 'entity-model-registry:models:write'
```