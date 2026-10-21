import json
import re
import urllib.parse
import urllib.request
import http.cookiejar

BASE = "https://mavendev.kalbenutritionals.web.id"
ANUGERAH = "20b177b2-5575-4c14-bb6d-be0623956e84"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def get(url):
    with op.open(url, timeout=25) as r:
        return r.geturl(), r.read().decode("utf-8", "replace")


def post_form(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
    with op.open(req, timeout=30) as r:
        return r.geturl(), r.read().decode("utf-8", "replace")


def token_of(html):
    m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', html) or re.search(
        r'value="([^"]+)"[^>]*name="__RequestVerificationToken"', html
    )
    return m.group(1)


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
req = urllib.request.Request(
    BASE + "/api/v1/df/MappingSubdistApi/GetById?id=" + ANUGERAH,
    headers={"RequestVerificationToken": tok},
)
with op.open(req, timeout=20) as r:
    data = json.loads(r.read().decode()).get("data") or {}
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
    "groupType": "Non Group",
    "namaGroup": "",
    "alamat": data.get("alamat") or "",
    "active": True,
}
req = urllib.request.Request(
    BASE + "/api/v1/df/MappingSubdistApi/Save",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json", "RequestVerificationToken": tok},
)
with op.open(req, timeout=20) as r:
    print(r.read()[:200].decode(), flush=True)
