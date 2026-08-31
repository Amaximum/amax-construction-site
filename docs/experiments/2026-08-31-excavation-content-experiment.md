# Excavation Content Experiment

- Service cluster: Excavation Services
- Release branch: `experiment/excavation-content-20260831`
- Baseline date: 2026-08-31
- Baseline GSC window: 2025-05-01 through 2026-08-28
- Sources: Google Search Console, Google Ads (30-day), DataForSEO organic SERPs/backlinks, source content audit.

## Baseline

| Metric | Value |
| --- | ---: |
| Clicks | 0 |
| Impressions | 1,830 |
| CTR | 0% |
| Average position | 65.76 |
| Ranking queries | 70 |

The primary hub accounts for 1,776 impressions and 68 ranking queries. Vaughan accounts for 54 impressions and two ranking queries. Markham, Newmarket, Richmond Hill, and Toronto had no query-level rows in the selected GSC query-page extraction.

Protected themes: excavation Toronto, excavation services Toronto, excavation companies Toronto, professional excavation services, commercial excavation Toronto, foundation excavation, grading, trenching, site preparation, mini excavation, and Vaughan excavation contractor/problem queries.

## Evidence and Risk

- GSC: low visibility/positions and zero clicks. There is no demonstrated click-producing wording to remove.
- Google Ads: seven landing-page impression rows for the hub in the latest 30 days, with zero clicks/conversions; no matching excavation search-term rows.
- GA4: DATA_UNAVAILABLE. The BigQuery link exists, but the export dataset is not provisioned.
- SERP: competitors consistently frame commercial intent around excavation contractor/services, foundation excavation, site preparation, grading, trenching, and residential/commercial project context.
- Backlinks: amaximumconstruction.com has 101 referring domains. Competitors observed in the SERPs range from 41 to 80 referring domains; directories also rank. No off-page submission is authorized or performed in this experiment.

## Page Map

| URL | Role | Primary intent | Distinct focus |
| --- | --- | --- | --- |
| /excavation-services/ | GTA-wide service hub | Commercial excavation services | Foundation excavation, site preparation, grading, trenching, drainage coordination, and project decision process |
| /excavation-services-in-toronto/ | Toronto local page | Toronto excavation contractor/services | Constrained-access planning, foundation work, trenching and grade planning |
| /excavation-services-in-markham/ | Markham local page | Markham excavation services | Residential site preparation, drainage and grading decisions |
| /excavation-services-in-newmarket/ | Newmarket local page | Newmarket excavation services | Foundation, utility trenching and drainage planning |
| /excavation-services-in-richmond-hill/ | Richmond Hill local page | Richmond Hill excavation services | Grade changes, foundation excavation and drainage planning |
| /excavation-services-in-vaughan/ | Vaughan local page | Vaughan excavation contractor/problem | Contractor-led excavation scope, grading, trenching and project coordination |

## Cannibalization

GSC shows expected topical overlap between the hub and General Contractor pages. The hub owns excavation-services/commercial-service terms; location pages own service-plus-location intent. There is no confirmed cannibalization: no cluster page has clicks, and the query/page data does not show the same valuable query producing competing performance among the selected pages.

## Content Plan

Keep the existing H1/title/meta/canonical/schema/FAQ implementation, page sections, photos, cards, header, footer, CSS, JS, and booking links. Replace only existing introductory/section copy to make each page's role explicit and reduce repeated generic filler. Add no new URLs. Existing blog pages are classified as weakly related or unrelated for this cluster and remain unchanged.

## Follow-up Checkpoints

Compare GSC at 14, 28, and 56 days after release against this baseline: clicks, impressions, CTR, average position, ranking-query count, query distribution, and location-page visibility. Account for normal GSC delay and seasonality.
