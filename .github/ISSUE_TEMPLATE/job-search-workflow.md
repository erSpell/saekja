---
name: Job search workflow improvement
description: Track improvements to the multi-source job search workflow
title: "Build multi-source job search workflow with ATS/company career-page support"
labels: ["automation", "job-search", "enhancement"]
assignees: []
---

## Goal

Build a repeatable job-search workflow that finds roles posted in the last 24 hours for Remote or Columbus, OH / nearby Columbus-area positions.

## Target categories

- [ ] IT Support
- [ ] Analyst
- [ ] Developer
- [ ] Infrastructure / Data Center
- [ ] Sysadmin / Network

## Implemented sources

- [x] LinkedIn public guest endpoint
- [x] Built In
- [x] Arbeitnow
- [x] Remotive
- [x] RemoteOK
- [x] The Muse
- [x] Greenhouse direct ATS adapter
- [x] Lever direct ATS adapter

## Next source adapters

- [ ] Workday
- [ ] SmartRecruiters
- [ ] Ashby
- [ ] GovernmentJobs / NeoGov
- [ ] Custom company career pages

## Output improvements

- [x] Show non-LinkedIn strict matches separately
- [x] Show direct ATS strict matches separately
- [x] Show number of direct ATS boards checked
- [ ] Show checked / matched / failed count by source
- [ ] Save timestamped JSON snapshots
- [ ] Save markdown or CSV application tracker
- [ ] Detect new jobs since last run
- [ ] Detect duplicates across sources

## Verification

- [x] `python -m py_compile job_search_workflow.py`
- [x] `npm run lint`
- [x] `npm run build`

## Notes

LinkedIn results should be treated as remote-filtered, not guaranteed remote. Direct ATS/company career pages should receive the highest trust score when a posting date and location are available.
