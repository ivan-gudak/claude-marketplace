# List Filtering
If a _List_ method supports result filtering, it **must** accept a query parameter named `filter` containing a filter expression. The default is that a filter expression can refer to any of the fields in the listed resource. 
A service **may** decide that only a subset of fields can be used for filtering. This set **must** be documented. 

The filtered result is always a list regardless of the amount of entries. An empty result is considered a successful execution of the List method with a Http 200 - Ok response code.

A filter expression is a set of field-level expressions combined with boolean operators 'or', 'and' and 'not'. Round braces are supported, standard boolean operator precedence **must** be applied ('and' before 'or') if no braces are used.

General form of the field-level expression: \<fieldname> _operator_ \<value> 

## Datatypes and Operators
| Datatype	      | Operators	        | Representation                                                 |
| --------------- | ------------------- | -------------------------------------------------------------- |
| Number (short, int, long, float, double) | =, !=, < , <=, >, >= | <li>Integers: decimal and hexadecimal (with leading '0x') </li><li>Floating Point: scientific notation with optional exponent 'e' or 'E'</li> |
| String	      | =, !=, contains, starts-with, ends-with	| <li>Single quotes only: 'Hello World!'</li> <li>Special characters (e.g. the quotes) are preceded with '\'</li> <li>exact operators '=' and '!=' are case sensitive</li> <li>inexact operators 'contains', 'starts-with' and 'ends-with' are case insensitive </li>|
| Boolean	      | =, !=	            | Comparison with constants 'true' or 'false' only               |
| Date/Time	      | =, !=, <, <=, >, >=	| As [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) compliant string, may support time zones |
| List	          | in, is-empty        | A list of values of the same type, surrounded by '(' and ')'   |

## The 'in' Operator
It is allowed to compare for equality within a list of possible values, this is provided by the `in` operator.

So instead of writing
```
s = '123' or s = '456' or s = '789'
```
you can write
```
s in('123','456','789')
```
The `in` operator is supported for all datatypes except for `boolean`.

#### Example Expressions
```
age = 30
firstName = 'Konrad' and lastName = 'Zuse'
owner = 'user1' and lastModified >= '2022-02-06T11:00:00Z'
tenantUuid starts-with 'abc' and not (deleted = false or active = true)
cacheHitRate < 90.5
distance >= 1.0E4
userList is-empty
```

## Options
Depending on the underlying data model a high level of nested braces might lead to performance problems when executing the request. A service **may** decide to limit the maximum nesting depth. This limit **must** be documented.

## Tag filtering
Filtering for tags associated to resources is a special case. Tags are dynamically defined by users and consist of a generic key name plus a value associated to the key. Key names may contain any character, including whitespaces. This makes it hard to use key names as field names in a filter expression.

Therefore, filtering for certain tags **must** be implemented in the same way: 
- The key **must** be referenced using `tag.key`
- The value **must** be referenced using `tag.value`

#### Example
```
tag.key = 'my keyname' AND tag.value = 'my tag value'
```

## Grammar
The basic filter grammar can be seen [here](https://bitbucket.lab.dynatrace.org/projects/PFS/repos/filter-evaluator/browse/filter-evaluator-parser/src/main/antlr/com/dynatrace/platform/filterevaluator/parser/FilterExpression.g4). Please note that it does not define operator precedence (i.e. it does not make an assumption about the parser being LL or LR). Operator precedence must be taken care of in the parser implementation.

### Reference Implementation (Java)
https://bitbucket.lab.dynatrace.org/projects/PFS/repos/filter-evaluator/browse

Note: the reference implementation is a bit relaxed when compared to the described grammar since it is also used in the 2nd Gen monolith and therefore supports some additional characters for backward compatibility.

# Field Filtering and Partial Results
A service **may** return only a subset of all available fields of a resource by default (i.e., a _partial result_). In certain scenarios this avoids expensive background operations and unnecessary network bandwidth usage in default cases. The fields returned in the default partial result **must** be carefully documented. If an API supports partial results, it **must** provide a query parameter named `add-fields` to include fields that are missing in the default response.

Field Filtering **must** only be used in _List_ and _Get_ methods as well as custom methods representing specialized versions of _List_ and _Get_.

- `add-fields` **must** contain a comma-separated list of field names that are added to the default set of fields.
- Duplicate fields in the list **may** result in an error.
- Adding fields that are already in the default response are considered redundant and **should** be ignored.
- Referencing unknown fields **must** result in an error.
- Nested field names **must** be separated by a dot.
- If partial results are supported by an API, it **must** also support [Partial Update](../rest-api-guidelines/Standard%20Methods.md#partial-update).

#### Example
```
GET /entities

{
    "totalCount": 72,
    "nextPageKey": "…",
    "entities": [
        {
            "entityId": "HOST-0004DD30F142D18C",
        }
    ]
}

GET /entities?add-fields=lastSeenTms,properties.bitness
{
    "totalCount": 72,
    "nextPageKey": "…",
    "entities": [
        {
            "entityId": "HOST-0004DD30F142D18C",
            "lastSeenTms": 1615991063257,
            "properties": {
                "bitness": "64"
            }
        }
    ]
}
```

# Sorting
If a _List_ method supports sorting, it **must** accept a query parameter named `sort`.

- `sort` **must** contain either a single fieldname or a comma separated list of field names that defines the sorting order (list ordering **must** be left to right).
- Ascending order **should** be the default.
- Field names **may'' be prefixed with '-' for _descending_ order.
- String comparison for sorting **should** be case-insensitive.
- The API **may** restrict the set of fields that support sorting (E.g., it is pointless to sort by some arbitrary internal database key). The API **must** document the sortable fields.
- Unknown or unsupported fieldnames **should** be ignored. This behavior corresponds with the general way to handle [unknown fields](../rest-api-guidelines/Design%20Patterns.md#handling-unknown-json-fields-in-resources) in resources.

#### Example
```
GET …/problems?sort=status,-startTime,relevance 
```
Sorts by ascending `status` first, then by descending `startTime` and finally ascending `relevance`.