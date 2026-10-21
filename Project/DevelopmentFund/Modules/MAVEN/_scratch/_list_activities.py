import json
import urllib.parse
import urllib.request

FLAT = "https://mavendev.kalbenutritionals.web.id/api/v1/df/outbound/SubdistApi/GetPaginateMappedFlat"
ACT = "https://mavendev.kalbenutritionals.web.id/api/v1/df/outbound/SubdistApi/GetActivitiesByGroup?groupName="

body = json.dumps({"draw": 1, "start": "0", "length": "100", "search": {"value": ""}}).encode()
req = urllib.request.Request(FLAT, data=body, headers={"Content-Type": "application/json"})
rows = json.loads(urllib.request.urlopen(req, timeout=30).read().decode()).get("data") or []
parents = []
seen = set()
for r in rows:
    if not r.get("bolParent"):
        continue
    key = r.get("id")
    if key in seen:
        continue
    seen.add(key)
    parents.append(r)

for r in parents:
    name = r.get("subdistGroupName") or ""
    url = ACT + urllib.parse.quote(name)
    try:
        raw = urllib.request.urlopen(url, timeout=20).read().decode()
        data = json.loads(raw)
        acts = data.get("activities") or data.get("Activities") or []
    except Exception as ex:
        acts = []
        print("ERR", name, ex)
    labels = ", ".join(f"{a.get('kode')} {a.get('nama')}" for a in acts[:4])
    print(f"{r.get('subdistGroupType')}|{name}|{r.get('subdistCode')}|{r.get('id')}|acts={len(acts)}|{labels}")
