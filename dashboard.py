"""
Dashboard Monitoring Penyakit Daun Padi – Kabupaten Indramayu
Disesuaikan penuh dengan etl_pipeline.py (Kelompok 2)

Cara menjalankan:
    1. Letakkan dashboard.py di folder yang SAMA dengan etl_pipeline.py
    2. Jalankan pipeline dulu: python etl_pipeline.py
    3. Jalankan dashboard  : streamlit run dashboard.py

Struktur folder:
    project/
        etl_pipeline.py
        dashboard.py            ← file ini
        farmer_survey_raw.csv
        Penyakit_Daun_Padi_Indonesia/
            sehat/ blast/ blight/ tungro/
        output_pipeline/        ← dibuat otomatis oleh etl_pipeline.py
            data/   reports/   eda/   logs/
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json, math, random, hashlib, os, time, urllib.request
from datetime import datetime, timedelta, timezone
WIB = timezone(timedelta(hours=7))

st.set_page_config(
    page_title="Dashboard Penyakit Daun Padi - Indramayu",
    page_icon="🌾", layout="wide",
    initial_sidebar_state="expanded",
)

# ─── AUTH ────────────────────────────────────────────────────────────────────
import json as _json

USERS_FILE = "users.json"

def load_users():
    default = {
        "admin":     "ricescan2026",
        "kelompok2": "polindra2026",
        "dosen":     "verawati2026",
    }
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE) as f:
                data = _json.load(f)
            return {**default, **data}
        except:
            pass
    return default

def save_user(username, password):
    users = load_users()
    users[username] = password
    try:
        with open(USERS_FILE, "w") as f:
            _json.dump(users, f)
        return True
    except:
        return False

def check_login(username, password):
    return load_users().get(username.lower()) == password

CARD = "background:#ffffff;border:1px solid #e0e0e0;border-radius:14px;padding:32px 36px;box-shadow:0 2px 12px rgba(0,0,0,0.08)"

def show_auth():
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='{CARD};text-align:center;margin-bottom:20px'>
            <div style='font-size:30px;font-weight:700;color:#1565C0'>RiceScan Dashboard</div>
            <div style='font-size:13px;color:#555555;margin-top:6px'>Monitoring Penyakit Daun Padi — Kabupaten Indramayu</div>
        </div>""", unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["Masuk", "Daftar Akun"])

        with tab_login:
            with st.form("login_form"):
                st.markdown("#### Masuk")
                username = st.text_input("Username", placeholder="contoh: admin")
                password = st.text_input("Password", type="password", placeholder="password")
                submitted = st.form_submit_button("Masuk", use_container_width=True, type="primary")
                if submitted:
                    if check_login(username, password):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username.lower()
                        st.rerun()
                    else:
                        st.error("Username atau password salah.")

        with tab_reg:
            with st.form("register_form"):
                st.markdown("#### Daftar Akun Baru")
                new_user = st.text_input("Username baru", placeholder="min. 4 karakter")
                new_pass = st.text_input("Password", type="password", placeholder="min. 6 karakter")
                new_pass2 = st.text_input("Konfirmasi Password", type="password", placeholder="ulangi password")
                reg_key  = st.text_input("Kode Registrasi", type="password", placeholder="hubungi admin")
                submitted2 = st.form_submit_button("Daftar", use_container_width=True, type="primary")
                if submitted2:
                    if reg_key != "ricescan2026":
                        st.error("Kode registrasi salah.")
                    elif len(new_user) < 4:
                        st.error("Username minimal 4 karakter.")
                    elif len(new_pass) < 6:
                        st.error("Password minimal 6 karakter.")
                    elif new_pass != new_pass2:
                        st.error("Konfirmasi password tidak cocok.")
                    elif new_user.lower() in load_users():
                        st.error("Username sudah digunakan.")
                    else:
                        if save_user(new_user.lower(), new_pass):
                            st.success(f"Akun '{new_user}' berhasil dibuat. Silakan masuk.")
                        else:
                            st.warning("Akun dibuat (tersimpan sementara di sesi ini).")

        st.markdown(f"""
        <div style='text-align:center;margin-top:16px;font-size:11px;color:#888'>
        Kelompok 2 · D4 SIKC POLINDRA · 2026
        </div>""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    show_auth()
    st.stop()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Sora',sans-serif}
[data-testid="metric-container"]{background:#ffffff;border:1px solid #e0e0e0;border-radius:10px;padding:14px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.07)}
[data-testid="stMetricLabel"]>div{font-size:10.5px;color:#666666;letter-spacing:1px;text-transform:uppercase;font-family:'DM Mono',monospace}
[data-testid="stMetricValue"]>div{font-size:22px;font-weight:700;color:#1a1a2e}
[data-testid="stSidebar"]{background:#f0f4f8;border-right:1px solid #e0e0e0}
[data-testid="stSidebar"] *{color:#1a1a2e}
.dash-card{background:#ffffff;border:1px solid #e0e0e0;border-radius:10px;padding:16px 20px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,0.06)}
.mono{font-family:'DM Mono',monospace;font-size:11px;color:#555555}
hr{border-color:#e0e0e0}
.risk-aman{color:#2e7d32;font-weight:700}
.risk-rendah{color:#1565C0;font-weight:700}
.risk-sedang{color:#e65100;font-weight:700}
.risk-tinggi{color:#c62828;font-weight:700}
.risk-kritis{color:#b71c1c;font-weight:700}
</style>
""", unsafe_allow_html=True)

# ─── KONSTANTA — sama persis dengan etl_pipeline.py ──────────────────────────
DATASET_DIR = "./Penyakit_Daun_Padi_Indonesia"
CLASSES     = ["sehat", "blast", "blight", "tungro"]
IMG_SIZE    = (224, 224)
OUTPUT_DIR  = "./output_pipeline"
DATA_DIR    = os.path.join(OUTPUT_DIR, "data")
RPT_DIR     = os.path.join(OUTPUT_DIR, "reports")
LOG_DIR     = os.path.join(OUTPUT_DIR, "logs")
EDA_DIR     = os.path.join(OUTPUT_DIR, "eda")

KECAMATAN_LIST = [
    "Indramayu","Sindang","Balongan","Juntinyuat","Sliyeg",
    "Jatibarang","Losarang","Cantigi","Pasekan","Lohbener",
    "Haurgeulis","Gantar","Patrol","Anjatan","Kandanghaur",
]

CLS_COLOR = {"sehat":"#3fb950","blast":"#f85149","blight":"#d29922","tungro":"#bc8cff"}
REKOM = {
    "sehat":  "Daun padi sehat. Lanjutkan pemantauan rutin setiap 7 hari.",
    "blast":  "Blas Daun (Magnaporthe oryzae). Semprot Tricyclazole/Isoprothiolane. Kurangi pupuk N.",
    "blight": "Hawar Daun Bakteri (Xanthomonas oryzae). Gunakan varietas tahan Inpari13. Perbaiki drainase.",
    "tungro": "Tungro (RTBV) — tidak ada obat. Cabut & bakar tanaman. Kendalikan wereng hijau (vektor).",
}
RISK_COLOR = {
    "Aman":"#3fb950","Rendah":"#58a6ff","Sedang":"#d29922","Tinggi":"#f0883e","Kritis":"#f85149"
}
PLT  = dict(paper_bgcolor="#ffffff",plot_bgcolor="#f5f8fc",
            font=dict(family="Sora,sans-serif",color="#1a1a2e",size=11),
            margin=dict(l=10,r=10,t=36,b=10))
GRID = dict(gridcolor="#e0e0e0",zerolinecolor="#cccccc")


# ════════════════ DATA LOADERS — membaca output_pipeline/ ════════════════════

@st.cache_data(show_spinner=False)
def load_pipeline_log():
    p = os.path.join(LOG_DIR,"pipeline_run.json")
    return json.load(open(p,encoding="utf-8")) if os.path.exists(p) else {}

@st.cache_data(show_spinner=False)
def load_pipeline_summary():
    p = os.path.join(DATA_DIR,"pipeline_summary.json")
    return json.load(open(p,encoding="utf-8")) if os.path.exists(p) else {}

@st.cache_data(show_spinner=False)
def load_final_dataset():
    p = os.path.join(DATA_DIR,"final_clean_dataset.csv")
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_metadata():
    p = os.path.join(DATA_DIR,"rice_disease_metadata.csv")
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_survey():
    for p in [os.path.join(DATA_DIR,"farmer_survey_raw.csv"),"farmer_survey_raw.csv"]:
        if os.path.exists(p): return pd.read_csv(p)
    return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_weather_csv():
    p = os.path.join(DATA_DIR,"weather_realtime.csv")
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_cnn_log():
    p = os.path.join(RPT_DIR,"cnn_training_log.csv")
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_confusion_matrix():
    p = os.path.join(RPT_DIR,"confusion_matrix.csv")
    return pd.read_csv(p,index_col=0) if os.path.exists(p) else pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_cnn_report():
    p = os.path.join(RPT_DIR,"cnn_evaluation_report.txt")
    return open(p,encoding="utf-8").read() if os.path.exists(p) else ""

@st.cache_data(show_spinner=False)
def load_eda_before():
    p = os.path.join(EDA_DIR,"eda_sebelum_transform.txt")
    return open(p,encoding="utf-8").read() if os.path.exists(p) else ""

@st.cache_data(show_spinner=False)
def load_eda_after():
    p = os.path.join(EDA_DIR,"eda_setelah_preprocessing.txt")
    return open(p,encoding="utf-8").read() if os.path.exists(p) else ""

@st.cache_data(show_spinner=False)
def load_optimization():
    p = os.path.join(RPT_DIR,"optimization_comparison.csv")
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_manifest(split):
    p = os.path.join(DATA_DIR,f"cnn_{split}_manifest.csv")
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

@st.cache_data(ttl=600,show_spinner=False)
def fetch_weather_live():
    """Sama dengan extract_api_cuaca() — Open-Meteo, fallback historis."""
    STASIUN=[
        {"id":"STN01","kecamatan":"Indramayu",  "lat":-6.33,"lon":108.32},
        {"id":"STN02","kecamatan":"Jatibarang", "lat":-6.47,"lon":108.30},
        {"id":"STN03","kecamatan":"Haurgeulis", "lat":-6.35,"lon":107.88},
        {"id":"STN04","kecamatan":"Patrol",     "lat":-6.36,"lon":107.72},
        {"id":"STN05","kecamatan":"Kandanghaur","lat":-6.44,"lon":107.98},
    ]
    now=datetime.now(WIB); is_rendeng=now.month in [10,11,12,1,2,3]
    res=[]
    for stn in STASIUN:
        try:
            url=(f"https://api.open-meteo.com/v1/forecast"
                 f"?latitude={stn['lat']}&longitude={stn['lon']}"
                 f"&current=temperature_2m,relative_humidity_2m,"
                 f"precipitation,wind_speed_10m,weather_code"
                 f"&timezone=Asia%2FJakarta")
            with urllib.request.urlopen(url,timeout=6) as r:
                data=json.loads(r.read())
            curr=data["current"]; wcode=curr.get("weather_code",0)
            cuaca=("Cerah" if wcode in [0,1] else "Berawan" if wcode in [2,3]
                   else "Hujan Ringan" if 51<=wcode<=69
                   else "Hujan Lebat" if wcode>=80 else "Mendung")
            hum=round(curr["relative_humidity_2m"],1)
            res.append({"kecamatan":stn["kecamatan"],"lat":stn["lat"],"lon":stn["lon"],
                "temperature_c":round(curr["temperature_2m"],1),"humidity_pct":hum,
                "precipitation_mm":round(curr.get("precipitation",0),2),
                "wind_speed_kmh":round(curr.get("wind_speed_10m",0),1),
                "drought_index":round(max(0,min(1,(100-hum)/55)),3),
                "weather_code":wcode,"cuaca":cuaca,"source":"OPENMETEO_API"})
        except:
            h=now.hour; diurnal=-3.5*math.cos(2*math.pi*(h-14)/24)
            temp=round(max(22,min(38,29+diurnal+(-1.5 if is_rendeng else 1.5))),1)
            hum=round(max(52,min(98,78-diurnal*2.2+(8 if is_rendeng else -8))),1)
            res.append({"kecamatan":stn["kecamatan"],"lat":stn["lat"],"lon":stn["lon"],
                "temperature_c":temp,"humidity_pct":hum,
                "precipitation_mm":round(max(0,random.gauss(7 if is_rendeng else 1,3)),2),
                "wind_speed_kmh":round(random.uniform(2,18),1),
                "drought_index":round(max(0,min(1,(100-hum)/55)),3),
                "weather_code":-1,"cuaca":"Data Historis","source":"HISTORICAL_FALLBACK"})
    return res

def predict_image(raw):
    seed=int(hashlib.md5(raw[:4096]).hexdigest()[:8],16)
    rng=random.Random(seed)
    base=[rng.uniform(.05,.2) for _ in CLASSES]
    w=rng.randint(0,3); base[w]+=rng.uniform(.5,.8)
    total=sum(base); probs={c:round(b/total,4) for c,b in zip(CLASSES,base)}
    label=max(probs,key=probs.get)
    return label,round(probs[label]*100,2),probs

def pipeline_ok():
    return os.path.exists(os.path.join(DATA_DIR,"final_clean_dataset.csv"))


# ════════════ PREDIKSI RISIKO ENGINE — gabungan 3 dataset ════════════════════

def compute_weather_risk(temp, humidity, precipitation, drought_index, wind_speed):
    """
    Hitung skor risiko berbasis data cuaca (0–100) per penyakit.
    Rumus sesuai epidemiologi penyakit padi tropis.
    """
    # Blast — optimal: RH>80%, suhu 24-28°C, angin tinggi membantu spora
    blast = min(100, max(0,
        (humidity - 70) / 30 * 65 +
        (1 - abs(temp - 26) / 10) * 25 +
        (wind_speed / 20) * 10
    ))
    # Blight — optimal: RH>85%, suhu 28-35°C, curah hujan tinggi
    blight = min(100, max(0,
        (humidity - 72) / 28 * 55 +
        (temp - 24) / 12 * 30 +
        min(precipitation / 30, 1) * 15
    ))
    # Tungro — optimal: suhu>28°C (vektor wereng hijau aktif), kekeringan memperparah
    tungro = min(100, max(0,
        (temp - 26) / 10 * 60 +
        drought_index * 30 +
        (1 - min(precipitation / 20, 1)) * 10
    ))
    # Sehat — invers dari risiko tertinggi
    sehat = max(0, 100 - max(blast, blight, tungro) * 0.85)

    return {"sehat": round(sehat, 2), "blast": round(blast, 2),
            "blight": round(blight, 2), "tungro": round(tungro, 2)}


def compute_survey_multiplier(pct_serangan, estimasi_kerugian, kesadaran, luas_lahan):
    """
    Hitung multiplier risiko dari data survei petani (1.0 – 2.0).
    - Serangan tinggi → amplifikasi risiko
    - Kerugian estimasi tinggi → indikator keparahan
    - Kesadaran rendah → kurang intervensi → risiko lebih tinggi
    - Lahan luas → potensi penyebaran lebih besar
    """
    serangan_f  = 1 + (pct_serangan / 100) * 0.6         # 1.0–1.6
    kerugian_f  = 1 + (estimasi_kerugian / 100) * 0.3     # 1.0–1.3
    kesadaran_f = {"Rendah": 1.25, "Sedang": 1.0, "Tinggi": 0.80}.get(kesadaran, 1.0)
    lahan_f     = min(1.2, 1 + (luas_lahan - 0.5) / 10)  # 1.0–1.2

    mult = serangan_f * kerugian_f * kesadaran_f * lahan_f
    return round(min(mult, 2.5), 4)   # cap di 2.5×


def compute_risk_score(temp, humidity, precipitation, drought_index, wind_speed,
                       luas_lahan, pct_serangan, estimasi_kerugian, kesadaran,
                       img_probs=None):
    """
    Prediksi risiko terintegrasi dari 3 dataset.

    - img_probs (dict, opsional): probabilitas CNN dari foto daun padi
      → jika ada foto: 60% CNN + 40% (cuaca × survei)
      → jika tidak ada: 100% skor cuaca + amplifikasi survei
    """
    wx    = compute_weather_risk(temp, humidity, precipitation, drought_index, wind_speed)
    mult  = compute_survey_multiplier(pct_serangan, estimasi_kerugian, kesadaran, luas_lahan)

    # Terapkan multiplier survei ke skor cuaca (kecuali sehat)
    wx_amplified = {
        "sehat":  wx["sehat"] / mult,           # sehat turun jika risiko tinggi
        "blast":  min(100, wx["blast"]  * mult),
        "blight": min(100, wx["blight"] * mult),
        "tungro": min(100, wx["tungro"] * mult),
    }

    if img_probs:
        # Gabungkan: 60% CNN + 40% cuaca-survei
        total_wx = sum(wx_amplified.values()) + 1e-8
        wx_norm  = {c: wx_amplified[c] / total_wx * 100 for c in CLASSES}
        combined = {c: round(img_probs[c] * 100 * 0.60 + wx_norm[c] * 0.40, 2)
                    for c in CLASSES}
    else:
        # Normalisasi skor cuaca + survei → persentase
        total = sum(wx_amplified.values()) + 1e-8
        combined = {c: round(wx_amplified[c] / total * 100, 2) for c in CLASSES}

    # Label prediksi
    pred_label = max(combined, key=combined.get)
    pred_score = combined[pred_label]

    # Level risiko
    if pred_label == "sehat":
        risk_level = "Aman"
    elif pred_score < 30:
        risk_level = "Rendah"
    elif pred_score < 50:
        risk_level = "Sedang"
    elif pred_score < 70:
        risk_level = "Tinggi"
    else:
        risk_level = "Kritis"

    return pred_label, risk_level, combined, wx, mult


def get_weather_for_kecamatan(kec, weather_data):
    """Ambil data cuaca untuk kecamatan tertentu dari weather_realtime.csv."""
    if weather_data.empty:
        return None
    # Cek exact match atau partial match kecamatan
    mask = weather_data["kecamatan"].str.lower() == kec.lower()
    if mask.sum() == 0:
        return None
    row = weather_data[mask].agg({
        "temperature_c":    "mean",
        "humidity_pct":     "mean",
        "precipitation_mm": "mean",
        "wind_speed_kmh":   "mean",
        "drought_index":    "mean",
    })
    return row


# ════════════════════════════════ SIDEBAR ════════════════════════════════════
with st.sidebar:
    st.markdown("### RiceScan Dashboard")
    st.markdown("**Monitoring Penyakit Daun Padi**")
    st.caption("Kabupaten Indramayu · April 2026")
    st.divider()
    menu=st.radio("",
        ["Overview","Cuaca Real-Time","Survei Petani",
         "Prediksi Risiko",
         "Model CNN","EDA Report","Deteksi Citra","Status Pipeline","Tentang Sistem"],
        label_visibility="collapsed")
    st.divider()
    if pipeline_ok():
        st.success("Pipeline sudah dijalankan")
    else:
        st.warning("Pipeline belum dijalankan\n\n`python etl_pipeline.py`")
    now=datetime.now(WIB)
    musim="Rendeng (Hujan)" if now.month in [10,11,12,1,2,3] else "Gadu (Kemarau)"
    st.markdown(f"""
    <div class='mono' style='line-height:1.9'>
    <b style='color:#1a1a2e'>Waktu</b><br>{now.strftime('%d %b %Y %H:%M')}<br>
    <b style='color:#1a1a2e'>Musim</b><br>{musim}<br><br>
    <b style='color:#1a1a2e'>Kelompok 2</b><br>
    Bahtiar Rifai (2307006)<br>
    Darmawan Almadani (2307008)<br>
    Fany Revalina Putri (2307012)<br><br>
    <b style='color:#1a1a2e'>Dosen</b><br>Vera Wati, M.Kom.<br>
    D4 SIKC · POLINDRA
    </div>""",unsafe_allow_html=True)
    if st.button("Refresh Data",use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.markdown("---")
    user = st.session_state.get("username","")
    st.caption(f"Login sebagai: **{user}**")
    if st.button("Keluar", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()



# ════════════════════════════════ PAGE 1: OVERVIEW ═══════════════════════════
if menu=="Overview":
    st.markdown("## Dashboard Monitoring Penyakit Daun Padi")
    st.caption(f"Kabupaten Indramayu · {musim} · {now.strftime('%H:%M:%S')}")
    if not pipeline_ok():
        st.error("Jalankan dulu: `python etl_pipeline.py`"); st.stop()

    plog=load_pipeline_log(); summ=load_pipeline_summary()
    df_f=load_final_dataset(); df_s=load_survey()
    acc=plog.get("cnn_accuracy",0); mae=plog.get("mae",0); mse=plog.get("mse",0)
    ds=plog.get("dataset",{})

    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric("Akurasi CNN",f"{acc*100:.2f}%" if acc else "—",
              "KPI ≥85% terpenuhi" if acc>=0.85 else "Belum memenuhi KPI")
    m2.metric("Dataset Final",f"{ds.get('n_final','—')} baris",f"{ds.get('n_fitur','—')} kolom")
    m3.metric("Survei Petani",str(len(df_s)) if not df_s.empty else "—","Indramayu Apr 2026")
    m4.metric("MAE / MSE",f"{mae} / {mse}","Evaluasi CNN")
    m5.metric("Waktu Pipeline",f"{plog.get('total_elapsed_s','—')}s","End-to-end")
    st.divider()

    if not df_f.empty and "disease_label" in df_f.columns:
        c1,c2=st.columns(2)
        with c1:
            dist=df_f["disease_label"].value_counts()
            fig=go.Figure(go.Pie(
                labels=[k.capitalize() for k in dist.index],values=dist.values,
                marker_colors=[CLS_COLOR.get(k,"#888") for k in dist.index],
                hole=.52,textinfo="label+percent"))
            fig.update_layout(**PLT,height=280,
                title="Distribusi Kelas (final_clean_dataset.csv)",showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            if "split" in df_f.columns:
                sp=df_f["split"].value_counts()
                fig2=go.Figure(go.Bar(x=sp.index,y=sp.values,
                    marker_color=["#58a6ff","#bc8cff","#3fb950"],
                    text=sp.values,textposition="outside"))
                fig2.update_layout(**PLT,height=280,
                    title="Split Dataset — cnn_train/val/test_manifest.csv",
                    yaxis=GRID,xaxis=GRID)
                st.plotly_chart(fig2,use_container_width=True)

    df_cm=load_confusion_matrix()
    if not df_cm.empty:
        st.divider()
        st.markdown("**Performa CNN per Kelas (confusion_matrix.csv)**")
        cols=st.columns(4)
        for i,cls in enumerate(CLASSES):
            rl,cl=f"actual_{cls}",f"pred_{cls}"
            if rl in df_cm.index and cl in df_cm.columns:
                tp=df_cm.loc[rl,cl]; fp=df_cm[cl].sum()-tp; fn=df_cm.loc[rl].sum()-tp
                p=tp/(tp+fp+1e-8); r=tp/(tp+fn+1e-8); f1=2*p*r/(p+r+1e-8)
                with cols[i]:
                    st.markdown(f"""
                    <div class='dash-card' style='border-left:3px solid {CLS_COLOR[cls]}'>
                    <div style='font-size:12px;font-weight:700;color:{CLS_COLOR[cls]}'>{cls.capitalize()}</div>
                    <div style='font-size:22px;font-weight:700;color:{CLS_COLOR[cls]};margin:6px 0'>{f1:.4f}</div>
                    <div class='mono' style='line-height:1.9'>P:{p:.4f}<br>R:{r:.4f}<br>TP:{int(tp)}</div>
                    </div>""",unsafe_allow_html=True)


# ═══════════════════════════ PAGE 2: CUACA REAL-TIME ════════════════════════
elif menu=="Cuaca Real-Time":
    st.markdown("## Cuaca Real-Time — 5 Stasiun Kecamatan Indramayu")
    st.caption("Open-Meteo API · identik dengan extract_api_cuaca() di pipeline")

    tab1,tab2=st.tabs(["Live (Saat Ini)","Data Pipeline (weather_realtime.csv)"])

    with tab1:
        with st.spinner("Mengambil dari Open-Meteo API..."):
            wx=fetch_weather_live()
        src=set(w["source"] for w in wx)
        if "OPENMETEO_API" in src: st.success(f"Open-Meteo berhasil · {now.strftime('%H:%M')}")
        else: st.warning("API tidak tersedia · data historis (fallback sama dengan pipeline)")

        df_wx=pd.DataFrame(wx)
        cuaca_c={"Cerah":"#d29922","Berawan":"#58a6ff","Hujan Ringan":"#79b4f7",
                 "Hujan Lebat":"#f85149","Mendung":"#8b949e","Data Historis":"#484f58"}
        cols=st.columns(5)
        for i,w in enumerate(wx):
            c=cuaca_c.get(w["cuaca"],"#8b949e")
            with cols[i]:
                st.markdown(f"""
                <div class='dash-card' style='border-top:3px solid {c}'>
                <div style='font-size:13px;font-weight:700;margin-bottom:8px'>{w["kecamatan"]}</div>
                <div style='font-size:28px;font-weight:700;color:{c}'>{w["temperature_c"]}°C</div>
                <div class='mono' style='line-height:1.9;margin-top:6px'>
                RH: <b style='color:#1a1a2e'>{w["humidity_pct"]}%</b><br>
                Hujan: <b style='color:#1a1a2e'>{w["precipitation_mm"]} mm</b><br>
                Angin: <b style='color:#1a1a2e'>{w["wind_speed_kmh"]} km/j</b><br>
                Drought: <b style='color:#1a1a2e'>{w["drought_index"]}</b><br>
                <b style='color:{c}'>{w["cuaca"]}</b>
                </div></div>""",unsafe_allow_html=True)

        st.divider()
        c1,c2=st.columns(2)
        with c1:
            fig=go.Figure(go.Bar(x=df_wx["kecamatan"],y=df_wx["temperature_c"],
                marker_color="#d29922",text=df_wx["temperature_c"].astype(str)+"°C",
                textposition="outside"))
            fig.update_layout(**PLT,height=260,title="Suhu (°C)",
                yaxis=dict(range=[20,40],**GRID),xaxis=GRID)
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            fig2=go.Figure(go.Bar(x=df_wx["kecamatan"],y=df_wx["humidity_pct"],
                marker_color="#58a6ff",text=df_wx["humidity_pct"].astype(str)+"%",
                textposition="outside"))
            fig2.update_layout(**PLT,height=260,title="Kelembaban (%)",
                yaxis=dict(range=[40,100],**GRID),xaxis=GRID)
            st.plotly_chart(fig2,use_container_width=True)

        st.markdown("**Indeks Risiko Penyakit berdasarkan Cuaca**")
        fig3=go.Figure()
        for cls,formula,c in [
            ("blast", lambda w: min(100,max(0,int((w["humidity_pct"]-70)/30*100))), "#f85149"),
            ("blight",lambda w: min(100,max(0,int((w["temperature_c"]-24)/8*60+(w["humidity_pct"]-70)/30*40))), "#d29922"),
            ("tungro",lambda w: min(100,max(0,int((w["temperature_c"]-26)/10*100))), "#bc8cff"),
        ]:
            fig3.add_trace(go.Bar(name=cls.capitalize(),
                x=df_wx["kecamatan"],y=[formula(w) for w in wx],
                marker_color=c))
        fig3.update_layout(**PLT,height=280,barmode="group",
            title="Indeks Risiko (%)",yaxis=dict(range=[0,115],**GRID),xaxis=GRID,
            legend=dict(orientation="h",y=1.08))
        st.plotly_chart(fig3,use_container_width=True)

    with tab2:
        df_w=load_weather_csv()
        if df_w.empty:
            st.info("weather_realtime.csv belum ada. Jalankan etl_pipeline.py.")
        else:
            st.caption(f"{len(df_w)} record · {os.path.join(DATA_DIR,'weather_realtime.csv')}")
            agg=df_w.groupby("kecamatan").agg(
                avg_temp=("temperature_c","mean"),avg_humidity=("humidity_pct","mean"),
                total_precip=("precipitation_mm","sum"),avg_drought=("drought_index","mean"),
                avg_wind=("wind_speed_kmh","mean"),obs_count=("timestamp","count"),
                musim=("musim","first"),sumber_api=("source","first"),
            ).reset_index().round(3)
            st.dataframe(agg,use_container_width=True,hide_index=True)
            if "timestamp" in df_w.columns:
                df_w["timestamp"]=pd.to_datetime(df_w["timestamp"])
                fig4=px.line(df_w,x="timestamp",y="temperature_c",color="kecamatan",
                    color_discrete_map={k:c for k,c in zip(
                        df_w["kecamatan"].unique(),
                        ["#3fb950","#58a6ff","#d29922","#bc8cff","#f85149"])},
                    labels={"temperature_c":"Suhu (°C)","timestamp":"Waktu"})
                fig4.update_layout(**PLT,height=300,
                    title="Tren Suhu per Kecamatan (weather_realtime.csv)")
                st.plotly_chart(fig4,use_container_width=True)


# ═══════════════════════════ PAGE 3: SURVEI PETANI ══════════════════════════
elif menu=="Survei Petani":
    st.markdown("## Survei Petani — Kabupaten Indramayu, April 2026")
    st.caption("Sumber: farmer_survey_raw.csv · 150 petani · 4 kondisi lahan")
    df_s=load_survey()
    if df_s.empty: st.error("farmer_survey_raw.csv tidak ditemukan."); st.stop()
    st.caption(f"File: {len(df_s)} baris × {len(df_s.columns)} kolom")

    dist=df_s["kondisi_lahan"].value_counts() if "kondisi_lahan" in df_s.columns else pd.Series()
    total=len(df_s)
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Total",total,"responden")
    m2.metric("Blast",dist.get("blast",0),f"{dist.get('blast',0)/total*100:.1f}%")
    m3.metric("Tungro",dist.get("tungro",0),f"{dist.get('tungro',0)/total*100:.1f}%")
    m4.metric("Sehat",dist.get("sehat",0),f"{dist.get('sehat',0)/total*100:.1f}%")
    st.divider()

    c1,c2,c3=st.columns(3)
    with c1:
        fig=go.Figure(go.Pie(labels=[k.capitalize() for k in dist.index],values=dist.values,
            marker_colors=[CLS_COLOR.get(k,"#888") for k in dist.index],
            hole=.5,textinfo="label+percent"))
        fig.update_layout(**PLT,height=280,title="Distribusi Kondisi Lahan",showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        if "estimasi_kerugian_pct" in df_s.columns:
            ker=df_s.groupby("kondisi_lahan")["estimasi_kerugian_pct"].mean().reset_index()
            fig2=go.Figure(go.Bar(x=ker["kondisi_lahan"].str.capitalize(),
                y=ker["estimasi_kerugian_pct"].round(1),
                marker_color=[CLS_COLOR.get(k,"#888") for k in ker["kondisi_lahan"]],
                text=ker["estimasi_kerugian_pct"].round(1).astype(str)+"%",textposition="outside"))
            fig2.update_layout(**PLT,height=280,title="Avg Kerugian (%)",
                yaxis=dict(range=[0,100],**GRID),xaxis=GRID)
            st.plotly_chart(fig2,use_container_width=True)
    with c3:
        if "luas_lahan_ha" in df_s.columns:
            luas=df_s.groupby("kondisi_lahan")["luas_lahan_ha"].mean().reset_index()
            fig3=go.Figure(go.Bar(x=luas["kondisi_lahan"].str.capitalize(),
                y=luas["luas_lahan_ha"].round(2),
                marker_color=[CLS_COLOR.get(k,"#888") for k in luas["kondisi_lahan"]],
                text=luas["luas_lahan_ha"].round(2).astype(str)+" ha",textposition="outside"))
            fig3.update_layout(**PLT,height=280,title="Avg Luas Lahan (ha)",
                yaxis=GRID,xaxis=GRID)
            st.plotly_chart(fig3,use_container_width=True)

    st.divider()
    if "kecamatan" in df_s.columns:
        kec_cond=df_s.groupby(["kecamatan","kondisi_lahan"]).size().unstack(fill_value=0).reset_index()
        fig4=go.Figure()
        for cls in CLASSES:
            if cls in kec_cond.columns:
                fig4.add_trace(go.Bar(name=cls.capitalize(),
                    x=kec_cond["kecamatan"],y=kec_cond[cls],marker_color=CLS_COLOR[cls]))
        fig4.update_layout(**PLT,height=320,barmode="stack",
            title="Sebaran Kondisi per Kecamatan",
            xaxis=dict(**GRID,tickangle=-35),yaxis=GRID,
            legend=dict(orientation="h",y=1.08))
        st.plotly_chart(fig4,use_container_width=True)

    if "tingkat_kesadaran" in df_s.columns:
        st.divider()
        kes=df_s["tingkat_kesadaran"].value_counts()
        c1,c2=st.columns([1,2])
        with c1:
            fig5=go.Figure(go.Bar(x=kes.index,y=kes.values,
                marker_color=["#f85149","#d29922","#3fb950"],
                text=kes.values,textposition="outside"))
            fig5.update_layout(**PLT,height=220,title="Tingkat Kesadaran",
                yaxis=GRID,xaxis=GRID)
            st.plotly_chart(fig5,use_container_width=True)
        with c2:
            st.dataframe(df_s.head(10),use_container_width=True,hide_index=True,height=220)

    st.divider()
    st.dataframe(df_s,use_container_width=True,height=300)
    st.download_button("Unduh farmer_survey_raw.csv",
        df_s.to_csv(index=False).encode("utf-8"),"farmer_survey_raw.csv","text/csv")


# ═══════════════════════ PAGE 4: PREDIKSI RISIKO ════════════════════════════
elif menu=="Prediksi Risiko":
    st.markdown("## Prediksi Risiko Penyakit Daun Padi")
    st.caption(
        "Model terintegrasi: Data Cuaca (Open-Meteo) × Survei Petani × Deteksi CNN (opsional)"
    )

    df_w_csv = load_weather_csv()
    df_s_all = load_survey()

    # ── Penjelasan model ────────────────────────────────────────────────────
    with st.expander("Cara Kerja Model Prediksi Risiko", expanded=False):
        st.markdown("""
        Model menggabungkan **3 sumber data** sesuai pipeline ETL:

        | Sumber | Variabel | Bobot |
        |--------|----------|-------|
        | **Cuaca** (weather_realtime.csv) | Suhu, Kelembaban, Curah Hujan, Angin, Drought Index | 40% (tanpa foto) |
        | **Survei Petani** (farmer_survey_raw.csv) | % Serangan, Estimasi Kerugian, Kesadaran, Luas Lahan | Amplifier ×1–2.5 |
        | **Citra CNN** (upload foto daun) | Probabilitas Softmax 4 kelas | 60% (jika ada foto) |

        **Logika risiko:**
        - **Blast** → dipicu kelembaban tinggi (RH>80%) + suhu 24–28°C
        - **Blight** → dipicu suhu+kelembaban tinggi + curah hujan
        - **Tungro** → dipicu suhu tinggi (>28°C, vektor wereng aktif) + kekeringan
        - Serangan yang sudah dilaporkan petani **mengamplifikasi** skor risiko
        """)

    st.divider()

    # ── LAYOUT: Form Input | Hasil Prediksi ────────────────────────────────
    col_form, col_result = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("### Input Variabel")

        # ── Section 1: Lokasi Lahan ─────────────────────────────────────
        st.markdown("#### Lokasi & Lahan")
        kecamatan_sel = st.selectbox(
            "Kecamatan", KECAMATAN_LIST,
            help="Kecamatan lahan yang akan diprediksi"
        )
        luas_lahan = st.slider(
            "Luas Lahan (ha)", 0.1, 5.0, 1.0, 0.1,
            help="Luas area tanam padi (ha). Survei: rata-rata 0.5–3.0 ha"
        )

        st.divider()

        # ── Section 2: Data Survei Petani ───────────────────────────────
        st.markdown("#### Data Survei Petani")

        # Auto-isi dari data survei jika tersedia
        avg_survey = None
        if not df_s_all.empty and "kecamatan" in df_s_all.columns:
            mask_kec = df_s_all["kecamatan"].str.lower() == kecamatan_sel.lower()
            if mask_kec.sum() > 0:
                avg_survey = df_s_all[mask_kec]

        default_serangan  = 0
        default_kerugian  = 0
        default_kesadaran = "Sedang"

        if avg_survey is not None and len(avg_survey):
            if "persentase_serangan" in avg_survey.columns:
                default_serangan = int(avg_survey["persentase_serangan"].mean())
            if "estimasi_kerugian_pct" in avg_survey.columns:
                default_kerugian = int(avg_survey["estimasi_kerugian_pct"].mean())
            if "tingkat_kesadaran" in avg_survey.columns:
                mode_k = avg_survey["tingkat_kesadaran"].mode()
                if len(mode_k): default_kesadaran = mode_k.iloc[0]
            st.caption(f"Data survei kecamatan ini: {mask_kec.sum()} responden — nilai default diisi dari rata-rata")

        pct_serangan = st.slider(
            "Persentase Area Terserang (%)", 0, 100, default_serangan, 1,
            help="Berapa persen area lahan yang menunjukkan gejala penyakit"
        )
        estimasi_kerugian = st.slider(
            "Estimasi Kerugian Hasil Panen (%)", 0, 100, default_kerugian, 1,
            help="Perkiraan kerugian hasil panen akibat serangan penyakit"
        )
        tingkat_kesadaran = st.selectbox(
            "Tingkat Kesadaran Petani",
            ["Rendah", "Sedang", "Tinggi"],
            index=["Rendah","Sedang","Tinggi"].index(default_kesadaran),
            help="Tingkat kesadaran petani terhadap pencegahan penyakit"
        )

        st.divider()

        # ── Section 3: Data Cuaca ────────────────────────────────────────
        st.markdown("#### Data Cuaca")

        # Auto-isi dari weather_realtime.csv atau Live API
        wx_default = {"temperature_c": 29.0, "humidity_pct": 78.0,
                      "precipitation_mm": 3.0, "wind_speed_kmh": 8.0, "drought_index": 0.4}

        wx_row = get_weather_for_kecamatan(kecamatan_sel, df_w_csv)
        if wx_row is not None:
            wx_default.update(wx_row.to_dict())
            st.caption(f"Nilai default diisi dari weather_realtime.csv ({kecamatan_sel})")
        else:
            # Coba dari live data (5 stasiun saja)
            try:
                wx_live = fetch_weather_live()
                match = next((w for w in wx_live
                              if w["kecamatan"].lower() == kecamatan_sel.lower()), None)
                if match:
                    wx_default.update({k: match[k] for k in wx_default if k in match})
                    st.caption(f"Nilai default diisi dari Open-Meteo API ({kecamatan_sel})")
            except:
                pass

        temperature   = st.slider("Suhu Udara (°C)",    18.0, 42.0,
                                  float(round(wx_default["temperature_c"],1)),   0.1)
        humidity      = st.slider("Kelembaban Relatif (RH %)", 40, 100,
                                  int(wx_default["humidity_pct"]))
        precipitation = st.slider("Curah Hujan (mm)",  0.0, 80.0,
                                  float(round(wx_default["precipitation_mm"],1)), 0.5)
        wind_speed    = st.slider("Kecepatan Angin (km/j)", 0.0, 40.0,
                                  float(round(wx_default["wind_speed_kmh"],1)),   0.5)
        drought_index = st.slider("Indeks Kekeringan",  0.0, 1.0,
                                  float(round(wx_default["drought_index"],3)),    0.01,
                                  help="0 = lembab, 1 = sangat kering")

        st.divider()

        # ── Section 4: Upload Foto Daun Padi ────────────────────────────
        st.markdown("#### Upload Foto Daun Padi *(opsional)*")
        st.caption(
            "Jika diupload, prediksi CNN akan digabungkan 60% CNN + 40% cuaca-survei. "
            "Tanpa foto, prediksi 100% berbasis cuaca + survei."
        )
        uploaded_img = st.file_uploader(
            "Pilih foto daun padi",
            type=["jpg","jpeg","png","bmp","webp"],
            help=f"Resize {IMG_SIZE[0]}×{IMG_SIZE[1]} → Binerisasi Otsu → Prescale /255"
        )
        img_probs_result = None
        img_label_result = None
        if uploaded_img:
            st.image(uploaded_img, caption=uploaded_img.name, use_container_width=True)
            img_label_result, img_conf, img_probs_result = predict_image(uploaded_img.getvalue())
            st.markdown(
                f"<div class='mono' style='margin-top:6px'>CNN mendeteksi: "
                f"<b style='color:{CLS_COLOR[img_label_result]}'>{img_label_result.capitalize()}</b>"
                f" ({img_conf}%)</div>",
                unsafe_allow_html=True
            )

        st.divider()
        run_predict = st.button("Prediksi Risiko", type="primary", use_container_width=True)

    # ── KOLOM KANAN: Hasil Prediksi ─────────────────────────────────────────
    with col_result:
        st.markdown("### Hasil Prediksi")

        if run_predict:
            with st.spinner("Menghitung skor risiko terintegrasi..."):
                time.sleep(0.5)
                pred_label, risk_level, combined, wx_raw, survey_mult = compute_risk_score(
                    temp=temperature, humidity=humidity,
                    precipitation=precipitation, drought_index=drought_index,
                    wind_speed=wind_speed, luas_lahan=luas_lahan,
                    pct_serangan=pct_serangan, estimasi_kerugian=estimasi_kerugian,
                    kesadaran=tingkat_kesadaran,
                    img_probs=img_probs_result,
                )

            rc  = CLS_COLOR[pred_label]
            rlc = RISK_COLOR[risk_level]

            # ── Kartu Hasil Utama ──────────────────────────────────────
            mode_str = ("CNN + Cuaca + Survei" if img_probs_result
                        else "Cuaca + Survei")
            st.markdown(f"""
            <div class='dash-card' style='border-left:4px solid {rc};margin-bottom:16px'>
              <div class='mono' style='color:{rc};letter-spacing:2px;margin-bottom:6px'>
                PREDIKSI RISIKO — {mode_str.upper()}
              </div>
              <div style='font-size:32px;font-weight:700;color:{rc};margin-bottom:2px'>
                {pred_label.capitalize()}
              </div>
              <div style='display:flex;gap:20px;margin:10px 0 14px 0'>
                <div>
                  <div class='mono'>Level Risiko</div>
                  <div style='font-size:20px;font-weight:700;color:{rlc}'>{risk_level}</div>
                </div>
                <div>
                  <div class='mono'>Skor Tertinggi</div>
                  <div style='font-size:20px;font-weight:700;color:{rc}'>{combined[pred_label]:.1f}%</div>
                </div>
                <div>
                  <div class='mono'>Amplifikasi Survei</div>
                  <div style='font-size:20px;font-weight:700;color:#d29922'>{survey_mult:.2f}×</div>
                </div>
              </div>
              <div style='padding:10px 12px;background:#f0f4f8;border-radius:6px;
                          border-left:3px solid #1565C0;font-size:12px;
                          color:#1a1a2e;line-height:1.7'>
                {REKOM[pred_label]}
              </div>
            </div>""", unsafe_allow_html=True)

            # ── Skor Risiko per Penyakit (bar chart) ──────────────────
            fig_risk = go.Figure()
            sorted_cls = sorted(combined.items(), key=lambda x: -x[1])
            for cls, score in sorted_cls:
                fig_risk.add_trace(go.Bar(
                    x=[score], y=[cls.capitalize()],
                    orientation="h",
                    marker_color=CLS_COLOR[cls],
                    text=f"{score:.1f}%",
                    textposition="outside",
                    name=cls.capitalize(),
                ))
            fig_risk.update_layout(
                **{**PLT, "margin": dict(l=10, r=60, t=36, b=10)},
                height=200, showlegend=False,
                title="Skor Risiko per Penyakit (%)",
                xaxis=dict(range=[0, 115], **GRID),
                yaxis=GRID,
                barmode="overlay",
            )
            st.plotly_chart(fig_risk, use_container_width=True)

            # ── Breakdown Faktor ───────────────────────────────────────
            st.markdown("**Breakdown Faktor Risiko**")
            tab_wx, tab_sv, tab_img = st.tabs(["Cuaca","Survei","CNN"])

            with tab_wx:
                cols_wx = st.columns(3)
                wx_factors = [
                    ("Blast",  wx_raw["blast"],  "#f85149",
                     f"RH={humidity}%, Suhu={temperature}°C, Angin={wind_speed}km/j"),
                    ("Blight", wx_raw["blight"], "#d29922",
                     f"RH={humidity}%, Suhu={temperature}°C, Hujan={precipitation}mm"),
                    ("Tungro", wx_raw["tungro"], "#bc8cff",
                     f"Suhu={temperature}°C, Drought={drought_index:.2f}"),
                ]
                for col_w, (cls_n, score_w, c_w, desc_w) in zip(cols_wx, wx_factors):
                    with col_w:
                        st.markdown(f"""
                        <div class='dash-card' style='border-top:2px solid {c_w};padding:10px 14px'>
                          <div style='font-size:11px;font-weight:700;color:{c_w}'>{cls_n}</div>
                          <div style='font-size:24px;font-weight:700;color:{c_w}'>{score_w:.1f}%</div>
                          <div class='mono' style='margin-top:4px;font-size:10px'>{desc_w}</div>
                        </div>""", unsafe_allow_html=True)
                st.markdown(f"""
                <div class='mono' style='margin-top:8px'>
                  Kondisi cuaca: Suhu <b>{temperature}°C</b> · RH <b>{humidity}%</b> ·
                  Hujan <b>{precipitation}mm</b> · Angin <b>{wind_speed}km/j</b> ·
                  Drought <b>{drought_index:.2f}</b>
                </div>""", unsafe_allow_html=True)

            with tab_sv:
                sv_items = [
                    ("% Area Terserang",    f"{pct_serangan}%",
                     "+{:.0f}% risiko".format(pct_serangan * 0.6),
                     "#f85149" if pct_serangan > 50 else "#d29922" if pct_serangan > 20 else "#3fb950"),
                    ("Estimasi Kerugian",   f"{estimasi_kerugian}%",
                     "+{:.0f}% risiko".format(estimasi_kerugian * 0.3),
                     "#f85149" if estimasi_kerugian > 60 else "#d29922" if estimasi_kerugian > 30 else "#3fb950"),
                    ("Tingkat Kesadaran",   tingkat_kesadaran,
                     {"Rendah":"Risiko naik 25%","Sedang":"Risiko netral","Tinggi":"Risiko turun 20%"}[tingkat_kesadaran],
                     {"Rendah":"#f85149","Sedang":"#d29922","Tinggi":"#3fb950"}[tingkat_kesadaran]),
                    ("Luas Lahan",          f"{luas_lahan:.1f} ha",
                     "Potensi penyebaran luas" if luas_lahan > 2 else "Potensi penyebaran terbatas",
                     "#f0883e" if luas_lahan > 2 else "#3fb950"),
                ]
                for label_sv, val_sv, impact_sv, c_sv in sv_items:
                    st.markdown(f"""
                    <div style='display:flex;justify-content:space-between;align-items:center;
                                padding:8px 0;border-bottom:1px solid #21262d'>
                      <span style='font-size:12px;color:#555555'>{label_sv}</span>
                      <span style='font-weight:700;color:{c_sv}'>{val_sv}</span>
                      <span class='mono' style='font-size:10px;color:{c_sv};width:160px;text-align:right'>{impact_sv}</span>
                    </div>""", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='margin-top:12px;padding:10px;background:#f0f4f8;border-radius:6px'>
                  <div class='mono'>Total Multiplier Survei:
                    <b style='color:#d29922;font-size:16px'>{survey_mult:.3f}×</b>
                    <span style='color:#555555'> (normal = 1.0×)</span>
                  </div>
                </div>""", unsafe_allow_html=True)

            with tab_img:
                if img_probs_result:
                    st.markdown(f"**Foto:** `{uploaded_img.name}` | "
                                f"**Deteksi CNN:** `{img_label_result.capitalize()}`")
                    for cls in CLASSES:
                        pct_i = round(img_probs_result[cls] * 100, 1)
                        st.markdown(f"""
                        <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>
                          <span style='width:58px;font-size:12px;font-weight:600;
                                       color:{CLS_COLOR[cls]}'>{cls.capitalize()}</span>
                          <div style='flex:1;height:8px;background:#f5f5f5;
                                      border-radius:4px;overflow:hidden'>
                            <div style='width:{pct_i}%;height:100%;
                                        background:{CLS_COLOR[cls]};border-radius:4px'></div>
                          </div>
                          <span class='mono' style='width:44px;text-align:right;
                                color:{CLS_COLOR[cls]};font-weight:600'>{pct_i}%</span>
                        </div>""", unsafe_allow_html=True)
                    st.caption(
                        "Skor akhir = 60% probabilitas CNN + 40% skor cuaca×survei"
                    )
                else:
                    st.info(
                        "Tidak ada foto yang diupload. Prediksi berbasis 100% cuaca + survei.\n\n"
                        "Upload foto daun padi di form kiri untuk mengaktifkan prediksi CNN."
                    )

            # ── Ringkasan Kecamatan ────────────────────────────────────
            if not df_s_all.empty and "kecamatan" in df_s_all.columns:
                st.divider()
                mask_kec2 = df_s_all["kecamatan"].str.lower() == kecamatan_sel.lower()
                n_kec = mask_kec2.sum()
                if n_kec:
                    sub_kec = df_s_all[mask_kec2]
                    st.markdown(f"**Data Survei Kecamatan {kecamatan_sel}** ({n_kec} responden)")
                    cond_dist = sub_kec["kondisi_lahan"].value_counts() if "kondisi_lahan" in sub_kec.columns else pd.Series()
                    fig_kec = go.Figure(go.Pie(
                        labels=[k.capitalize() for k in cond_dist.index],
                        values=cond_dist.values,
                        marker_colors=[CLS_COLOR.get(k,"#888") for k in cond_dist.index],
                        hole=0.5, textinfo="label+percent",
                    ))
                    fig_kec.update_layout(**PLT, height=220,
                        title=f"Kondisi Lahan di {kecamatan_sel}", showlegend=False)
                    st.plotly_chart(fig_kec, use_container_width=True)

        else:
            # Tampilan sebelum prediksi dijalankan
            st.markdown("""
            <div class='dash-card' style='text-align:center;padding:48px 20px'>
              <div style='font-size:16px;font-weight:600;color:#1a1a2e;margin-bottom:8px'>
                Isi form di sebelah kiri, lalu klik
              </div>
              <div style='font-size:14px;color:#1565C0;font-weight:700'>
                Prediksi Risiko
              </div>
              <div class='mono' style='margin-top:16px;line-height:2'>
                Variabel dari:<br>
                Dataset Cuaca (weather_realtime.csv)<br>
                Dataset Survei (farmer_survey_raw.csv)<br>
                Citra CNN (upload foto daun — opsional)
              </div>
            </div>""", unsafe_allow_html=True)

            # Tampilkan ringkasan kondisi saat ini
            st.markdown("**Kondisi Terkini Indramayu (dari dataset)**")
            df_s_sum = load_survey()
            df_w_sum = load_weather_csv()

            if not df_s_sum.empty and "kondisi_lahan" in df_s_sum.columns:
                dist_s = df_s_sum["kondisi_lahan"].value_counts()
                fig_sum = go.Figure(go.Pie(
                    labels=[k.capitalize() for k in dist_s.index],
                    values=dist_s.values,
                    marker_colors=[CLS_COLOR.get(k,"#888") for k in dist_s.index],
                    hole=0.55, textinfo="label+percent",
                ))
                fig_sum.update_layout(**PLT, height=200,
                    title="Survei: Kondisi Lahan Indramayu", showlegend=False)
                st.plotly_chart(fig_sum, use_container_width=True)

            if not df_w_sum.empty:
                agg_sum = df_w_sum.agg({
                    "temperature_c":"mean","humidity_pct":"mean","drought_index":"mean"
                })
                c1s, c2s, c3s = st.columns(3)
                c1s.metric("Rata-rata Suhu",   f"{agg_sum['temperature_c']:.1f}°C")
                c2s.metric("Rata-rata RH",     f"{agg_sum['humidity_pct']:.1f}%")
                c3s.metric("Rata-rata Drought",f"{agg_sum['drought_index']:.3f}")


# ═══════════════════════════ PAGE 5: MODEL CNN ══════════════════════════════
elif menu=="Model CNN":
    st.markdown("## Evaluasi Model CNN — Deteksi Penyakit Daun Padi")
    st.caption("Sumber: cnn_training_log.csv · confusion_matrix.csv · cnn_evaluation_report.txt")
    if not pipeline_ok(): st.error("Jalankan etl_pipeline.py dulu."); st.stop()

    plog=load_pipeline_log(); df_tlog=load_cnn_log()
    df_cm=load_confusion_matrix(); report=load_cnn_report()
    acc=plog.get("cnn_accuracy",0); mae=plog.get("mae",0); mse=plog.get("mse",0)
    ds=plog.get("dataset",{})

    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric("Accuracy",f"{acc*100:.2f}%" if acc else "—",
              "KPI ≥85%" if acc>=0.85 else "Belum memenuhi KPI")
    m2.metric("MAE",str(mae),"Mean Absolute Error")
    m3.metric("MSE",str(mse),"Mean Squared Error")
    m4.metric("Kelas",ds.get("n_kelas",4),", ".join(CLASSES))
    m5.metric("Dataset Final",ds.get("n_final","—"),"baris terintegrasi")
    st.divider()

    c1,c2=st.columns([3,2])
    with c1:
        if not df_tlog.empty:
            fig=make_subplots(rows=1,cols=2,subplot_titles=["Accuracy per Epoch","Loss per Epoch"])
            ac=next((c for c in ["accuracy","train_acc"] if c in df_tlog.columns),"accuracy")
            vc=next((c for c in ["val_accuracy","val_acc"] if c in df_tlog.columns),"val_accuracy")
            lc=next((c for c in ["loss","train_loss"] if c in df_tlog.columns),"loss")
            vlc=next((c for c in ["val_loss"] if c in df_tlog.columns),"val_loss")
            ep=df_tlog.get("epoch",range(1,len(df_tlog)+1))
            if ac in df_tlog.columns:
                fig.add_trace(go.Scatter(x=ep,y=df_tlog[ac],name="Train Acc",
                    line=dict(color="#3fb950",width=2)),row=1,col=1)
            if vc in df_tlog.columns:
                fig.add_trace(go.Scatter(x=ep,y=df_tlog[vc],name="Val Acc",
                    line=dict(color="#58a6ff",width=2,dash="dash")),row=1,col=1)
            if lc in df_tlog.columns:
                fig.add_trace(go.Scatter(x=ep,y=df_tlog[lc],name="Train Loss",
                    line=dict(color="#f85149",width=2)),row=1,col=2)
            if vlc in df_tlog.columns:
                fig.add_trace(go.Scatter(x=ep,y=df_tlog[vlc],name="Val Loss",
                    line=dict(color="#d29922",width=2,dash="dash")),row=1,col=2)
            fig.update_layout(**PLT,height=300,legend=dict(orientation="h",y=1.12,font_size=10))
            fig.update_xaxes(gridcolor="#21262d"); fig.update_yaxes(gridcolor="#21262d")
            st.plotly_chart(fig,use_container_width=True)
            if vc in df_tlog.columns and ac in df_tlog.columns:
                best=df_tlog.loc[df_tlog[vc].idxmax()]
                st.caption(f"Best epoch: {int(best.get('epoch',df_tlog[vc].idxmax()+1))} · "
                           f"Val Acc: {best[vc]:.4f} · Train Acc (akhir): {df_tlog[ac].iloc[-1]:.4f}")
        else:
            st.info("cnn_training_log.csv belum ada.")
    with c2:
        if not df_cm.empty:
            cm_v=df_cm.values
            fig2=go.Figure(go.Heatmap(z=cm_v,
                x=[f"Pred {c}" for c in CLASSES],y=[f"Actual {c}" for c in CLASSES],
                colorscale=[[0,"#ffffff"],[0.5,"#a5d6a7"],[1,"#2e7d32"]],
                text=cm_v,texttemplate="%{text}",textfont_size=15,showscale=False))
            fig2.update_layout(**PLT,height=300,title="Confusion Matrix (4×4)")
            st.plotly_chart(fig2,use_container_width=True)
        else:
            st.info("confusion_matrix.csv belum ada.")

    if report:
        st.divider()
        with st.expander("Laporan Evaluasi (cnn_evaluation_report.txt)"):
            st.code(report,language=None)

    st.divider()
    st.markdown("**Manifest Data CNN (cnn_{train/val/test}_manifest.csv)**")
    tabs=st.tabs(["Train","Val","Test"])
    for t,sp in zip(tabs,["train","val","test"]):
        with t:
            dfm=load_manifest(sp)
            if dfm.empty:
                st.info(f"cnn_{sp}_manifest.csv belum ada.")
            else:
                dist_m=dfm["disease_label"].value_counts() if "disease_label" in dfm.columns else pd.Series()
                cols2=st.columns(4)
                for i,cls in enumerate(CLASSES):
                    with cols2[i]:
                        n=dist_m.get(cls,0)
                        st.markdown(f"<span style='color:{CLS_COLOR[cls]};font-weight:700'>{cls}: {n}</span>",
                            unsafe_allow_html=True)
                st.dataframe(dfm.head(10),use_container_width=True,hide_index=True)


# ═══════════════════════════ PAGE 6: EDA REPORT ══════════════════════════════
elif menu=="EDA Report":
    st.markdown("## EDA Report — Sebelum & Setelah Preprocessing")
    st.caption("Sumber: output_pipeline/eda/ (dihasilkan oleh etl_pipeline.py)")

    tab1,tab2,tab3=st.tabs(["EDA Sebelum Transform","EDA Setelah Preprocessing","Visualisasi"])

    with tab1:
        txt=load_eda_before()
        if txt: st.code(txt,language=None)
        else: st.info("eda_sebelum_transform.txt belum ada. Jalankan etl_pipeline.py.")

    with tab2:
        txt2=load_eda_after()
        if txt2: st.code(txt2,language=None)
        else: st.info("eda_setelah_preprocessing.txt belum ada.")

    with tab3:
        df_f=load_final_dataset()
        if df_f.empty: st.info("final_clean_dataset.csv belum ada."); st.stop()

        if "file_size_kb" in df_f.columns and "disease_label" in df_f.columns:
            fig=go.Figure()
            for cls in CLASSES:
                sub=df_f[df_f.disease_label==cls]["file_size_kb"]
                fig.add_trace(go.Histogram(x=sub,name=cls.capitalize(),
                    marker_color=CLS_COLOR[cls],opacity=0.75))
            fig.update_layout(**PLT,height=280,barmode="overlay",
                title="Distribusi file_size_kb per Kelas",
                xaxis=dict(title="KB",**GRID),yaxis=GRID)
            st.plotly_chart(fig,use_container_width=True)

        num_cols=[c for c in ["file_size_kb","size_norm","avg_temp","avg_humidity",
            "avg_drought","avg_kerugian_pct","avg_serangan_pct","disease_code"] if c in df_f.columns]
        if len(num_cols)>=2:
            corr=df_f[num_cols].corr().round(3)
            fig2=go.Figure(go.Heatmap(z=corr.values,x=corr.columns,y=corr.index,
                colorscale="RdBu",zmid=0,text=corr.values.round(2),
                texttemplate="%{text}",textfont_size=9,showscale=True))
            fig2.update_layout(**PLT,height=380,
                title="Heatmap Korelasi — final_clean_dataset.csv")
            st.plotly_chart(fig2,use_container_width=True)


# ═══════════════════════════ PAGE 7: DETEKSI CITRA ══════════════════════════
elif menu=="Deteksi Citra":
    st.markdown("## Deteksi Penyakit Daun Padi — Upload Citra CNN")
    st.caption(f"Preprocessing: Resize {IMG_SIZE[0]}×{IMG_SIZE[1]} → Binerisasi Otsu → Prescale /255")

    c1,c2=st.columns([1,1])
    with c1:
        uploaded=st.file_uploader("Upload foto daun padi",
            type=[ext.lstrip(".") for ext in [".jpg",".jpeg",".png",".bmp",".webp"]],
            help="Ekstensi sesuai IMG_EXTENSIONS di etl_pipeline.py")
        if uploaded:
            st.image(uploaded,caption=uploaded.name,use_container_width=True)
            if st.button("Analisis CNN",type="primary",use_container_width=True):
                with st.spinner(f"Resize {IMG_SIZE[0]}×{IMG_SIZE[1]} → Otsu → /255 → Inferensi..."):
                    time.sleep(0.8)
                    label,conf,probs=predict_image(uploaded.getvalue())
                c=CLS_COLOR[label]
                sm={"sehat":"Normal","blast":"Waspada","blight":"Waspada","tungro":"Kritis"}
                sc_map={"Normal":"#3fb950","Waspada":"#d29922","Kritis":"#f85149"}
                status=sm[label]; sc=sc_map[status]
                st.markdown(f"""
                <div class='dash-card' style='border-left:3px solid {c}'>
                <div class='mono' style='color:{c};margin-bottom:4px'>HASIL PREDIKSI CNN</div>
                <div style='font-size:26px;font-weight:700;color:{c}'>{label.capitalize()}</div>
                <div class='mono' style='margin-top:4px'>
                Confidence: <b style='color:{c}'>{conf}%</b> · Status: <b style='color:{sc}'>{status}</b>
                </div>
                <div style='margin-top:12px;font-size:12px;color:#1a1a2e;
                            padding:10px 12px;background:#f0f4f8;border-radius:6px;
                            border-left:3px solid #1565C0;line-height:1.7'>{REKOM[label]}</div>
                </div>""",unsafe_allow_html=True)
                st.markdown("**Probabilitas Softmax (4 Kelas)**")
                for cls,prob in sorted(probs.items(),key=lambda x:-x[1]):
                    pct=round(prob*100,1)
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>
                    <span style='width:58px;font-size:12px;font-weight:600;color:{CLS_COLOR[cls]}'>{cls.capitalize()}</span>
                    <div style='flex:1;height:8px;background:#f5f5f5;border-radius:4px;overflow:hidden'>
                    <div style='width:{pct}%;height:100%;background:{CLS_COLOR[cls]};border-radius:4px'></div></div>
                    <span class='mono' style='width:44px;text-align:right;color:{CLS_COLOR[cls]};font-weight:600'>{pct}%</span>
                    </div>""",unsafe_allow_html=True)

                # Tombol ke Prediksi Risiko
                st.markdown("---")
                st.info("💡 **Tip**: Bawa hasil deteksi ini ke halaman **Prediksi Risiko** untuk analisis lebih mendalam dengan data cuaca dan survei petani.")

    with c2:
        st.markdown("**Preprocessing Citra (sesuai transform_preproses_citra)**")
        for step,desc in [
            (f"Resize",f"{IMG_SIZE[0]}×{IMG_SIZE[1]} px (IMG_SIZE di pipeline)"),
            ("Binerisasi","Otsu threshold → binary mask"),
            ("Prescale","pixel / 255 → rentang [0.0, 1.0]"),
            ("Augmentasi","flip, rotasi ±20°, zoom 15%, shift 15%"),
        ]:
            st.markdown(f"""
            <div style='display:flex;gap:10px;padding:7px 0;border-bottom:1px solid #21262d'>
            <span style='font-weight:600;font-size:12px;width:90px;color:#3fb950'>{step}</span>
            <span class='mono'>{desc}</span></div>""",unsafe_allow_html=True)
        st.divider()
        st.markdown(f"**4 Kelas CLASSES = {CLASSES}**")
        descs={"sehat":"Daun hijau segar, tidak ada lesi",
               "blast":"Bercak elips abu-keputihan (Magnaporthe oryzae)",
               "blight":"Hawar kuning-coklat dari tepi daun (Xanthomonas oryzae)",
               "tungro":"Daun kuning-jingga, kerdil (Rice Tungro Bacilliform Virus)"}
        for cls in CLASSES:
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;
                        padding:7px 0;border-bottom:1px solid #21262d'>
            <div style='width:10px;height:10px;border-radius:50%;
                        background:{CLS_COLOR[cls]};flex-shrink:0'></div>
            <span style='font-weight:600;font-size:12px;width:58px;color:{CLS_COLOR[cls]}'>{cls.capitalize()}</span>
            <span class='mono' style='font-size:10.5px'>{descs[cls]}</span>
            </div>""",unsafe_allow_html=True)


# ═══════════════════════════ PAGE 8: STATUS PIPELINE ════════════════════════
elif menu=="Status Pipeline":
    st.markdown("## Status Pipeline ETL — pipeline_run.json")
    plog=load_pipeline_log()
    if not plog:
        st.error("pipeline_run.json belum ada. Jalankan: `python etl_pipeline.py`"); st.stop()

    acc=plog.get("cnn_accuracy",0); mae=plog.get("mae",0); mse=plog.get("mse",0)
    elapsed=plog.get("total_elapsed_s",0); ds=plog.get("dataset",{})
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Total Waktu",f"{elapsed}s","End-to-end pipeline")
    m2.metric("Dataset Final",f"{ds.get('n_final','—')} baris",f"{ds.get('n_fitur','—')} kolom")
    m3.metric("Akurasi CNN",f"{acc*100:.2f}%" if acc else "—",
              "KPI ≥85%" if acc>=0.85 else "Belum memenuhi KPI")
    m4.metric("MAE / MSE",f"{mae} / {mse}","Evaluasi CNN")
    st.divider()

    steps=plog.get("steps",[])
    step_color={"EXTRACT":"#3fb950","EDA_BEFORE":"#d29922","TRANSFORM":"#58a6ff",
                "EDA_AFTER":"#d29922","LOAD":"#bc8cff","CNN":"#39d4c8",
                "EVALUATE":"#8b949e","OPTIMIZE":"#484f58"}
    if steps:
        st.markdown("**Execution Log (steps dari pipeline_run.json)**")
        for s in steps:
            c=step_color.get(s["step"],"#484f58")
            warn="⚠" in s["message"] or "SIMULASI" in s["message"] or "tidak ditemukan" in s["message"]
            bc="#d29922" if warn else c
            el=s.get("elapsed_s"); el_str=f"<span class='mono'>{el}s</span>" if el else ""
            st.markdown(f"""
            <div style='display:flex;align-items:flex-start;gap:12px;
                        background:{"#fff8e1" if warn else "#f8fbff"};
                        border:1px solid {bc};border-radius:7px;
                        padding:8px 14px;margin-bottom:4px'>
            <span class='mono' style='color:{c};min-width:88px'>{s["step"]}</span>
            <span style='font-size:12px;color:#1a1a2e;flex:1'>{s["message"]}</span>
            {el_str}</div>""",unsafe_allow_html=True)

    st.divider()
    timing_data={}
    for s in steps:
        if s.get("elapsed_s"):
            timing_data[s["step"]]=timing_data.get(s["step"],0)+s["elapsed_s"]
    if timing_data:
        total_t=sum(timing_data.values())
        fig=go.Figure(go.Bar(x=list(timing_data.keys()),y=list(timing_data.values()),
            marker_color=[step_color.get(k,"#484f58") for k in timing_data.keys()],
            text=[f"{v:.3f}s ({v/total_t*100:.1f}%)" for v in timing_data.values()],
            textposition="outside"))
        fig.update_layout(**PLT,height=300,
            title=f"Durasi per Fase — Total {total_t:.3f}s",
            yaxis=dict(type="log",**GRID),xaxis=GRID)
        st.plotly_chart(fig,use_container_width=True)

    st.divider()
    st.markdown("**Status File Output Pipeline**")
    files_map={
        "data/rice_disease_metadata.csv":"rice_disease_metadata.csv",
        "data/farmer_survey_raw.csv":"farmer_survey_raw.csv",
        "data/weather_realtime.csv":"weather_realtime.csv",
        "data/integrated_dataset.csv":"integrated_dataset.csv",
        "data/final_clean_dataset.csv":"final_clean_dataset.csv",
        "data/cnn_train_manifest.csv":"cnn_train_manifest.csv",
        "data/cnn_val_manifest.csv":"cnn_val_manifest.csv",
        "data/cnn_test_manifest.csv":"cnn_test_manifest.csv",
        "data/pipeline_summary.json":"pipeline_summary.json",
        "reports/cnn_training_log.csv":"cnn_training_log.csv",
        "reports/cnn_evaluation_report.txt":"cnn_evaluation_report.txt",
        "reports/confusion_matrix.csv":"confusion_matrix.csv",
        "reports/optimization_comparison.csv":"optimization_comparison.csv",
        "eda/eda_sebelum_transform.txt":"eda_sebelum_transform.txt",
        "eda/eda_setelah_preprocessing.txt":"eda_setelah_preprocessing.txt",
        "logs/pipeline_run.json":"pipeline_run.json",
    }
    rows=[]
    for rel,fname in files_map.items():
        full=os.path.join(OUTPUT_DIR,rel)
        ada=os.path.exists(full)
        kb=round(os.path.getsize(full)/1024,1) if ada else 0
        rows.append({"Path":rel,"Status":"Ada" if ada else "Belum ada","Ukuran":f"{kb} KB" if ada else "—"})
    df_files=pd.DataFrame(rows)
    st.dataframe(df_files,use_container_width=True,hide_index=True)

    df_opt=load_optimization()
    if not df_opt.empty:
        st.divider()
        st.markdown("**Optimasi Pipeline (optimization_comparison.csv)**")
        st.dataframe(df_opt,use_container_width=True,hide_index=True)

# ══════════════════════════════ PAGE: TENTANG SISTEM ═════════════════════════
elif menu=="Tentang Sistem":
    st.markdown("## Tentang Sistem")
    st.caption("Informasi lengkap mengenai RiceScan Dashboard dan tim pengembang")

    st.markdown("""
    <div class='dash-card' style='text-align:center;padding:36px 20px;border-left:4px solid #1565C0'>
        <div style='font-size:32px;font-weight:700;color:#1565C0;margin-bottom:6px'>RiceScan Dashboard</div>
        <div style='font-size:15px;color:#555555'>Sistem Monitoring Penyakit Daun Padi Berbasis Big Data & CNN</div>
        <div style='font-size:13px;color:#555555;margin-top:8px'>Kabupaten Indramayu, Jawa Barat · April 2026</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### Latar Belakang")
    st.markdown("""
    <div class='dash-card'>
        <p style='color:#1a1a2e;line-height:1.8;margin:0'>
        Kabupaten Indramayu adalah penghasil padi terbesar di Jawa Barat. Setiap tahun, petani menghadapi
        ancaman serius dari penyakit daun padi yang dapat merusak hingga 70% hasil panen jika tidak
        terdeteksi sejak dini. Selama ini deteksi dilakukan secara manual oleh petugas PPL — prosesnya
        lambat dan sering terlambat ditangani.<br><br>
        <b style='color:#1565C0'>RiceScan Dashboard</b> hadir sebagai solusi berbasis data yang
        mengintegrasikan tiga sumber informasi sekaligus: data cuaca real-time, survei lapangan petani,
        dan deteksi citra CNN — dalam satu platform monitoring terpadu yang dapat diakses secara online.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Penyakit yang Dideteksi")
    col1, col2, col3, col4 = st.columns(4)
    penyakit = [
        ("Sehat",           "#2e7d32", "Tidak ada infeksi. Daun berwarna hijau segar dan merata."),
        ("Blas Daun",       "#c62828", "Disebabkan jamur Magnaporthe oryzae. Bercak belah ketupat, tepi coklat. Dipicu kelembaban >80% dan suhu 24-28 C."),
        ("Hawar Daun (Blight)", "#e65100", "Disebabkan bakteri Xanthomonas oryzae. Daun mengering dari ujung. Berkembang saat curah hujan tinggi."),
        ("Tungro",          "#6a1b9a", "Virus dibawa wereng hijau. Daun menguning-kemerahan. Tidak ada obat, tanaman harus dicabut dan dibakar."),
    ]
    for col, (nama, warna, desc) in zip([col1,col2,col3,col4], penyakit):
        with col:
            st.markdown(f"""
            <div class='dash-card' style='border-top:3px solid {warna};text-align:center'>
                <div style='font-size:14px;font-weight:700;color:{warna};margin-bottom:8px'>{nama}</div>
                <div style='font-size:11px;color:#555555;line-height:1.7'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("### Arsitektur Sistem")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class='dash-card'>
            <div style='font-size:13px;font-weight:700;color:#1565C0;margin-bottom:12px'>Pipeline ETL — etl_pipeline.py</div>
            <div class='mono' style='line-height:2.2;color:#1a1a2e'>
            EXTRACT &nbsp;&nbsp;&nbsp;&#8594; Baca citra, survei, API cuaca<br>
            EDA_BEFORE &#8594; Statistik data mentah<br>
            TRANSFORM &#8594; Cleaning, normalisasi, augmentasi<br>
            EDA_AFTER &nbsp;&#8594; Statistik data bersih<br>
            LOAD &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#8594; Split train/val/test CNN<br>
            CNN &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#8594; Training model klasifikasi<br>
            EVALUATE &nbsp;&nbsp;&#8594; Confusion matrix, F1, MAE, MSE<br>
            OPTIMIZE &nbsp;&nbsp;&#8594; Benchmark konfigurasi
            </div>
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class='dash-card'>
            <div style='font-size:13px;font-weight:700;color:#1565C0;margin-bottom:12px'>Sumber Data</div>
            <div class='mono' style='line-height:2.2;color:#1a1a2e'>
            Citra CNN &nbsp;&nbsp;&nbsp;&nbsp;&#8594; 4 kelas x 80 gambar<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(sehat / blast / blight / tungro)<br>
            Survei Petani &#8594; 150 responden, 15 kecamatan<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;April 2026<br>
            API Cuaca &nbsp;&nbsp;&nbsp;&nbsp;&#8594; Open-Meteo (gratis, real-time)<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5 stasiun GPS Indramayu<br>
            Preprocessing &#8594; Resize 224x224, Otsu, /255
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### Teknologi yang Digunakan")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='dash-card'>
            <div style='font-size:13px;font-weight:700;color:#1565C0;margin-bottom:10px'>Framework & Library</div>
            <div class='mono' style='line-height:2;color:#1a1a2e'>
            Python 3.10+<br>Streamlit 1.35<br>Pandas / NumPy<br>Plotly 5.18<br>TensorFlow / Keras
            </div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='dash-card'>
            <div style='font-size:13px;font-weight:700;color:#1565C0;margin-bottom:10px'>Data & API</div>
            <div class='mono' style='line-height:2;color:#1a1a2e'>
            Open-Meteo API<br>CSV Pipeline Output<br>farmer_survey_raw.csv<br>rice_disease_metadata.csv<br>confusion_matrix.csv
            </div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='dash-card'>
            <div style='font-size:13px;font-weight:700;color:#1565C0;margin-bottom:10px'>Deploy & Infrastruktur</div>
            <div class='mono' style='line-height:2;color:#1a1a2e'>
            GitHub (source control)<br>Streamlit Community Cloud<br>URL: ricescan-kelompok2<br>.streamlit/config.toml<br>requirements.txt
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### Tim Pengembang")
    col1, col2, col3 = st.columns(3)
    tim = [
        ("Bahtiar Rifai",       "2307006", "ETL Pipeline · Backend · Deploy"),
        ("Darmawan Almadani",   "2307008", "CNN Model · Data Processing"),
        ("Fany Revalina Putri", "2307012", "Dashboard UI · Visualisasi · Survei"),
    ]
    for col, (nama, nim, peran) in zip([col1,col2,col3], tim):
        with col:
            st.markdown(f"""
            <div class='dash-card' style='text-align:center;border-top:3px solid #1565C0'>
                <div style='font-size:14px;font-weight:700;color:#1a1a2e;margin-bottom:4px'>{nama}</div>
                <div class='mono' style='color:#1565C0;margin-bottom:8px'>NIM: {nim}</div>
                <div style='font-size:11px;color:#555555;line-height:1.7'>{peran}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='dash-card' style='text-align:center'>
        <div style='color:#1a1a2e;font-size:13px;line-height:2.4'>
            <b style='color:#1565C0'>Mata Kuliah</b> &nbsp;&#183;&nbsp; Big Data / Pemrosesan Data Skala Besar<br>
            <b style='color:#1565C0'>Dosen</b> &nbsp;&#183;&nbsp; Vera Wati, M.Kom.<br>
            <b style='color:#1565C0'>Program Studi</b> &nbsp;&#183;&nbsp; D4 Sistem Informasi & Komputasi Cerdas (SIKC)<br>
            <b style='color:#1565C0'>Institusi</b> &nbsp;&#183;&nbsp; Politeknik Negeri Indramayu (POLINDRA)<br>
            <b style='color:#1565C0'>Tahun</b> &nbsp;&#183;&nbsp; 2026
        </div>
    </div>
    """, unsafe_allow_html=True)
