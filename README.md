# Commerce Data Engineering Portfolio

This project is a **90-day challenge** to design and build a public data engineering portfolio focused on **real-time, commerce-scale systems**.  
The goal: to practice building pipelines that can handle **scale, reliability, and adaptability**, while documenting the process step by step.

---

## Project Scope

- **Data Ingestion (Bronze)**  
  Capture raw clickstream events (user_id, session_id, page_url, timestamp, referrer, ip).  
  Store events as-is, with no filtering or transformation.  

- **Data Refinement (Silver)**  
  Clean and enrich Bronze data into a stable, typed schema.  
  Add derived fields like:
  - Deterministic `event_id` (for idempotency)  
  - `event_date` (for partitioning)  
  - `page_type` (home, product, cart, checkout, etc.)  
  - `ref_domain` (normalized from referrer)  

- **Data Serving (Gold)**  
  Aggregate Silver into business-ready tables and metrics:  
  - Funnel analysis (home → product → cart → checkout)  
  - Session metrics  
  - Daily rollups  

- **Pipelines**  
  Implemented with **Apache Beam**, with orchestration and monitoring to follow.  
  Output formats will include **JSONL** for dev and **Parquet** for analytics.  

---

## Medallion Architecture Overview

This project follows the **Medallion Architecture** pattern, which organizes data into three layers:

- 🥉 **Bronze (Raw Layer)**  
  Store data exactly as it arrives. *Permissive* by design — if upstream adds a new field tomorrow (`device_type`, `browser_version`), you still ingest it. Nothing is lost.

- 🥈 **Silver (Refined Layer)**  
  Enforce schema and apply transformations.  
  *Strict* contract: only the fields you explicitly support, with consistent types, enrichment, and validation.  
  Consumers can trust Silver data for analytics.

- 🥇 **Gold (Serving Layer)**  
  Curated, business-ready datasets. Aggregated, denormalized, optimized for end-user queries and dashboards.  
  These are the tables/data products stakeholders actually use.

---

## Current Status

- ✅ Folder structure set up with `.gitkeep` placeholders  
- ✅ `.gitignore` added to control noise  
- ✅ Bronze and Silver schemas documented in `models/`  
- ✅ First Beam pipeline scaffolded: Bronze CSV → parsed dicts → Silver JSONL  
- ⏳ Next steps: enrichments, schema validation, Parquet output, orchestration

---

## Next Steps

- Harden CSV parsing (use Python’s `csv` module instead of naive split)  
- Implement enrichments: `event_id`, `event_date`, `page_type`, `ref_domain`  
- Validate Silver outputs against the JSON Schema  
- Write Silver data in Parquet, partitioned by `event_date`  
- Begin Gold-layer aggregations
