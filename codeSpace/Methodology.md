# Phase 1: Automated RAG Methodology

## Core Philosophy: Decoupling Math from Subjectivity
In traditional enterprise project tracking, RAG (Red, Amber, Green) statuses are highly subjective. Project managers may flag a project as "Green" to avoid steering committee scrutiny, even when the project is mathematically bleeding budget or slipping past its baseline end date.

To eliminate this bias, our AI Agent decouples **Deterministic Quantitative Metrics** from **Qualitative LLM Synthesis**, combining them into a unified, mathematically rigorous health score.

---

## 1. Quantitative Baseline Formulation (70% Weight)

The system automatically scrubs and normalizes raw CSV exports using Pandas. It extracts two critical numeric signals before an LLM is even invoked:

### A. Schedule Slippage (45% Weight)
* **Definition:** The deviation between the original Baseline Finish date and the current projected End Date.
* **Calculation:** If the `Variance` column is missing or `#UNPARSEABLE`, the system dynamically calculates: `Variance = End Date - Baseline Finish`. 
* **Scoring Thresholds:** 
  - < 0 days (Ahead) = Green
  - 0 to 14 days (Minor Drift) = Amber
  - > 14 days (Critical Delay) = Red

### B. Time-to-Complete Burn Ratio (25% Weight)
* **Definition:** A proxy for budget burn. It measures the percentage of physical progress against the percentage of time elapsed.
* **Calculation:** `(% Complete) / (Elapsed Time / Total Duration)`.
* **Scoring Thresholds:**
  - Ratio >= 1.0 (Burning efficiently) = Green
  - Ratio 0.85 - 0.99 (Slightly behind schedule for time spent) = Amber
  - Ratio < 0.85 (Burning time significantly faster than progress) = Red

---

## 2. Qualitative LLM Synthesis (30% Weight)

Once the mathematical baseline is established, the data is routed to an OpenRouter LLM (Llama 3 8B Instruct). The AI is prompted to strictly analyze the Project Manager's text comments and extract systemic blockers.

* **Blocker Extraction:** The LLM evaluates text for keywords indicating supply chain issues, resource constraints, or technical blockers.
* **Scoring Thresholds:**
  - No critical blockers mentioned = Green
  - Blockers mentioned but mitigated/actioned = Amber
  - Unmitigated systemic blockers = Red

---

## 3. Final RAG Determination

The final RAG status is determined by aggregating the three signals. To ensure safety, the system operates on a **"Highest Risk Triumphs"** principle:
- If *either* the Schedule Slippage OR the LLM Blocker extraction flags a "Red", the entire project is instantly flagged as **Red**.
- If the metrics are mixed between Green and Amber, the project is flagged as **Amber**.
- A **Green** status requires unanimous positive signals across all three vectors.

### Data Assumptions & Graceful Degradation
* **Missing Data:** Empty cells, spaces, or `#UNPARSEABLE` strings are explicitly scrubbed and cast to `np.nan` (or "Unknown").
* **API Failures:** If the LLM gateway times out or rate-limits, the system falls back entirely to the deterministic quantitative score, ensuring the pipeline never halts and the RAG status is still delivered.
