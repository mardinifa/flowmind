"""
FlowMind Streamlit Dashboard
ClearPath Capital - Lagos, Nigeria
Human-in-the-Loop Review Queue & Operational Intelligence
"""

import streamlit as st
import pandas as pd
import json
import os
import io

# Setup Page Configuration
st.set_page_config(
    page_title="FlowMind | ClearPath Capital",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import backend modules
from db.database import (
    supabase,
    load_briefing,
    save_human_decision,
    update_status,
    get_dashboard_metrics,
)
from db.seed_data import seed_sample_data
from src.actions.letter_validator import validate_letter
from src.actions.letter_generator import (
    generate_conditional_approval_letter,
    generate_decline_letter,
)
from src.intake.pdf_extractor import extract_text_from_pdf
from src.pipeline import process_application
from config.thresholds import get_current_thresholds, analyze_calibration

# Load Custom CSS
css_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/isometric/100/money-box.png", width=60)
st.sidebar.title("FlowMind AI")
st.sidebar.caption("Intelligent Credit Automation & Guardrails")

app_mode = st.sidebar.radio(
    "Navigation",
    ["📋 Loan Officer Queue", "📊 Admin & Metrics", "🧪 Guardrails & Simulation Lab"],
    index=0,
)

current_officer = st.sidebar.selectbox(
    "Active Officer Profile",
    ["officer_1 (Senior Underwriter)", "officer_2 (Credit Analyst)", "compliance_lead"],
    index=0,
)
officer_id = current_officer.split()[0]

st.sidebar.divider()
if st.sidebar.button("🔄 Reset / Reseed Demo Data"):
    seed_sample_data(reset=True)
    st.sidebar.success("Database re-seeded with ClearPath Capital sample applications!")
    st.rerun()


# =========================================================================
# PAGE 1: LOAN OFFICER VIEW (REVIEW QUEUE)
# =========================================================================
if app_mode == "📋 Loan Officer Queue":
    st.markdown(
        """
        <div class="main-header">
            <h1>FlowMind — Loan Officer Review Queue</h1>
            <p>ClearPath Capital · Ambiguous, high-risk, and flagged applications requiring human judgement.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch escalated applications
    rows = supabase.table("applications").select("*").eq("status", "escalated").execute()
    escalated_items = rows.data or []

    # Top summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Pending In Queue", len(escalated_items), delta=f"{len(escalated_items)} to review", delta_color="inverse")
    total_requested = sum(float(r.get("loan_amount", 0)) for r in escalated_items)
    col2.metric("Queue Volume", f"₦{total_requested:,.2f}")
    col3.metric("Review SLA", "< 4 Hours", "On Track")

    st.write("")

    if not escalated_items:
        st.success("🎉 All caught up! No pending applications in the escalation queue.")
    else:
        st.subheader(f"Applications Awaiting Decision ({len(escalated_items)})")
        
        for r in escalated_items:
            app_id = r.get("id")
            biz_name = r.get("business_name")
            amt = float(r.get("loan_amount", 0))
            turnover = float(r.get("monthly_turnover", 0))
            applicant = r.get("applicant_name")

            expander_title = f"{biz_name} — ₦{amt:,.2f}  (Applicant: {applicant})"
            
            with st.expander(expander_title, expanded=False):
                # Application Quick Facts Grid
                fcol1, fcol2, fcol3, fcol4 = st.columns(4)
                fcol1.markdown(f"**Operating Tenure:** {r.get('operating_months')} months")
                fcol2.markdown(f"**Monthly Turnover:** ₦{turnover:,.2f}")
                fcol3.markdown(f"**Applicant Age:** {r.get('applicant_age')} yrs")
                fcol4.markdown(f"**Purpose Category:** {r.get('purpose_category', '').replace('_', ' ').title()}")

                st.markdown("---")
                
                # Render AI Generated Briefing Text
                briefing_content = load_briefing(app_id)
                st.markdown(briefing_content)

                # If a letter was generated with a hallucination flag, show warning
                if r.get("letter_validation_status") == "flagged_hallucination":
                    st.warning("⚠️ **ANTI-HALLUCINATION GUARDRAIL WARNING:** The AI generated a letter for this application that contained unverified or contradictory factual claims. Review before approving.")

                st.markdown("---")
                st.markdown("#### 📝 Record Officer Decision")

                officer_notes = st.text_area(
                    "Review Notes & Decision Justification (Recorded for Compliance Audit):",
                    key=f"notes_{app_id}",
                    placeholder="Enter context, phone verification notes, or reason for override...",
                )

                bcol1, bcol2, bcol3 = st.columns(3)
                
                # 1. Approve Button
                if bcol1.button("✅ Approve Application", key=f"a{app_id}", use_container_width=True, type="primary"):
                    save_human_decision(app_id, "human_approved", officer_id, officer_notes)
                    update_status(app_id, "human_approved")
                    st.success(f"Application {app_id} approved by {officer_id}!")
                    st.rerun()

                # 2. Decline Button
                if bcol2.button("❌ Decline Application", key=f"d{app_id}", use_container_width=True):
                    save_human_decision(app_id, "human_declined", officer_id, officer_notes)
                    update_status(app_id, "human_declined")
                    st.warning(f"Application {app_id} declined by {officer_id}.")
                    st.rerun()

                # 3. Request More Info Button
                if bcol3.button("❓ Request More Info", key=f"i{app_id}", use_container_width=True):
                    save_human_decision(app_id, "human_info_requested", officer_id, officer_notes)
                    update_status(app_id, "human_info_requested")
                    st.info(f"Information request dispatched for {app_id}.")
                    st.rerun()

    # Completed Human Reviews section
    st.write("")
    st.divider()
    with st.expander("🕒 View Recently Decided Applications"):
        decided_res = supabase.table("applications").select("*").neq("status", "escalated").neq("status", "submitted").order("updated_at", desc=True).execute()
        if decided_res.data:
            df_decided = pd.DataFrame(decided_res.data)[
                ["id", "business_name", "loan_amount", "status", "officer_id", "is_override", "updated_at"]
            ]
            st.dataframe(df_decided, use_container_width=True)


# =========================================================================
# PAGE 2: ADMIN VIEW (METRICS & CALIBRATION)
# =========================================================================
elif app_mode == "📊 Admin & Metrics":
    st.markdown(
        """
        <div class="main-header">
            <h1>FlowMind — Operational Intelligence & Calibration</h1>
            <p>ClearPath Capital · Autonomous throughput, escalation ratios, and human override telemetry.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = get_dashboard_metrics()

    # Metric Cards Row
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("Total Applications", metrics["total_applications"])
    mcol2.metric("% Handled Autonomously", f"{metrics['autonomous_pct']}%", f"{metrics['autonomous_count']} decisions")
    mcol3.metric("% Escalated to Human", f"{metrics['escalated_pct']}%", f"{metrics['escalated_total']} escalated")
    
    override_delta = f"{metrics['override_count']} overrides"
    override_color = "inverse" if metrics["human_override_pct"] > 10.0 else "normal"
    mcol4.metric("Human Override Rate", f"{metrics['human_override_pct']}%", override_delta, delta_color=override_color)

    st.markdown("---")

    # Visual Breakdown Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Pipeline Performance", "⚙️ Threshold Calibration", "📑 Audit Trail"])

    with tab1:
        st.subheader("Decision Breakdown Across Pipeline")
        pcol1, pcol2 = st.columns(2)
        
        status_counts = {
            "Auto Approved": metrics["auto_approved"],
            "Auto Declined": metrics["auto_declined"],
            "Escalated (Pending)": metrics["escalated_pending"],
            "Human Decided": metrics["human_reviewed"],
        }
        df_status = pd.DataFrame(list(status_counts.items()), columns=["Decision Outcome", "Count"])
        pcol1.bar_chart(df_status.set_index("Decision Outcome"))

        with pcol2:
            st.markdown("#### System Health & Automation Target")
            st.info(
                f"**Target Escalation Rate:** 25% – 35%\n\n"
                f"**Current Escalation Rate:** **{metrics['escalated_pct']}%**\n\n"
                f"**Target Human Override Rate:** < 10%\n\n"
                f"**Current Human Override Rate:** **{metrics['human_override_pct']}%**"
            )
            if metrics["human_override_pct"] > 10.0:
                st.warning("⚠️ High Override Warning: Over 10% of decisions were modified by loan officers. Review risk thresholds.")
            else:
                st.success("✅ Healthy Operations: Override rate is within safe parameters.")

    with tab2:
        st.subheader("Threshold Calibration Engine")
        st.markdown(
            "Analyze whether current operational thresholds are **too conservative** (clogging human queues) "
            "or **too loose** (causing false certainty and officer overrides)."
        )

        calibration = analyze_calibration(
            total_apps=metrics["total_applications"],
            escalated_count=metrics["escalated_total"],
            autonomous_count=metrics["autonomous_count"],
            human_overrides_count=metrics["override_count"],
        )

        st.markdown(f"**Current Calibration Status:** `{calibration['status']}`")
        for rec in calibration["recommendations"]:
            st.info(f"💡 {rec}")

        st.markdown("#### Active Threshold Configurations")
        thresholds = get_current_thresholds()
        st.json(thresholds)

    with tab3:
        st.subheader("Complete Application Audit Log")
        all_apps = supabase.table("applications").select("*").execute()
        if all_apps.data:
            df_all = pd.DataFrame(all_apps.data)
            st.dataframe(df_all, use_container_width=True)
            
            # Export CSV button
            csv_buffer = io.StringIO()
            df_all.to_csv(csv_buffer, index=False)
            st.download_button(
                "📥 Download Compliance Audit CSV",
                data=csv_buffer.getvalue(),
                file_name="flowmind_compliance_audit.csv",
                mime="text/csv",
            )


# =========================================================================
# PAGE 3: GUARDRAILS & SIMULATION LAB (DELIVERABLES D4, EDGE CASES, FRAUD)
# =========================================================================
elif app_mode == "🧪 Guardrails & Simulation Lab":
    st.markdown(
        """
        <div class="main-header">
            <h1>FlowMind — Guardrails & Edge Case Lab</h1>
            <p>Interactive verification for Anti-Hallucination validation (D4), PDF intake resilience, and Fraud detection.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    lab_tab1, lab_tab2, lab_tab3 = st.tabs([
        "🛡️ Anti-Hallucination Guardrail (D4)",
        "📄 PDF Intake Edge Cases (Scanned / Truncated)",
        "🚨 Fraud & Identity Mismatch Detection",
    ])

    # ---------------- TAB 1: ANTI-HALLUCINATION GUARDRAIL ----------------
    with lab_tab1:
        st.subheader("Deliverable D4: Letter Validation Guardrail (`validate_letter`)")
        st.markdown(
            "ClearPath Capital enforces a strict anti-hallucination guardrail: **Every single number, duration, age, and date claim** "
            "in an AI-generated letter is cross-referenced with structured ground truth. Any unverified claim flags the letter for human review."
        )

        # Baseline Ground Truth Record
        sample_record = {
            "applicant_name": "Tolu Adebayo",
            "applicant_age": 32,
            "business_name": "Adebayo Logistics Hub",
            "operating_months": 18,
            "loan_amount": 2000000.0,
            "monthly_turnover": 400000.0,
            "purpose": "Fleet maintenance and tyre acquisition",
            "purpose_category": "equipment_acquisition",
        }

        col_l1, col_l2 = st.columns([1, 1])

        with col_l1:
            st.markdown("#### 1. Ground Truth Application Record")
            st.json(sample_record)

            test_scenario = st.selectbox(
                "Select Test Scenario to Inject:",
                [
                    "Accurate Conditional Approval Letter (Valid)",
                    "Deliberate Failure: Hallucinated Operating Duration ('less than 12 months' vs 18 months)",
                    "Deliberate Failure: Hallucinated Monetary Amount (₦9,500,000 vs ₦2,000,000)",
                    "Deliberate Failure: Hallucinated Applicant Age (55 yrs vs 32 yrs)",
                ],
            )

        with col_l2:
            st.markdown("#### 2. Generated Letter Body")
            
            if test_scenario == "Accurate Conditional Approval Letter (Valid)":
                default_letter = generate_conditional_approval_letter(sample_record)
            elif test_scenario == "Deliberate Failure: Hallucinated Operating Duration ('less than 12 months' vs 18 months)":
                default_letter = (
                    "Dear Tolu Adebayo,\n\n"
                    "We regret to inform you that your loan application for Adebayo Logistics Hub for ₦2,000,000 has been declined "
                    "because your business has operated for less than 12 months. ClearPath Capital requires a minimum of 12 months in business.\n\n"
                    "ClearPath Capital Team"
                )
            elif test_scenario == "Deliberate Failure: Hallucinated Monetary Amount (₦9,500,000 vs ₦2,000,000)":
                default_letter = (
                    "Dear Tolu Adebayo,\n\n"
                    "We are pleased to approve your loan facility of ₦9,500,000 for Adebayo Logistics Hub. "
                    "Your operating duration of 18 months meets our standard.\n\n"
                    "ClearPath Capital Team"
                )
            else:
                default_letter = (
                    "Dear Tolu Adebayo,\n\n"
                    "Your application for Adebayo Logistics Hub has been declined as our records indicate an applicant age of 55 years.\n\n"
                    "ClearPath Capital Team"
                )

            letter_input = st.text_area("Letter Text for Guardrail Verification:", value=default_letter, height=220)

            if st.button("🔍 Run validate_letter(letter, record)", type="primary"):
                result = validate_letter(letter_input, sample_record)

                st.markdown("#### 3. Guardrail Result")
                if result.is_valid:
                    st.markdown(
                        f"""<div class="guardrail-pass">
                        <strong>✅ VALIDATION PASSED:</strong> Safe to send automatically.<br/>
                        {result.explanation}
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    st.success("Verified Claims:")
                    for v in result.verified_claims:
                        st.write(f"- {v}")
                else:
                    st.markdown(
                        f"""<div class="guardrail-fail">
                        <strong>⛔ GUARDRAIL BLOCKED AUTO-SEND:</strong> Letter flagged for human review.<br/>
                        {result.explanation}
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    st.error(f"Detected Hallucinations ({len(result.hallucinations)}):")
                    for h in result.hallucinations:
                        st.write(f"- {h}")

    # ---------------- TAB 2: PDF INTAKE EDGE CASES ----------------
    with lab_tab2:
        st.subheader("Document Intake Resilience: Scanned & Truncated PDFs")
        st.markdown(
            "ClearPath Capital's document intake pipeline uses PyMuPDF with defensive wrappers. "
            "Flat scanned PDFs (no text layer) and truncated/corrupt bytes are caught cleanly without crashing."
        )

        icol1, icol2 = st.columns(2)

        with icol1:
            st.markdown("#### Test Scenarios")
            intake_mode = st.radio(
                "Choose Intake Test Case:",
                ["Normal Searchable PDF", "Scanned / Flat Image-Only PDF", "Truncated / Corrupted PDF Bytes"],
            )

            test_button = st.button("⚡ Test PyMuPDF Extractor")

        with icol2:
            if test_button:
                import pymupdf as fitz

                if intake_mode == "Normal Searchable PDF":
                    doc = fitz.open()
                    page = doc.new_page()
                    page.insert_text((50, 72), "CAC Certificate of Incorporation\nRC-982104\nBusiness: Golden Grains Ltd")
                    pdf_bytes = doc.write()
                    doc.close()
                elif intake_mode == "Scanned / Flat Image-Only PDF":
                    # Create blank page with zero text stream (simulates scanned image)
                    doc = fitz.open()
                    doc.new_page()
                    pdf_bytes = doc.write()
                    doc.close()
                else:
                    # Corrupt / Truncated byte stream
                    pdf_bytes = b"%PDF-1.4\n%InvalidTruncatedByteStreamContent..."

                intake_res = extract_text_from_pdf(pdf_bytes)

                st.markdown("#### Extraction Result")
                st.json(intake_res.model_dump())

                if intake_res.is_successful:
                    st.success(f"Extracted clean text: '{intake_res.extracted_text[:100]}...'")
                elif intake_res.is_scanned:
                    st.warning("⚠️ Scanned Image Detected: System flagged `requires_ocr` and escalated gracefully without crashing.")
                elif intake_res.is_corrupted:
                    st.error("🛑 Corrupted PDF Caught: System caught EOF/parse error, flagged `corrupted_file` and escalated gracefully.")

    # ---------------- TAB 3: FRAUD & IDENTITY MISMATCH ----------------
    with lab_tab3:
        st.subheader("Fraud Detection: Name Mismatch between Form & Bank Statement")
        st.markdown(
            "When an applicant submits third-party financial records (e.g. Bank statement under a completely different name), "
            "FlowMind immediately flags High Risk with specific reasoning."
        )

        fcol1, fcol2 = fcol3 = st.columns(3)
        applicant_in = fcol1.text_input("Applicant Name", "Kelechi Obi")
        biz_in = fcol2.text_input("Business Name", "Obi Electronics")
        bank_in = fcol3.text_input("Bank Statement Account Name", "Zuma Mining Logistics PLC")

        if st.button("🚨 Run Identity & Risk Classifier"):
            test_app = {
                "applicant_name": applicant_in,
                "business_name": biz_in,
                "bank_statement_account_name": bank_in,
                "loan_amount": 3000000.0,
                "monthly_turnover": 600000.0,
                "operating_months": 24,
                "applicant_age": 35,
                "purpose": "Inventory purchase",
                "purpose_category": "inventory_purchase",
            }
            res = process_application(test_app, save_to_db=False)
            st.json(res["risk"])
            if res["risk"]["risk_level"] == "High":
                st.error(f"High Risk Detected! Reasoning: {res['risk']['reasoning']}")
            else:
                st.success(f"Risk Level: {res['risk']['risk_level']}")
