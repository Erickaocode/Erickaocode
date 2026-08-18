#!/usr/bin/env python3
"""Gera assets/stats.svg com dados reais da API do GitHub.

Uso:
    python scripts/build_stats.py --login Erickaocode --out assets/stats.svg
    python scripts/build_stats.py --mock            # testa o layout sem API

Token: le GH_TOKEN (PAT) ou GITHUB_TOKEN (padrao das Actions).
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com/graphql"

# ─────────────────────────── paleta / tipografia ───────────────────────────
VOID, PANEL = "#05070A", "#0A0E14"
BLUE, CYAN = "#1F6FEB", "#58C4FF"
TXT, DIM, DIM2 = "#F0F6FC", "#6E7681", "#7D8590"
BODY = "#C9D1D9"
MONO = ("ui-monospace, SFMono-Regular, &#34;SF Mono&#34;, Menlo, Consolas, "
        "&#34;Liberation Mono&#34;, monospace")
# rampa de azul para as barras (mantem a paleta em vez das cores das linguagens)
RAMP = ["#58C4FF", "#3B95F0", "#1F6FEB", "#1A55B8", "#173F85", "#152F5E"]

Q_REPOS = """
query($login:String!, $cursor:String) {
  user(login:$login) {
    createdAt
    repositories(first:100, after:$cursor, ownerAffiliations:OWNER, isFork:false) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first:12, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}"""

Q_YEAR = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def gql(query, variables, token):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "readme-stats-builder",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(json.dumps(payload["errors"])[:600])
    return payload["data"]


def fetch(login, token):
    # repositorios: estrelas + tamanho por linguagem (paginado)
    stars, repos, langs, cursor, created = 0, 0, {}, None, None
    while True:
        d = gql(Q_REPOS, {"login": login, "cursor": cursor}, token)["user"]
        created = created or d["createdAt"]
        rp = d["repositories"]
        repos = rp["totalCount"]
        for n in rp["nodes"]:
            stars += n["stargazerCount"]
            for e in n["languages"]["edges"]:
                langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
        if not rp["pageInfo"]["hasNextPage"]:
            break
        cursor = rp["pageInfo"]["endCursor"]

    # contribuicoes ano a ano (a API limita cada consulta a 1 ano)
    start = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
    today = dt.datetime.now(dt.timezone.utc)
    days, commits, prs = {}, 0, 0
    for year in range(start.year, today.year + 1):
        frm = max(start, dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
        to = min(today, dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        if frm >= to:
            continue
        c = gql(Q_YEAR, {"login": login,
                         "from": frm.isoformat(), "to": to.isoformat()},
                token)["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"]
        prs += c["totalPullRequestContributions"]
        for w in c["contributionCalendar"]["weeks"]:
            for d2 in w["contributionDays"]:
                days[d2["date"]] = d2["contributionCount"]

    return {"days": days, "commits": commits, "prs": prs, "stars": stars,
            "repos": repos, "langs": langs, "created": start.date().isoformat()}


def streaks(days):
    """Retorna (total, streak atual, maior streak)."""
    if not days:
        return 0, 0, 0
    total = sum(days.values())
    ordered = sorted(days)

    longest = run = 0
    prev = None
    for d in ordered:
        cur = dt.date.fromisoformat(d)
        if days[d] > 0:
            run = run + 1 if (prev and (cur - prev).days == 1) else 1
            longest = max(longest, run)
        else:
            run = 0
        prev = cur

    # atual: conta de hoje pra tras; se hoje ainda esta zerado, comeca de ontem
    today = dt.date.today()
    anchor = today if days.get(today.isoformat(), 0) > 0 else today - dt.timedelta(days=1)
    current = 0
    while days.get(anchor.isoformat(), 0) > 0:
        current += 1
        anchor -= dt.timedelta(days=1)
    return total, current, longest


# ─────────────────────────── render ───────────────────────────
W, H = 1000, 300
PAD = 46
DIV = 520          # divisoria vertical
RCOL = 560         # inicio da coluna direita
BAR_X, BAR_W = 700, 182


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def brackets(x, y, w, h, off=9, arm=20, sw=2):
    c = [(x - off, y - off, 1, 1), (x + w + off, y - off, -1, 1),
         (x - off, y + h + off, 1, -1), (x + w + off, y + h + off, -1, -1)]
    return "\n  ".join(
        f'<path d="M {bx+dx*arm} {by} H {bx} V {by+dy*arm}" fill="none" '
        f'stroke="{BLUE}" stroke-width="{sw}" stroke-linecap="square"/>'
        for bx, by, dx, dy in c)


def figure(x, value, l1, l2):
    return (f'<text x="{x}" y="126" font-family="{MONO}" font-size="40" font-weight="700" '
            f'fill="{TXT}">{value}</text>'
            f'<text x="{x}" y="150" font-family="{MONO}" font-size="9.5" letter-spacing="1.9" '
            f'fill="{DIM}">{l1}</text>'
            f'<text x="{x}" y="163" font-family="{MONO}" font-size="9.5" letter-spacing="1.9" '
            f'fill="{DIM}">{l2}</text>')


def render(d):
    total, cur, longest = streaks(d["days"])

    tot_size = sum(d["langs"].values()) or 1
    top = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:5]

    rows = []
    for i, (name, size) in enumerate(top):
        y = 136 + i * 25
        pct = size / tot_size * 100
        w = max(2.5, BAR_W * size / tot_size)
        rows.append(
            f'<text x="{RCOL}" y="{y+3}" font-family="{MONO}" font-size="12" '
            f'fill="{BODY}">{esc(name)[:14]}</text>'
            f'<rect x="{BAR_X}" y="{y-5}" width="{BAR_W}" height="8" rx="4" '
            f'fill="{BLUE}" fill-opacity="0.10"/>'
            f'<rect x="{BAR_X}" y="{y-5}" width="{w:.1f}" height="8" rx="4" '
            f'fill="{RAMP[i % len(RAMP)]}"/>'
            f'<text x="{W-PAD}" y="{y+3}" font-family="{MONO}" font-size="11.5" '
            f'text-anchor="end" fill="{DIM2}">{pct:.1f}%</text>')

    today = dt.date.today().isoformat()
    span = f'{d["created"]} &#8594; {today}'

    def plural(n, word):
        return f'{n} {word}' if n == 1 else f'{n} {word}s'

    secondary = ' &#183; '.join([
        plural(d["commits"], "commit"), plural(d["prs"], "PR"),
        plural(d["repos"], "repo"), plural(d["stars"], "star"),
    ])

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     role="img" aria-label="Atividade no GitHub: {total} contribuicoes, streak atual de {cur} dias">
  <title>GitHub activity</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{VOID}"/>
    </linearGradient>
    <pattern id="raster" width="4" height="3" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="{CYAN}"/>
    </pattern>
  </defs>

  <rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="14"
        fill="url(#bg)" stroke="{BLUE}" stroke-opacity="0.26" stroke-width="1.5"/>
  <rect x="{PAD}" y="24" width="{W-PAD*2}" height="{H-48}" fill="url(#raster)" opacity="0.045"/>
  {brackets(PAD-8, 24, W-PAD*2+16, H-48)}

  <text x="{PAD}" y="42" font-family="{MONO}" font-size="10" letter-spacing="3"
        fill="{BLUE}" font-weight="700">ACTIVITY</text>
  <text x="{W-PAD}" y="42" font-family="{MONO}" font-size="10" letter-spacing="1.4"
        text-anchor="end" fill="{DIM}">{span}</text>
  <rect x="{PAD}" y="54" width="{W-PAD*2}" height="1.4" fill="{BLUE}" fill-opacity="0.42"/>

  {figure(PAD, total, "TOTAL", "CONTRIBUTIONS")}
  {figure(PAD+190, cur, "CURRENT", "STREAK")}
  {figure(PAD+350, longest, "LONGEST", "STREAK")}
  <text x="{PAD}" y="205" font-family="{MONO}" font-size="12" fill="{DIM2}">{secondary}</text>

  <rect x="{DIV}" y="76" width="1.2" height="150" fill="{BLUE}" fill-opacity="0.30"/>

  <text x="{RCOL}" y="100" font-family="{MONO}" font-size="10" letter-spacing="3"
        fill="{BLUE}" font-weight="700">LANGUAGES</text>
  <rect x="{RCOL}" y="110" width="{W-PAD-RCOL}" height="1.2" fill="{BLUE}" fill-opacity="0.30"/>
  {''.join(rows)}

  <rect x="{PAD}" y="248" width="{W-PAD*2}" height="1.2" fill="{BLUE}" fill-opacity="0.22"/>
  <text x="{PAD}" y="270" font-family="{MONO}" font-size="10.5"
        fill="{DIM2}">&#62; rebuilt daily by GitHub Actions &#183; last run {today}</text>
</svg>
'''


MOCK = {
    "days": {(dt.date.today() - dt.timedelta(days=i)).isoformat():
             (3 if i in (0, 1) or 40 <= i <= 43 else (1 if i % 7 == 0 else 0))
             for i in range(420)},
    "commits": 47, "prs": 3, "repos": 12, "stars": 1,
    "langs": {"HTML": 866, "TypeScript": 125, "CSS": 5, "JavaScript": 3, "PHP": 15},
    "created": "2025-01-07",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", default=os.environ.get("GH_LOGIN", "Erickaocode"))
    ap.add_argument("--out", default="assets/stats.svg")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()

    if a.mock:
        data = MOCK
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("erro: defina GH_TOKEN ou GITHUB_TOKEN")
        try:
            data = fetch(a.login, token)
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
            sys.exit(f"erro ao consultar a API do GitHub: {e}\n"
                     "se persistir, crie um PAT (scope: read:user) e salve como "
                     "secret GH_TOKEN no repositorio.")

    out = a.out
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(data))
    t, c, l = streaks(data["days"])
    print(f"{out} escrito - total={t} atual={c} maior={l} "
          f"commits={data['commits']} repos={data['repos']}")


if __name__ == "__main__":
    main()
