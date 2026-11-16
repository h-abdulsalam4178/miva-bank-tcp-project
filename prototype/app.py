import datetime
import hashlib
import os
import json

import pandas as pd
import streamlit as st
from google import genai


st.set_page_config(
    page_title="Risk-Based Test Case Prioritization",
    page_icon="🧪",
    layout="wide",
)

st.title("Intelligent Risk-Based Test Case Prioritization System")
st.write(
    "Research prototype for prioritizing regression test cases "
    "for financial web applications."
)

RISK_ATTRIBUTES = {
    "business_criticality": "Business Criticality",
    "security_sensitivity": "Security Sensitivity",
    "transaction_impact": "Transaction Impact",
    "change_relevance": "Current Change Relevance",
    "historical_defect_exposure": "Historical Defect Exposure",
}

DEFAULT_WEIGHTS = {
    "business_criticality": 0.25,
    "security_sensitivity": 0.20,
    "transaction_impact": 0.25,
    "change_relevance": 0.20,
    "historical_defect_exposure": 0.10,
}

REQUIRED_COLUMNS = ["test_case_id", "description", "functionality"]
SCORE_FIELDS = list(RISK_ATTRIBUTES.keys())
GEMINI_MODEL = "gemini-3.5-flash-lite"


st.subheader("1. Upload Regression Test Cases")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
)

if uploaded_file is None:
    st.info("Upload a CSV file to begin.")
    st.stop()

# Identify a changed file and clear results belonging to the previous file.
file_signature = hashlib.sha256(uploaded_file.getvalue()).hexdigest()

if st.session_state.get("uploaded_file_signature") != file_signature:
    st.session_state["uploaded_file_signature"] = file_signature
    st.session_state.pop("gemini_suggestions", None)
    st.session_state.pop("prioritization_results", None)
    st.session_state.pop("calculation_signature", None)
    st.session_state["suggestion_version"] = (
        st.session_state.get("suggestion_version", 0) + 1
    )

try:
    test_cases = pd.read_csv(uploaded_file)
except Exception as error:
    st.error(f"The CSV file could not be read: {error}")
    st.stop()

missing_columns = [
    column for column in REQUIRED_COLUMNS
    if column not in test_cases.columns
]

if missing_columns:
    st.error("Missing required columns: " + ", ".join(missing_columns))
    st.stop()

if test_cases.empty:
    st.warning("The CSV file contains no test cases.")
    st.stop()

if test_cases[REQUIRED_COLUMNS].isna().any().any():
    st.error(
        "Complete the required test-case ID, description, and "
        "functionality fields before proceeding."
    )
    st.stop()

# Convert IDs to trimmed strings so IDs are handled consistently.
test_cases["test_case_id"] = test_cases["test_case_id"].astype(str).str.strip()

if (test_cases["test_case_id"] == "").any():
    st.error("Every test case must have a non-empty ID.")
    st.stop()

if test_cases["test_case_id"].duplicated().any():
    st.error("Test case IDs must be unique.")
    st.stop()

st.success(f"Loaded {len(test_cases)} test cases.")

st.subheader("2. Provide Application Context")

application_context = st.text_area(
    "Describe recent changes, business rules, security concerns, "
    "or known defects",
    placeholder=(
        "Example: Recent changes were made to fund transfer validation. "
        "Incorrect processing could result in financial loss. The transfer "
        "functionality has experienced defects before."
    ),
    height=150,
    help=(
        "Provide contextual information that may help assess the risk "
        "of the uploaded test cases."
    ),
    key=f"application_context_{file_signature[:12]}",
)

st.subheader("3. Gemini-Assisted Risk Assessment")

if st.button("Ask Gemini to Assess Risks", key="gemini_assess_btn"):
    if not application_context.strip():
        st.warning("Please enter application context before requesting a risk assessment.")
    else:
        try:
            client = genai.Client(api_key=st.secrets["google"]["api_key"])

            cases_for_analysis = test_cases[
                REQUIRED_COLUMNS
            ].to_dict(orient="records")

            prompt = f"""
You are assisting with risk-based test case prioritization for a financial web application.

APPLICATION CONTEXT:
{application_context}

TEST CASES:
{json.dumps(cases_for_analysis, ensure_ascii=False)}

For every test case, suggest an integer score from 1 to 5 for each attribute:
1. business_criticality
2. security_sensitivity
3. transaction_impact
4. change_relevance
5. historical_defect_exposure

A score of 1 means low assessed risk. A score of 5 means high assessed risk.
Use only the supplied information. Do not use outside knowledge.

Score meanings (use the whole 1-5 range):
business_criticality: 5 = failure stops customers using the bank or moves
money wrongly; 3 = an important but not essential feature; 1 = a
convenience feature with little business effect.
security_sensitivity: 5 = failure could let an unauthorised person access
accounts or move money; 3 = failure weakens a security control or exposes
some personal data; 1 = no security consequence.
transaction_impact: 5 = failure directly changes the amount of money moved,
charged or credited; 3 = failure affects records or access to money but not
the amounts; 1 = no effect on money or records.

For every score, also give an evidence label and the source:
- "supported": a document states it directly. A statement that nothing
  changed, or that there were no defects, counts as supported.
- "inferred": no document states it, and you reasoned your way to the score.
- "missing": the documents say nothing at all about it. Use score 3.
Write the label, a colon, the document reference (for example R2, C1, D2;
if the statement is in an unnumbered closing note, write "closing note"),
and a few words, for example "supported: C1 login code reorganised".

Return a JSON array containing exactly one object per test case. Each object
must contain test_case_id, the five scores, five evidence fields named
business_criticality_evidence, security_sensitivity_evidence,
transaction_impact_evidence, change_relevance_evidence and
historical_defect_exposure_evidence, and explanation.
Scores must be integers from 1 to 5. Return JSON only.
"""

            with st.spinner("Gemini is analysing the test cases..."):
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config={"response_mime_type": "application/json"},
                )

            os.makedirs("run_logs", exist_ok=True)
            with open("run_logs/runs.jsonl", "a", encoding="utf-8") as log_file:
                log_file.write(json.dumps({
                    "time": datetime.datetime.now().isoformat(timespec="seconds"),
                    "model": GEMINI_MODEL,
                    "temperature": "default (not set)",
                    "prompt": prompt,
                    "raw_response": response.text,
                }, ensure_ascii=False) + "\n")

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            suggestions = json.loads(response.text)

            if not isinstance(suggestions, list):
                raise ValueError("Gemini did not return a JSON list.")

            required_fields = ["test_case_id", *SCORE_FIELDS, "explanation"]
            expected_ids = set(test_cases["test_case_id"].astype(str))
            received_ids = []

            for item in suggestions:
                if not isinstance(item, dict):
                    raise ValueError("A suggestion is not a valid object.")

                if not all(field in item for field in required_fields):
                    raise ValueError("A response is missing required fields.")

                received_ids.append(str(item["test_case_id"]))

                for attribute in SCORE_FIELDS:
                    score = item[attribute]
                    if (
                        isinstance(score, bool)
                        or not isinstance(score, int)
                        or score < 1
                        or score > 5
                    ):
                        raise ValueError(
                            "Gemini returned an invalid score. Scores must be "
                            "integers from 1 to 5."
                        )

            if (
                len(suggestions) != len(test_cases)
                or set(received_ids) != expected_ids
                or len(set(received_ids)) != len(received_ids)
            ):
                raise ValueError(
                    "Gemini's returned test cases do not match the uploaded file."
                )

            st.session_state["gemini_suggestions"] = {
                str(item["test_case_id"]): item for item in suggestions
            }
            st.session_state["suggestion_version"] = (
                st.session_state.get("suggestion_version", 0) + 1
            )
            st.session_state.pop("prioritization_results", None)
            st.session_state.pop("calculation_signature", None)

            st.success(
                "Gemini has suggested risk assessments. Review them before use."
            )

        except Exception as error:
            st.error(
                "Risk assessment failed. You can still enter scores manually below."
            )
            st.caption(f"{type(error).__name__}: {error}")

if "gemini_suggestions" in st.session_state:
    st.write("Review Gemini's suggested assessments.")
    suggestion_rows = list(st.session_state["gemini_suggestions"].values())
    st.dataframe(
        pd.DataFrame(suggestion_rows),
        use_container_width=True,
        hide_index=True,
    )

st.subheader("4. Review the Five Risk Attributes")

st.info(
    "Scores range from 1 (low assessed risk) to 5 (high assessed risk). "
    "Gemini's suggestions are pre-filled when available; otherwise, a neutral "
    "score of 3 is used. Review and edit the scores before calculating."
)

scoring_data = test_cases[REQUIRED_COLUMNS].copy()
suggestions_lookup = st.session_state.get("gemini_suggestions", {})

for attribute in SCORE_FIELDS:
    scoring_data[attribute] = [
        suggestions_lookup.get(str(test_id), {}).get(attribute, 3)
        for test_id in scoring_data["test_case_id"]
    ]

editor_key = (
    "risk_assessment_editor_"
    + str(st.session_state.get("suggestion_version", 0))
)

edited_data = st.data_editor(
    scoring_data,
    use_container_width=True,
    hide_index=True,
    disabled=REQUIRED_COLUMNS,
    column_config={
        attribute: st.column_config.NumberColumn(
            label=label,
            min_value=1,
            max_value=5,
            step=1,
            help="1 = low assessed risk; 5 = high assessed risk",
        )
        for attribute, label in RISK_ATTRIBUTES.items()
    },
    key=editor_key,
)

st.subheader("5. Configure Risk Weights")

st.caption(
    "Illustrative starting weights only. Justify and finalise the research "
    "weights before conducting the comparative evaluation."
)

weights = {}
for attribute, label in RISK_ATTRIBUTES.items():
    weights[attribute] = st.number_input(
        label,
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_WEIGHTS[attribute],
        step=0.05,
        format="%.2f",
        key=f"weight_{attribute}",
    )

weight_total = sum(weights.values())
st.write(f"Total weight: **{weight_total:.2f}**")

if abs(weight_total - 1.0) > 0.000001:
    st.warning("The weights must sum to 1.00 before risk scores can be calculated.")
else:
    if st.button("Calculate Risk Scores", type="primary", key="calculate_btn"):
        results = edited_data.copy()

        results["risk_score"] = sum(
            results[attribute] * weights[attribute]
            for attribute in SCORE_FIELDS
        )

        results = results.sort_values(
            by=["risk_score", "test_case_id"],
            ascending=[False, True],
        ).reset_index(drop=True)

        results.insert(0, "priority_rank", range(1, len(results) + 1))
        results["risk_score"] = results["risk_score"].round(2)

        # Store a signature of the inputs used for this calculation.
        calculation_inputs = {
            "scores": edited_data[
                ["test_case_id", *SCORE_FIELDS]
            ].to_dict(orient="records"),
            "weights": weights,
        }
        st.session_state["calculation_signature"] = json.dumps(
            calculation_inputs,
            sort_keys=True,
            default=str,
        )
        st.session_state["prioritization_results"] = results

# Do not display old results as current if scores or weights have changed.
current_inputs = {
    "scores": edited_data[["test_case_id", *SCORE_FIELDS]].to_dict(orient="records"),
    "weights": weights,
}
current_signature = json.dumps(current_inputs, sort_keys=True, default=str)

stored_results = st.session_state.get("prioritization_results")
stored_signature = st.session_state.get("calculation_signature")

if stored_results is not None and stored_signature == current_signature:
    st.subheader("6. Prioritized Test Cases")
    st.dataframe(
        stored_results,
        use_container_width=True,
        hide_index=True,
        column_config={
            "risk_score": st.column_config.NumberColumn(
                "Risk Score",
                format="%.2f",
            )
        },
    )

    csv_data = stored_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Prioritized Results (CSV)",
        data=csv_data,
        file_name="prioritized_test_cases.csv",
        mime="text/csv",
        key="download_btn",
    )

    st.caption(
        "Higher scores indicate higher assessed risk. Equal scores are ordered "
        "by test-case ID. Scores reflect the entered assessments and current "
        "weights; they are not independently verified measures of actual risk."
    )
elif stored_results is not None:
    st.info(
        "Your scores or weights have changed since the last calculation. "
        "Click **Calculate Risk Scores** again to update the results."
    )
