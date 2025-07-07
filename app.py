import streamlit as st
import pandas as pd
import plotly.express as px
from modules import ahp, saw, topsis
from utils.logger import log_result
import io
import random

st.set_page_config(page_title="SPK AHP Destinasi Backpacker", layout="wide")

# Custom CSS pastel
st.markdown("""
    <style>
    .main {
        background-color: #fffafa;
    }
    .css-1xarl3l th {
        background-color: #f8d7da !important;
        color: #5d001e !important;
        font-weight: 600 !important;
        border-bottom: 1px solid #f3b0b8 !important;
    }
    .css-1xarl3l td {
        background-color: #fff1f3 !important;
        color: #333333 !important;
        border-bottom: 1px solid #f3b0b8 !important;
    }
    .css-1xarl3l tbody tr:hover {
        background-color: #ffe0e5 !important;
    }
    .css-10trblm.e1nzilvr1 {
        color: #b03060;
        font-weight: 700;
    }
    .css-6qob1r {
        background-color: #fbe6eb;
    }
    .stButton>button {
        background-color: #e75480;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #d43d6e;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎒 Sistem Pendukung Keputusan Destinasi Backpacker")
st.write("Upload dataset Anda atau gunakan contoh bawaan.")

uploaded_file = st.sidebar.file_uploader("🎒 Upload CSV Dataset", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("data/destinasi.csv")

# Filter Destinasi
st.sidebar.subheader("🔍 Filter Destinasi")
biaya_min, biaya_max = st.sidebar.slider(
    "Rentang Biaya Harian",
    min_value=int(df["Biaya Harian"].min()),
    max_value=int(df["Biaya Harian"].max()),
    value=(int(df["Biaya Harian"].min()), int(df["Biaya Harian"].max()))
)
df_filtered = df[(df["Biaya Harian"] >= biaya_min) & (df["Biaya Harian"] <= biaya_max)]

st.subheader("📊 Dataset")
st.dataframe(df_filtered)

# Bobot Kriteria
criteria = [
    'Biaya Harian', 'Biaya Perjalanan', 'Tingkat Keamanan',
    'Stabilitas Politik', 'Kemudahan Visa',
    'Transportasi Publik', 'Keberagaman Aktivitas'
]

st.sidebar.subheader("⚖️ Bobot Kriteria (%)")

mode = st.sidebar.radio("Mode Input Bobot", ["Manual", "Random", "Otomatis Normalisasi"])

weights = {}

if mode == "Manual":
    total_weight = 0
    for c in criteria:
        w = st.sidebar.slider(c, 0, 100, 10, 5)/100
        weights[c] = w
        total_weight += w
    st.sidebar.markdown(f"**🔢 Total Bobot Saat Ini: {round(total_weight*100)}%**")
elif mode == "Random":
    random_values = [random.uniform(0, 1) for _ in criteria]
    s = sum(random_values)
    for i, c in enumerate(criteria):
        weights[c] = random_values[i]/s
    st.sidebar.success("✅ Bobot acak telah digenerate otomatis.")
    for c in criteria:
        st.sidebar.write(f"{c}: {round(weights[c]*100)}%")
elif mode == "Otomatis Normalisasi":
    manual_values = {}
    for c in criteria:
        w = st.sidebar.slider(c, 0, 100, 10, 5)/100
        manual_values[c] = w
    s = sum(manual_values.values())
    if s == 0:
        st.sidebar.error("Semua bobot nol. Silakan isi.")
        st.stop()
    for c in criteria:
        weights[c] = manual_values[c]/s
    st.sidebar.success("✅ Bobot otomatis dinormalisasi jadi 100%.")
    for c in criteria:
        st.sidebar.write(f"{c}: {round(weights[c]*100)}%")

method = st.sidebar.selectbox("Metode SPK", ["AHP", "SAW", "TOPSIS"])

# Penjelasan kriteria
with st.expander("ℹ️ Penjelasan Kriteria"):
    st.write("""
    - **Biaya Harian**: Pengeluaran rata-rata per hari.
    - **Biaya Perjalanan**: Ongkos perjalanan menuju destinasi.
    - **Tingkat Keamanan**: Tingkat keamanan umum.
    - **Stabilitas Politik**: Situasi politik negara.
    - **Kemudahan Visa**: Kemudahan mendapatkan visa.
    - **Transportasi Publik**: Kualitas transportasi lokal.
    - **Keberagaman Aktivitas**: Banyaknya aktivitas menarik.
    """)

if mode == "Manual" and abs(total_weight - 1) > 0.001:
    st.error("Total bobot harus 100% (gunakan mode Otomatis jika ingin dinormalisasi).")
    st.stop()

# Perhitungan
if method == "AHP":
    result, df_norm = ahp.compute_ahp_scores(df_filtered, weights)
elif method == "SAW":
    result, df_norm = saw.compute_saw_scores(df_filtered, weights)
else:
    result, df_norm = topsis.compute_topsis_scores(df_filtered, weights)

log_result(result, method)

# Ranking Destinasi
st.subheader("🏆 Ranking Destinasi")
result['Highlight'] = ["🏆" if i == 0 else "" for i in range(len(result))]
st.dataframe(result)

# Heatmap
st.subheader("🔥 Heatmap Normalisasi")
heatmap_data = df_norm[[c+'_norm' for c in criteria]]
st.dataframe(heatmap_data)

# Multi-Radar Chart
st.subheader("📈 Multi-Radar Chart")
selected = st.multiselect("Pilih destinasi", result["Destinasi"].tolist())
if selected:
    fig = px.line_polar(
        pd.concat([
            pd.DataFrame({
                "r": [df_norm.loc[df_norm["Destinasi"] == d, c+"_norm"].values[0] for c in criteria],
                "theta": criteria,
                "Destinasi": d
            }) for d in selected
        ]),
        r="r",
        theta="theta",
        color="Destinasi",
        line_close=True
    )
    fig.update_traces(fill="toself")
    st.plotly_chart(fig)

# Download Excel
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    result.to_excel(writer, index=False)
st.download_button("💾 Download Excel", output.getvalue(), "hasil.xlsx")

# Analisis Sensitivitas
st.subheader("⚙️ Analisis Sensitivitas Bobot")
sens_weight = st.slider("Simulasi Bobot Biaya Harian (%)", 0, 100, int(weights["Biaya Harian"]*100))/100
sim_weights = weights.copy()
adjustment = (1 - sens_weight) / (1 - weights["Biaya Harian"])
sim_weights["Biaya Harian"] = sens_weight
for k in sim_weights:
    if k != "Biaya Harian":
        sim_weights[k] *= adjustment

if method == "AHP":
    sim_result, _ = ahp.compute_ahp_scores(df_filtered, sim_weights)
elif method == "SAW":
    sim_result, _ = saw.compute_saw_scores(df_filtered, sim_weights)
else:
    sim_result, _ = topsis.compute_topsis_scores(df_filtered, sim_weights)

st.write("Ranking setelah simulasi:")
st.dataframe(sim_result)
