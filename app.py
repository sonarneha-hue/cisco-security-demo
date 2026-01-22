import streamlit as st
import pandas as pd

# --- Imports ---
import streamlit as st


BANK_ARCHETYPES = {
    "PSU Large Bank": {
        "Regulatory Pressure": 5,
        "Data Sovereignty": 5,
        "Legacy Footprint": 4,
        "Cloud Maturity": 2
    },
    "Private Large Bank": {
        "Regulatory Pressure": 4,
        "Data Sovereignty": 3,
        "Legacy Footprint": 2,
        "Cloud Maturity": 4
    },
    "Central Bank / Regulator": {
        "Regulatory Pressure": 5,
        "Data Sovereignty": 5,
        "Legacy Footprint": 5,
        "Cloud Maturity": 1
    }
}

BANK_ARCHETYPE_HINTS = {
    "State Bank of India": "PSU Large Bank",
    "SBI": "PSU Large Bank",
    "Bank of Baroda": "PSU Large Bank",
    "Punjab National Bank": "PSU Large Bank",

    "HDFC Bank": "Private Large Bank",
    "ICICI Bank": "Private Large Bank",
    "Axis Bank": "Private Large Bank",

    "Reserve Bank of India": "Central Bank / Regulator",
    "RBI": "Central Bank / Regulator"
}


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Cisco Security Comparison Tool (Demo)",
    layout="wide"
)

st.title("🔐 Cisco Security Capability Comparison (Demo)")
st.caption("Internal demo – capability-based, product-scoped comparison")

# -----------------------------
# DATA MODELS (DEMO)
# -----------------------------

# Vendor Capability Master (simplified)
VENDOR_CAPABILITIES = {
    "Cisco": {
        "Network Security": 5,
        "Email Security": 5,
        "Threat Prevention": 4,
        "Identity & Zero Trust": 5,
        "Cloud Security (SSE)": 4,
        "Compliance & Sovereignty": 5
    },
    "Palo Alto Networks": {
        "Network Security": 5,
        "Email Security": 3,
        "Threat Prevention": 5,
        "Identity & Zero Trust": 3,
        "Cloud Security (SSE)": 5,
        "Compliance & Sovereignty": 4
    }
}

# Product → Capability Mapping
PRODUCT_CAPABILITY_MAP = {
    "Cisco Secure Firewall": [
        "Network Security",
        "Threat Prevention",
        "Compliance & Sovereignty"
    ],
    "Cisco Secure Email": [
        "Email Security",
        "Threat Prevention"
    ],
    "Cisco Duo": [
        "Identity & Zero Trust",
        "Compliance & Sovereignty"
    ],
    "Cisco Umbrella": [
        "Cloud Security (SSE)",
        "Threat Prevention"
    ]
}

ALL_CAPABILITIES = list(VENDOR_CAPABILITIES["Cisco"].keys())

# -----------------------------
# UI INPUTS
# -----------------------------
st.sidebar.header("🔧 Input Parameters")

customer = st.sidebar.text_input("Customer Name", "State Bank of India")

# bank_type = st.sidebar.selectbox(
#   "Bank Archetype",
#    options=list(BANK_ARCHETYPES.keys()),
#    index=0
#)

# Auto-suggest archetype based on customer name
suggested_archetype = BANK_ARCHETYPE_HINTS.get(customer)

# Fallback if bank is unknown or not mapped
if suggested_archetype not in BANK_ARCHETYPES:
    suggested_archetype = list(BANK_ARCHETYPES.keys())[0]

bank_type = st.sidebar.selectbox(
    "Bank Archetype (auto-suggested, editable)",
    options=list(BANK_ARCHETYPES.keys()),
    index=list(BANK_ARCHETYPES.keys()).index(suggested_archetype)
)

st.sidebar.caption(
    "Archetype is auto-suggested based on bank metadata. "
    "User can override if required."
)


cisco_products = st.sidebar.multiselect(
    "Select Cisco Products",
    options=list(PRODUCT_CAPABILITY_MAP.keys()),
    default=["Cisco Secure Firewall", "Cisco Duo"]
)

competitor = st.sidebar.selectbox(
    "Select Competitor",
    options=["Palo Alto Networks"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Demo assumptions baked into tool")

# -----------------------------
# CAPABILITY ACTIVATION LOGIC
# -----------------------------
activated_capabilities = set()

for product in cisco_products:
    activated_capabilities.update(PRODUCT_CAPABILITY_MAP[product])

st.subheader("🏦 Industry Weight Drivers")

drivers = BANK_ARCHETYPES.get(bank_type)

if drivers:
    driver_df = pd.DataFrame(
        drivers.items(),
        columns=["Industry Factor", "Weight (1–5)"]
    )

    st.dataframe(driver_df, use_container_width=True)

    avg_weight = round(sum(drivers.values()) / len(drivers), 1)

    if avg_weight >= 4:
        weight_label = "HIGH"
    elif avg_weight >= 3:
        weight_label = "MEDIUM"
    else:
        weight_label = "LOW"

    st.info(f"**Derived Industry Weight:** {weight_label} (Avg: {avg_weight})")

else:
    st.warning("No industry drivers defined for this customer.")


# -----------------------------
# BUILD COMPARISON MATRIX
# -----------------------------
rows = []

for capability in ALL_CAPABILITIES:
    if capability in activated_capabilities:
        cisco_score = VENDOR_CAPABILITIES["Cisco"][capability]
        competitor_score = VENDOR_CAPABILITIES[competitor][capability]

        if cisco_score > competitor_score:
            position = "🟢 Cisco Advantage"
        elif cisco_score < competitor_score:
            position = "🔴 Competitor Advantage"
        else:
            position = "🟡 Comparable"

        status = "✅ In Scope"
    else:
        cisco_score = "—"
        competitor_score = VENDOR_CAPABILITIES[competitor][capability]
        position = "⚪ Not Compared"
        status = "❌ Out of Scope"

    rows.append([
        capability,
        cisco_score,
        competitor_score,
        position,
        status
    ])

df = pd.DataFrame(
    rows,
    columns=[
        "Capability",
        "Cisco Score",
        f"{competitor} Score",
        "Positioning",
        "Scope Status"
    ]
)


# --- Final Score Calculation ---
final_score = calculate_final_score(
    industry_weight,
    vendor_strength,
    capability_active
)

st.subheader("📊 Final Score Calculation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Industry Weight", industry_weight)

with col2:
    st.metric("Vendor Strength", vendor_strength)

with col3:
    st.metric(
        "Capability Active",
        "Yes" if capability_active else "No"
    )

with col4:
    st.metric("Final Score", final_score)

# --- Show the formula clearly ---



# -----------------------------
# OUTPUTS
# -----------------------------
st.subheader(f"📊 Capability Comparison – {customer}")

st.dataframe(df, use_container_width=True)

# -----------------------------
# INSIGHTS
# -----------------------------
st.subheader("🧠 Auto-Generated Insights")

wins = df[df["Positioning"] == "🟢 Cisco Advantage"]["Capability"].tolist()
losses = df[df["Positioning"] == "🔴 Competitor Advantage"]["Capability"].tolist()
out_of_scope = df[df["Scope Status"] == "❌ Out of Scope"]["Capability"].tolist()

if wins:
    st.success(f"**Cisco Advantages:** {', '.join(wins)}")

if losses:
    st.warning(f"**Competitive Pressure Areas:** {', '.join(losses)}")

if out_of_scope:
    st.info(
        "Capabilities intentionally out of scope for selected Cisco products: "
        + ", ".join(out_of_scope)
    )

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption(
    "This demo uses simplified scores for illustration. "
    "Production version should externalize data into JSON and apply governance."
)
