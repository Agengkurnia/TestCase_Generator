import json
import re
import urllib.parse
import urllib.request
import http.cookiejar

BASE = "https://mavendev.kalbenutritionals.web.id"
PARENT = "a6b924f0-cf88-4d63-b50f-28b4737069ed"
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


def token(html):
    m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', html)
    if not m:
        m = re.search(r'value="([^"]+)"[^>]*name="__RequestVerificationToken"', html)
    if not m:
        raise SystemExit("no token")
    return m.group(1)


url, html = get(BASE + "/Account/Login")
print("LOGIN PAGE", url, flush=True)
url, html = post_form(BASE + "/Account/Login", {
    "__RequestVerificationToken": token(html),
    "TxtUserName": "ageng.sugianto",
    "TxtPassword": "bypass",
    "TxtCaptcha": "bypass",
})
print("AFTER LOGIN", url, flush=True)
if "ChooseRole" in url or "IntRoleId" in html:
    url, html = post_form(BASE + "/Account/ChooseRole", {
        "__RequestVerificationToken": token(html),
        "IntRoleId": "3452",
    })
    print("AFTER ROLE", url, flush=True)

url, html = get(BASE + "/DF/MappingSubdist")
print("MAP", url, flush=True)
tok = token(html)
api = BASE + "/api/v1/df/MappingSubdistApi/"
req = urllib.request.Request(api + "GetById?id=" + PARENT, headers={"RequestVerificationToken": tok})
with op.open(req, timeout=20) as r:
    detail = json.loads(r.read().decode())
data = detail.get("data") or detail
print("DETAIL", data.get("groupType"), data.get("namaGroup"), flush=True)
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
    "namaGroup": "PUTRA BUMI ASIH",
    "alamat": data.get("alamat") or "",
    "active": True,
}
req = urllib.request.Request(
    api + "Save",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json", "RequestVerificationToken": tok},
)
with op.open(req, timeout=20) as r:
    print("SAVE", r.status, r.read()[:400].decode(), flush=True)
