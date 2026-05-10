"""
mock_data.py — In-memory mock database for MedAgent.

Realistic but entirely fictional patient, lab, drug interaction, and
clinical guideline data. No real patient information is used.
"""

# ---------------------------------------------------------------------------
# Patient records
# ---------------------------------------------------------------------------

PATIENTS = {
    "PAT-00123": {
        "patient_id": "PAT-00123",
        "name": "Jane Doe",
        "age": 67,
        "dob": "1959-02-14",
        "weight_kg": 72.5,
        "allergies": ["penicillin"],
        "current_medications": [
            {"name": "warfarin", "dose_mg": 5, "frequency": "daily"},
            {"name": "metoprolol", "dose_mg": 25, "frequency": "twice daily"},
            {"name": "ramipril", "dose_mg": 5, "frequency": "daily"},
        ],
        "primary_diagnosis": "Atrial fibrillation",
        "last_visit_date": "2026-04-15",
    },
    "PAT-00456": {
        "patient_id": "PAT-00456",
        "name": "Marcus Williams",
        "age": 54,
        "dob": "1972-09-03",
        "weight_kg": 88.0,
        "allergies": ["sulfonamides", "codeine"],
        "current_medications": [
            {"name": "metformin", "dose_mg": 1000, "frequency": "twice daily"},
            {"name": "atorvastatin", "dose_mg": 40, "frequency": "daily"},
            {"name": "lisinopril", "dose_mg": 10, "frequency": "daily"},
        ],
        "primary_diagnosis": "Type 2 diabetes mellitus, hypertension",
        "last_visit_date": "2026-03-20",
    },
    "PAT-00789": {
        "patient_id": "PAT-00789",
        "name": "Aisha Patel",
        "age": 31,
        "dob": "1995-06-18",
        "weight_kg": 61.0,
        "allergies": [],
        "current_medications": [
            {"name": "nitrofurantoin", "dose_mg": 100, "frequency": "twice daily"},
            {"name": "ibuprofen", "dose_mg": 400, "frequency": "as required"},
        ],
        "primary_diagnosis": "Recurrent urinary tract infection",
        "last_visit_date": "2026-05-01",
    },
}

# ---------------------------------------------------------------------------
# Lab results — keyed by (patient_id, test_type_lower)
# ---------------------------------------------------------------------------

LAB_RESULTS = {
    # Jane Doe — PAT-00123
    ("PAT-00123", "inr"): {
        "patient_id": "PAT-00123",
        "test_type": "INR",
        "value": 2.8,
        "unit": "ratio",
        "reference_range": "2.0–3.0 (therapeutic for AF)",
        "flag": "normal",
        "collected_at": "2026-05-08T09:14:00Z",
    },
    ("PAT-00123", "creatinine"): {
        "patient_id": "PAT-00123",
        "test_type": "creatinine",
        "value": 1.4,
        "unit": "mg/dL",
        "reference_range": "0.6–1.2",
        "flag": "high",
        "collected_at": "2026-05-08T09:14:00Z",
    },
    ("PAT-00123", "cbc"): {
        "patient_id": "PAT-00123",
        "test_type": "CBC",
        "value": 12.1,
        "unit": "g/dL",  # Haemoglobin component
        "reference_range": "12.0–16.0",
        "flag": "normal",
        "collected_at": "2026-05-08T09:14:00Z",
    },
    ("PAT-00123", "lft"): {
        "patient_id": "PAT-00123",
        "test_type": "LFT",
        "value": 38,
        "unit": "U/L",  # ALT component
        "reference_range": "7–40",
        "flag": "normal",
        "collected_at": "2026-04-15T10:30:00Z",
    },
    ("PAT-00123", "bmp"): {
        "patient_id": "PAT-00123",
        "test_type": "BMP",
        "value": 4.1,
        "unit": "mmol/L",  # Potassium component
        "reference_range": "3.5–5.0",
        "flag": "normal",
        "collected_at": "2026-05-08T09:14:00Z",
    },
    # Marcus Williams — PAT-00456
    ("PAT-00456", "hba1c"): {
        "patient_id": "PAT-00456",
        "test_type": "HbA1c",
        "value": 7.9,
        "unit": "%",
        "reference_range": "<7.0 (target for T2DM)",
        "flag": "high",
        "collected_at": "2026-03-20T08:00:00Z",
    },
    ("PAT-00456", "creatinine"): {
        "patient_id": "PAT-00456",
        "test_type": "creatinine",
        "value": 1.1,
        "unit": "mg/dL",
        "reference_range": "0.7–1.3",
        "flag": "normal",
        "collected_at": "2026-03-20T08:00:00Z",
    },
    ("PAT-00456", "bmp"): {
        "patient_id": "PAT-00456",
        "test_type": "BMP",
        "value": 4.8,
        "unit": "mmol/L",
        "reference_range": "3.5–5.0",
        "flag": "normal",
        "collected_at": "2026-03-20T08:00:00Z",
    },
    ("PAT-00456", "lft"): {
        "patient_id": "PAT-00456",
        "test_type": "LFT",
        "value": 52,
        "unit": "U/L",
        "reference_range": "7–40",
        "flag": "high",
        "collected_at": "2026-03-20T08:00:00Z",
    },
    # Aisha Patel — PAT-00789
    ("PAT-00789", "creatinine"): {
        "patient_id": "PAT-00789",
        "test_type": "creatinine",
        "value": 0.8,
        "unit": "mg/dL",
        "reference_range": "0.5–1.1",
        "flag": "normal",
        "collected_at": "2026-05-01T11:00:00Z",
    },
    ("PAT-00789", "cbc"): {
        "patient_id": "PAT-00789",
        "test_type": "CBC",
        "value": 14.2,
        "unit": "g/dL",
        "reference_range": "12.0–16.0",
        "flag": "normal",
        "collected_at": "2026-05-01T11:00:00Z",
    },
}

# ---------------------------------------------------------------------------
# Drug interaction database — keyed by sorted (drug_a, drug_b) tuple
# ---------------------------------------------------------------------------

DRUG_INTERACTIONS = {
    ("aspirin", "warfarin"): {
        "drug_a": "aspirin",
        "drug_b": "warfarin",
        "severity": "major",
        "mechanism": (
            "Additive anticoagulant effect. Aspirin displaces warfarin from plasma "
            "proteins and inhibits platelet aggregation independently via COX-1 inhibition."
        ),
        "clinical_recommendation": (
            "Avoid combination unless benefit clearly outweighs bleeding risk (e.g., acute "
            "coronary syndrome). If used concurrently, monitor INR closely and prescribe a "
            "PPI for gastric protection."
        ),
    },
    ("metformin", "contrast"): {
        "drug_a": "metformin",
        "drug_b": "contrast",
        "severity": "major",
        "mechanism": (
            "Iodinated contrast media can impair renal clearance of metformin, increasing "
            "plasma concentrations and risk of lactic acidosis."
        ),
        "clinical_recommendation": (
            "Withhold metformin 48 hours before and after iodinated contrast administration. "
            "Restart only after confirming stable renal function."
        ),
    },
    ("azithromycin", "warfarin"): {
        "drug_a": "azithromycin",
        "drug_b": "warfarin",
        "severity": "moderate",
        "mechanism": (
            "Azithromycin may inhibit CYP1A2 and reduce gut flora that produce vitamin K, "
            "potentiating warfarin's anticoagulant effect."
        ),
        "clinical_recommendation": (
            "Monitor INR more frequently during and for one week after the azithromycin "
            "course. Dose adjustment may be required."
        ),
    },
    ("metoprolol", "warfarin"): {
        "drug_a": "metoprolol",
        "drug_b": "warfarin",
        "severity": "none",
        "mechanism": "Minimal pharmacokinetic interaction documented in the literature.",
        "clinical_recommendation": "No dose adjustment required. Standard INR monitoring applies.",
    },
    ("ibuprofen", "warfarin"): {
        "drug_a": "ibuprofen",
        "drug_b": "warfarin",
        "severity": "major",
        "mechanism": (
            "NSAIDs inhibit platelet aggregation and may cause GI erosion, compounding "
            "bleeding risk. Ibuprofen also displaces warfarin from protein binding sites."
        ),
        "clinical_recommendation": (
            "Avoid concurrent use. Consider paracetamol as an alternative analgesic. "
            "If NSAID is unavoidable, reduce warfarin dose and monitor INR closely."
        ),
    },
    ("metformin", "alcohol"): {
        "drug_a": "metformin",
        "drug_b": "alcohol",
        "severity": "moderate",
        "mechanism": (
            "Alcohol impairs gluconeogenesis and increases lactate production, raising "
            "lactic acidosis risk when combined with metformin."
        ),
        "clinical_recommendation": (
            "Advise patient to limit or avoid alcohol. Binge drinking is contraindicated. "
            "Reinforce at every diabetes review."
        ),
    },
    ("nitrofurantoin", "antacids"): {
        "drug_a": "nitrofurantoin",
        "drug_b": "antacids",
        "severity": "moderate",
        "mechanism": (
            "Magnesium-containing antacids reduce the absorption of nitrofurantoin from "
            "the GI tract, decreasing urinary drug concentrations."
        ),
        "clinical_recommendation": (
            "Separate nitrofurantoin and antacid doses by at least two hours. "
            "Take nitrofurantoin with food to improve tolerability."
        ),
    },
    ("atorvastatin", "clarithromycin"): {
        "drug_a": "atorvastatin",
        "drug_b": "clarithromycin",
        "severity": "major",
        "mechanism": (
            "Clarithromycin is a potent CYP3A4 inhibitor. Co-administration raises "
            "atorvastatin plasma levels significantly, increasing myopathy and "
            "rhabdomyolysis risk."
        ),
        "clinical_recommendation": (
            "Temporarily withhold atorvastatin during clarithromycin course, or switch "
            "to a statin not metabolised by CYP3A4 (e.g., pravastatin)."
        ),
    },
    ("lisinopril", "potassium"): {
        "drug_a": "lisinopril",
        "drug_b": "potassium",
        "severity": "moderate",
        "mechanism": (
            "ACE inhibitors reduce aldosterone secretion, causing potassium retention. "
            "Concomitant potassium supplementation or potassium-sparing diuretics may "
            "cause hyperkalaemia."
        ),
        "clinical_recommendation": (
            "Monitor serum potassium regularly. Avoid routine potassium supplementation "
            "unless documented deficiency. Check BMP before initiating and at 1–2 weeks."
        ),
    },
    ("ibuprofen", "lisinopril"): {
        "drug_a": "ibuprofen",
        "drug_b": "lisinopril",
        "severity": "moderate",
        "mechanism": (
            "NSAIDs antagonise the antihypertensive effect of ACE inhibitors by "
            "inhibiting prostaglandin-mediated vasodilation and promoting sodium retention."
        ),
        "clinical_recommendation": (
            "Avoid regular NSAID use in patients on ACE inhibitors. Monitor blood pressure "
            "and renal function if short-term use is unavoidable."
        ),
    },
    ("ramipril", "spironolactone"): {
        "drug_a": "ramipril",
        "drug_b": "spironolactone",
        "severity": "major",
        "mechanism": (
            "Both agents increase potassium retention: ramipril by reducing aldosterone, "
            "spironolactone by antagonising aldosterone receptors. Risk of life-threatening "
            "hyperkalaemia."
        ),
        "clinical_recommendation": (
            "Combination is appropriate in heart failure under specialist supervision only. "
            "Monitor potassium and renal function at 1, 4, and 12 weeks after initiation, "
            "then every 6 months."
        ),
    },
}

# ---------------------------------------------------------------------------
# Clinical guidelines
# ---------------------------------------------------------------------------

CLINICAL_GUIDELINES = {
    "atrial_fibrillation": {
        "condition": "Atrial Fibrillation",
        "guideline_source": "ESC 2023",
        "anticoagulation": {
            "first_line": "Warfarin (target INR 2.0–3.0) or DOAC (apixaban, rivaroxaban, edoxaban)",
            "note": (
                "DOACs preferred in new diagnoses without valvular AF. "
                "Warfarin continues where INR is well-controlled or DOAC contraindicated."
            ),
        },
        "rate_control": {
            "first_line": "Beta-blocker (metoprolol, bisoprolol) or rate-limiting CCB",
            "target": "Resting heart rate < 110 bpm; < 80 bpm if symptomatic",
        },
        "monitoring": {
            "inr_frequency": "Monthly when stable; 2-weekly after dose change",
            "renal_function": "Annually",
        },
    },
    "type2_diabetes": {
        "condition": "Type 2 Diabetes Mellitus",
        "guideline_source": "NICE NG28 2022",
        "first_line": "Metformin 500 mg BD, titrate to 1 g BD over 4 weeks as tolerated",
        "second_line": "Add SGLT2 inhibitor or GLP-1 agonist if HbA1c > 7.5% on metformin",
        "targets": {
            "HbA1c": "< 7.0% (53 mmol/mol) on monotherapy; < 7.5% on dual therapy",
            "BP": "< 140/80 mmHg; < 130/80 mmHg if renal disease or CVD present",
        },
        "monitoring": {
            "HbA1c": "Every 3 months until stable; 6-monthly when at target",
            "renal_function": "Annually; more frequent if eGFR < 45",
            "LFT": "Annually (metformin hepatotoxicity is rare but monitored)",
        },
    },
    "uti": {
        "condition": "Urinary Tract Infection (uncomplicated, female)",
        "guideline_source": "NICE NG109 2022",
        "first_line": "Nitrofurantoin 100 mg MR BD for 5 days (if eGFR ≥ 30 mL/min)",
        "alternatives": {
            "trimethoprim": "200 mg BD for 7 days (avoid if sulfonamide allergy or high local resistance)",
            "pivmecillinam": "400 mg TDS for 3 days",
        },
        "avoid": "Fluoroquinolones for uncomplicated UTI (resistance risk)",
        "recurrent_uti": (
            "Investigate for structural or functional abnormality. "
            "Consider low-dose prophylaxis or self-start therapy after review."
        ),
    },
    "hypertension": {
        "condition": "Hypertension",
        "guideline_source": "NICE NG136 2022",
        "stage1": {
            "threshold": "Clinic BP ≥ 140/90 mmHg, ABPM daytime average ≥ 135/85 mmHg",
            "treatment": "Lifestyle modification; drug treatment if target organ damage or 10-year CVD risk ≥ 10%",
        },
        "first_line": {
            "under_55": "ACE inhibitor (e.g., ramipril 2.5–10 mg OD) or ARB",
            "over_55_or_afro_caribbean": "CCB (e.g., amlodipine 5–10 mg OD)",
        },
        "targets": {
            "under_80": "< 140/90 mmHg clinic; < 135/85 ABPM",
            "over_80": "< 150/90 mmHg clinic",
        },
    },
}
