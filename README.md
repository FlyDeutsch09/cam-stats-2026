# Cambridge Application Statistics 2026

University of Cambridge Undergraduate Application Statistics — Engineering College Selection Analysis (June 2026)

## Overview

This project analyzes Cambridge University admissions data to help a DP1 (IB Year 1) student from China Mainland select the optimal college for Engineering (2026 entry). The analysis evaluates all 29 undergraduate colleges against six weighted criteria, incorporating both quantitative admissions statistics and qualitative factors such as Chinese student community strength and Winter Pool behavior.

## Project Structure

```
cam-stats-2026/
├── raw/                          # Original data sources (screenshots & PDFs from Power BI dashboard)
│   ├── Cambridge Application Data.pdf         # Full dashboard PDF export
│   ├── ug_admissions_statistics_2025_cycle.pdf # Official Cambridge 2025 cycle statistics
│   ├── 2025 Engineering Application breakdown.png
│   ├── 2026 Engineering Application breakdown.png
│   ├── 2025 Engineering Offers.png
│   ├── 2026 Engineering offers.png
│   ├── 2025 Engineering Offer Breakdown Form.png
│   ├── 2026 Engineering Offer Breakdown Form.png
│   ├── 2025 Acceptance breakdown.png
│   ├── 2026 Overall.png
│   ├── 2024 Form.png
│   ├── IBPG.png                  # IB/Pre-U/GCSE grade breakdown
│   ├── Mainland Engineering Applicants, sorted by college.png
│   ├── Winter Pool Data for international Engineering applicants from international schools.png
│   ├── Winter Pool Data for international Engineering applicants, any school type.png
│   └── 2025 Engineering Application Break Form.png
├── src/                          # Structured data & research
│   ├── college_data.json         # Compiled college admissions data with confidence ratings
│   └── research_notes.md         # College profiles, Engineering Department info, selection context
├── tools/                        # Analysis methodology
│   ├── AHP.py                    # Analytic Hierarchy Process (friend's code — adapted for reference)
│   ├── CRI.py                    # CRITIC Method for criteria weighting (friend's code — reference)
│   ├── Entropy.py                # Entropy Weight Method + AHP comparison (friend's code — reference)
│   └── evaluation_criteria.md    # Custom 6-criteria scoring system with marking bands
└── output/                       # Results & recommendations
    ├── college_scoring.json      # Complete scoring of all 18 eligible colleges
    └── recommendation_letter.md  # Final recommendation with Top 3 colleges and detailed reasoning
```

## Data Sources

- **Primary:** Cambridge University Undergraduate Admissions Statistics (Power BI dashboard at `undergraduate.study.cam.ac.uk/apply/before/application-statistics`)
- **Supplementary:** FOI responses (FOI 2025/510, FOI 2025/675), published college admissions data, Chinese education platform analyses
- **Context:** Cambridge Engineering Department website, college official websites, The Student Room applicant forums

## Key Findings

### Engineering Admissions (2025-2026)

| Metric | 2025 Cycle | 2026 Cycle (Preliminary) |
|--------|-----------|--------------------------|
| Total Applications (all subjects) | 22,817 | ~25,000 |
| Engineering Applications | 3,263 | 3,972 |
| Engineering Offers | 393 | 414 |
| Engineering Offer Rate | 12.0% | ~10.4% |
| China Mainland Engineering Apps | 599 | — |
| China Mainland Engineering Offers | ~66 | — |
| China Mainland Engineering Rate | ~11% | — |

### College Exclusions Applied

11 colleges excluded: Trinity, Churchill, Peterhouse (too demanding); Newnham, Murray Edwards (female-only); Hughes Hall, St Edmund's, Wolfson (mature, 21+); Downing, Magdalene, Lucy Cavendish (user preference).

### Top Recommendation: Robinson College (86.5/100)

Robinson offers the best combination of Chinese-friendliness (highest Chinese student proportion at Cambridge), above-average Engineering offer rate (~13.3%), stable admissions patterns, and a well-sized Engineering cohort. Homerton College (84.5/100) is a close second with the largest Chinese applicant community.

**Full results and detailed reasoning:** See `output/recommendation_letter.md`

## Methodology

The evaluation uses a weighted 6-criteria scoring system (100-point scale):

| Criterion | Weight | Direction |
|-----------|--------|-----------|
| Engineering Offer Rate | 25% | Higher = better |
| Chinese-Friendliness | 25% | Higher = better |
| Winter Pool Independence | 20% | Less pool dependency = better |
| Admissions Stability | 15% | More stable = better |
| Engineering Cohort Size | 10% | Optimal range (80-120) = best |
| Entry Requirements Reasonableness | 5% | Standard = better |

Weights were validated using AHP pairwise comparison logic. Three decision-analysis tools (AHP, CRITIC, Entropy Weight Method) are provided in `tools/` for sensitivity analysis.

## Thinking Process

1. **Data Collection:** Raw screenshots and PDFs captured from the Cambridge Power BI statistics dashboard — the 2026 dashboard moved from the old HTML form endpoint to Microsoft Power BI, making the legacy `statistics.py` scraping approach (from the sibling `cambridge-statistics-main` project) obsolete.

2. **College Filtering:** Applied the user's explicit exclusion criteria plus research-validated additions. The remaining 18 colleges were scored.

3. **Criterion Selection:** The six criteria were chosen based on the user's stated preferences (Chinese-friendliness, stability, pool behavior, reasonable requirements) and general admissions strategy (offer rate, cohort size).

4. **Weighting:** Offer Rate and Chinese-Friendliness share the highest weight (25% each) because they represent the two most important questions: "Will I get in?" and "Will I be happy there?" Pool Independence (20%) reflects the user's specific concern about the Winter Pool system.

5. **Fitzwilliam Dilemma:** Fitzwilliam is often the top recommendation for Chinese Engineering applicants, but its +20.31% application spike in 2025 triggered the user's stability criterion. This is a judgment call — Fitzwilliam could be right if the growth stabilizes.

6. **Gap Between #2 and #3:** The scoring reveals a clear 9-point gap between Homerton (84.5) and Clare (75.5). Robinson and Homerton are genuinely in a tier of their own for this specific applicant profile.

## License & Attribution

Data collected from publicly available University of Cambridge admissions statistics. Analysis and recommendations are for personal educational planning use.
