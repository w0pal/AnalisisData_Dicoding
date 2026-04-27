# Proyek Analisis Data: E-Commerce Public Dataset

## Deskripsi
Proyek ini melakukan analisis data pada dataset E-Commerce Brazil (Olist) untuk menjawab dua pertanyaan bisnis utama terkait tren pesanan bulanan dan kualitas produk berdasarkan review pelanggan.

## Struktur Direktori
```
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── customers_dataset.csv
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── products_dataset.csv
│   ├── sellers_dataset.csv
│   └── product_category_name_translation.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment

```bash
pip install -r requirements.txt
```

## Menjalankan Dashboard

```bash
cd submission
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`.

## Pertanyaan Bisnis
1. Bagaimana tren pertumbuhan jumlah pesanan secara bulanan (Month-over-Month) pada platform e-commerce Olist sepanjang tahun 2017-2018, dan pada bulan apa terjadi puncak pesanan tertinggi?
2. Kategori produk apa yang memiliki rata-rata skor review terendah (di bawah 4.0) dan volume penjualan signifikan (>100 transaksi) selama periode 2017-2018, sehingga perlu diprioritaskan untuk perbaikan kualitas produk atau layanan?
