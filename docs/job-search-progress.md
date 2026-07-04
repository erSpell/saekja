# Multi-source job search workflow progress

## Objective

Create a transparent job-search automation workflow that finds roles posted in the last 24 hours for:

- Data Center Technician
- IT Analyst
- IT Support
- Data Analyst
- Business Analyst
- Junior Developer
- Junior NOC Analyst
- Junior Sysadmin
- related entry/junior IT, analyst, developer, infrastructure, and network roles

Locations:

- Remote
- Columbus, OH
- nearby Columbus-area suburbs including Dublin, New Albany, Hilliard, Plain City, Westerville, Reynoldsburg, Marysville, Worthington, and Grove City

## Completed

- [x] Created initial Python workflow script
- [x] Added broad role categories
- [x] Added last-24-hour filtering
- [x] Added Columbus-area / Remote filtering
- [x] Added LinkedIn public guest endpoint search
- [x] Added Built In scraping
- [x] Added Arbeitnow API
- [x] Added Remotive API
- [x] Added RemoteOK API
- [x] Added The Muse API
- [x] Added non-LinkedIn strict-match output section
- [x] Added direct company ATS source registry
- [x] Added Greenhouse adapter
- [x] Added Lever adapter
- [x] Added direct ATS checked-count output
- [x] Verified script compiles with `python -m py_compile`
- [x] Verified frontend repo lint/build after script changes

## In progress / next steps

- [ ] Add Workday adapter for Columbus-area employers
- [ ] Add SmartRecruiters adapter
- [ ] Add GovernmentJobs / NeoGov adapter
- [ ] Add direct company source registry for Columbus-area employers using Workday or custom boards
- [ ] Add JSON result snapshots under `job_search_results/`
- [ ] Add duplicate detection across sources
- [ ] Add `new since last run` detection
- [ ] Add source coverage summary with checked / matched / failed counts per source
- [ ] Add cleaner markdown/CSV export for applications tracking

## Candidate Columbus-area employers to map

- AWS / Amazon
- Google
- Microsoft
- Meta
- Vertiv
- Black Box
- Quantum Health
- Nationwide
- Huntington
- JPMorgan Chase
- Cardinal Health
- CoverMyMeds / McKesson
- OhioHealth
- Root Insurance
- Upstart
- Bread Financial
- Ohio State / OSU Wexner
- State of Ohio
- City of Columbus
- Battelle
- Honda / Marysville
- data center vendors around New Albany, Hilliard, Dublin, and Plain City

## Source-quality policy

Prefer sources in this order:

1. Direct company career pages / ATS APIs
2. Structured ATS platforms such as Greenhouse, Lever, Workday, SmartRecruiters, Ashby
3. Built In, The Muse, Remotive, RemoteOK, Arbeitnow
4. LinkedIn public listings
5. Aggregators/reposters only when results are sparse

## Caveats

- LinkedIn remote filtering is imperfect; remote-filtered roles must be verified before applying.
- Some sites block scraping, require login, or rely on browser-rendered data.
- Some direct ATS boards have no matching roles in a given 24-hour window; this should be reported as `checked but no strict matches`, not hidden.
