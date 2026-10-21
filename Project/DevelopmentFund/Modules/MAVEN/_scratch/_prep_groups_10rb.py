"""Link one activity to groups that have none, and store the Non Group name in uppercase."""
import json
import re
import urllib.parse
import urllib.request
import http.cookiejar

BASE = "https://mavendev.kalbenutritionals.web.id"
CSA = "677259f0-75a8-4d15-a328-72e5793f8362"
NEED_ACTIVITY = [
    "5187bd3c-8419-4132-809d-5573c39a0776",
    "20b177b2-5575-4c14-bb6d-be0623956e84",
    "4068e000-9b87-47de-8d69-91d053124534",
    "c6130300-6307-4b6f-9143-8e8d0b9985ef",
    "f3c177de-354c-49d8-868d-90a6000c0473",
    "b5c145d2-56e9-414a-a480-bba112ee517c",
    "24f25fbd-257b-4020-8e5f-795be06285b1",
    "ddb4b89f-f6eb-496d-b9fe-fee0dc273382",
]
ANUGERAH = "20b177b2-5575-4c14-bb6d-be0623956e84"

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get(url):
    with op.open(url, timeout=25) as r:
        return r.geturl(), r.read().decode("utf-8", "replace")


def post_form(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body)
    with op.open(req, timeout=30) as r:
        return r.geturl(), r.read().decode("utf-8", "replace")


def token_of(html):
    m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', html)
    if not m:
        m = re.search(r'value="([^"]+)"[^>]*name="__RequestVerificationToken"', html)
    if not m:
        raise SystemExit("no token")
    return m.group(1)


def api(tok, method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"RequestVerificationToken": tok}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with op.open(req, timeout=25) as r:
        return r.status, r.read().decode("utf-8", "replace")


url, html = get(BASE + "/Account/Login")
url, html = post_form(BASE + "/Account/Login", {
    "__RequestVerificationToken": token_of(html),
    "TxtUserName": "ageng.sugianto",
    "TxtPassword": "bypass",
    "TxtCaptcha": "bypass",
})
if "ChooseRole" in url or "IntRoleId" in html:
    url, html = post_form(BASE + "/Account/ChooseRole", {
        "__RequestVerificationToken": token_of(html),
        "IntRoleId": "3452",
    })
url, html = get(BASE + "/DF/MappingSubdist")
tok = token_of(html)
print("LOGGED IN", url, flush=True)

status, text = api(tok, "GET", "/api/v1/df/MappingSubdistApi/GetById?id=" + CSA)
detail = json.loads(text).get("data") or {}
acts = detail.get("activities") or []
cof = next(a for a in acts if a.get("kode") == "380202")
activity_id = cof.get("activityId") or cof.get("activityID")
print("COF", activity_id, cof.get("nama"), flush=True)

for parent_id in NEED_ACTIVITY:
    status, text = api(tok, "POST", "/api/v1/df/MappingSubdistApi/AddActivities", {
        "parentId": parent_id,
        "activityIds": [activity_id],
    })
    print("LINK", parent_id[:8], status, text[:180], flush=True)

status, text = api(tok, "GET", "/api/v1/df/MappingSubdistApi/GetById?id=" + ANUGERAH)
data = json.loads(text).get("data") or {}
print("ANUGERAH BEFORE", data.get("groupType"), data.get("namaGroup"), flush=True)
payload = {
    "id": data.get("id"),
    "kodeKmmd": data.get("kodeKmmd"),
    "namaKmmd": data.get("namaKmmd"),
    "outletName": data.get("outletName"),
    "tipeKmmd": data.get("tipeKmmd"),
    "region": data.get("region"),
    "kodeBranchEpm": data.get("kodeBranchEpm"),
    "branchEpm": data.get("branchEpm"),
    "shipToSiteUseId": data.get("shipToSiteUseId"),
    "groupType": "Group",
    "namaGroup": "ANUGERAH JAYA TJEMERLANG",
    "alamat": data.get("alamat") or "",
    "active": True,
}
status, text = api(tok, "POST", "/api/v1/df/MappingSubdistApi/Save", payload)
print("ANUGERAH SAVE", status, text[:220], flush=True)
