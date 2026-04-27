import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# CONFIG & STYLING
# ============================================================
st.set_page_config(
    page_title="E-Commerce Olist Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4C72B0, #E74C3C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

analysis_df = load_data()

# ============================================================
# SIDEBAR FILTER
# ============================================================
st.sidebar.title("🔎 Filter Data")

min_date = analysis_df["order_purchase_timestamp"].min().date()
max_date = analysis_df["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = analysis_df[
    (analysis_df["order_purchase_timestamp"].dt.date >= start_date) &
    (analysis_df["order_purchase_timestamp"].dt.date <= end_date)
]

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="main-header">🛒 E-Commerce Olist Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analisis Data E-Commerce Brazil | 2017-2018</div>', unsafe_allow_html=True)

# ============================================================
# METRICS ROW
# ============================================================
total_orders = filtered["order_id"].nunique()
total_revenue = filtered["price"].sum()
avg_review = filtered["review_score"].mean()
total_customers = filtered["customer_id"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total Pesanan", f"{total_orders:,}")
col2.metric("💰 Total Revenue", f"R$ {total_revenue:,.2f}")
col3.metric("⭐ Avg Review Score", f"{avg_review:.2f}")
col4.metric("👥 Total Pelanggan", f"{total_customers:,}")

st.markdown("---")

# ============================================================
# PERTANYAAN 1: Tren Pesanan Bulanan
# ============================================================
st.subheader("📈 Pertanyaan 1: Tren Pesanan Bulanan (Month-over-Month)")
st.markdown("""
> **SMART Question:** *Bagaimana tren pertumbuhan jumlah pesanan secara bulanan (MoM) pada platform
> e-commerce Olist sepanjang 2017-2018, dan pada bulan apa terjadi puncak pesanan tertinggi?*
""")

filtered_copy = filtered.copy()
filtered_copy["order_month"] = filtered_copy["order_purchase_timestamp"].dt.to_period("M")
monthly = filtered_copy.groupby("order_month")["order_id"].nunique().reset_index()
monthly.columns = ["month", "total_orders"]
monthly["month_dt"] = monthly["month"].dt.to_timestamp()
monthly["mom_growth_pct"] = monthly["total_orders"].pct_change() * 100

fig1, ax1 = plt.subplots(figsize=(14, 6))
colors_bar = ['#E74C3C' if x == monthly["total_orders"].max() else '#4C72B0' for x in monthly["total_orders"]]
ax1.bar(monthly["month_dt"], monthly["total_orders"], width=25, color=colors_bar, alpha=0.8, edgecolor='white')
ax1.set_xlabel("Bulan", fontsize=12, fontweight='bold')
ax1.set_ylabel("Jumlah Pesanan", fontsize=12, fontweight='bold', color='#4C72B0')
ax1.tick_params(axis='x', rotation=45)

ax2 = ax1.twinx()
ax2.plot(monthly["month_dt"], monthly["mom_growth_pct"], color='#E67E22', marker='o', linewidth=2.5, markersize=5)
ax2.set_ylabel("MoM Growth (%)", fontsize=12, fontweight='bold', color='#E67E22')
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

ax1.set_title("Tren Jumlah Pesanan Bulanan & Pertumbuhan MoM", fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
st.pyplot(fig1)

peak = monthly.loc[monthly["total_orders"].idxmax()]
st.info(f"📊 **Puncak pesanan** terjadi pada **{peak['month']}** dengan **{peak['total_orders']:,}** pesanan.")

st.markdown("---")

# ============================================================
# PERTANYAAN 2: Kategori dengan Review Terendah
# ============================================================
st.subheader("⭐ Pertanyaan 2: Kategori Produk dengan Review Terendah")
st.markdown("""
> **SMART Question:** *Kategori produk apa yang memiliki rata-rata skor review terendah (< 4.0)
> dan volume penjualan signifikan (>100 transaksi) selama 2017-2018, sehingga perlu diprioritaskan
> untuk perbaikan kualitas?*
""")

min_transactions = st.slider("Minimum jumlah transaksi per kategori:", 50, 500, 100, step=50)

cat_review = filtered.groupby("product_category_name_english").agg(
    avg_score=("review_score", "mean"),
    total_tx=("order_id", "count")
).reset_index()
cat_filtered = cat_review[cat_review["total_tx"] > min_transactions].sort_values("avg_score")

col_a, col_b = st.columns(2)

with col_a:
    fig2, ax = plt.subplots(figsize=(8, 8))
    top15 = cat_filtered.head(15).sort_values("avg_score")
    colors = ['#E74C3C' if x < 4.0 else '#F39C12' if x < 4.2 else '#4C72B0' for x in top15["avg_score"]]
    ax.barh(top15["product_category_name_english"], top15["avg_score"], color=colors, edgecolor='white')
    ax.axvline(x=4.0, color='red', linestyle='--', alpha=0.7, label='Threshold 4.0')
    ax.set_xlabel("Rata-rata Review Score", fontweight='bold')
    ax.set_title("15 Kategori Review Terendah", fontweight='bold')
    ax.legend()
    ax.set_xlim(3.0, 4.5)
    plt.tight_layout()
    st.pyplot(fig2)

with col_b:
    fig3, ax = plt.subplots(figsize=(8, 8))
    ax.barh(top15["product_category_name_english"], top15["total_tx"], color='#5DADE2', edgecolor='white')
    ax.set_xlabel("Jumlah Transaksi", fontweight='bold')
    ax.set_title("Volume Transaksi per Kategori", fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig3)

low_rev = cat_filtered[cat_filtered["avg_score"] < 4.0]
if len(low_rev) > 0:
    st.warning(f"⚠️ Terdapat **{len(low_rev)} kategori** dengan rata-rata review di bawah 4.0")
    st.dataframe(low_rev.rename(columns={
        "product_category_name_english": "Kategori",
        "avg_score": "Avg Review",
        "total_tx": "Total Transaksi"
    }).reset_index(drop=True), use_container_width=True)

st.markdown("---")

# ============================================================
# RFM ANALYSIS
# ============================================================
st.subheader("🎯 Analisis Lanjutan: RFM Analysis")
st.markdown("""
RFM (Recency, Frequency, Monetary) mengelompokkan pelanggan berdasarkan perilaku pembelian:
- **Recency**: Hari sejak pembelian terakhir
- **Frequency**: Jumlah transaksi
- **Monetary**: Total pengeluaran
""")

reference_date = filtered["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
rfm = filtered.groupby("customer_id").agg(
    recency=("order_purchase_timestamp", lambda x: (reference_date - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("price", "sum")
).reset_index()

col_r, col_f, col_m = st.columns(3)

with col_r:
    fig_r, ax = plt.subplots(figsize=(6, 4))
    ax.hist(rfm["recency"], bins=50, color="#4C72B0", edgecolor="white", alpha=0.8)
    ax.set_title("Distribusi Recency", fontweight="bold")
    ax.set_xlabel("Hari")
    ax.set_ylabel("Jumlah Pelanggan")
    plt.tight_layout()
    st.pyplot(fig_r)

with col_f:
    fig_f, ax = plt.subplots(figsize=(6, 4))
    ax.hist(rfm["frequency"], bins=range(1, min(rfm["frequency"].max() + 2, 15)),
            color="#E67E22", edgecolor="white", alpha=0.8)
    ax.set_title("Distribusi Frequency", fontweight="bold")
    ax.set_xlabel("Jumlah Transaksi")
    ax.set_ylabel("Jumlah Pelanggan")
    plt.tight_layout()
    st.pyplot(fig_f)

with col_m:
    fig_m, ax = plt.subplots(figsize=(6, 4))
    ax.hist(rfm["monetary"], bins=50, color="#27AE60", edgecolor="white", alpha=0.8)
    ax.set_title("Distribusi Monetary", fontweight="bold")
    ax.set_xlabel("Total Pengeluaran (R$)")
    ax.set_ylabel("Jumlah Pelanggan")
    plt.tight_layout()
    st.pyplot(fig_m)

st.markdown("---")

# ============================================================
# CONCLUSION
# ============================================================
st.subheader("📝 Kesimpulan & Rekomendasi")

st.markdown("""
**Kesimpulan Pertanyaan 1:**
Tren jumlah pesanan menunjukkan pertumbuhan signifikan sepanjang 2017-2018. Platform mengalami
adopsi pesat di pertengahan 2017 dengan MoM growth yang tinggi, lalu stabil di akhir periode.
Pola musiman teridentifikasi yang berguna untuk perencanaan bisnis.

**Kesimpulan Pertanyaan 2:**
Terdapat beberapa kategori produk dengan review rendah (<4.0) meski volume transaksinya tinggi.
Kategori-kategori ini menjadi prioritas perbaikan kualitas untuk meningkatkan kepuasan pelanggan.

**Rekomendasi Action Items:**
1. 📅 **Perencanaan Musiman** — Siapkan stok & kampanye promosi menjelang bulan puncak pesanan.
2. 🔍 **Audit Kualitas** — Lakukan audit seller & produk di kategori review rendah, terapkan standar minimum.
3. 💬 **Feedback Loop** — Bangun sistem feedback agar seller dapat memperbaiki kualitas secara proaktif.
""")

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard Analisis Data E-Commerce Olist | Dicoding Submission")
