# Common Datatypes
## Integer Value (32-bit)
- Unsigned types **should not** be used
- If a signed integer where negative values are unused has a special meaning like e.g., "undefined", "infinite" the value -1 **must** be used. Arbitrary values like Integer.MAX_VALUE, etc. **must not** be used.
- All special values (including 0 if it is not obvious) **must** be clearly documented to avoid confusion.

## Long Integer Value (64-bit)
Long (64-bit) values **must** be represented as strings. This is necessary because of limitations to Javascript clients which lose precision on 64-bit values (they are represented as floating point numbers). Timestamps **may** be represented as long values as described in [Timestamp](#timestamp) (approx. valid until year 3000 in Javascript environments).

## Timezone
Time zones **must** be represented as a field named `timeZone`, which is a string containing the time zone identifier as specified in the [IANA timezone database](https://www.iana.org/time-zones)).

#### Examples
```
America/New_York
Asia/Shanghai  
Etc/GMT+8  
Europe/Berlin
```

## Timestamp
Unless explicitly defined otherwise all timestamps **should** be represented as UTC times. Time zone designators **should** be represented with offsets to the UTC timezone.

Fields representing a point in time **should** end with "Time" such as `startTime` or `endTime`. In general, if a time refers to an action, the name **should** have the form '_\<verb>Time_' such as `createTime`. Avoid using past tense for the verb, such as `createdTime`.

If timestamps are encoded as strings, they **must** be encoded in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format:
```
YYYY-MM-DD”T”HH:MM:SS.ssssss”Z”
```
#### Examples
```
startTime = "2021-10-06T11:08:14.859831Z"
endTime = "2021-10-06T11:08:14.859831-05:00"
```
An additional separate field **may** be added to clarify the time zone that is used in the timestamp (only used to increase the readability, may be used for UI display purposes).

#### Examples

| timestamp                        | timezone |
| -------------------------------- | -------- |
| 2021-10-06T11:08:14.859831Z      | GMT      |
| 2021-10-06T11:08:14.859831-05:00 | EST      |
| 2021-10-06T11:08:14.859831+01:00 | DE       |

Timestamps **may** be encoded using [Posix Epoch](https://en.wikipedia.org/wiki/Unix_time) 64-bit long values in second, millisecond, microsecond, or nanosecond resolution. Keep in mind that 64-bit values might cause problems on Javascript clients if not handled correctly.

Timestamp fields **must** contain the resolution (_seconds_, _millis_, _micros_, _nanos_) in the field name.

#### Examples
```
startTimeSeconds = 1633523598
createTimeMillis = 1633523598453
updateTimeMicros = 1633523598453862
endTimeNanos = 1633523598453862094
```

## Time Span
Time spans **should** be reflected by 2 separate fields defining the start and the end of the time span. The default interpretation being that the start time is inclusive, and the end time is exclusive. If the interpretation is different, it **must** be carefully documented.

#### Example
```
startTimeMillis = 1633523598453
endTimeMillis = 1643523598453
``` 

## Date
Dates without time-zone and time **should** be represented as strings in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) date format "YYYY-MM-DD". Field names representing a date **should** end with "Date" such as `startDate`.

#### Example
```
startDate = “2021-10-06”
```

## Language Code
Language codes **must** be represented in a field named `languageCode` containing a string that follows the [ISO 639-1](https://www.iso.org/iso-639-language-codes.html) standard. E.g., "en" for English

## Country Code
Country codes **must** be represented in a field named `countryCode` containing a string that follows the [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) standard. E.g., "DE" for Germany