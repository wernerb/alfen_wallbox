# Alfen API endpoints

## Login
`HTTP POST https://<HOST_IP>/api/login`
```
{
    "username": "admin",
    "password": ""
}
```

## Logout
`HTTP POST https://<HOST_IP>/api/logout`


## Info
`HTTP GET https://<HOST_IP>/api/info`

## Restart
`HTTP POST https://<HOST_IP>/api/cmd`

## Log
`HTTP GET https://<HOST_IP>/api/log?offset=<OFFSET>`

>Default offset (256)

# Props
`HTTP GET https://<HOST_IP>/api/prop?ids=<PROP_CODES>`

Sample Response
```
{
    "version": 2,
    "properties": [
        {
            "id": "2060_0",
            "access": 1,
            "type": 27,
            "len": 0,
            "cat": "generic",
            "value": 6271674
        },
        {
            "id": "2056_0",
            "access": 1,
            "type": 7,
            "len": 0,
            "cat": "generic",
            "value": 27
        },
        {
            "id": "2221_3",
            "access": 1,
            "type": 8,
            "len": 0,
            "cat": "meter1",
            "value": 222.19999694824219
        },
        {
            "id": "2221_4",
            "access": 1,
            "type": 8,
            "len": 0,
            "cat": "meter1",
            "value": 222.29998779296875
        },
        {
            "id": "2221_5",
            "access": 1,
            "type": 8,
            "len": 0,
            "cat": "meter1",
            "value": 221.97000122070312
        },
        {
            "id": "2221_A",
            "access": 1,
            "type": 8,
            "len": 0,
            "cat": "meter1",
            "value": 4.56500005722046
        },
        {
            "id": "2221_B",
            "access": 1,
            "type": 8,
            "len": 0,
            "cat": "meter1",
            "value": 0
        },
        {
            "id": "2221_C",
            "access": 1,
            "type": 8,
            "len": 0,
            "cat": "meter1",
            "value": 0
        },
        {
            "id": "2221_16",
            "access": 1,
            "type": 8,
            "len": 0,
            "cat": "meter1",
            "value": 981.4000244140625
        },
        {
            "id": "2201_0",
            "access": 1,
            "type": 8,
            "len": 0,
            "cat": "temp",
            "value": 42.875
        }
    ],
    "offset": 0,
    "total": 10
}
```

### Alfen prop codes

| Code | description |
| ----------- | ----------- |
|2060_0| system uptime|
|2056_0| Number of bootups|
|2221_3| Voltage L1|
|2221_4| Voltage L2|
|2221_5| Voltage L3|
|2221_A| Current L1|
|2221_B| Current L2|
|2221_C| Current L3|
|2221_16| Active power total|
|2201_0| Temperature|
