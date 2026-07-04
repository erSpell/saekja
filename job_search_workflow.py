import urllib.request, urllib.parse, json, datetime, re, html, time

now = datetime.datetime.now(datetime.timezone.utc)
cutoff = now - datetime.timedelta(hours=24)

categories = {
    'IT Support': ['it support', 'help desk', 'service desk', 'desktop support', 'technical support'],
    'Analyst': ['it analyst', 'data analyst', 'business analyst', 'business systems analyst', 'business intelligence analyst', 'noc analyst', 'network analyst'],
    'Developer': ['junior developer', 'entry level developer', 'junior software developer', 'jr web developer', 'frontend developer', 'web developer', 'software engineer i'],
    'Infrastructure / Data Center': ['data center technician', 'infrastructure technician', 'engineering operations technician', 'data center operations technician'],
    'Sysadmin / Network': ['junior sysadmin', 'junior system administrator', 'system administrator', 'systems administrator', 'network administrator', 'noc technician', 'network technician'],
}

include = {
    'IT Support': re.compile(r'\b(IT Support|Help Desk|Service Desk|Desktop Support|Technical Support|Support Engineer|Support Analyst|IT Services Specialist)\b', re.I),
    'Analyst': re.compile(r'\b(Data Analyst|Business Analyst|Business Systems Analyst|Business Intelligence|BI Analyst|IT Analyst|NOC Analyst|Network Analyst|Program Analyst|Risk Analyst|Solution Center Analyst|[A-Za-z/& -]+ Analyst)\b', re.I),
    'Developer': re.compile(r'\b(Junior|Jr\.?|Entry[- ]Level|New Grad|Software Engineer I|Software Developer|Web Developer|Frontend|Front End|FrontEnd|React|JavaScript|TypeScript)\b', re.I),
    'Infrastructure / Data Center': re.compile(r'\b(Data Center|Infrastructure Technician|Engineering Operations Technician|InfraDelivery|Central Office/Data Center|Network Deploy|Deployment Build Planner)\b', re.I),
    'Sysadmin / Network': re.compile(r'\b(System Administrator|Systems Administrator|Sysadmin|Network Administrator|Network Technician|NOC|NOSC|IT Systems Administrator|Linux System Administrator|Windows Systems Administrator|Network/Systems Administrator)\b', re.I),
}

exclude = re.compile(r'(Senior|Sr\.|Lead|Principal|Manager|Director|Sales|Warehouse|Attorney|Nurse|Executive Assistant|Patient Access|Clinical Research|Transportation Engineer|Hospital Billing|Scheduling Dispatcher|Product Manager|Maintenance Technician|Mechatronics|Robotics|Associate Director)', re.I)
columbus_re = re.compile(r'\b(Columbus|Dublin|New Albany|Hilliard|Plain City|Westerville|Reynoldsburg|Marysville|Worthington|Grove City)\b|\bOhio\b|\bOH\b', re.I)
remote_re = re.compile(r'\bremote\b|United States|USA|anywhere', re.I)

direct_company_sources = [
    {'company': 'GitLab', 'ats': 'greenhouse', 'slug': 'gitlab'},
    {'company': 'Stripe', 'ats': 'greenhouse', 'slug': 'stripe'},
    {'company': 'Cloudflare', 'ats': 'greenhouse', 'slug': 'cloudflare'},
    {'company': 'Datadog', 'ats': 'greenhouse', 'slug': 'datadog'},
    {'company': 'Elastic', 'ats': 'greenhouse', 'slug': 'elastic'},
    {'company': 'MongoDB', 'ats': 'greenhouse', 'slug': 'mongodb'},
    {'company': 'Robinhood', 'ats': 'greenhouse', 'slug': 'robinhood'},
    {'company': 'Coinbase', 'ats': 'greenhouse', 'slug': 'coinbase'},
    {'company': 'OpenAI', 'ats': 'greenhouse', 'slug': 'openai'},
    {'company': 'Affirm', 'ats': 'greenhouse', 'slug': 'affirm'},
    {'company': 'Asana', 'ats': 'greenhouse', 'slug': 'asana'},
    {'company': 'Okta', 'ats': 'greenhouse', 'slug': 'okta'},
    {'company': 'Twilio', 'ats': 'greenhouse', 'slug': 'twilio'},
    {'company': 'Duolingo', 'ats': 'greenhouse', 'slug': 'duolingo'},
    {'company': 'Pinterest', 'ats': 'greenhouse', 'slug': 'pinterest'},
    {'company': 'Instacart', 'ats': 'greenhouse', 'slug': 'instacart'},
    {'company': 'Samsara', 'ats': 'greenhouse', 'slug': 'samsara'},
    {'company': 'Verkada', 'ats': 'greenhouse', 'slug': 'verkada'},
    {'company': 'Brex', 'ats': 'greenhouse', 'slug': 'brex'},
    {'company': 'Figma', 'ats': 'greenhouse', 'slug': 'figma'},
    {'company': 'Canonical', 'ats': 'greenhouse', 'slug': 'canonical'},
    {'company': 'Upstart', 'ats': 'greenhouse', 'slug': 'upstart'},
    {'company': 'Underdog', 'ats': 'greenhouse', 'slug': 'underdogfantasy'},
    {'company': 'Foxen', 'ats': 'greenhouse', 'slug': 'foxen'},
    {'company': 'EOS IT Solutions', 'ats': 'greenhouse', 'slug': 'eositsolutions'},
]

direct_sources = {'Greenhouse', 'Lever'}


def parse_dt(s):
    if not s:
        return None
    s = str(s).strip().replace('Z', '+00:00')
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.astimezone(datetime.timezone.utc)
    except Exception:
        pass
    try:
        return datetime.datetime.fromtimestamp(float(s), datetime.timezone.utc)
    except Exception:
        return None


def clean_text(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub('<.*?>', '', str(s or '')))).strip()


def parse_relative_age(text):
    text = clean_text(text).lower()
    if not text or 'just now' in text:
        return now
    m = re.search(r'(\d+)\s+minute', text)
    if m:
        return now - datetime.timedelta(minutes=int(m.group(1)))
    m = re.search(r'(\d+)\s+hour', text)
    if m:
        return now - datetime.timedelta(hours=int(m.group(1)))
    m = re.search(r'(\d+)\s+day', text)
    if m:
        return now - datetime.timedelta(days=int(m.group(1)))
    return None


def add_job(jobs, source, title, company, loc, url, dt, desc=''):
    if not title or not url:
        return
    title = clean_text(title)
    company = clean_text(company)
    loc = clean_text(loc)
    desc = str(desc or '')
    if not dt or dt < cutoff:
        return
    locblob = ' '.join([title, loc, desc[:700]])
    is_col = bool(columbus_re.search(locblob))
    is_rem = bool(remote_re.search(locblob))
    if not (is_col or is_rem):
        return
    for cat, pat in include.items():
        if pat.search(title):
            if exclude.search(title):
                continue
            typ = 'Columbus area' if is_col and not is_rem else ('Remote' if is_rem and not is_col else 'Remote/Columbus')
            age_min = int((now - dt).total_seconds() / 60) if dt else 99999
            jobs.append({
                'source': source,
                'category': cat,
                'type': typ,
                'title': title,
                'company': company,
                'location': loc,
                'posted_utc': dt.isoformat() if dt else '',
                'age_min': age_min,
                'url': url,
            })
            break


def fetch_json(url, headers=None):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore'))


def scrape_linkedin(jobs):
    for qs in categories.values():
        for q in qs:
            for loc, remote in [('Columbus, Ohio, United States', False), ('United States', True)]:
                params = {'keywords': q, 'location': loc, 'f_TPR': 'r86400', 'start': '0'}
                if remote:
                    params['f_WT'] = '2'
                url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?' + urllib.parse.urlencode(params)
                try:
                    text = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode('utf-8', 'ignore')
                except Exception:
                    continue
                for card in re.split(r'<li>\s*', text):
                    if 'job-search-card' not in card:
                        continue

                    def get(p):
                        m = re.search(p, card, re.S)
                        return clean_text(m.group(1)) if m else ''

                    title = get(r'<h3[^>]*class="[^"]*base-search-card__title[^"]*"[^>]*>(.*?)</h3>')
                    comp = get(r'<h4[^>]*class="[^"]*base-search-card__subtitle[^"]*"[^>]*>(.*?)</h4>')
                    jloc = get(r'<span[^>]*class="[^"]*job-search-card__location[^"]*"[^>]*>(.*?)</span>')
                    tm = re.search(r'<time[^>]*datetime="([^"]+)"[^>]*>(.*?)</time>', card, re.S)
                    date = tm.group(1) if tm else ''
                    posted_txt = clean_text(tm.group(2)) if tm else ''
                    dt = parse_dt(date)
                    if dt and posted_txt:
                        m = re.search(r'(\d+)\s+minute', posted_txt.lower())
                        if m:
                            dt = now - datetime.timedelta(minutes=int(m.group(1)))
                        m = re.search(r'(\d+)\s+hour', posted_txt.lower())
                        if m:
                            dt = now - datetime.timedelta(hours=int(m.group(1)))
                    linkm = re.search(r'<a[^>]+class="base-card__full-link[^>]+href="([^"]+)"', card)
                    link = html.unescape(linkm.group(1)).split('?')[0] if linkm else ''
                    add_job(jobs, 'LinkedIn', title, comp, jloc, link, dt, ('remote ' if remote else 'columbus ') + q)
                time.sleep(0.08)


def scrape_remotive(jobs):
    seen_query = set()
    for qs in categories.values():
        for q in qs:
            if q in seen_query:
                continue
            seen_query.add(q)
            try:
                data = fetch_json('https://remotive.com/api/remote-jobs?search=' + urllib.parse.quote(q))
            except Exception:
                continue
            for r in data.get('jobs', []):
                add_job(jobs, 'Remotive', r.get('title'), r.get('company_name'), 'Remote', r.get('url'), parse_dt(r.get('publication_date')), r.get('description', ''))
            time.sleep(0.05)


def scrape_remoteok(jobs):
    try:
        data = fetch_json('https://remoteok.com/api')
    except Exception:
        return
    for r in data[1:]:
        add_job(jobs, 'RemoteOK', r.get('position'), r.get('company'), 'Remote', r.get('url'), parse_dt(r.get('date')), ' '.join(r.get('tags') or []))


def scrape_arbeitnow(jobs):
    for page in range(1, 4):
        try:
            data = fetch_json('https://www.arbeitnow.com/api/job-board-api?page=' + str(page))
        except Exception:
            continue
        for r in data.get('data', []):
            loc = r.get('location') or ('Remote' if r.get('remote') else '')
            dt = datetime.datetime.fromtimestamp(r.get('created_at'), datetime.timezone.utc) if r.get('created_at') else None
            add_job(jobs, 'Arbeitnow', r.get('title'), r.get('company_name'), loc, r.get('url'), dt, r.get('description', ''))


def scrape_themuse(jobs):
    muse_locs = ['Remote', 'Columbus, OH']
    muse_cats = ['Computer and IT', 'Data and Analytics', 'Software Engineering', 'Customer Service']
    for loc in muse_locs:
        for catname in muse_cats:
            try:
                url = 'https://www.themuse.com/api/public/jobs?' + urllib.parse.urlencode({'location': loc, 'category': catname, 'page': 1})
                data = fetch_json(url)
            except Exception:
                continue
            for r in data.get('results', []):
                dt = parse_dt(r.get('publication_date'))
                locs = ', '.join([x.get('name', '') for x in r.get('locations', [])])
                add_job(jobs, 'The Muse', r.get('name'), r.get('company', {}).get('name'), locs, r.get('refs', {}).get('landing_page'), dt, '')


def scrape_builtin(jobs):
    pages = [
        'https://builtin.com/jobs/remote/customer-support',
        'https://builtin.com/jobs/remote/data-analytics',
        'https://builtin.com/jobs/remote/dev-engineering',
        'https://builtin.com/jobs/remote/it',
        'https://builtin.com/jobs/columbus/customer-support',
        'https://builtin.com/jobs/columbus/data-analytics',
        'https://builtin.com/jobs/columbus/dev-engineering',
        'https://builtin.com/jobs/columbus/it',
    ]
    for page in pages:
        try:
            req = urllib.request.Request(page, headers={'User-Agent': 'Mozilla/5.0'})
            text = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
        except Exception:
            continue
        for card in re.split(r'<div id="job-card-\d+"', text)[1:]:
            title_m = re.search(r'<a href="([^"]+)"[^>]*data-id="job-card-title"[^>]*>(.*?)</a>', card, re.S)
            company_m = re.search(r'<a [^>]*data-id="company-title"[^>]*>\s*<span>(.*?)</span>', card, re.S)
            age_m = re.search(r'<i class="fa-regular fa-clock[^>]*></i>\s*([^<]+)</span>', card, re.S)
            loc_matches = re.findall(r'<span class="font-barlow text-gray-04">([^<]+)</span>', card, re.S)
            if not title_m:
                continue
            link = title_m.group(1)
            if link.startswith('/'):
                link = 'https://builtin.com' + link
            loc = ' | '.join(clean_text(x) for x in loc_matches[:3])
            desc = 'remote' if '/remote/' in page else 'Columbus, OH'
            add_job(
                jobs,
                'Built In',
                title_m.group(2),
                company_m.group(1) if company_m else '',
                loc,
                link,
                parse_relative_age(age_m.group(1) if age_m else ''),
                desc,
            )
        time.sleep(0.1)


def scrape_greenhouse_company(jobs, company, slug):
    try:
        url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true'
        data = fetch_json(url)
    except Exception:
        return
    for job in data.get('jobs', []):
        location = (job.get('location') or {}).get('name', '')
        description = job.get('content') or ''
        add_job(
            jobs,
            'Greenhouse',
            job.get('title'),
            job.get('company_name') or company,
            location,
            job.get('absolute_url'),
            parse_dt(job.get('first_published')),
            description,
        )


def scrape_lever_company(jobs, company, slug):
    try:
        url = f'https://api.lever.co/v0/postings/{slug}?mode=json'
        data = fetch_json(url)
    except Exception:
        return
    for job in data:
        categories_data = job.get('categories') or {}
        created_at = job.get('createdAt')
        dt = datetime.datetime.fromtimestamp(created_at / 1000, datetime.timezone.utc) if created_at else None
        location = categories_data.get('location') or ''
        description = job.get('descriptionPlain') or job.get('description') or ''
        add_job(
            jobs,
            'Lever',
            job.get('text'),
            company,
            location,
            job.get('hostedUrl'),
            dt,
            description,
        )


def scrape_direct_company_sources(jobs):
    for source in direct_company_sources:
        if source['ats'] == 'greenhouse':
            scrape_greenhouse_company(jobs, source['company'], source['slug'])
        elif source['ats'] == 'lever':
            scrape_lever_company(jobs, source['company'], source['slug'])
        time.sleep(0.05)


def main():
    jobs = []
    scrape_linkedin(jobs)
    scrape_remotive(jobs)
    scrape_remoteok(jobs)
    scrape_arbeitnow(jobs)
    scrape_themuse(jobs)
    scrape_builtin(jobs)
    scrape_direct_company_sources(jobs)

    source_rank = {'Greenhouse': 0, 'Lever': 0, 'Built In': 1, 'The Muse': 1, 'Remotive': 1, 'RemoteOK': 1, 'Arbeitnow': 1, 'LinkedIn': 2}
    seen = set()
    clean = []
    for j in sorted(jobs, key=lambda x: (x['age_min'], source_rank.get(x['source'], 3))):
        norm = (re.sub(r'[^a-z0-9]+', ' ', j['title'].lower()).strip(), re.sub(r'[^a-z0-9]+', ' ', j['company'].lower()).strip())
        if norm in seen:
            continue
        seen.add(norm)
        j['score'] = 'A' if j['source'] in direct_sources or (j['type'] in ('Remote', 'Columbus area', 'Remote/Columbus') and j['source'] != 'LinkedIn') else 'B'
        clean.append(j)

    bycat = {c: [] for c in categories}
    for j in clean:
        bycat[j['category']].append(j)

    print('NOW', now.astimezone().isoformat(), 'TOTAL', len(clean), 'SOURCES', ', '.join(sorted(set(j['source'] for j in clean))))
    print('DIRECT_ATS_BOARDS_CHECKED', len(direct_company_sources), 'GREENHOUSE_LEVER')
    direct_matches = [j for j in clean if j['source'] in direct_sources]
    print('\n## Direct ATS strict matches ' + str(len(direct_matches)))
    for j in direct_matches[:20]:
        age = (str(j['age_min']) + 'm') if j['age_min'] < 60 else (str(j['age_min'] // 60) + 'h')
        print(f"- {j['score']} | {j['source']} | {age} | {j['category']} | {j['type']} | {j['title']} | {j['company']} | {j['location']} | {j['url']}")
    non_linkedin = [j for j in clean if j['source'] != 'LinkedIn']
    print('\n## Non-LinkedIn strict matches ' + str(len(non_linkedin)))
    for j in non_linkedin[:20]:
        age = (str(j['age_min']) + 'm') if j['age_min'] < 60 else (str(j['age_min'] // 60) + 'h')
        print(f"- {j['score']} | {j['source']} | {age} | {j['category']} | {j['type']} | {j['title']} | {j['company']} | {j['location']} | {j['url']}")
    for cat, arr in bycat.items():
        print('\n## ' + cat + ' ' + str(len(arr)))
        for j in arr[:12]:
            age = (str(j['age_min']) + 'm') if j['age_min'] < 60 else (str(j['age_min'] // 60) + 'h')
            print(f"- {j['score']} | {j['source']} | {age} | {j['type']} | {j['title']} | {j['company']} | {j['location']} | {j['url']}")


if __name__ == '__main__':
    main()
