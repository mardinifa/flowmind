# Deliverable D6: Streamlit Human-in-the-Loop Dashboard

**Client:** ClearPath Capital (Lagos, Nigeria)  
**App Entrypoint:** `dashboard/app.py`  
**Command:** `streamlit run dashboard/app.py`

---

## 1. Dashboard Capabilities

The FlowMind dashboard provides loan officers and credit risk administrators with a real-time, zero-friction operations command center.

```
+--------------------------------------------------------------------------------+
|  ⚡ FLOWMIND AI — CLEARPATH CAPITAL                                             |
+--------------------------------------------------------------------------------+
|  [Navigation: 📋 Loan Officer Queue | 📊 Admin & Metrics | 🧪 Guardrails Lab]  |
|                                                                                |
|  QUEUE SUMMARY:                                                                |
|  [ Pending In Queue: 3 ]   [ Total Volume: ₦10,500,000 ]   [ SLA: < 4 Hours ]  |
|                                                                                |
|  ▼ Yusuf Textiles & Tailoring — ₦3,500,000.00  (Applicant: Amina Yusuf)        |
|    +------------------------------------------------------------------------+  |
|    |  FLOWMIND ESCALATION BRIEFING                                          |  |
|    |  - Eligibility: 3/4 Passed, Turnover Ratio (9.2x) near 10x cap.       |  |
|    |  - Risk Level: Medium (Confidence: 0.72)                               |  |
|    |  - Core Ambiguity: Off-peak revenue seasonal volatility.               |  |
|    |  - Recommended Action: Officer review or reduce principal to ₦2.5M.    |  |
|    +------------------------------------------------------------------------+  |
|    [ Review Notes & Justification: _____________________________________ ]  |
|    [ ✅ Approve ]          [ ❌ Decline ]          [ ❓ Request More Info ]   |
|                                                                                |
+--------------------------------------------------------------------------------+
```

---

## 2. Views & Key Performance Indicators (KPIs)

### 1. Loan Officer Review Queue
- **Live Queue:** Fetches all records where `status == 'escalated'`.
- **Structured Briefing Presentation:** Loads the pre-compiled AI briefing (`load_briefing(app_id)`).
- **Three Core Decisions:**
  - `✅ Approve` -> Sets status to `human_approved`, saves officer audit ID.
  - `❌ Decline` -> Sets status to `human_declined`.
  - `❓ Request More Info` -> Sets status to `human_info_requested`.
- **Compliance Audit Logging:** Automatically logs timestamps, notes, and records whether the human decision represented an **override** of the AI recommendation.

### 2. Admin Operational Intelligence
- **% Handled Autonomously:** Target 65%-75%.
- **% Escalated:** Target 25%-35%.
- **Human Override Rate:** `% of auto / AI-guided decisions corrected by human loan officers`.
  - *Healthy Threshold:* `< 10%`.
  - *Diagnostic Alert:* Triggered if override rate exceeds 10%, indicating model drift or conservative miscalibration.
- **Threshold Calibration Engine:** Live telemetry running `analyze_calibration()` to evaluate queue bottlenecks and recommend adjustments.

### 3. Guardrails & Simulation Lab
- **D4 Anti-Hallucination Testing Sandbox:** Test accurate vs fake claim letters with real-time feedback.
- **Intake Edge Case Sandbox:** Test scanned and truncated PDFs.
- **Fraud Anomaly Sandbox:** Test name mismatches between forms and bank statements.
