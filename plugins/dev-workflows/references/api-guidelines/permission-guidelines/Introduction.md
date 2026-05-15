# Conventions
This document uses a set of key words to indicate requirement levels as defined in [rfc2119](https://www.ietf.org/rfc/rfc2119.txt):
| Keywords                     | Definition                                                                                                            |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| MUST, SHALL, REQUIRED	       | The definition is a mandatory requirement, violation is considered a mistake                                          |
| MUST NOT, SHALL NOT	       | The definition is prohibited, violation is considered a mistake                                                       |
| SHOULD, RECOMMENDED	       | The definition is not mandatory but should be carefully understood and weighted before choosing a different approach  |
| SHOULD NOT, NOT RECOMMENDED  | The definition is not prohibited but should be carefully understood and weighted before choosing a different approach |
| MAY, OPTIONAL	               | The definition is truly optional                                                                                      |

These key words are written in **bold** font.

Names of parameters, fields, objects, etc. are written in `code` font.

# Important Advice
This guide refers to concepts described in the [REST API guidelines](../rest-api-guidelines/Introduction.md). Please make yourself familiar with the [general structure](../rest-api-guidelines/General%20Structure.md) of the Dynatrace platform before reading this guide. It will help you to understand the concepts.

# Motivation
Permissions in IAM control access to everything in the Dynatrace platform: 

- Customer access to data in the database
- Customer access to platform APIs
- Dynatrace access to internal and operations APIs

Since IAM permissions are customer facing they **must** be treated as a part of the platform API. Therefore IAM permissions **must** follow a certain naming schema to be easily humanly mappable to the services and APIs they are controlling.

# Goals
- Public API naming **should** consistently match IAM permission naming
- IAM permissions **must** support K8s services with multiple different APIs
- IAM permissions **must** support multiple K8s services or APIs contributing to one public service

# IAM in a Nutshell
The general IAM permission format looks like this: 
```
{service-name}:{resource}:{action}
```

The semantics is to grant permission to execute the `{action}` on the `{resource}` that is located in the service named `{service-name}`. 

- There are no special reserved names
- There are no hierarchical permissions (e.g. no resource hierarchy as in REST)
- IAM does not support wildcards (could come later though)
- Customers can see permissions and assign them to users and user groups via IAM _policies_
- Customers cannot create their own permissions

#### Examples
```
app-engine:apps:install
storage:logs:read
document:documents:write
```

**Authentication is always user-based**. For service-to-service communication that does not involve an end user this means that in IAM a so-called _service user_ representing the calling service is introduced.

Details can be found in [Wiki](https://dt-rnd.atlassian.net/wiki/spaces/IAM/pages/34898241/IAM+policies+naming+conventions).