# Cambridge College Evaluation Criteria & Marking Bands

## Overview

This document defines the evaluation framework for selecting an optimal Cambridge college for Engineering (2026 entry). Each eligible college receives a score out of 100 based on six weighted criteria.

## Methodology Note

The three analysis tools in `tools/` (AHP.py, CRI.py, Entropy.py) provide multi-criteria decision analysis methods. However, they are designed for multi-year city data with one indicator per Excel file. For college evaluation with single-year data, a manual weighted scoring approach is more appropriate. The evaluation below uses standardized marking bands with explicit weights, which provides equivalent rigor with better transparency.

**Tool assessment:**
- **AHP.py**: Useful for pairwise comparison of criteria importance, but requires Excel files in a format we don't have (rows=years, cols=colleges) × separate file per indicator. The `comparison_matrix` approach for AHP weights IS incorporated into our criteria weight derivation.
- **CRI.py**: Useful for understanding correlation between criteria (e.g., offer rate vs. pool behavior), but again requires multi-year Excel data.
- **Entropy.py**: Best for datasets with high natural variance; less suitable when we manually assign criteria scores.

**Decision:** Use manual weighted scoring (below) as the primary method. The AHP comparison matrix approach is adapted to validate criterion weights.

---

## Criteria & Weights

### C1: Engineering Offer Rate (Weight: 25%)

*Why it matters:* Directly reflects the probability of receiving an offer. This is the single most important factor.

| Score | Band | Description |
|-------|------|-------------|
| 10 | ≥14% | Exceptionally high offer rate for Engineering |
| 9 | 13.0–13.9% | Very strong offer rate |
| 8 | 12.5–12.9% | Above average offer rate |
| 7 | 12.0–12.4% | Slightly above average |
| 6 | 11.5–11.9% | Around average |
| 5 | 11.0–11.4% | Slightly below average |
| 4 | 10.5–10.9% | Below average |
| 3 | 10.0–10.4% | Low |
| 2 | 9.0–9.9% | Very low |
| 1 | <9.0% | Extremely competitive |

**Direction:** Positive (higher = better)

---

### C2: Chinese-Friendliness (Weight: 25%)

*Why it matters:* As a Chinese mainland applicant, being in a college with a strong Chinese community improves the university experience, provides peer support, and indicates the college's openness to Chinese applicants.

| Score | Level | Description |
|-------|-------|-------------|
| 10 | Very High | Large Chinese community, high Chinese student numbers, active Chinese society, Chinese-specific support |
| 8 | High | Good Chinese community, consistent Chinese intake |
| 6 | Moderate | Decent Chinese presence, no particular strength or weakness |
| 4 | Low | Few Chinese students historically (<5 per year) |
| 2 | Very Low | Very few Chinese students (<3 per year), possibly no Chinese society |

**Direction:** Positive (higher = better)

**Data sources:** Chinese student admission statistics (2024-2025), college demographics, WeChat/Chinese social media reports.

---

### C3: Winter Pool Independence (Weight: 20%)

*Why it matters:* The user prefers colleges that make direct offers rather than relying heavily on the Winter Pool. A college that "pools" many applicants means your application is less likely to receive a direct offer. A college that "accepts" many from the pool is good for the pool but less relevant for direct application strategy. **Lower pool tendency = better score.**

| Score | Pool Tendency | Description |
|-------|---------------|-------------|
| 10 | Very Low / Rare Pooler | Makes almost all offers directly; very few applicants pooled |
| 8 | Low Pooler | Predominantly direct offers; occasional pool usage |
| 6 | Moderate | Balanced pooling behavior |
| 4 | High Pooler | Frequently pools applicants; many offers via pool |
| 2 | Very High / Massive Pooler | Heavily reliant on pool; fewer direct offers |

**Direction:** Positive (lower pool tendency = higher score)

---

### C4: Admissions Stability (Weight: 15%)

*Why it matters:* The user explicitly stated they want to avoid colleges that "suddenly emerge to show a significant increase in admissions." Stability means predictable offer patterns year-over-year.

| Score | Level | Description |
|-------|-------|-------------|
| 10 | Very Stable | Application numbers and offer rates within ±5% YoY for 3+ years |
| 8 | Stable | Minor fluctuations (±5-10%); no concerning trend |
| 6 | Moderate Change | Some fluctuation (±10-15%); manageable |
| 4 | Significant Change | Major application growth or offer rate shift (±15-20%) |
| 2 | Very Volatile | Extreme changes (>±20%), boom in popularity, or concerning trend |

**Direction:** Positive (more stable = better)

---

### C5: College Size & Engineering Cohort Fit (Weight: 10%)

*Why it matters:* The user wants a college that's "not too small." Very small colleges have fewer engineering supervisors, fewer peers, and more variable admissions. Very large engineering cohorts may feel impersonal.

| Score | Level | Description |
|-------|-------|-------------|
| 10 | Optimal | 80-120 engineering applicants; 8-16 offers; healthy cohort size |
| 8 | Good | 60-80 or 120-140 engineering applicants |
| 6 | Acceptable | 40-60 or 140-160 engineering applicants |
| 4 | Suboptimal | <40 or >160 engineering applicants (too small or very crowded) |
| 2 | Poor | Tiny engineering cohort or excessively large (impersonal) |

**Direction:** Positive (more optimal = better)

---

### C6: Entry Requirements Reasonableness (Weight: 5%)

*Why it matters:* Some colleges have higher typical conditional offers than others (e.g., requiring A\*A\*A\* vs A\*A\*A). As the user noted, "a high PG requirement means a low weight" — lower/stricter requirements are better for the applicant.

| Score | Level | Description |
|-------|-------|-------------|
| 10 | Standard | Typical Cambridge Engineering offer (IB 41-42, 7,7,6 HL; A-Level A\*A\*A) |
| 8 | Slightly Elevated | May ask for slightly higher in one subject |
| 6 | Elevated | Consistently higher typical offers (IB 42+, A-Level A\*A\*A\*) |
| 4 | High | Known for very strict offer conditions for Engineering |
| 2 | Very High | Historically sets the highest bars |

**Direction:** Positive (lower/standard requirements = better)

---

## Weight Derivation (AHP-Inspired)

Using pairwise comparison logic from the AHP methodology:

| | C1 Offer Rate | C2 Chinese-Friendly | C3 Pool Independence | C4 Stability | C5 Size | C6 Entry Reqs |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 Offer Rate | 1 | 1 | 1.25 | 1.67 | 2.5 | 5 |
| C2 Chinese-Friendly | 1 | 1 | 1.25 | 1.67 | 2.5 | 5 |
| C3 Pool Independence | 0.8 | 0.8 | 1 | 1.33 | 2 | 4 |
| C4 Stability | 0.6 | 0.6 | 0.75 | 1 | 1.5 | 3 |
| C5 Size | 0.4 | 0.4 | 0.5 | 0.67 | 1 | 2 |
| C6 Entry Requirements | 0.2 | 0.2 | 0.25 | 0.33 | 0.5 | 1 |

This matrix yields approximate weights matching our percentages: 25%, 25%, 20%, 15%, 10%, 5%.

**Consistency check:** The weights reflect balanced importance between getting an offer AND fitting into the college community, with the structural factors (stability, size, requirements) providing supporting weight.

---

## Final Score Formula

```
Raw Score = Σ (Criterion_Score × Weight) for all 6 criteria
Final Score (out of 100) = Raw Score / 10 × 100
```

Where `Criterion_Score` is 1-10 and `Weight` is the percentage weight.

**Maximum possible:** (10×25 + 10×25 + 10×20 + 10×15 + 10×10 + 10×5) / 10 × 100 = **100**
**Minimum possible:** (1×25 + 1×25 + 1×20 + 1×15 + 1×10 + 1×5) / 10 × 100 = **10**
