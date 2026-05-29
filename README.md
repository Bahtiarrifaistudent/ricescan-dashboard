# RiceScan Dashboard

**Monitoring Penyakit Daun Padi — Kabupaten Indramayu**

Dashboard ini memantau risiko penyakit daun padi (Blas, Blight, Tungro) berbasis:
- Data cuaca real-time (Open-Meteo API)
- Survei lapangan petani (150 responden, 15 kecamatan)
- Deteksi citra CNN

## Cara Jalankan Lokal

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Struktur Project

```
├── dashboard.py              # Aplikasi Streamlit
├── etl_pipeline.py           # Pipeline ETL 8 fase
├── farmer_survey_raw.csv     # Dataset survei petani
├── requirements.txt
├── .streamlit/config.toml    # Konfigurasi tema
└── output_pipeline/          # Output otomatis dari pipeline
    ├── data/
    ├── reports/
    ├── eda/
    └── logs/
```

## Tim

Kelompok 2 — D4 SIKC POLINDRA  
Mata Kuliah: Big Data | Dosen: Vera Wati, M.Kom.
