import datetime as dt
import json
import os
import pathlib
import re
import urllib.request
import urllib.parse
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]

def trending_weekly():
    request = urllib.request.Request('https://github.com/trending?since=weekly', headers={'User-Agent': 'github-weekly-radar', 'Accept-Language': 'en-US'})
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode('utf-8')
    return parse_trending(html)

def parse_trending(html):
    ranked = []
    for article in re.findall(r'<article class="Box-row"[^>]*>(.*?)</article>', html, re.S):
        name = re.search(r'<h2\b[^>]*>.*?<a\b[^>]*href="/([^"/]+/[^"/]+)"', article, re.S)
        stars = re.search(r'([\d,]+)\s+stars? this week', article)
        if name and stars:
            ranked.append((name.group(1), int(stars.group(1).replace(',', ''))))
    if len(ranked) < 10:
        raise ValueError('GitHub Trending weekly returned fewer than 10 projects')
    return sorted(ranked, key=lambda item: (-item[1], item[0]))[:10]

def get(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'github-weekly-radar'}
    if os.getenv('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://api.github.com/' + path, headers=headers), timeout=30) as r:
                return json.load(r)
        except Exception:
            if attempt == 2: raise
            time.sleep(2 ** attempt)

def main():
    now = dt.datetime.now(dt.timezone.utc)
    today = now.astimezone(dt.timezone(dt.timedelta(hours=8))).date()
    trending = trending_weekly()
    items = {}
    for query in ['created:>=' + (now-dt.timedelta(days=7)).date().isoformat() + ' archived:false fork:false', 'stars:>1000 archived:false', 'stars:>50 archived:false created:>' + (today-dt.timedelta(days=90)).isoformat(), 'topic:ai stars:>100 archived:false']:
        for repo in get('search/repositories?' + urllib.parse.urlencode({'q': query, 'sort': 'stars', 'order': 'desc', 'per_page': 100}))['items']:
            items[repo['full_name']] = repo
        time.sleep(2)
    for name, _ in trending:
        items[name] = get('repos/' + name)
    projects = []
    for name, r in items.items():
        projects.append(dict(name=name, url=r['html_url'], description=r.get('description') or '暂无介绍', language=r.get('language') or '其他', stars=r['stargazers_count'], created=r['created_at'], topics=r.get('topics', []), updated=r['pushed_at'], license=(r.get('license') or {}).get('spdx_id', '未知')))
    by_name = {p['name']: p for p in projects}
    weekly = [dict(by_name[name], weekly_stars=stars) for name, stars in trending]
    reports_file = ROOT / 'data/reports.json'
    reports = json.loads(reports_file.read_text('utf-8')) if reports_file.exists() else []
    if today.weekday() == 0 and weekly:
        reports = [r for r in reports if r['date'] != today.isoformat()]
        reports.append({'date': today.isoformat(), 'projects': weekly})
    payload = {'updated': now.isoformat(), 'projects': projects, 'weekly': weekly, 'reports': reports}
    for file, data in [(reports_file, reports), (ROOT/'dist/data.json', payload)]:
        file.parent.mkdir(parents=True, exist_ok=True)
        temp = file.with_suffix('.tmp')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf-8')
        temp.replace(file)
    print(f'Collected {len(projects)} projects; {len(reports)} weekly reports')

if __name__ == '__main__': main()
