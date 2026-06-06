# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Extracting and structuring University of Cambridge undergraduate admissions statistics for the 2026 application cycle. The data comes from the admissions statistics dashboard (Microsoft Power BI) at `https://www.undergraduate.study.cam.ac.uk/apply/before/application-statistics`.

## Current State

The project is in the **data collection phase**. All raw source material lives in `raw/` — screenshots (PNG) and PDFs captured from the Power BI dashboard. No extraction/conversion code exists yet. The commit message states intent to convert into `.json` or `.py`.

## Raw Data Inventory (`raw/`)

- `Cambridge Application Data.pdf` and `ug_admissions_statistics_2025_cycle.pdf` — full PDF exports from the dashboard
- `2026 Overall.png` — high-level summary for 2026 cycle
- `2025 Engineering Application breakdown.png`, `2026 Engineering Application breakdown.png` — application breakdowns by year
- `2025 Engineering Application Break Form.png`, `2026 Engineering Application breakdown form.png` — form-style breakdown views
- `2025 Engineering Offer Breakdown Form.png`, `2026 Engineering Offer Breakdown Form.png` — offer breakdown form views
- `2025 Engineering Offers.png`, `2026 Engineering offers.png` — offer data visualizations
- `2025 Acceptance breakdown.png` — acceptance data
- `2024 Form.png` — 2024 cycle form data
- `IBPG.png` — IB/Pre-U/GCSE breakdown
- `Mainland Engineering Applicants, sorted by college.png` — China mainland applicants by college
- `Winter Pool Data for international Engineering applicants from international schools.png` — winter pool data (international schools)
- `Winter Pool Data for international Engineering applicants, any school type.png` — winter pool data (all school types)

## Reference Implementation

The sibling project `cambridge-statistics-main/cambridge-statistics-main/statistics.py` shows how the older (pre-Power BI) statistics page worked:

1. `POST` to `https://www.undergraduate.study.cam.ac.uk/apply/statistics` with form data specifying year, subject, course, and grouping (college)
2. Extract chart data from `data-chart` attribute in the HTML response via regex
3. Unescape HTML entities, parse as JSON
4. Iterate over `xAxis[0].categories` (colleges) and `series` (data categories) to produce tab-separated output for spreadsheet paste

The data categories in the old system were: Direct applications, Open applications, Direct offers, Winter pool offers, Pool offers by other Colleges, Acceptances by offering College.

## Important Context

- The 2026 dashboard is Power BI-based, so the old `statistics.py` approach (POST to HTML form, regex extract) **will not work directly**. The current data sources are screenshots/PDFs — OCR or manual extraction will be needed, or the Power BI API must be reverse-engineered.
- The repo owner is `FlyDeutsch09` on GitHub; the remote is `https://github.com/FlyDeutsch09/cam-stats-2026.git`.
- The `2026 Cambridge Application Data Support/` directory at `E:/Projects/` (outside the repo) contains extracted/annotated PNGs used for analysis — these are working files, not committed to git.
- `raw/` files are committed with Git LFS tracking (repository has `lfs.repositoryformatversion=0`), but any new large binary additions should verify LFS is properly configured.

## Data Structure

This is a GitHub Project to be released. It is true that the raw data is from a Microsoft BI Form, but I have captured all important Statistical figures in pictures. These might include Engineering offers for 2025 and 2026, divided by colleges or schools. You may refer a collection of all the data in that Cambridge Application Data.pdf file.

## Initiations and Aims

I am a DP1 student aged 16 from China Mainland and I am going to study Engineering. I am now choosing colleges for Cambridge to apply. There are colleges to avoid, including Peterhouse, Trinity, Churchill that are much too demanding; Female colleges including Newnham College and Murray Edwards College; Mature colleges including Hughes Hall, St Edmund's and Wolfson. I also hate Lucy Cavendish, Downing and Magdalene College. I want to pick those which are Chinese-friendly, not too small, not suddenly emerge to show a significant increase in admissions, and not pick too many students from the Winter Pool. You may also go to University of Cambridge Official website including college information and Engineering Department information to better support your choice. (Yes you need to Websearch) To conclude, I want a final analysis of data and a recommendation of top 3 colleges that I could choose.

## Workflow
You may flexibly design your workflow, and I will recommend one for you. 
-1.raw. GO to raw file, find that PDF collection and other images, these are your own data support
-2.src. You need to collect information from the raw section, integrate them and arrange these data into .json or .xlsx or whatever form you like. Also include a description of my preferences and what you have found on the official website as a .md file in this folder. The cam-statistics-main might provide you with an example to collect and integrate data in a clean way.
-3.tools. The 3 .py programmes provide a way that my friend have given me to analyse .xlsx data, but I have not checked them yet, You may examine them and freely decide whether to use. In a word, this section includes the methodology you use to analyse data. You may also create a file describing the mark bands or the evaluation creteria, this is an evaluation system to decide which college to choose, convert data from all sections into a mark out of 100 and give each college a mark. Criterias might include but not only Winter pool students, Stability, Offer rate, Acceptance Rate, PG Requirements. Some of them are positive aspect and some are negative (like a high PG requirement means a low weight). You may construct a marking band to evaluate the colleges.
-4.output. Start to give the colleges marks based on the mark band I have given you, give the marks for each college, demonstrate in any file type. Then, Provide a conclusion with what you have found and a final recommendation letter to the user (me) in .md form.
-5.pull. Revise the README.md file in cam-stats-2026 to help explain what this project has done. You may include your thoughts or thinking process in it, be detailed.