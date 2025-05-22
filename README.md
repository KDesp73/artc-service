# artc-service

```bash
$ uvicorn main:app --reload
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
