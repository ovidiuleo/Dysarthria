import streamlit as st
import pandas as pd
from collections import defaultdict
from datetime import date

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Dysarthria Decision Atlas", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
/* ── Utility cards (used in Analysis & Map tabs) ── */
.dim-card { background:#f0f4ff; border-left:4px solid #4472c4; padding:8px 12px;
            border-radius:4px; margin:4px 0; }
.step-card { background:#fafafa; border:1px solid #e0e0e0; padding:10px 14px;
             border-radius:6px; margin:6px 0; }
.step-label { font-weight:600; color:#333; }

/* ── Reset ALL Streamlit buttons to grey by default ── */
.stButton > button {
    background-color: #e8ecf0 !important;
    color: #3a3a3a !important;
    border: 1.5px solid #c8cdd4 !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: background-color 0.15s, border-color 0.15s !important;
}
.stButton > button:hover {
    background-color: #d5dbe3 !important;
    border-color: #aab0bb !important;
}
.stButton > button:focus {
    box-shadow: none !important;
}

/* ── Nav active button: dark navy ── */
button[data-nav-active="true"] {
    background-color: #1e2d42 !important;
    color: #ffffff !important;
    border-color: #1e2d42 !important;
    font-weight: 700 !important;
}
button[data-nav-active="true"]:hover {
    background-color: #2c3e57 !important;
    border-color: #2c3e57 !important;
}

/* ── Selected feature button: deep forest green ── */
button[data-selected="true"] {
    background-color: #0d4f28 !important;
    color: #ffffff !important;
    border-color: #0d4f28 !important;
    font-weight: 600 !important;
}
button[data-selected="true"]:hover {
    background-color: #093d1f !important;
    border-color: #093d1f !important;
}

/* ── System Map active type button: teal ── */
button[data-map-active="true"] {
    background-color: #0d4f28 !important;
    color: #ffffff !important;
    border-color: #0d4f28 !important;
    font-weight: 600 !important;
}
button[data-map-active="true"]:hover {
    background-color: #093d1f !important;
    border-color: #093d1f !important;
}

/* ── Shelf containers ── */
.shelf-header {
    font-weight: 700;
    font-size: 0.82em;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #2c3e50;
    padding: 6px 0 4px 14px;
    border-left: 4px solid #4472c4;
    margin: 18px 0 8px 0;
    background: #f7f9fc;
    border-radius: 0 4px 4px 0;
}

/* ── Textarea: grey when empty, white when filled ── */
.stTextArea textarea {
    background-color: #f0f4ff !important;
    color: #aaa !important;
    border: 1px solid #d0d8e4 !important;
    transition: background-color 0.2s, color 0.2s !important;
}
.stTextArea textarea:not(:placeholder-shown) {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border-color: #4472c4 !important;
}
.stTextArea textarea:focus {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border-color: #4472c4 !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════════

DYSARTHRIA_TYPES = {
    "Flaccid": {
        "locus": "Lower motor neuron (final common pathway)",
        "primary_deficit": "Weakness / hypotonia",
        "description": "Damage to the final common pathway — lower motor neurons, cranial nerves, neuromuscular junction or cranial nerve nuclei. Also known as bulbar palsy.",
        "aetiologies": [
            "Degenerative (ALS / MND)",
            "Tumours (posterior fossa)",
            "Stroke",
            "Trauma",
            "Muscular dystrophy",
            "Myasthenia gravis",
            "Guillain-Barré syndrome",
            "Bell's palsy",
        ],
        "salient_features": [
            "Hypotonia (reduced muscle tone)",
            "Muscle weakness",
            "Reduced or absent reflexes",
            "Muscle atrophy (long-term)",
            "Fasciculation",
            "Little resistance to passive movement",
            "Affects speed, range & accuracy of movement",
        ],
        "perceptual_features": [
            "Breathiness",
            "Hoarseness",
            "Hypernasality",
            "Nasal emission",
            "Imprecise consonants",
            "Short phrases",
            "Monopitch",
        ],
        "also_known_as": "Bulbar palsy",
        "assessment_notes": (
            "Check cranial nerves (especially VII, IX, X, XII). Observe for tongue atrophy and fasciculation. "
            "Maximum phonation time is often reduced. Soft palate function critical — assess hypernasality "
            "with oral vs nasal consonant contrasts."
        ),
        "intervention": {
            "Impairment-based": [
                "Respiratory support: diaphragmatic breathing, breath control, maximum vowel prolongation",
                "Phonation: effortful closure techniques for vocal fold weakness",
                "Head turn to side of vocal fold weakness to improve adduction",
                "Medical: medialization laryngoplasty or injectable substances for persistent VF paralysis",
                "Resonance: resistance training (CPAP), biofeedback (mirror, nasal-flow transducer)",
                "Articulation: integral stimulation, phonetic placement, intelligibility drills",
            ],
            "Compensatory": [
                "Palatal lift prosthesis for velopharyngeal incompetence",
                "Portable voice amplifier for hypophonia",
                "Listener strategies: reduce background noise, maintain eye contact",
                "AAC if intelligibility severely impaired",
            ],
        },
        "references": ["Duffy, J.R. (2013). Motor Speech Disorders. Chapters 4–5."],
    },
    "Spastic": {
        "locus": "Bilateral upper motor neuron (corticobulbar tract)",
        "primary_deficit": "Spasticity / hypertonicity",
        "description": (
            "Bilateral UMN damage affecting the corticobulbar tract. "
            "Results in hypertonicity, hyperactive reflexes, and slow, effortful speech. "
            "Also known as pseudobulbar or corticobulbar palsy."
        ),
        "aetiologies": [
            "Degenerative disease (MND–ALS)",
            "Bilateral stroke or brainstem stroke",
            "Traumatic brain injury (TBI)",
            "Progressive supranuclear palsy",
            "CNS tumour",
            "Congenital (e.g. cerebral palsy)",
        ],
        "salient_features": [
            "Increased muscle tone (hypertonicity)",
            "Limitation of range of movement",
            "Slowness of movement",
            "Hyperactive gag reflex",
            "No atrophy",
            "Dysphagia common (sometimes severe)",
            "Saliva escape common",
            "Pseudobulbar affect (pathological laughing/crying)",
        ],
        "perceptual_features": [
            "Strained-strangled voice quality",
            "Harsh voice quality",
            "Imprecise consonants",
            "Excess and equal stress",
            "Slow rate",
            "Pitch breaks",
            "Distorted vowels",
        ],
        "also_known_as": "Pseudobulbar / corticobulbar palsy",
        "assessment_notes": (
            "Gag reflex is often hyperactive. Check for pseudobulbar affect (emotional lability). "
            "AMRs will be slow and effortful. Jaw jerk reflex may be increased. "
            "Strained-strangled quality + excess and equal stress is a key cluster."
        ),
        "intervention": {
            "Impairment-based": [
                "Relaxation exercises to reduce hypertonicity",
                "Easy/breathy voice onset (yawn-sigh technique) for hyperadduction",
                "Rate reduction strategies (pacing board, metronomic cueing)",
                "Contrastive stress tasks to improve prosodic variation",
                "Articulation drills for consonant precision",
            ],
            "Compensatory": [
                "Alphabet board or AAC to supplement intelligibility",
                "Communicate in quieter environments",
                "Listener strategies: give time, seek clarification",
                "Written backup for key messages",
            ],
        },
        "references": ["Duffy, J.R. (2013). Motor Speech Disorders. Chapter 6."],
    },
    "Unilateral UMN": {
        "locus": "Unilateral upper motor neuron",
        "primary_deficit": "Unilateral weakness, incoordination, spasticity",
        "description": (
            "Damage to the unilateral UMN. Less severe than bilateral spastic dysarthria because most cranial "
            "nerves have bilateral innervation — EXCEPT facial (VII) and hypoglossal (XII). "
            "May co-occur with aphasia or AOS."
        ),
        "aetiologies": [
            "CVA (stroke) — most common",
            "Trauma",
            "Tumour",
        ],
        "salient_features": [
            "Contralateral tongue weakness (deviates to weaker side on protrusion)",
            "Lower facial weakness (contralateral)",
            "May co-occur with aphasia or AOS",
            "Often recovers significantly over time",
        ],
        "perceptual_features": [
            "Imprecise articulation",
            "Dysdiadochokinesis (reduced AMRs / SMRs)",
            "Slow rate",
        ],
        "also_known_as": "UUMN dysarthria",
        "assessment_notes": (
            "Observe tongue deviation on protrusion (toward weaker side). Assess lower facial asymmetry. "
            "VII and XII lack full bilateral innervation — hence articulatory imprecision. "
            "Often mild and improves with spontaneous recovery."
        ),
        "intervention": {
            "Impairment-based": [
                "Articulation drills (integral stimulation, phonetic placement)",
                "Rate control strategies",
                "Strengthening exercises for affected articulators",
            ],
            "Compensatory": [
                "Listener strategies",
                "Written backup if needed",
                "AAC rarely required given typically mild presentation",
            ],
        },
        "references": ["Duffy, J.R. (2013). Motor Speech Disorders. Chapter 7."],
    },
    "Ataxic": {
        "locus": "Cerebellum (control circuit)",
        "primary_deficit": "Incoordination / timing errors",
        "description": (
            "Associated with damage to the cerebellum, most commonly bilateral or diffuse cerebellar disease. "
            "When unilateral, more often right-sided. Speech movements are slow, inaccurate, and poorly timed. "
            "Also called cerebellar dysarthria."
        ),
        "aetiologies": [
            "Degenerative (cerebellar degeneration) — 44%",
            "Cerebellar lesion — 13%",
            "Stroke (cerebellar or brainstem) — 11%",
            "Tumours (cerebellar or brainstem)",
            "Demyelinating disease (MS)",
            "Trauma",
        ],
        "salient_features": [
            "Movement slow to start, execute, and stop",
            "Irregular repetitive movements (irregular AMRs)",
            "Intention tremor",
            "Hypotonic muscles",
            "Over/undershooting of movement (dysmetria)",
            "Impaired coordination of speech subsystems",
        ],
        "perceptual_features": [
            "Irregular articulatory breakdown",
            "Excess and equal stress",
            "Excess loudness variations",
            "Harsh voice quality",
            "Imprecise consonants",
            "Distorted vowels",
            "Slow rate",
            "Prolonged phonemes",
            "Prolonged intervals",
            "Monopitch",
        ],
        "also_known_as": "Cerebellar dysarthria",
        "assessment_notes": (
            "Irregular AMRs/SMRs are a hallmark — distinguish from spastic (slow but regular). "
            "Check for intention tremor, nystagmus, ataxic gait. "
            "Excess and equal stress on syllables is a key perceptual differentiator from hypokinetic."
        ),
        "intervention": {
            "Impairment-based": [
                "Rate reduction: rhythmic cueing, pacing board, metronomic pacing",
                "Contrastive stress tasks to improve prosodic control",
                "Articulation precision drills",
                "Biofeedback (acoustic, visual)",
            ],
            "Compensatory": [
                "Pacing strategies (alphabet board, finger tapping)",
                "AAC if severe",
                "Listener education about pacing",
            ],
        },
        "references": ["Duffy, J.R. (2013). Motor Speech Disorders. Chapter 8."],
    },
    "Hypokinetic": {
        "locus": "Basal ganglia control circuit",
        "primary_deficit": "Rigidity / reduced range of movement (hypokinesia)",
        "description": (
            "Damage to the basal ganglia control circuit, predominantly (but not exclusively) associated with "
            "Parkinson's Disease. Impaired basal ganglia over-dampens motor outputs, causing reduced amplitude "
            "and range of speech movements. Sensorimotor feedback is also impaired — speakers may underestimate "
            "their loudness."
        ),
        "aetiologies": [
            "Degenerative (mostly Parkinson's Disease) — 87%",
            "Vascular — 4%",
            "Multiple causes — 3%",
            "Trauma — 2%",
            "Undetermined — 2%",
            "Infectious — 1%",
        ],
        "salient_features": [
            "Resting tremor (jaw, lips, tongue)",
            "Reduced range of movement (hypokinesia)",
            "Rigidity (stiffness, resistance to passive movement)",
            "Bradykinesia (slowness, false starts)",
            "Difficulty starting and stopping movements",
            "Mask-like facies (reduced facial expression)",
        ],
        "perceptual_features": [
            "Monopitch",
            "Reduced stress",
            "Monoloudness",
            "Inappropriate silences",
            "Short rushes of speech",
            "Variable rate",
            "Breathy voice",
            "Harsh voice quality",
            "Imprecise consonants",
            "Low pitch",
            "Quiet voice (hypophonia)",
        ],
        "also_known_as": "Parkinsonian dysarthria",
        "assessment_notes": (
            "AMRs may be rapid but irregular. Assess loudness particularly — patient often underestimates volume. "
            "Note festination (increasing rate/decreasing loudness). "
            "LSVT LOUD is the gold-standard evidence-based intervention."
        ),
        "intervention": {
            "Impairment-based": [
                "LSVT LOUD (Lee Silverman Voice Treatment): intensive loudness therapy — strong evidence (Ramig et al., 2001)",
                "Diaphragmatic breathing for breath support",
                "Rate control: metronomic pacing, delayed auditory feedback (DAF)",
                "Contrastive stress tasks for prosodic variation",
                "Articulation precision drills",
            ],
            "Compensatory": [
                "Portable voice amplifier",
                "Delayed auditory feedback (DAF) device",
                "Alphabet board / AAC for severe cases",
                "Listener education: give time, seek clarification",
            ],
        },
        "references": [
            "Duffy, J.R. (2013). Motor Speech Disorders. Chapter 9.",
            "Ramig, L.O. et al. (2001). Intensive voice treatment (LSVT LOUD) for Parkinson's disease.",
        ],
    },
    "Hyperkinetic": {
        "locus": "Basal ganglia control circuit",
        "primary_deficit": "Involuntary movements (failure to inhibit)",
        "description": (
            "Damage to the basal ganglia results in failure to inhibit involuntary movement. "
            "Includes quick tics, jerks (chorea), slow athetosis, and dystonia. "
            "Note: spasmodic dysphonia and organic voice tremor account for ~70% of hyperkinetic cases."
        ),
        "aetiologies": [
            "Huntington's disease",
            "Cerebral palsy (choreoathetoid type)",
            "Drug-induced (neuroleptics / tardive dyskinesia)",
            "Tourette's syndrome",
            "Isolated dysphonia (spasmodic dysphonia, organic voice tremor)",
        ],
        "salient_features": [
            "Dyskinesias: abnormal, irregular, fast or slow involuntary movements",
            "Movements may occur at rest or during voluntary movement",
            "May affect face, extremities, or whole body",
            "Chorea: quick, jerky movements",
            "Athetosis: slow, writhing movements",
            "Dystonia: sustained abnormal posturing",
        ],
        "perceptual_features": [
            "Distorted vowels",
            "Harsh voice quality",
            "Excess loudness variations",
            "Irregular articulatory breakdowns",
            "Prolonged phonemes",
            "Variable rate",
            "Stress alterations",
            "Audible inspiration",
        ],
        "also_known_as": "Choreoathetoid / dystonic dysarthria",
        "assessment_notes": (
            "Observe for involuntary movements during assessment and at rest. "
            "Contextual speech will show high variability. Distinguish from ataxic (intention-related) vs "
            "hyperkinetic (involuntary, unpredictable). Spasmodic dysphonia = adductor type (strained) or "
            "abductor type (breathy)."
        ),
        "intervention": {
            "Impairment-based": [
                "Rate reduction and breath control exercises",
                "Articulatory precision drills (when voluntary speech possible)",
                "Medical: Botox injection for spasmodic dysphonia / focal dystonia",
            ],
            "Compensatory": [
                "AAC when involuntary movements severely impact speech",
                "Communication strategies",
                "Environmental modifications (reduce distraction, maximise predictability)",
            ],
        },
        "references": ["Duffy, J.R. (2013). Motor Speech Disorders. Chapter 10."],
    },
    "Mixed": {
        "locus": "More than one neurological site",
        "primary_deficit": "Combination of deficits from ≥2 types",
        "description": (
            "Neurological disease frequently affects multiple CNS/PNS areas simultaneously. "
            "Mixed dysarthria is a combination of two or more dysarthria types. "
            "Most common: flaccid-spastic (42%), ataxic-spastic (23%), hypokinetic-spastic (7%)."
        ),
        "aetiologies": [
            "ALS (amyotrophic lateral sclerosis) → flaccid-spastic (LMN + UMN)",
            "Multiple sclerosis → spastic-ataxic",
            "Multiple System Atrophy → hypokinetic/hyperkinetic/ataxic/spastic",
            "Progressive Supranuclear Palsy → hypokinetic/spastic/ataxic",
            "Friedreich's Ataxia → ataxic or ataxic-spastic",
            "Multiple strokes",
            "Brainstem stroke → spastic/ataxic/flaccid mix",
            "Wilson's disease → hypokinetic/spastic/ataxic",
            "TBI / tumour",
        ],
        "salient_features": [
            "Features of multiple dysarthria types present simultaneously",
            "Common pairings: flaccid-spastic, ataxic-spastic, hypokinetic-spastic",
            "Progressive conditions: plan AAC early",
        ],
        "perceptual_features": [
            "Variable — combination of features from constituent types",
        ],
        "also_known_as": "e.g. flaccid-spastic (ALS), ataxic-spastic (MS)",
        "assessment_notes": (
            "Identify which component types are present by systematically mapping perceptual features. "
            "ALS: look for both flaccid (breathiness, hypernasality) and spastic (strained quality, slow rate) features. "
            "For progressive conditions, establish baseline early and plan AAC proactively."
        ),
        "intervention": {
            "Impairment-based": [
                "Target the dominant deficit first",
                "Combine approaches matching each component type",
                "For ALS: early LSVT or breath support + AAC planning simultaneously",
            ],
            "Compensatory": [
                "AAC planning should begin EARLY in progressive conditions (ALS, Huntington's)",
                "Anticipate trajectory and plan ahead — introduce AAC before speech fails",
                "Multimodal communication for as long as possible",
            ],
        },
        "references": ["Duffy, J.R. (2013). Motor Speech Disorders. Chapters 11–12."],
    },
    "AOS": {
        "locus": "Cortical speech planning/programming (left fronto-parietal / perisylvian area)",
        "primary_deficit": "Impaired motor speech planning / programming",
        "description": (
            "A neurologic speech disorder reflecting an impaired capacity to plan or program sensorimotor "
            "commands for speech. The neuromuscular apparatus is INTACT (no weakness). "
            "Oral mechanism exam may be normal. Often co-occurs with aphasia. "
            "(Duffy, 2005)"
        ),
        "aetiologies": [
            "Stroke (most common)",
            "Tumour",
            "Trauma",
            "Degenerative disease (rare)",
        ],
        "salient_features": [
            "Impairment in purposeful, voluntary movements",
            "Automatic movements often preserved (e.g. overlearnt phrases intact)",
            "No weakness of oral musculature",
            "Trial and error groping for target sounds",
            "Inconsistent errors on the same target",
            "Increased difficulty with increased phonemic complexity",
            "Sequencing errors",
            "Dabul (1986): 15 diagnostic behaviours",
        ],
        "perceptual_features": [
            "Inconsistent errors",
            "Errors increase with complexity",
            "Sequencing errors",
            "Trial and error groping",
            "Abnormal prosody (AOS)",
            "Intrusion of schwa between syllables",
            "Perseverative phonemic errors",
        ],
        "also_known_as": "Dyspraxia / verbal dyspraxia / acquired AOS",
        "assessment_notes": (
            "Key test: words of increasing length — cat → catnip → catapult → catastrophe. "
            "Use Dabul's 15 diagnostic behaviours (1986). Assess spontaneous vs volitional speech — "
            "automatic speech often better. Distinguish from aphasia (language problem) and dysarthria "
            "(neuromuscular execution). Oral mechanism may be normal."
        ),
        "intervention": {
            "Impairment-based": [
                "Rosenbek 8-step continuum (integral stimulation → gradual withdrawal of cues)",
                "Sound Production Treatment (SPT): Wambaugh et al.",
                "Articulatory kinematic approach (Rosenbek)",
                "Drilling and repetition",
                "Phonetic placement cues and visual feedback (mirror)",
                "Sentence completion tasks (spontaneous > volitional)",
            ],
            "Compensatory": [
                "Pacing strategies",
                "Alphabet/word board to support communication",
                "AAC to supplement voluntary speech",
                "Carer/family education",
            ],
        },
        "references": [
            "Duffy, J.R. (2013). Motor Speech Disorders. Chapters 11 & 13.",
            "Dabul, B. (1986). Apraxia Battery for Adults.",
        ],
    },
}

# ── Perceptual features → dysarthria type mapping ──────────────────────────
FEATURE_TYPE_MAP = {
    # Phonation
    "Breathiness":                  ["Flaccid", "Hypokinetic"],
    "Hoarseness":                   ["Flaccid"],
    "Strained-strangled quality":   ["Spastic"],
    "Harsh voice quality":          ["Spastic", "Ataxic", "Hypokinetic", "Hyperkinetic"],
    "Monopitch":                    ["Flaccid", "Hypokinetic", "Ataxic"],
    "Pitch breaks":                 ["Spastic"],
    "Low pitch":                    ["Hypokinetic"],
    # Resonance
    "Hypernasality":                ["Flaccid"],
    "Nasal emission":               ["Flaccid"],
    # Articulation
    "Imprecise consonants":         ["Flaccid", "Spastic", "Unilateral UMN", "Ataxic", "Hypokinetic"],
    "Distorted vowels":             ["Spastic", "Ataxic", "Hyperkinetic"],
    "Irregular articulatory breakdown": ["Ataxic", "Hyperkinetic"],
    "Dysdiadochokinesis":           ["Unilateral UMN"],
    # Prosody / rate
    "Slow rate":                    ["Spastic", "Unilateral UMN", "Ataxic"],
    "Short rushes of speech":       ["Hypokinetic"],
    "Variable rate":                ["Hypokinetic", "Hyperkinetic"],
    "Excess and equal stress":      ["Spastic", "Ataxic"],
    "Reduced stress":               ["Hypokinetic"],
    "Stress alterations":           ["Hyperkinetic"],
    "Inappropriate silences":       ["Hypokinetic"],
    "Prolonged phonemes":           ["Ataxic", "Hyperkinetic"],
    "Prolonged intervals":          ["Ataxic"],
    # Volume / respiratory
    "Monoloudness":                 ["Hypokinetic"],
    "Excess loudness variations":   ["Ataxic", "Hyperkinetic"],
    "Quiet voice (hypophonia)":     ["Hypokinetic"],
    "Short phrases":                ["Flaccid"],
    "Audible inspiration":          ["Hyperkinetic"],
    # AOS
    "Inconsistent errors":          ["AOS"],
    "Errors increase with complexity": ["AOS"],
    "Sequencing errors":            ["AOS"],
    "Trial and error groping":      ["AOS"],
    "Abnormal prosody (AOS)":       ["AOS"],
    "Intrusion of schwa":           ["AOS"],
    "Perseverative errors":         ["AOS"],
}

DIMENSIONS = {
    "Phonation": {
        "description": "Quality and characteristics of voice produced by the larynx.",
        "types": ["Flaccid", "Spastic", "Hypokinetic", "Hyperkinetic"],
        "significance": (
            "Voice quality is a key differentiator: breathiness → flaccid; "
            "strained-strangled → spastic; harsh → spastic/ataxic/hypokinetic; "
            "monopitch → flaccid/hypokinetic."
        ),
        "features": [
            "Breathiness", "Hoarseness", "Strained-strangled quality",
            "Harsh voice quality", "Monopitch", "Pitch breaks", "Low pitch",
        ],
    },
    "Resonance": {
        "description": "Nasal vs oral balance of vocal tract resonance (velopharyngeal function).",
        "types": ["Flaccid"],
        "significance": (
            "Hypernasality and nasal emission are hallmarks of flaccid dysarthria "
            "due to velopharyngeal incompetence from LMN weakness of the soft palate."
        ),
        "features": ["Hypernasality", "Nasal emission"],
    },
    "Articulation": {
        "description": "Precision and accuracy of consonant and vowel production.",
        "types": ["Flaccid", "Spastic", "Unilateral UMN", "Ataxic", "Hypokinetic", "Hyperkinetic"],
        "significance": (
            "Imprecise consonants span most types — specificity lies in clustering with other features. "
            "Distorted vowels → spastic/ataxic/hyperkinetic. Irregular breakdown → ataxic/hyperkinetic."
        ),
        "features": [
            "Imprecise consonants", "Distorted vowels",
            "Irregular articulatory breakdown", "Dysdiadochokinesis",
        ],
    },
    "Prosody": {
        "description": "Rate, rhythm, stress, and intonation patterns of speech.",
        "types": ["Spastic", "Ataxic", "Hypokinetic", "Hyperkinetic"],
        "significance": (
            "Prosodic features are among the most discriminating: excess & equal stress → spastic/ataxic; "
            "reduced stress + monoloudness → hypokinetic; variable rate → hypokinetic/hyperkinetic; "
            "slow rate → spastic/ataxic."
        ),
        "features": [
            "Slow rate", "Short rushes of speech", "Variable rate",
            "Excess and equal stress", "Reduced stress", "Stress alterations",
            "Inappropriate silences", "Prolonged phonemes", "Prolonged intervals",
        ],
    },
    "Volume & Respiration": {
        "description": "Loudness level and breath support underlying speech.",
        "types": ["Flaccid", "Hypokinetic", "Ataxic", "Hyperkinetic"],
        "significance": (
            "Monoloudness + quiet voice → hypokinetic (LSVT is evidence-based). "
            "Short phrases → flaccid (poor breath support). "
            "Excess loudness variations → ataxic/hyperkinetic."
        ),
        "features": [
            "Monoloudness", "Excess loudness variations",
            "Quiet voice (hypophonia)", "Short phrases", "Audible inspiration",
        ],
    },
    "Motor Planning (AOS)": {
        "description": "Cortical-level planning and programming of speech movements.",
        "types": ["AOS"],
        "significance": (
            "AOS is distinguished from dysarthria by inconsistent, complexity-dependent errors "
            "with an intact oral mechanism. Critical differential diagnosis — "
            "management is fundamentally different."
        ),
        "features": [
            "Inconsistent errors", "Errors increase with complexity", "Sequencing errors",
            "Trial and error groping", "Abnormal prosody (AOS)",
            "Intrusion of schwa", "Perseverative errors",
        ],
    },
}

CLINICAL_ACTIONS = {
    "Differential diagnosis — perceptual assessment": [
        "Observe and describe voice quality, articulation, prosody, rate, resonance systematically (Darley, Aronson & Brown, 1969).",
        "Oro-motor exam: assess appearance and movement of jaw, lips, tongue, soft palate.",
        "Vowel prolongation: assess maximum phonation time (norms: male 20–28s, female 15–22s).",
        "AMRs /pəpəpə/: norm ~6 syllables/second — slow suggests spastic/ataxic; irregular → ataxic.",
        "SMRs /pətəkə/: norm ~5/second — assess sequencing ability and consistency.",
        "Contextual speech: connected speech sample + reading passage (e.g. Caterpillar passage, Patel et al., 2013).",
        "Distinguish dysarthria from AOS: test with cat → catnip → catapult → catastrophe.",
    ],
    "Formal assessment tools": [
        "Frenchay Dysarthria Assessment (Enderby & Palmer, 2007): reflexes, respiration, lips, palate, laryngeal, tongue, intelligibility.",
        "Assessment of Intelligibility of Dysarthric Speakers (Yorkston & Beukelman, 1981).",
        "Sentence Intelligibility Test (SIT) (Yorkston & Beukelman, 1996).",
        "Robertson Dysarthria Profile (Robertson, 1982).",
        "Apraxia Battery for Adults (ABA-2, 2000): for AOS — diadochokinetic rate, increasing word length, limb/oral apraxia.",
        "ICF framework: assess body function AND activity limitation AND participation restriction.",
    ],
    "Impairment-based intervention": [
        "Respiratory: diaphragmatic breathing, breath control, maximum vowel prolongation.",
        "Phonation: effortful closure (weakness), easy onset/yawn-sigh (hyperadduction), LSVT LOUD (hypokinetic — Ramig et al., 2001).",
        "Resonance: CPAP resistance training, biofeedback (mirror, nasal-flow transducer, nasoendoscope).",
        "Articulation: integral stimulation, phonetic placement, phoneme/syllable/word drills.",
        "Prosody: contrastive stress tasks, rate modification, rhythmic cueing, pacing board.",
        "AOS: Rosenbek 8-step continuum, Sound Production Treatment (SPT), articulatory kinematic approach.",
    ],
    "Compensatory management": [
        "Environmental changes: reduce background noise, improve lighting.",
        "Prosthetic: portable voice amplifier (phonation), palatal lift prosthesis (velopharyngeal dysfunction).",
        "Listener strategies: maintain eye contact, seek clarification, give time, familiarisation.",
        "Overarticulation and deeper inhalation as compensatory speaking strategies.",
        "NSOMExs (non-speech oro-motor exercises) — evidence limited; Mackenzie et al. (2010, 2014).",
    ],
    "AAC planning": [
        "Assess residual speech to determine AAC need.",
        "For progressive conditions (ALS, Huntington's): introduce AAC EARLY, before speech fails.",
        "Low-tech: alphabet boards, word/symbol communication charts.",
        "High-tech: speech-generating devices (SGDs), eye-tracking systems, partner-assisted scanning.",
        "Maintain multimodal communication for as long as possible.",
        "Involve AAC specialist and MDT early in management.",
    ],
    "MDT / specialist referral": [
        "Refer to neurologist if aetiology is unclear or diagnosis uncertain.",
        "MDT involvement: physiotherapy, OT, dietetics, neurology, palliative care as appropriate.",
        "Consider laryngology referral if vocal fold pathology suspected (medialization laryngoplasty).",
        "Palliative care involvement for end-stage progressive conditions.",
        "Carer and family education and support sessions.",
    ],
    "Monitoring": [
        "Establish baseline measures (intelligibility %, rate in wpm, MPT, AMR) for comparison.",
        "For progressive conditions: monitor trajectory and adjust management proactively.",
        "Re-assess post-intervention to measure change against baseline.",
        "Use ICF-based functional communication measures — not just impairment.",
        "Review at MDT if deterioration is noted.",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

ALL_FEATURES = sorted(FEATURE_TYPE_MAP.keys())
TYPE_COLORS = {
    "Flaccid": "#4472c4",
    "Spastic": "#e74c3c",
    "Unilateral UMN": "#e67e22",
    "Ataxic": "#27ae60",
    "Hypokinetic": "#8e44ad",
    "Hyperkinetic": "#16a085",
    "Mixed": "#7f8c8d",
    "AOS": "#c0392b",
}


def run_detection(selected_features):
    """Given a list of selected features, return scored types."""
    type_counts = defaultdict(int)
    type_features = defaultdict(list)
    for feat in selected_features:
        for t in FEATURE_TYPE_MAP.get(feat, []):
            type_counts[t] += 1
            type_features[t].append(feat)

    # Score each type against its full feature list
    scored = {}
    for t, count in type_counts.items():
        total_possible = len(DYSARTHRIA_TYPES[t]["perceptual_features"])
        pct = round((count / total_possible) * 100) if total_possible else 0
        scored[t] = {"count": count, "pct": pct, "features": type_features[t]}

    return dict(sorted(scored.items(), key=lambda x: -x[1]["count"]))


def interpret_scores(scored, selected_features):
    """Generate a clinical interpretation from scored types."""
    if not scored:
        return None

    top_types = list(scored.keys())
    top_count = scored[top_types[0]]["count"]
    aos_present = "AOS" in scored and scored["AOS"]["count"] >= 3
    multi = [t for t in top_types if t != "AOS" and scored[t]["count"] >= 2]

    if aos_present and multi:
        label = "AOS with co-occurring dysarthria features"
        colour = "warning"
        msg = (
            "Features consistent with AOS are present alongside dysarthria features. "
            "AOS and dysarthria can co-occur. Careful differential diagnosis is essential — "
            "consider the Rosenbek 8-step continuum for AOS component alongside dysarthria management."
        )
        actions = ["Differential diagnosis — perceptual assessment", "Formal assessment tools",
                   "Impairment-based intervention", "MDT / specialist referral"]
    elif aos_present:
        label = "Features consistent with Apraxia of Speech (AOS)"
        colour = "error"
        msg = (
            "Multiple AOS features detected with limited dysarthria features. "
            "Distinguish from dysarthria: test with words of increasing length (cat → catastrophe). "
            "Remember: AOS = planning impairment; dysarthria = neuromuscular execution."
        )
        actions = ["Differential diagnosis — perceptual assessment", "Formal assessment tools",
                   "Impairment-based intervention"]
    elif len(multi) >= 2:
        label = f"Mixed dysarthria likely — features matching {', '.join(multi[:3])}"
        colour = "warning"
        msg = (
            f"Features span {len(multi)} dysarthria types. Consider Mixed Dysarthria. "
            f"Most common mixed types: flaccid-spastic (ALS), ataxic-spastic (MS), hypokinetic-spastic. "
            "Clarify aetiology to guide management."
        )
        actions = ["Differential diagnosis — perceptual assessment", "Formal assessment tools",
                   "Impairment-based intervention", "Compensatory management", "MDT / specialist referral"]
    elif top_types and top_count >= 2:
        top = top_types[0]
        label = f"Profile most consistent with {top} Dysarthria"
        colour = "success"
        msg = (
            f"The selected features most strongly indicate {top} Dysarthria "
            f"({scored[top]['count']} features matched). "
            f"Neurological locus: {DYSARTHRIA_TYPES[top]['locus']}."
        )
        actions = ["Differential diagnosis — perceptual assessment", "Formal assessment tools",
                   "Impairment-based intervention", "Compensatory management"]
    else:
        label = "Insufficient features for a confident profile"
        colour = "info"
        msg = (
            "Too few features have been selected to indicate a strong match. "
            "Add more observed speech characteristics, or complete a formal assessment."
        )
        actions = ["Differential diagnosis — perceptual assessment", "Formal assessment tools"]

    return dict(label=label, colour=colour, msg=msg, actions=actions, top_types=top_types[:4])


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

for k, v in {
    "selected_features": [],
    "observations_text": "",
    "client_name": "",
    "client_age": "",
    "condition": "",
    "assessment_date": str(date.today()),
    "test_used": "Frenchay Dysarthria Assessment",
    "notes": "",
    "map_dim": None,
    "map_type": None,
    "edu_type": None,
    "edu_search": "",
    "page": "input",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("Dysarthria Decision Atlas")
    st.caption("Motor Speech Disorders — Clinical Tool")
    st.divider()
    st.subheader("Case Metadata")

    with st.form("meta"):
        name_in = st.text_input("Client Name / ID", value=st.session_state.client_name,
                                placeholder="e.g. J. Smith")
        age_in  = st.text_input("Client Age", value=st.session_state.client_age,
                                placeholder="e.g. 68")
        cond_in = st.text_input("Known / Suspected Condition", value=st.session_state.condition,
                                placeholder="e.g. Parkinson's Disease")
        tests = [
            "Frenchay Dysarthria Assessment",
            "Robertson Dysarthria Profile",
            "ABA-2 (Apraxia Battery for Adults)",
            "Assessment of Intelligibility (Yorkston & Beukelman)",
            "SIT",
            "Clinical observation",
            "Other",
        ]
        tidx = tests.index(st.session_state.test_used) if st.session_state.test_used in tests else 0
        test_in = st.selectbox("Assessment Used", tests, index=tidx)
        notes_in = st.text_area("Clinician Notes", value=st.session_state.notes,
                                height=80, placeholder="Optional...")
        if st.form_submit_button("Update", type="primary", use_container_width=True):
            st.session_state.client_name   = name_in
            st.session_state.client_age    = age_in
            st.session_state.condition     = cond_in
            st.session_state.test_used     = test_in
            st.session_state.notes         = notes_in
            st.rerun()

    st.divider()
    if st.button("🏠  New Case", use_container_width=True, type="primary"):
        for k in ["selected_features", "observations_text", "client_name", "client_age",
                  "condition", "notes", "map_dim", "map_type", "edu_type", "edu_search"]:
            st.session_state[k] = [] if k == "selected_features" else ""
        st.session_state.page = "input"
        st.rerun()

    if st.button("Clear Features", use_container_width=True):
        st.session_state.selected_features = []
        st.session_state.page = "input"
        st.rerun()

    st.caption(f"Session: {date.today().strftime('%d %b %Y')}")

    st.divider()
    with st.expander("📖 Type Quick Reference"):
        ref_type = st.selectbox("Dysarthria Type", list(DYSARTHRIA_TYPES.keys()), key="sidebar_ref")
        rt = DYSARTHRIA_TYPES[ref_type]
        st.markdown(f"**Locus:** {rt['locus']}")
        st.markdown(f"**Primary deficit:** {rt['primary_deficit']}")
        st.markdown(f"**Also known as:** {rt.get('also_known_as', '—')}")
        st.markdown("**Key perceptual features:**")
        for f in rt["perceptual_features"][:5]:
            st.write(f"- {f}")

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

sel = st.session_state.selected_features
if sel:
    scored = run_detection(sel)
    interp = interpret_scores(scored, sel)
else:
    scored = {}
    interp = None

active_types = set(scored.keys()) if scored else set()

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════

st.title("Dysarthria Decision Atlas")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Client", st.session_state.client_name or "—")
c2.metric("Age", st.session_state.client_age or "—")
c3.metric("Condition", st.session_state.condition or "—")
c4.metric("Features Selected", len(sel))
if st.session_state.notes:
    st.info(f"**Notes:** {st.session_state.notes}")

# ═══════════════════════════════════════════════════════════════════════════════
# NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

_PAGE_LABELS = ["Input & Observations", "Analysis & Reasoning",
                "System Map", "Educational Exploration", "Export"]
_PAGE_KEYS   = ["input", "analysis", "map", "edu", "export"]

_nav_cols = st.columns(5)
for _i, (_label, _key) in enumerate(zip(_PAGE_LABELS, _PAGE_KEYS)):
    with _nav_cols[_i]:
        if st.button(_label, key=f"nav_{_key}", use_container_width=True):
            st.session_state.page = _key
            st.rerun()
st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — INPUT & OBSERVATIONS
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "input":
    st.subheader("Select Observed Speech Features")
    st.caption(
        "Click the feature buttons to toggle them on or off. "
        "Grey = not observed · Green = observed. Analysis updates automatically."
    )

    for dim_name, dim_info in DIMENSIONS.items():
        # Shelf header
        st.markdown(f'<div class="shelf-header">{dim_name}</div>', unsafe_allow_html=True)
        n_cols = min(len(dim_info["features"]), 4)
        cols = st.columns(n_cols)
        for i, feat in enumerate(dim_info["features"]):
            with cols[i % n_cols]:
                if st.button(feat, key=f"feat_{feat}", use_container_width=True):
                    if feat in st.session_state.selected_features:
                        st.session_state.selected_features.remove(feat)
                    else:
                        st.session_state.selected_features.append(feat)
                    st.rerun()

    st.divider()
    st.subheader("Additional Observations")
    obs_txt = st.text_area(
        "Free-text observations (contextual speech, AMRs, oro-motor findings, etc.)",
        value=st.session_state.observations_text,
        height=120,
        placeholder="e.g. AMRs: slow and irregular at ~4/s. Tongue deviation to left on protrusion. "
                    "MPT: 8 seconds. Reading passage: marked excess and equal stress on all syllables.",
        label_visibility="visible",
    )
    if obs_txt != st.session_state.observations_text:
        st.session_state.observations_text = obs_txt

    st.divider()
    st.subheader("Selected Features Summary")
    if sel:
        cols_pg = st.columns(min(len(sel), 4))
        for i, feat in enumerate(sel):
            types_for_feat = FEATURE_TYPE_MAP.get(feat, [])
            type_str = " / ".join(types_for_feat)
            cols_pg[i % len(cols_pg)].markdown(
                f"<div class='dim-card'><strong>{feat}</strong><br>"
                f"<span style='font-size:0.82em;color:#555'>{type_str}</span></div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No features selected yet. Click the buttons above to record your observations.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — ANALYSIS & REASONING
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "analysis":
    if not sel:
        st.info("Add observations in **Input & Observations** to see analysis here.")
    else:
        # ── Type Scores ───────────────────────────────────────────────────────
        st.subheader("Dysarthria Type Profile Match")
        if not scored:
            st.warning("No type matches detected. Try selecting more specific features.")
        else:
            for dtype, data in scored.items():
                dt_info = DYSARTHRIA_TYPES.get(dtype, {})
                badge_color = TYPE_COLORS.get(dtype, "#888")
                with st.expander(
                    f"**{dtype}** — {data['count']} feature(s) matched — {data['pct']}% of type's profile"
                ):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Locus:** {dt_info.get('locus', '')}")
                        st.markdown(f"**Primary deficit:** {dt_info.get('primary_deficit', '')}")
                        st.markdown(f"**Description:** {dt_info.get('description', '')}")
                        st.markdown(f"**Assessment note:** {dt_info.get('assessment_notes', '')}")
                    with col_b:
                        st.markdown("**Your matched features:**")
                        for f in data["features"]:
                            st.write(f"✓ {f}")
                        remaining = [
                            f for f in dt_info.get("perceptual_features", [])
                            if f not in data["features"]
                        ]
                        if remaining:
                            st.markdown("**Unmatched features for this type:**")
                            for f in remaining:
                                st.caption(f"○ {f}")

        st.divider()

        # ── Dimensions Affected ───────────────────────────────────────────────
        st.subheader("Subsystems Affected")
        dims_hit = set()
        for feat in sel:
            for dim_name, dim_info in DIMENSIONS.items():
                if feat in dim_info["features"]:
                    dims_hit.add(dim_name)

        if dims_hit:
            dcols = st.columns(min(len(dims_hit), 3))
            for i, dim in enumerate(dims_hit):
                with dcols[i % 3]:
                    dim_info = DIMENSIONS[dim]
                    st.markdown(
                        f"<div class='dim-card'><div class='step-label'>{dim}</div>"
                        f"<div style='font-size:0.85em;margin-top:4px'>{dim_info['description']}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        st.divider()

        # ── Reasoning Pathway ─────────────────────────────────────────────────
        st.subheader("Reasoning Pathway")

        st.markdown(
            f"""<div class="step-card">
            <div class="step-label">Step 1 — Observation</div>
            {len(sel)} perceptual feature(s) selected: {', '.join(sel[:6])}{'...' if len(sel) > 6 else ''}
            </div>""",
            unsafe_allow_html=True,
        )

        if scored:
            top_summary = "; ".join(
                f"{t} ({d['count']})" for t, d in list(scored.items())[:4]
            )
            st.markdown(
                f"""<div class="step-card">
                <div class="step-label">Step 2 — Type Matching</div>
                Feature-to-type mapping: {top_summary}
                </div>""",
                unsafe_allow_html=True,
            )

            dims_str = ", ".join(dims_hit) if dims_hit else "None identified"
            st.markdown(
                f"""<div class="step-card">
                <div class="step-label">Step 3 — Subsystems Affected</div>
                {dims_str}
                </div>""",
                unsafe_allow_html=True,
            )

            if interp and interp.get("top_types"):
                top = interp["top_types"][0]
                locus = DYSARTHRIA_TYPES.get(top, {}).get("locus", "unknown")
                st.markdown(
                    f"""<div class="step-card">
                    <div class="step-label">Step 4 — Neurological Interpretation</div>
                    Strongest match: <strong>{top}</strong> — Locus: {locus}
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.divider()

        # ── System-Level Interpretation ───────────────────────────────────────
        st.subheader("Clinical Interpretation")
        if interp:
            body = f"**{interp['label']}**\n\n{interp['msg']}"
            col = interp["colour"]
            if col == "error":
                st.error(body)
            elif col == "warning":
                st.warning(body)
            elif col == "success":
                st.success(body)
            else:
                st.info(body)
            st.caption(
                "These are clinical suggestions based on perceptual features, not a diagnosis. "
                "Professional clinical judgement and formal assessment are always required."
            )

        st.divider()

        # ── Clinical Next Steps ────────────────────────────────────────────────
        st.subheader("Possible Next Steps")
        if interp:
            for action in interp.get("actions", []):
                with st.expander(f"**{action}**"):
                    for step in CLINICAL_ACTIONS.get(action, []):
                        st.write(f"- {step}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — SYSTEM MAP
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "map":
    st.subheader("Neurological System Map")
    st.caption("Click a dimension to explore. Types matched in the current session are highlighted.")

    if active_types:
        st.markdown(f"**Active type matches:** {', '.join(sorted(active_types))}")

    dim_names = list(DIMENSIONS.keys())
    dim_cols = st.columns(len(dim_names))
    for i, dim in enumerate(dim_names):
        dim_info = DIMENSIONS[dim]
        dim_active = any(t in active_types for t in dim_info["types"])
        label = f"{'🔴 ' if dim_active else ''}{dim}"
        with dim_cols[i]:
            if st.button(label, key=f"map_{dim}", use_container_width=True):
                st.session_state.map_dim = None if st.session_state.map_dim == dim else dim
                st.session_state.map_type = None
                st.rerun()

    if st.session_state.map_dim:
        dim = st.session_state.map_dim
        dinfo = DIMENSIONS[dim]
        st.divider()
        st.markdown(f"### {dim}")
        st.write(dinfo["description"])
        st.info(f"**Clinical significance:** {dinfo['significance']}")
        st.markdown("**Dysarthria types associated with this dimension:**")

        type_cols = st.columns(min(len(dinfo["types"]), 4))
        for j, tname in enumerate(dinfo["types"]):
            is_active = tname in active_types
            cnt = scored.get(tname, {}).get("count", 0)
            btn_label = f"{tname}{f' ✓ ({cnt})' if is_active else ''}"
            with type_cols[j % 4]:
                if st.button(
                    btn_label, key=f"mtype_{tname}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.map_type = None if st.session_state.map_type == tname else tname
                    st.rerun()

        if st.session_state.map_type and st.session_state.map_type in dinfo["types"]:
            tname = st.session_state.map_type
            tdata = DYSARTHRIA_TYPES.get(tname, {})
            st.divider()
            st.markdown(f"#### {tname} Dysarthria")
            pa, pb = st.columns(2)
            with pa:
                st.markdown(f"**Locus:** {tdata.get('locus', '')}")
                st.markdown(f"**Primary deficit:** {tdata.get('primary_deficit', '')}")
                st.markdown(f"**Description:** {tdata.get('description', '')}")
                st.markdown(f"**Assessment note:** {tdata.get('assessment_notes', '')}")
                st.markdown("**Intervention (impairment-based):**")
                for t in tdata.get("intervention", {}).get("Impairment-based", [])[:3]:
                    st.write(f"- {t}")
            with pb:
                st.markdown("**Aetiologies:**")
                for a in tdata.get("aetiologies", [])[:5]:
                    st.write(f"- {a}")
                st.markdown("**All perceptual features:**")
                for f in tdata.get("perceptual_features", []):
                    matched = f in sel
                    icon = "✓" if matched else "○"
                    st.write(f"{icon} {f}")
                if tname in active_types:
                    st.success(f"**Matched in current session** — {scored[tname]['count']} feature(s)")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — EDUCATIONAL EXPLORATION
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "edu":
    st.subheader("Educational Exploration Mode")
    st.markdown(
        "Explore dysarthria types and perceptual features. "
        "Search by feature name, condition, aetiology, or intervention approach."
    )

    search_q = st.text_input(
        "Search",
        placeholder="e.g. Parkinson's, breathiness, LSVT, strained, ALS, basal ganglia, inconsistent...",
        label_visibility="collapsed",
    )

    def build_search_corpus(tname, tdata):
        parts = [
            tname,
            tdata.get("description", ""),
            tdata.get("locus", ""),
            tdata.get("primary_deficit", ""),
            tdata.get("also_known_as", ""),
            tdata.get("assessment_notes", ""),
            " ".join(tdata.get("aetiologies", [])),
            " ".join(tdata.get("salient_features", [])),
            " ".join(tdata.get("perceptual_features", [])),
            " ".join(tdata.get("intervention", {}).get("Impairment-based", [])),
            " ".join(tdata.get("intervention", {}).get("Compensatory", [])),
            " ".join(tdata.get("references", [])),
        ]
        return " ".join(parts).lower()

    def render_type_panel(tname):
        tdata = DYSARTHRIA_TYPES.get(tname, {})
        st.markdown(f"## {tname} Dysarthria")
        st.markdown(f"*Locus: {tdata.get('locus', '')}*")
        st.divider()
        st.markdown(f"**Description:** {tdata.get('description', '')}")
        st.markdown(f"**Also known as:** {tdata.get('also_known_as', '—')}")

        st.markdown("**Aetiologies:**")
        for a in tdata.get("aetiologies", []):
            st.write(f"- {a}")

        st.markdown("**Salient (clinical) features:**")
        for s in tdata.get("salient_features", []):
            st.write(f"- {s}")

        st.markdown("**Perceptual speech features:**")
        df_feat = pd.DataFrame({"Feature": tdata.get("perceptual_features", [])})
        st.table(df_feat)

        st.markdown("**Assessment notes:**")
        st.info(tdata.get("assessment_notes", ""))

        st.markdown("**Intervention — Impairment-based:**")
        for t in tdata.get("intervention", {}).get("Impairment-based", []):
            st.write(f"- {t}")

        st.markdown("**Intervention — Compensatory:**")
        for t in tdata.get("intervention", {}).get("Compensatory", []):
            st.write(f"- {t}")

        if tdata.get("references"):
            st.markdown("**References:**")
            for r in tdata["references"]:
                st.caption(r)

        if tname in active_types and scored:
            st.success(f"**Active in current session** — {scored[tname]['count']} feature(s) matched")

    if search_q.strip():
        q = search_q.strip().lower()
        matches = [
            tname for tname, tdata in DYSARTHRIA_TYPES.items()
            if q in build_search_corpus(tname, tdata)
        ]

        col_l, col_r = st.columns([1, 2])
        with col_l:
            if matches:
                st.markdown(f"**{len(matches)} match(es)**")
                for m in matches:
                    is_active = m in active_types
                    btn_label = f"{m}{'  ✓' if is_active else ''}"
                    if st.button(btn_label, key=f"search_{m}",
                                 type="primary" if is_active else "secondary",
                                 use_container_width=True):
                        st.session_state.edu_type = m
                        st.session_state.edu_search = search_q
                        st.rerun()
            else:
                st.warning("No matches found.")
        with col_r:
            if st.session_state.edu_type and st.session_state.edu_type in DYSARTHRIA_TYPES:
                render_type_panel(st.session_state.edu_type)

    else:
        col_l, col_r = st.columns([1, 2])
        with col_l:
            st.markdown("**Dysarthria types:**")
            for tname in DYSARTHRIA_TYPES.keys():
                is_active = tname in active_types
                btn_label = f"{tname}{'  ✓' if is_active else ''}"
                if st.button(btn_label, key=f"edu_{tname}",
                             type="primary" if is_active else "secondary",
                             use_container_width=True):
                    st.session_state.edu_type = None if st.session_state.edu_type == tname else tname
                    st.rerun()
        with col_r:
            if st.session_state.edu_type and st.session_state.edu_type in DYSARTHRIA_TYPES:
                render_type_panel(st.session_state.edu_type)
            else:
                st.info("Select a dysarthria type on the left to explore its features, "
                        "aetiologies, assessment, and intervention.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — EXPORT
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "export":
    st.subheader("Session Summary — Export")
    st.caption("Review and copy the summary below for your clinical records.")

    lines = [
        f"# Dysarthria Decision Atlas — Session Summary",
        f"**Date:** {date.today().strftime('%d %B %Y')}",
        f"**Client:** {st.session_state.client_name or '—'}  |  "
        f"**Age:** {st.session_state.client_age or '—'}  |  "
        f"**Condition:** {st.session_state.condition or '—'}",
        f"**Assessment used:** {st.session_state.test_used}",
        "",
    ]

    if st.session_state.notes:
        lines += [f"**Clinician notes:** {st.session_state.notes}", ""]

    if sel:
        lines += ["## Observed Perceptual Features", ""]
        for feat in sel:
            types_for_feat = " / ".join(FEATURE_TYPE_MAP.get(feat, []))
            lines.append(f"- {feat}  →  *{types_for_feat}*")
        lines.append("")

    if st.session_state.observations_text:
        lines += ["## Additional Observations", st.session_state.observations_text, ""]

    if scored:
        lines += ["## Type Profile Match", ""]
        for dtype, data in scored.items():
            lines.append(
                f"- **{dtype}**: {data['count']} feature(s) matched ({data['pct']}% of type's profile)"
            )
            lines.append(f"  - Matched features: {', '.join(data['features'])}")
        lines.append("")

    if interp:
        lines += [
            "## Clinical Interpretation",
            f"**{interp['label']}**",
            interp["msg"],
            "",
            "## Recommended Next Steps",
        ]
        for action in interp.get("actions", []):
            lines.append(f"- {action}")
        lines.append("")

    lines += [
        "---",
        "*Generated by Dysarthria Decision Atlas. These suggestions are not a diagnosis. "
        "Clinical judgement and formal assessment are always required.*",
        "*Primary reference: Duffy, J.R. (2013). Motor Speech Disorders: Substrates, "
        "Differential Diagnosis and Management. Elsevier.*",
    ]

    summary_text = "\n".join(lines)
    st.markdown(summary_text)
    st.divider()

    # ── Export buttons ────────────────────────────────────────────────────────
    ex1, ex2, ex3 = st.columns(3)

    with ex1:
        st.download_button(
            "⬇  Download (.txt)",
            data=summary_text,
            file_name=f"Dysarthria_Atlas_{date.today().isoformat()}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with ex2:
        # Build a clean HTML page for PDF via print dialog
        def _to_html_body(raw):
            parts = []
            for ln in raw.replace("**", "").replace("*", "").split("\n"):
                if ln.startswith("# "):
                    parts.append(f"<h1>{ln[2:]}</h1>")
                elif ln.startswith("## "):
                    parts.append(f"<h2>{ln[3:]}</h2>")
                elif ln.startswith("---"):
                    parts.append("<hr>")
                elif ln.strip():
                    parts.append(f"<p>{ln}</p>")
            return "\n".join(parts)

        _today_str = date.today().strftime('%d %b %Y')
        _body_html = _to_html_body(summary_text)
        html_content = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>Dysarthria Decision Atlas — {_today_str}</title>"
            "<style>"
            "body{font-family:Arial,sans-serif;font-size:13px;margin:40px;color:#1a1a1a}"
            "h1{font-size:20px;color:#1e2d42;border-bottom:2px solid #4472c4;padding-bottom:6px}"
            "h2{font-size:15px;color:#2c3e50;margin-top:20px}"
            "p,li{line-height:1.6}"
            "hr{border:none;border-top:1px solid #ccc;margin:16px 0}"
            "</style></head><body>"
            + _body_html +
            "</body></html>"
        )
        st.download_button(
            "⬇  Download (.html → print as PDF)",
            data=html_content,
            file_name=f"Dysarthria_Atlas_{date.today().isoformat()}.html",
            mime="text/html",
            use_container_width=True,
        )

    with ex3:
        import streamlit.components.v1 as _exp_comp
        _exp_comp.html("""
<style>
  .print-btn {
    width: 100%; padding: 0.45rem 1rem;
    background-color: #1e2d42; color: white;
    border: none; border-radius: 6px;
    font-size: 14px; font-weight: 600;
    cursor: pointer; transition: background 0.15s;
  }
  .print-btn:hover { background-color: #2c3e57; }
</style>
<button class="print-btn" onclick="window.parent.print()">🖨  Print page</button>
""", height=45)

# ═══════════════════════════════════════════════════════════════════════════════
# JS INJECTION — colour nav & feature buttons after every render
# ═══════════════════════════════════════════════════════════════════════════════
import json as _json
import streamlit.components.v1 as _components

_active_label = _PAGE_LABELS[_PAGE_KEYS.index(st.session_state.page)]
_selected_json = _json.dumps(st.session_state.selected_features)
_nav_labels_json = _json.dumps(_PAGE_LABELS)
_active_types_json = _json.dumps(list(active_types))

_components.html(f"""
<script>
(function() {{
    const selected = {_selected_json};
    const navLabels = {_nav_labels_json};
    const activeLabel = {_json.dumps(_active_label)};
    const activeTypes = {_active_types_json};

    function applyStyles() {{
        const doc = window.parent.document;
        doc.querySelectorAll('button').forEach(function(btn) {{
            const text = btn.innerText.trim();
            // Reset custom attributes first
            btn.removeAttribute('data-selected');
            btn.removeAttribute('data-nav-active');
            // Apply
            if (selected.includes(text)) {{
                btn.setAttribute('data-selected', 'true');
            }}
            if (text === activeLabel && navLabels.includes(text)) {{
                btn.setAttribute('data-nav-active', 'true');
            }}
            if (activeTypes.includes(text) && !navLabels.includes(text) && !selected.includes(text)) {{
                btn.setAttribute('data-map-active', 'true');
            }} else {{
                btn.removeAttribute('data-map-active');
            }}
        }});
    }}

    // Run immediately and after short delays to catch late renders
    applyStyles();
    setTimeout(applyStyles, 80);
    setTimeout(applyStyles, 300);

    // Watch for DOM changes (Streamlit rerenders)
    const obs = new MutationObserver(function() {{
        setTimeout(applyStyles, 50);
    }});
    obs.observe(window.parent.document.body, {{ childList: true, subtree: true }});
}})();
</script>
""", height=0)
