# sz_api

API wrapper for https://zapisy.ii.uni.wroc.pl/

## Installation:

    python3 -m pip install --user git+ssh://git@github.com/iiuni/projektzapisy.git#egg=sz_api\&subdirectory=zapisy/apps/api/rest/v1/api_wrapper

## Example:

```python
from sz_api import ZapisyApi
api = ZapisyApi('Token valid_key')
for semester in api.semesters():
    print(semester.display_name)
```

## Troubleshooting:

before opening an issue check that:

1. token is a string beginning with "Token "
