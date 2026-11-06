import datetime as dt
import json
import os
import pathlib
import urllib.request
import urllib.parse
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
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

def growth(history, today, name, stars):
    baseline = history.get((today - dt.timedelta(days=7)).isoformat(), {}).get(name)
    return stars - baseline if baseline is not None else None

def main():
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
    history_file = ROOT / 'data/history.json'
    history = json.loads(history_file.read_text('utf-8')) if history_file.exists() else {}
    items = {}
    for query in ['stars:>1000 archived:false', 'stars:>50 archived:false created:>' + (today-dt.timedelta(days=90)).isoformat(), 'topic:ai stars:>100 archived:false']:
        for repo in get('search/repositories?' + urllib.parse.urlencode({'q': query, 'sort': 'stars', 'order': 'desc', 'per_page': 100}))['items']:
            items[repo['full_name']] = repo
        time.sleep(2)
    # Previously tracked projects stay in the observation pool.
    previous_file = ROOT / 'dist/data.json'
    previous = json.loads(previous_file.read_text('utf-8')).get('projects', []) if previous_file.exists() else []
    for old in previous:
        if old['name'] not in items:
            try: items[old['name']] = get('repos/' + old['name'])
            except urllib.error.HTTPError as e:
                if e.code not in (404, 410): raise
    projects = []
    snapshot = {}
    for name, r in items.items():
        snapshot[name] = r['stargazers_count']
        projects.append(dict(name=name, url=r['html_url'], description=r.get('description') or '暂无介绍', language=r.get('language') or '其他', stars=r['stargazers_count'], delta=growth(history, today, name, r['stargazers_count']), topics=r.get('topics', []), updated=r['pushed_at'], license=(r.get('license') or {}).get('spdx_id', '未知')))
    history[today.isoformat()] = snapshot
    reports_file = ROOT / 'data/reports.json'
    reports = json.loads(reports_file.read_text('utf-8')) if reports_file.exists() else []
    if today.weekday() == 0:
        eligible = sorted([p for p in projects if p['delta'] is not None], key=lambda p:p['delta'], reverse=True)[:10]
        if eligible:
            reports = [r for r in reports if r['date'] != today.isoformat()]
            reports.append({'date': today.isoformat(), 'projects': eligible})
    payload = {'updated': dt.datetime.now(dt.timezone.utc).isoformat(), 'projects': projects, 'reports': reports}
    for file, data in [(history_file, history), (reports_file, reports), (ROOT/'dist/data.json', payload)]:
        file.parent.mkdir(parents=True, exist_ok=True)
        temp = file.with_suffix('.tmp')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf-8')
        temp.replace(file)
    print(f'Collected {len(projects)} projects; {len(reports)} weekly reports')

if __name__ == '__main__': main()
