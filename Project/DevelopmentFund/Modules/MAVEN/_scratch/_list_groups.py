import json
import urllib.request
from collections import Counter

url = "https://mavendev.kalbenutritionals.web.id/api/v1/df/outbound/SubdistApi/GetPaginateMappedFlat"
body = json.dumps({"draw": 1, "start": "0", "length": "100", "search": {"value": ""}}).encode()
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
rows = data.get("data") or []
print("TOTAL", data.get("recordsTotal"), "RETURNED", len(rows))
parents = [r for r in rows if r.get("bolParent")]
print("PARENTS", len(parents))
print("PARENT TYPES", dict(Counter((r.get("subdistGroupType") or "") for r in parents)))
seen = set()
for r in parents:
    key = (r.get("subdistGroupName"), r.get("subdistGroupType"), r.get("subdistCode"))
    if key in seen:
        continue
    seen.add(key)
    print("|".join([
        str(r.get("subdistGroupType") or ""),
        str(r.get("subdistGroupName") or ""),
        str(r.get("subdistCode") or ""),
        str(r.get("subdistName") or ""),
    ]))
