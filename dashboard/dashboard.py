import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
# Gunakan path relatif dari lokasi script, bukan dari cwd,
# agar dashboard bisa berjalan dari mana saja.
# ============================================================
@st.cache_data
def load_data():
    # Resolve path relatif terhadap lokasi file dashboard.py ini
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(csv_path)
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

# Pastikan user sudah memilih 2 tanggal sebelum memfilter
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.sidebar.warning("Pilih rentang tanggal (start & end).")
    st.stop()

if start_date > end_date:
    st.sidebar.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
    st.stop()

filtered = analysis_df[
    (analysis_df["order_purchase_timestamp"].dt.date >= start_date) &
    (analysis_df["order_purchase_timestamp"].dt.date <= end_date)
]

if filtered.empty:
    st.warning("⚠️ Tidak ada data pada rentang tanggal yang dipilih. Silakan ubah filter.")
    st.stop()

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
col3.metric("⭐ Avg Review Score", f"{avg_review:.2f}" if pd.notna(avg_review) else "N/A")
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

if len(monthly) < 2:
    st.info("ℹ️ Rentang tanggal terlalu sempit untuk menampilkan tren MoM. Perluas rentang tanggal minimal 2 bulan.")
else:
    fig1, ax1 = plt.subplots(figsize=(14, 6))
    colors_bar = [
        '#E74C3C' if x == monthly["total_orders"].max() else '#4C72B0'
        for x in monthly["total_orders"]
    ]
    ax1.bar(monthly["month_dt"], monthly["total_orders"], width=25, color=colors_bar, alpha=0.8, edgecolor='white')
    ax1.set_xlabel("Bulan", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Jumlah Pesanan", fontsize=12, fontweight='bold', color='#4C72B0')
    ax1.tick_params(axis='x', rotation=45)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    ax2 = ax1.twinx()
    ax2.plot(monthly["month_dt"], monthly["mom_growth_pct"], color='#E67E22',
             marker='o', linewidth=2.5, markersize=5, label='MoM Growth (%)')
    ax2.set_ylabel("MoM Growth (%)", fontsize=12, fontweight='bold', color='#E67E22')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

    ax1.set_title("Tren Jumlah Pesanan Bulanan & Pertumbuhan MoM", fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    peak = monthly.loc[monthly["total_orders"].idxmax()]
    st.info(f"📊 **Puncak pesanan** terjadi pada **{peak['month']}** dengan **{peak['total_orders']:,}** pesanan.")

st.markdown("---")

# ============================================================
# PERTANYAAN 2: Kategori dengan Review Terendah
# ============================================================
st.subheader("⭐ Pertanyaan 2: Kategori Produk dengan Review Terendah")
st.markdown("""
> **SMART Question:** *Kategori produk apa yang memiliki rata-rata skor review terendah (< 4.0)
> dan volume penjualan signifikan (> 100 transaksi) selama 2017-2018, sehingga perlu diprioritaskan
> untuk perbaikan kualitas?*
""")

min_transactions = st.slider("Minimum jumlah transaksi per kategori:", 50, 500, 100, step=50)

cat_review = filtered.groupby("product_category_name_english").agg(
    avg_score=("review_score", "mean"),
    total_tx=("order_id", "count")
).reset_index()

cat_filtered = cat_review[cat_review["total_tx"] > min_transactions].sort_values("avg_score").reset_index(drop=True)

if cat_filtered.empty:
    st.warning("⚠️ Tidak ada kategori yang memenuhi kriteria minimum transaksi pada rentang tanggal ini. Coba turunkan nilai slider atau perluas rentang tanggal.")
else:
    top15 = cat_filtered.head(15).sort_values("avg_score")

    col_a, col_b = st.columns(2)

    with col_a:
        fig2, ax = plt.subplots(figsize=(8, 8))
        colors = [
            '#E74C3C' if x < 4.0 else '#F39C12' if x < 4.2 else '#4C72B0'
            for x in top15["avg_score"]
        ]
        bars = ax.barh(top15["product_category_name_english"], top15["avg_score"],
                       color=colors, edgecolor='white')
        ax.axvline(x=4.0, color='red', linestyle='--', alpha=0.7, label='Threshold 4.0')
        ax.set_xlabel("Rata-rata Review Score", fontweight='bold')
        ax.set_title("15 Kategori dengan Review Terendah", fontweight='bold')
        ax.legend()
        # Batas x dinamis: dari min score - 0.3 hingga 5.0
        x_min = max(0, top15["avg_score"].min() - 0.3)
        ax.set_xlim(x_min, 5.0)
        # Tambahkan label nilai di setiap bar
        for bar, val in zip(bars, top15["avg_score"]):
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                    f'{val:.2f}', va='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    with col_b:
        fig3, ax = plt.subplots(figsize=(8, 8))
        bars2 = ax.barh(top15["product_category_name_english"], top15["total_tx"],
                        color='#5DADE2', edgecolor='white')
        ax.set_xlabel("Jumlah Transaksi", fontweight='bold')
        ax.set_title("Volume Transaksi per Kategori", fontweight='bold')
        # Tambahkan label nilai di setiap bar
        for bar, val in zip(bars2, top15["total_tx"]):
            ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                    f'{val:,}', va='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    low_rev = cat_filtered[cat_filtered["avg_score"] < 4.0]
    if len(low_rev) > 0:
        st.warning(f"⚠️ Terdapat **{len(low_rev)} kategori** dengan rata-rata review di bawah 4.0 (threshold kualitas).")
        st.dataframe(
            low_rev.rename(columns={
                "product_category_name_english": "Kategori",
                "avg_score": "Avg Review Score",
                "total_tx": "Total Transaksi"
            }).style.format({"Avg Review Score": "{:.2f}", "Total Transaksi": "{:,}"}),
            use_container_width=True
        )
    else:
        st.success("✅ Semua kategori (dengan filter transaksi ini) memiliki rata-rata review ≥ 4.0.")

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

if rfm.empty:
    st.info("ℹ️ Data RFM tidak tersedia untuk rentang tanggal ini.")
else:
    col_r, col_f, col_m = st.columns(3)

    with col_r:
        fig_r, ax = plt.subplots(figsize=(6, 4))
        ax.hist(rfm["recency"], bins=50, color="#4C72B0", edgecolor="white", alpha=0.8)
        ax.set_title("Distribusi Recency", fontweight="bold")
        ax.set_xlabel("Hari")
        ax.set_ylabel("Jumlah Pelanggan")
        plt.tight_layout()
        st.pyplot(fig_r)
        plt.close(fig_r)

    with col_f:
        freq_max = rfm["frequency"].max()
        bins_f = range(1, min(freq_max + 2, 15))
        fig_f, ax = plt.subplots(figsize=(6, 4))
        ax.hist(rfm["frequency"], bins=bins_f, color="#E67E22", edgecolor="white", alpha=0.8)
        ax.set_title("Distribusi Frequency", fontweight="bold")
        ax.set_xlabel("Jumlah Transaksi")
        ax.set_ylabel("Jumlah Pelanggan")
        plt.tight_layout()
        st.pyplot(fig_f)
        plt.close(fig_f)

    with col_m:
        fig_m, ax = plt.subplots(figsize=(6, 4))
        ax.hist(rfm["monetary"], bins=50, color="#27AE60", edgecolor="white", alpha=0.8)
        ax.set_title("Distribusi Monetary", fontweight="bold")
        ax.set_xlabel("Total Pengeluaran (R$)")
        ax.set_ylabel("Jumlah Pelanggan")
        plt.tight_layout()
        st.pyplot(fig_m)
        plt.close(fig_m)

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
4. 🎯 **Program Loyalitas** — Targetkan pelanggan Champions dari RFM untuk program referral & retensi.
""")

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard Analisis Data E-Commerce Olist | Dicoding Submission")
