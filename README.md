# artc-service

[artc](https://github.com/KDesp73/artc)

```bash
$ make start
```

## Request

```json
{
    "script": "-- lua script",
    "duration": 10
}
```

## Response

```json
{
    "video_url": "/videos/<uuid>.mp4"
}
```
