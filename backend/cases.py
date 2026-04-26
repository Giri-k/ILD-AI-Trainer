"""
Interstitial Lung Disease (ILD) Case Data
Each case includes patient presentation, full case details, ground truth diagnosis,
ideal diagnostic pathway, test costs, and expected findings.
"""

from typing import Optional
from pathlib import Path
import glob

ILD_CASES = [
    {
        "id": "ild_001",
        "title": "Progressive Dyspnea in a 62-Year-Old Former Smoker",
        "difficulty": "moderate",
        "initial_presentation": (
            "A 62-year-old man presents with progressive exertional dyspnea over 6 months "
            "and a dry, nonproductive cough. He is a former smoker with a 30-pack-year history, "
            "having quit 10 years ago. He reports no fevers, weight loss, or hemoptysis."
        ),
        "full_case_details": {
            "demographics": "62-year-old Caucasian male, retired construction worker, BMI 27",
            "chief_complaint": "Progressive exertional dyspnea and dry cough for 6 months",
            "hpi": (
                "Patient noticed breathlessness climbing stairs 6 months ago. Dyspnea has "
                "progressively worsened; now occurs with walking one block on flat ground. "
                "Dry cough is persistent, worse in the morning. No wheezing, chest pain, "
                "orthopnea, or PND. No hemoptysis. No fevers, night sweats, or weight loss."
            ),
            "past_medical_history": [
                "Hypertension – controlled on lisinopril 10mg daily",
                "Type 2 Diabetes – managed with metformin 1000mg BID",
                "GERD – on omeprazole 20mg daily",
                "No prior lung disease diagnosed"
            ],
            "medications": [
                "Lisinopril 10mg daily",
                "Metformin 1000mg BID",
                "Omeprazole 20mg daily",
                "Aspirin 81mg daily"
            ],
            "family_history": "Father died of lung cancer at 72. Mother alive with COPD. No family history of autoimmune disease.",
            "social_history": (
                "Former smoker – 30 pack-years, quit 10 years ago. Retired construction worker "
                "with significant asbestos exposure during the 1980s-1990s. Drinks alcohol socially. "
                "Lives with wife. Has pet parakeet for 2 years."
            ),
            "review_of_systems": {
                "constitutional": "Fatigue, no weight loss or fevers",
                "respiratory": "Dyspnea on exertion, dry cough, no wheezing or hemoptysis",
                "cardiovascular": "No chest pain, palpitations, or edema",
                "musculoskeletal": "Mild joint stiffness in hands bilaterally, no swelling",
                "skin": "No rashes",
                "gi": "Occasional heartburn, no dysphagia"
            },
            "physical_exam": {
                "vitals": "BP 138/82, HR 88, RR 20, SpO2 93% on room air, Temp 98.4°F",
                "general": "Alert, comfortable at rest, mild tachypnea with conversation",
                "lungs": "Bilateral fine inspiratory crackles (Velcro crackles) at lung bases, no wheezing",
                "heart": "Regular rate and rhythm, no murmurs",
                "extremities": "Digital clubbing present bilaterally, no edema",
                "skin": "No rashes or cyanosis",
                "musculoskeletal": "Mild MCP joint tenderness bilaterally without swelling"
            },
            "test_results": {
                "CBC": "WBC 8.2, Hgb 14.1, Hct 42.3, Platelets 245. Normal differential.",
                "BMP": "Na 140, K 4.1, Cl 102, CO2 24, BUN 18, Cr 1.0, Glucose 132",
                "Pulmonary Function Tests": (
                    "FVC 62% predicted, FEV1 68% predicted, FEV1/FVC ratio 0.82 (normal). "
                    "TLC 65% predicted. DLCO 48% predicted. Restrictive pattern with severely reduced diffusion capacity."
                ),
                "Chest X-ray": (
                    "Bilateral reticular opacities predominantly in the lower lung zones. "
                    "Reduced lung volumes. No pleural effusions or masses."
                ),
                "HRCT Chest": (
                    "Bilateral, predominantly basal and subpleural, reticular opacities with "
                    "honeycombing and traction bronchiectasis. Minimal ground-glass opacities. "
                    "Pattern consistent with usual interstitial pneumonia (UIP). No mediastinal lymphadenopathy."
                ),
                "ANA": "Positive at 1:80, speckled pattern",
                "RF": "12 IU/mL (mildly elevated, normal <14)",
                "Anti-CCP": "Negative",
                "ESR": "28 mm/hr (mildly elevated)",
                "CRP": "1.2 mg/dL (mildly elevated)",
                "BNP": "85 pg/mL (normal)",
                "ABG": "pH 7.42, PaCO2 36, PaO2 68, HCO3 24 on room air",
                "6-Minute Walk Test": "Distance 320m (reduced). SpO2 dropped from 94% to 86% during exercise.",
                "Echocardiogram": "Normal LV function, EF 60%. Estimated RVSP 38mmHg (mildly elevated). No significant valvular disease.",
                "Bronchoalveolar Lavage": "Predominantly neutrophilic. No eosinophilia. Negative cultures. No malignant cells.",
                "Surgical Lung Biopsy": (
                    "Histology shows temporal heterogeneity with areas of normal lung adjacent to "
                    "fibrotic areas. Fibroblastic foci at the interface of normal and scarred lung. "
                    "Honeycombing with subpleural and paraseptal distribution. Pattern consistent with "
                    "usual interstitial pneumonia (UIP). No granulomas, no vasculitis."
                )
            }
        },
        "ground_truth_diagnosis": "Idiopathic Pulmonary Fibrosis (IPF)",
        "ideal_diagnostic_pathway": [
            {
                "step": 1,
                "action": "history",
                "ideal_questions": [
                    "Onset, progression, and character of dyspnea",
                    "Cough characteristics – productive vs dry",
                    "Smoking history in detail",
                    "Occupational exposure history (asbestos, silica, coal, etc.)",
                    "Environmental exposures (birds, mold, hot tubs)",
                    "Medication history including any drug-induced lung disease risk",
                    "Family history of lung or autoimmune disease"
                ],
                "reasoning": "Establish timeline, identify risk factors for ILD subtypes, and narrow differential"
            },
            {
                "step": 2,
                "action": "physical_exam",
                "ideal_questions": [
                    "Lung auscultation findings",
                    "Presence of digital clubbing",
                    "Signs of connective tissue disease (skin changes, joint findings)",
                    "Oxygen saturation at rest"
                ],
                "reasoning": "Velcro crackles + clubbing strongly suggest IPF. CTD signs would redirect toward CTD-ILD."
            },
            {
                "step": 3,
                "action": "test",
                "ideal_tests": ["Pulmonary Function Tests", "Chest X-ray"],
                "reasoning": "PFTs confirm restrictive pattern with reduced DLCO. CXR shows basal reticular opacities."
            },
            {
                "step": 4,
                "action": "test",
                "ideal_tests": ["HRCT Chest"],
                "reasoning": "HRCT is the cornerstone for ILD diagnosis. UIP pattern (basal, subpleural honeycombing + traction bronchiectasis) is pathognomonic for IPF when clinical context is consistent."
            },
            {
                "step": 5,
                "action": "test",
                "ideal_tests": ["ANA", "RF", "Anti-CCP", "ESR", "CRP"],
                "reasoning": "Serologic workup to exclude connective tissue disease-associated ILD, which can mimic IPF."
            },
            {
                "step": 6,
                "action": "test",
                "ideal_tests": ["6-Minute Walk Test", "ABG"],
                "reasoning": "Assess functional capacity and gas exchange. Exercise desaturation helps stage severity."
            },
            {
                "step": 7,
                "action": "diagnosis",
                "reasoning": (
                    "With a definite UIP pattern on HRCT, appropriate clinical context (age >60, male, former smoker), "
                    "absence of identifiable cause (negative CTD serologies, no significant ongoing exposure), "
                    "surgical lung biopsy is NOT required. Diagnosis of IPF can be made with high confidence based on "
                    "HRCT pattern + clinical presentation per ATS/ERS 2018 guidelines."
                )
            }
        ],
        "differential_diagnoses": [
            "Idiopathic Pulmonary Fibrosis (IPF)",
            "Asbestosis",
            "Connective Tissue Disease-associated ILD (CTD-ILD)",
            "Chronic Hypersensitivity Pneumonitis",
            "Drug-induced ILD"
        ],
        "key_distinguishing_features": {
            "IPF vs Asbestosis": "Both show UIP pattern but asbestosis requires significant asbestos exposure history AND pleural plaques. HRCT showed no pleural plaques.",
            "IPF vs CTD-ILD": "Low-titer ANA without specific antibodies, no significant CTD symptoms. MCP tenderness is nonspecific.",
            "IPF vs Chronic HP": "No ongoing antigen exposure identified (parakeet is recent, 2 years). HRCT pattern favors UIP over HP (no air trapping, no upper lobe predominance)."
        }
    },
    {
        "id": "ild_002",
        "title": "Cough and Bilateral Hilar Lymphadenopathy in a 34-Year-Old Woman",
        "difficulty": "moderate",
        "initial_presentation": (
            "A 34-year-old African American woman presents with a 3-month history of dry cough, "
            "mild dyspnea on exertion, fatigue, and painful red nodules on her shins. "
            "She has no smoking history and no known occupational exposures."
        ),
        "full_case_details": {
            "demographics": "34-year-old African American female, school teacher, BMI 24",
            "chief_complaint": "Dry cough, dyspnea, fatigue, and skin lesions for 3 months",
            "hpi": (
                "Patient developed a dry cough 3 months ago along with progressive fatigue and "
                "exertional dyspnea. She noticed painful red-purple bumps on her shins 6 weeks ago. "
                "She also reports dry, red eyes and blurred vision intermittently for the past month. "
                "Mild joint pains in ankles bilaterally. No fevers, weight loss, or night sweats."
            ),
            "past_medical_history": ["No significant past medical history"],
            "medications": ["Ibuprofen 400mg PRN for joint pain", "Multivitamin daily"],
            "family_history": "No family history of lung disease or autoimmune conditions.",
            "social_history": (
                "Never smoker. School teacher, no occupational exposures. Lives in urban apartment. "
                "No pets. No travel history. No drug use."
            ),
            "review_of_systems": {
                "constitutional": "Fatigue, no fevers or weight loss",
                "respiratory": "Dry cough, mild exertional dyspnea",
                "cardiovascular": "No chest pain or palpitations",
                "eyes": "Dry eyes, intermittent blurred vision, photophobia",
                "musculoskeletal": "Bilateral ankle pain and swelling",
                "skin": "Painful red-purple nodules on anterior shins",
                "gi": "No symptoms"
            },
            "physical_exam": {
                "vitals": "BP 118/72, HR 76, RR 16, SpO2 97% on room air, Temp 98.6°F",
                "general": "Well-appearing, no acute distress",
                "lungs": "Clear to auscultation bilaterally, no crackles or wheezing",
                "heart": "Regular rate and rhythm, no murmurs",
                "eyes": "Bilateral conjunctival injection, anterior chamber cells on slit lamp exam",
                "skin": "Multiple tender, raised, erythematous nodules on bilateral anterior shins consistent with erythema nodosum",
                "extremities": "Mild bilateral ankle swelling, no clubbing",
                "lymph_nodes": "No peripheral lymphadenopathy palpable"
            },
            "test_results": {
                "CBC": "WBC 6.8, Hgb 13.2, Hct 39.5, Platelets 280. Mild lymphopenia (900/uL).",
                "BMP": "Normal",
                "Calcium": "10.8 mg/dL (mildly elevated, normal 8.5-10.5)",
                "ACE level": "82 U/L (elevated, normal 8-52)",
                "ESR": "42 mm/hr (elevated)",
                "CRP": "2.8 mg/dL (elevated)",
                "24-hour urine calcium": "380 mg/24hr (elevated, normal <300)",
                "Vitamin D 1,25-dihydroxy": "78 pg/mL (elevated, normal 18-72)",
                "Pulmonary Function Tests": (
                    "FVC 85% predicted, FEV1 82% predicted, FEV1/FVC 0.80 (normal). "
                    "TLC 82% predicted. DLCO 72% predicted (mildly reduced). Mild restrictive pattern."
                ),
                "Chest X-ray": (
                    "Bilateral hilar lymphadenopathy. Right paratracheal lymphadenopathy. "
                    "No parenchymal infiltrates. No effusions."
                ),
                "HRCT Chest": (
                    "Bilateral symmetric hilar and mediastinal lymphadenopathy. "
                    "Perilymphatic nodules along bronchovascular bundles and fissures. "
                    "No ground-glass opacities or honeycombing. Upper and middle lobe predominance."
                ),
                "Bronchoalveolar Lavage": "Lymphocyte-predominant (38%), CD4/CD8 ratio 5.2 (elevated). No organisms. No malignant cells.",
                "Transbronchial Biopsy": (
                    "Multiple well-formed, non-caseating granulomas composed of epithelioid histiocytes "
                    "and multinucleated giant cells. No necrosis. No acid-fast bacilli or fungal organisms "
                    "on special stains. Negative tissue cultures for mycobacteria and fungi."
                ),
                "TB testing": "QuantiFERON-TB Gold: Negative",
                "Fungal serologies": "Histoplasma and Coccidioides antibodies: Negative",
                "Ophthalmology exam": "Bilateral anterior uveitis confirmed on slit lamp examination"
            }
        },
        "ground_truth_diagnosis": "Pulmonary Sarcoidosis (Scadding Stage II)",
        "ideal_diagnostic_pathway": [
            {
                "step": 1,
                "action": "history",
                "ideal_questions": [
                    "Cough characteristics and timeline",
                    "Skin lesion description, location, and timeline",
                    "Eye symptoms – dryness, redness, vision changes",
                    "Joint symptoms",
                    "Constitutional symptoms – fevers, weight loss, night sweats",
                    "Race/ethnicity (sarcoidosis has higher prevalence in African Americans)",
                    "Occupational and environmental exposures"
                ],
                "reasoning": "The triad of bilateral hilar lymphadenopathy + erythema nodosum + ankle arthritis = Löfgren syndrome, a presentation of acute sarcoidosis."
            },
            {
                "step": 2,
                "action": "physical_exam",
                "ideal_questions": [
                    "Skin examination – description of nodules",
                    "Eye examination findings",
                    "Lung auscultation",
                    "Lymph node examination",
                    "Joint examination"
                ],
                "reasoning": "Erythema nodosum + anterior uveitis are extrapulmonary manifestations of sarcoidosis."
            },
            {
                "step": 3,
                "action": "test",
                "ideal_tests": ["Chest X-ray", "CBC", "BMP", "Calcium"],
                "reasoning": "CXR reveals bilateral hilar lymphadenopathy. Hypercalcemia and lymphopenia support sarcoidosis."
            },
            {
                "step": 4,
                "action": "test",
                "ideal_tests": ["ACE level", "24-hour urine calcium", "Vitamin D 1,25-dihydroxy"],
                "reasoning": "Elevated ACE, hypercalciuria, and elevated 1,25-dihydroxy vitamin D are markers of granulomatous disease."
            },
            {
                "step": 5,
                "action": "test",
                "ideal_tests": ["HRCT Chest", "Pulmonary Function Tests"],
                "reasoning": "HRCT confirms lymphadenopathy and shows perilymphatic nodules characteristic of sarcoidosis."
            },
            {
                "step": 6,
                "action": "test",
                "ideal_tests": ["Transbronchial Biopsy", "Bronchoalveolar Lavage", "TB testing", "Fungal serologies"],
                "reasoning": "Tissue diagnosis with non-caseating granulomas is essential. Must exclude infections (TB, fungi) that cause granulomas."
            },
            {
                "step": 7,
                "action": "diagnosis",
                "reasoning": (
                    "Non-caseating granulomas on biopsy + bilateral hilar lymphadenopathy + "
                    "erythema nodosum + anterior uveitis + elevated ACE + hypercalcemia + "
                    "negative infectious workup = Sarcoidosis. Scadding Stage II (lymphadenopathy + parenchymal involvement)."
                )
            }
        ],
        "differential_diagnoses": [
            "Pulmonary Sarcoidosis",
            "Lymphoma (Hodgkin's)",
            "Tuberculosis",
            "Fungal infection (Histoplasmosis, Coccidioidomycosis)",
            "Berylliosis"
        ],
        "key_distinguishing_features": {
            "Sarcoidosis vs Lymphoma": "Lymphoma less likely given age, bilateral symmetric LAD, erythema nodosum, uveitis, and elevated ACE. Biopsy shows granulomas not malignancy.",
            "Sarcoidosis vs TB": "Negative QuantiFERON, no caseating necrosis on biopsy, no risk factors for TB.",
            "Sarcoidosis vs Fungal": "Negative fungal serologies, no endemic area travel, non-caseating granulomas."
        }
    },
    {
        "id": "ild_003",
        "title": "Recurrent Pneumonia in a 48-Year-Old Bird Breeder",
        "difficulty": "hard",
        "initial_presentation": (
            "A 48-year-old woman presents with a 9-month history of progressive dyspnea, "
            "productive cough with occasional mucus, low-grade fevers, and 8-pound weight loss. "
            "She raises parakeets and cockatiels as a hobby. She has had three courses of "
            "antibiotics from her primary care physician for presumed pneumonia without improvement."
        ),
        "full_case_details": {
            "demographics": "48-year-old Caucasian female, homemaker, BMI 22",
            "chief_complaint": "Progressive dyspnea, cough, fevers, and weight loss for 9 months",
            "hpi": (
                "Symptoms began insidiously 9 months ago with mild exertional dyspnea and occasional cough. "
                "Over the past 3 months, dyspnea has worsened significantly – she is now breathless with "
                "household activities. Cough is sometimes productive of white mucus. She reports intermittent "
                "low-grade fevers (up to 100.4°F), chills, and has lost 8 pounds unintentionally. Symptoms "
                "seem worse on days she spends cleaning bird cages. She noticed improvement during a 2-week "
                "vacation away from home 2 months ago, but symptoms recurred upon return."
            ),
            "past_medical_history": [
                "Seasonal allergies",
                "No prior lung disease",
                "No autoimmune conditions"
            ],
            "medications": [
                "Cetirizine 10mg daily for allergies",
                "Recently completed azithromycin course"
            ],
            "family_history": "No family history of lung disease or autoimmune conditions.",
            "social_history": (
                "Never smoker. Homemaker. Raises parakeets and cockatiels for 6 years – currently has "
                "12 birds in an indoor aviary in her home. Cleans cages daily. No other occupational exposures. "
                "Lives in a suburban home, no mold or water damage. No hot tub."
            ),
            "review_of_systems": {
                "constitutional": "Low-grade fevers, chills, weight loss, fatigue",
                "respiratory": "Progressive dyspnea, productive cough, no hemoptysis",
                "cardiovascular": "No chest pain or edema",
                "musculoskeletal": "Mild myalgias",
                "skin": "No rashes",
                "gi": "Decreased appetite, no nausea or diarrhea"
            },
            "physical_exam": {
                "vitals": "BP 122/78, HR 92, RR 22, SpO2 90% on room air, Temp 100.2°F",
                "general": "Thin-appearing, mild respiratory distress with talking",
                "lungs": "Bilateral mid-lung and upper-lung inspiratory squeaks and fine crackles. No wheezing.",
                "heart": "Tachycardic, regular rhythm, no murmurs",
                "extremities": "No clubbing, no edema",
                "skin": "No rashes"
            },
            "test_results": {
                "CBC": "WBC 11.2 (elevated), Hgb 12.8, Hct 38.4, Platelets 310. Lymphocytosis.",
                "BMP": "Normal",
                "ESR": "55 mm/hr (elevated)",
                "CRP": "4.2 mg/dL (elevated)",
                "LDH": "280 U/L (mildly elevated)",
                "Precipitating antibodies (avian)": "Strongly positive for pigeon, parakeet, and cockatiel antigens",
                "Pulmonary Function Tests": (
                    "FVC 58% predicted, FEV1 55% predicted, FEV1/FVC 0.78 (normal). "
                    "TLC 60% predicted. DLCO 42% predicted. Mixed restrictive/obstructive pattern with severely reduced diffusion capacity."
                ),
                "Chest X-ray": (
                    "Bilateral diffuse reticulonodular opacities, predominantly in the mid and upper lung zones. "
                    "No hilar lymphadenopathy."
                ),
                "HRCT Chest": (
                    "Diffuse ground-glass opacities with centrilobular nodules in the mid and upper lung zones. "
                    "Mosaic attenuation pattern with air trapping on expiratory images. "
                    "Early fibrotic changes with traction bronchiolectasis in the upper lobes. "
                    "No honeycombing. No significant lymphadenopathy."
                ),
                "Bronchoalveolar Lavage": "Lymphocyte-predominant (62%), CD4/CD8 ratio 0.5 (low/inverted). No organisms. No malignant cells.",
                "Transbronchial Biopsy": (
                    "Chronic bronchiolocentric inflammation with poorly formed granulomas. "
                    "Peribronchiolar lymphocytic infiltration with organizing pneumonia features. "
                    "No caseation. Consistent with hypersensitivity pneumonitis."
                ),
                "Avian IgG antibodies": "Highly elevated",
                "Fungal and mycobacterial cultures": "Negative"
            }
        },
        "ground_truth_diagnosis": "Chronic Hypersensitivity Pneumonitis (Bird Fancier's Lung)",
        "ideal_diagnostic_pathway": [
            {
                "step": 1,
                "action": "history",
                "ideal_questions": [
                    "Detailed timeline of symptom progression",
                    "Environmental and occupational exposure history – critical to ask about birds, mold, hot tubs",
                    "Temporal relationship between symptoms and specific activities or locations",
                    "Improvement away from home / worsening upon return",
                    "Previous treatments and their efficacy",
                    "Smoking history",
                    "Pet history – types, number, duration of exposure"
                ],
                "reasoning": "The key diagnostic clue is the temporal relationship between bird exposure and symptoms. Improvement on vacation and worsening upon return is classic for HP."
            },
            {
                "step": 2,
                "action": "physical_exam",
                "ideal_questions": [
                    "Lung auscultation – location and character of abnormal sounds",
                    "Oxygen saturation",
                    "Signs of weight loss / cachexia",
                    "Clubbing",
                    "Skin exam for rashes"
                ],
                "reasoning": "Mid-lung crackles (not basal like IPF) and inspiratory squeaks are characteristic of HP. Hypoxemia indicates severity."
            },
            {
                "step": 3,
                "action": "test",
                "ideal_tests": ["Chest X-ray", "CBC", "ESR", "CRP"],
                "reasoning": "CXR shows mid/upper zone predominant changes. Leukocytosis and elevated inflammatory markers support active inflammation."
            },
            {
                "step": 4,
                "action": "test",
                "ideal_tests": ["Precipitating antibodies (avian)", "HRCT Chest"],
                "reasoning": "Positive precipitins confirm antigenic exposure. HRCT shows classic HP triad: ground-glass, centrilobular nodules, mosaic attenuation."
            },
            {
                "step": 5,
                "action": "test",
                "ideal_tests": ["Pulmonary Function Tests", "Bronchoalveolar Lavage"],
                "reasoning": "PFTs show severity. BAL lymphocytosis with low CD4/CD8 ratio is characteristic of HP."
            },
            {
                "step": 6,
                "action": "test",
                "ideal_tests": ["Transbronchial Biopsy"],
                "reasoning": "Histology confirms HP: bronchiolocentric inflammation with poorly formed granulomas."
            },
            {
                "step": 7,
                "action": "diagnosis",
                "reasoning": (
                    "Chronic bird antigen exposure + temporal symptom-exposure correlation + "
                    "positive precipitins + HRCT with ground-glass, centrilobular nodules, air trapping + "
                    "BAL lymphocytosis with low CD4/CD8 + histology showing bronchiolocentric granulomatous inflammation "
                    "= Chronic Hypersensitivity Pneumonitis (Bird Fancier's Lung)."
                )
            }
        ],
        "differential_diagnoses": [
            "Chronic Hypersensitivity Pneumonitis",
            "Sarcoidosis",
            "Idiopathic Pulmonary Fibrosis",
            "Connective Tissue Disease-associated ILD",
            "Cryptogenic Organizing Pneumonia"
        ],
        "key_distinguishing_features": {
            "HP vs Sarcoidosis": "HP shows centrilobular nodules and air trapping vs perilymphatic nodules in sarcoidosis. Low CD4/CD8 in HP vs high in sarcoidosis.",
            "HP vs IPF": "HP has upper/mid zone predominance vs basal in IPF. Ground-glass and air trapping in HP vs honeycombing in IPF. HP has identifiable antigen exposure.",
            "HP vs COP": "COP shows consolidation in peripheral distribution. HP has centrilobular nodules and exposure history."
        }
    },
    {
        "id": "ild_004",
        "title": "Progressive Dyspnea and Joint Stiffness in a 62-Year-Old Woman",
        "difficulty": "hard",
        "initial_presentation": (
            "A 62-year-old woman is referred for ILD evaluation after 18 months of progressive "
            "exertional dyspnea and dry cough. An HRCT ordered by her primary care physician "
            "showed a fibrotic pattern. She also reports 2 years of worsening joint pain and "
            "morning stiffness."
        ),
        "full_case_details": {
            "demographics": "62-year-old Caucasian female, retired office worker, BMI 25",
            "chief_complaint": "Progressive exertional dyspnea and dry cough for 18 months",
            "hpi": (
                "Patient first noticed breathlessness with moderate exertion 18 months ago. "
                "Dyspnea has progressed steadily; she is now short of breath walking half a block "
            "or climbing a single flight of stairs. She has a persistent dry cough without "
            "hemoptysis, fevers, or night sweats. Over the past 2 years she has developed "
            "bilateral hand and wrist pain with prominent morning stiffness lasting 1–2 hours "
            "daily. She has noticed swelling of her MCP and PIP joints. She reports a small "
            "firm nodule on her right elbow that appeared about a year ago. No Raynaud phenomenon, "
            "skin thickening, muscle weakness, oral ulcers, or rashes. Mild heartburn controlled "
            "with antacids. No significant weight loss."
        ),
        "past_medical_history": [
            "Hypertension – controlled on amlodipine 5mg daily",
            "Osteoporosis – on calcium and vitamin D supplementation",
            "GERD – occasional antacid use",
            "No prior lung disease diagnosed",
            "No prior rheumatologic diagnosis"
        ],
        "medications": [
            "Amlodipine 5mg daily",
            "Calcium 600mg with vitamin D 400 IU daily",
            "Antacid PRN",
            "Acetaminophen PRN for joint pain"
        ],
        "family_history": (
            "Mother had rheumatoid arthritis. Sister has hypothyroidism. "
            "No family history of lung disease or pulmonary fibrosis."
        ),
        "social_history": (
            "Never smoker. Retired office administrator, no occupational dust, chemical, "
            "or asbestos exposure. No birds, mold exposure, hot tub use, or farming. "
            "Lives in a suburban home with her husband. No pets. Drinks alcohol rarely. "
            "No illicit drug use or vaping."
        ),
        "review_of_systems": {
            "constitutional": "Mild fatigue, no fevers, night sweats, or significant weight loss",
            "respiratory": "Progressive exertional dyspnea, dry cough, no wheezing or hemoptysis",
            "cardiovascular": "No chest pain, palpitations, or lower extremity edema",
            "musculoskeletal": (
                "Bilateral MCP and PIP joint pain and swelling for 2 years, "
                "morning stiffness lasting 1–2 hours, firm nodule on right elbow"
            ),
            "skin": "No rashes, no Raynaud phenomenon, no skin thickening",
            "eyes": "No dryness, redness, or vision changes",
            "gi": "Mild heartburn, no dysphagia or regurgitation"
        },
        "physical_exam": {
            "vitals": "BP 132/78, HR 82, RR 18, SpO2 94% on room air, Temp 98.2°F",
            "general": "Well-appearing, no acute distress at rest, mild dyspnea with prolonged speech",
            "lungs": "Bilateral fine inspiratory crackles (Velcro crackles) at lung bases, no wheezing",
            "heart": "Regular rate and rhythm, P2 not accentuated, no murmurs or gallops",
            "extremities": (
                "Bilateral MCP and PIP joint swelling with warmth and tenderness (synovitis), "
                "no ulnar deviation. Mild digital clubbing. No lower extremity edema."
            ),
            "skin": (
                "A firm, nontender, 1.5 cm subcutaneous nodule on the extensor surface of "
                "the right elbow consistent with a rheumatoid nodule. No rashes, no nailfold "
                "capillary changes."
            ),
            "musculoskeletal": (
                "Symmetric swelling and tenderness of MCP and PIP joints bilaterally. "
                "Wrists mildly tender with reduced range of motion. Grip strength reduced bilaterally."
            )
        },
        "test_results": {
            "CBC": "WBC 7.8, Hgb 12.4, Hct 37.2, Platelets 310. Normal differential.",
            "CMP": "Na 141, K 4.0, Cl 103, CO2 25, BUN 16, Cr 0.9, Glucose 98, Albumin 3.6, AST 22, ALT 18. Normal.",
            "ESR": "38 mm/hr (elevated)",
            "CRP": "1.8 mg/dL (mildly elevated)",
            "RF": "86 IU/mL (elevated, normal <14)",
            "Anti-CCP": "Strongly positive (>250 U/mL)",
            "ANA": "Positive at 1:160, homogeneous pattern",
            "ENA panel": "Negative (anti-Ro, anti-La, anti-Sm, anti-RNP, anti-Scl-70, anti-Jo-1 all negative)",
            "ANCA": "Negative",
            "BNP": "65 pg/mL (normal)",
            "Pulmonary Function Tests": (
                "FVC 68% predicted, FEV1 72% predicted, FEV1/FVC ratio 0.83 (normal). "
                "TLC 70% predicted. DLCO 45% predicted. Restrictive pattern with severely "
                "reduced diffusion capacity."
            ),
            "Chest X-ray": (
                "Bilateral basilar reticular opacities. Reduced lung volumes. "
                "No pleural effusions or masses."
            ),
            "HRCT Chest": (
                "Basal-predominant, subpleural reticulation with traction bronchiectasis. "
                "No definite honeycombing. Minimal ground-glass opacities. Pattern consistent "
                "with probable UIP. Coexistent mild cylindrical bronchiectasis in the lower lobes. "
                "No mediastinal lymphadenopathy. No mosaic attenuation or air trapping."
            ),
            "6-Minute Walk Test": (
                "Distance 310m (reduced). SpO2 dropped from 94% to 86% during exercise. "
                "Significant exertional desaturation requiring supplemental oxygen titration."
            ),
            "ABG": "pH 7.43, PaCO2 38, PaO2 72, HCO3 25 on room air",
            "Echocardiogram": (
                "Normal LV function, EF 60%. Estimated RVSP 32 mmHg (normal). "
                "No significant valvular disease. No pericardial effusion."
            ),
            "Bronchoalveolar Lavage": (
                "Not performed. Multidisciplinary discussion determined that the clinical, "
                "serologic, and radiographic picture was sufficiently diagnostic. "
                "BAL/biopsy reserved for cases with diagnostic uncertainty."
            ),
            "Surgical Lung Biopsy": "Not performed – clinical diagnosis established via MDD without biopsy."
        }
        },
        "ground_truth_diagnosis": "Rheumatoid Arthritis–Associated Interstitial Lung Disease (RA-ILD), Probable UIP Pattern",
        "ideal_diagnostic_pathway": [
        {
            "step": 1,
            "action": "history",
            "ideal_questions": [
                "Triage: red flags – resting hypoxemia, rapid progression over weeks, fever, hemoptysis, chest pain, syncope, massive desaturation on minimal exertion",
                "Onset, rate of progression, and trajectory of dyspnea (months vs weeks) and functional decline",
                "Cough characteristics – productive vs dry, hemoptysis",
                "Inhalational/environmental exposures – birds, mold, water damage, humidifiers, hot tubs, farming, wood dust, metal dust, silica, asbestos, vaping/smoking",
                "Drug/treatment exposures – amiodarone, nitrofurantoin, methotrexate, leflunomide, checkpoint inhibitors, bleomycin, radiation",
                "Autoimmune/CTD clues – morning stiffness duration, symmetric small-joint pain/swelling, rheumatoid nodules, sicca symptoms, Raynaud, skin thickening, myositis symptoms, inflammatory back pain, oral ulcers",
                "Reflux/aspiration – heartburn, regurgitation, nocturnal cough, dysphagia, OSA",
                "Family history of autoimmune or lung disease"
            ],
            "reasoning": (
                "Structured ILD history must systematically cover exposures, drugs, CTD clues, "
                "reflux/aspiration, and trajectory. In this patient, the combination of 2-year "
                "symmetric small-joint symptoms with prolonged morning stiffness and a subcutaneous "
                "nodule immediately raises suspicion for rheumatoid arthritis as the underlying "
                "cause of the ILD. Absence of inhalational exposures and culprit medications helps "
                "narrow the differential."
            )
        },
        {
            "step": 2,
            "action": "physical_exam",
            "ideal_questions": [
                "Lung auscultation – basilar dry crackles (Velcro crackles)",
                "Digital clubbing",
                "Joint exam – synovitis of MCP/PIP joints, ulnar deviation",
                "Rheumatoid nodules on extensor surfaces",
                "Skin and nailfold changes suggesting CTD overlap (Raynaud, sclerodactyly, nailfold capillary changes)",
                "Signs of pulmonary hypertension – loud P2, lower extremity edema, elevated JVP"
            ],
            "reasoning": (
                "Basilar Velcro crackles confirm ILD on exam. Synovitis of MCP/PIP joints "
                "and a rheumatoid nodule on the elbow are key findings pointing toward RA-ILD. "
                "Absence of skin thickening, nailfold changes, and Raynaud argues against "
                "scleroderma-associated ILD. Assessment for pulmonary hypertension signs is "
                "critical for prognosis."
            )
        },
        {
            "step": 3,
            "action": "test",
            "ideal_tests": [
                "Pulmonary Function Tests",
                "6-Minute Walk Test",
                "HRCT Chest"
            ],
            "reasoning": (
                "PFTs quantify severity: restrictive defect (FVC 68%) with severely reduced "
                "DLCO (45%) indicates significant parenchymal and gas-exchange impairment. "
                "6MWT documents functional capacity and exertional desaturation (94% → 86%), "
                "informing oxygen titration needs. HRCT is the cornerstone: probable UIP pattern "
                "(basal subpleural reticulation + traction bronchiectasis without honeycombing) "
                "with coexistent airway disease supports RA-ILD over IPF."
            )
        },
        {
            "step": 4,
            "action": "test",
            "ideal_tests": [
                "CBC",
                "CMP",
                "ESR",
                "CRP",
                "RF",
                "Anti-CCP",
                "ANA",
                "ENA panel",
                "ANCA"
            ],
            "reasoning": (
                "Autoimmune serologies are essential to identify the underlying cause of ILD. "
                "Strongly positive anti-CCP (high specificity for RA) and elevated RF confirm "
                "seropositive RA. ANA with negative ENA panel makes other CTDs (SLE, scleroderma, "
                "myositis) unlikely. Negative ANCA excludes vasculitis. ESR/CRP elevation reflects "
                "systemic inflammation."
            )
        },
        {
            "step": 5,
            "action": "test",
            "ideal_tests": [
                "Echocardiogram",
                "BNP",
                "ABG"
            ],
            "reasoning": (
                "Echocardiogram screens for pulmonary hypertension, a complication of chronic "
                "ILD that worsens prognosis. BNP helps when dyspnea is out of proportion to "
                "ILD severity. ABG quantifies baseline gas exchange impairment. In this case, "
                "RVSP is normal and BNP is reassuring, but these become important for serial monitoring."
            )
        },
        {
            "step": 6,
            "action": "diagnosis",
            "reasoning": (
                "Multidisciplinary discussion (MDD) integrating pulmonology, radiology, and "
                "rheumatology confirms the diagnosis. Strongly positive anti-CCP + elevated RF + "
                "symmetric inflammatory polyarthritis with morning stiffness >45 minutes + "
                "rheumatoid nodules fulfills ACR/EULAR criteria for RA. HRCT probable UIP pattern "
                "with coexistent airway disease in the setting of confirmed RA = RA-ILD. "
                "No competing etiology identified (no exposures, no culprit drugs, negative ANCA, "
                "negative ENA). BAL/surgical biopsy not required given high diagnostic confidence "
                "from clinical, serologic, and radiographic concordance. "
                "Next steps: rheumatology co-management for systemic RA treatment, baseline "
                "severity trending (PFTs every 3–6 months, DLCO/FVC trajectory), oxygen titration, "
                "PH screening, GERD management, and shared decision-making on antifibrotic therapy "
                "if progressive fibrotic phenotype criteria are met."
            )
        }
    ],
    "differential_diagnoses": [
        "Rheumatoid Arthritis–Associated ILD (RA-ILD)",
        "Idiopathic Pulmonary Fibrosis (IPF)",
        "Other Connective Tissue Disease–Associated ILD (CTD-ILD, e.g., scleroderma, myositis)",
        "Chronic Hypersensitivity Pneumonitis",
        "Drug-induced ILD"
    ],
    "key_distinguishing_features": {
        "RA-ILD vs IPF": (
            "Both can present with UIP pattern on HRCT. RA-ILD is distinguished by the "
            "presence of seropositive inflammatory arthritis (strongly positive anti-CCP, "
            "elevated RF, synovitis, rheumatoid nodules) and coexistent airway disease "
            "(bronchiectasis). IPF is a diagnosis of exclusion requiring absence of a known "
            "cause for UIP."
        ),
        "RA-ILD vs Other CTD-ILD": (
            "Negative ENA panel (anti-Ro, anti-La, anti-Scl-70, anti-Jo-1, anti-RNP) "
            "and absence of scleroderma features (Raynaud, skin thickening, nailfold changes) "
            "or myositis features (proximal weakness, elevated CK) argues against other CTDs. "
            "The joint pattern (symmetric MCP/PIP synovitis) and anti-CCP positivity are "
            "specific for RA."
        ),
        "RA-ILD vs Chronic HP": (
            "No identifiable antigen exposure (no birds, mold, hot tubs). HRCT shows basal "
            "predominance without air trapping or centrilobular nodules, favoring UIP/RA-ILD "
            "over HP. HP typically shows mid-to-upper zone predominance with mosaic attenuation."
        ),
            "RA-ILD vs Drug-induced ILD": (
            "No exposure to known ILD-causing drugs (amiodarone, nitrofurantoin, methotrexate, "
            "bleomycin, checkpoint inhibitors). Current medications (amlodipine, calcium/vitamin D) "
            "are not associated with pulmonary toxicity."
            )
        }
    }
]


# US Healthcare test costs (approximate, based on 2023 CPT code pricing)
TEST_COSTS = {
    "CBC": 35,
    "BMP": 45,
    "CMP": 65,
    "Calcium": 25,
    "ESR": 20,
    "CRP": 30,
    "LDH": 25,
    "ACE level": 45,
    "ANA": 55,
    "RF": 40,
    "Anti-CCP": 65,
    "Anti-dsDNA": 75,
    "ENA panel": 120,
    "ANCA": 95,
    "BNP": 50,
    "Pro-BNP": 55,
    "Troponin": 45,
    "D-dimer": 40,
    "ABG": 85,
    "Vitamin D 1,25-dihydroxy": 95,
    "Vitamin D 25-hydroxy": 60,
    "24-hour urine calcium": 55,
    "Precipitating antibodies (avian)": 120,
    "Avian IgG antibodies": 130,
    "Hypersensitivity pneumonitis panel": 250,
    "Fungal serologies": 110,
    "TB testing": 65,
    "QuantiFERON-TB Gold": 85,
    "Sputum culture": 45,
    "Blood cultures": 55,
    "Pulmonary Function Tests": 350,
    "6-Minute Walk Test": 180,
    "Chest X-ray": 150,
    "HRCT Chest": 850,
    "CT Chest with contrast": 900,
    "CT Chest without contrast": 650,
    "CT Abdomen/Pelvis": 950,
    "MRI Chest": 1200,
    "PET-CT": 3500,
    "Echocardiogram": 450,
    "Right heart catheterization": 2800,
    "Bronchoalveolar Lavage": 1200,
    "Transbronchial Biopsy": 1800,
    "Surgical Lung Biopsy": 8500,
    "CT-guided lung biopsy": 2500,
    "Mediastinoscopy": 4500,
    "Ophthalmology exam": 200,
    "Skin biopsy": 350,
    "Fungal and mycobacterial cultures": 120,
    "Sputum cytology": 90,
    "Procalcitonin": 55,
    "IgE total": 45,
    "KL-6": 150,
    "SP-D (Surfactant Protein D)": 160,
    "Physician visit": 300
}


def get_test_cost(test_name: str) -> float:
    """Look up cost for a test. Uses fuzzy matching for flexibility."""
    test_lower = test_name.lower().strip()
    for known_test, cost in TEST_COSTS.items():
        if known_test.lower() in test_lower or test_lower in known_test.lower():
            return cost
    # Default cost for unrecognized tests
    return 200.0


def get_hrct_images_for_case(case_id: str) -> list[str]:
    """
    Automatically discover HRCT images for a case based on naming convention.
    
    Convention: Place images in backend/images/ with naming pattern:
    - {case_id}_hrct_*.png (e.g., ild_004_hrct_axial_1.png)
    - OR {case_id}_*.png (e.g., ild_004_axial_1.png)
    
    Returns list of image paths relative to backend directory.
    """
    images_dir = Path(__file__).parent / "images"
    if not images_dir.exists():
        return []
    
    # Try both naming patterns
    patterns = [
        f"{case_id}_hrct_*.png",
        f"{case_id}_hrct_*.jpg",
        f"{case_id}_*.png",
        f"{case_id}_*.jpg"
    ]
    
    found_images = []
    for pattern in patterns:
        matches = glob.glob(str(images_dir / pattern))
        found_images.extend(matches)
    
    # Remove duplicates and sort
    found_images = sorted(list(set(found_images)))
    
    # Convert to relative paths from backend directory
    relative_paths = []
    for img_path in found_images:
        # Just use the filename since we know they're in backend/images/
        filename = Path(img_path).name
        relative_paths.append(f"images/{filename}")
    
    return relative_paths


def get_case_by_id(case_id: str) -> Optional[dict]:
    for case in ILD_CASES:
        if case["id"] == case_id:
            # Automatically add HRCT images if they exist
            hrct_images = get_hrct_images_for_case(case_id)
            if hrct_images:
                case["full_case_details"]["hrct_images"] = hrct_images
            return case
    return None


def list_cases() -> list[dict]:
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "difficulty": c["difficulty"],
            "initial_presentation": c["initial_presentation"]
        }
        for c in ILD_CASES
    ]
