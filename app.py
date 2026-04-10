import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime, timedelta, date

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Atlas Engineering Services — Trésorerie",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

SOLDE_INITIAL   = 0        # Solde avant la première transaction enregistrée
SEUIL_CRITIQUE  = 10_000
COMPANY_NAME    = "Atlas Engineering Services"

# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN SYSTEM (CSS)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Sidebar ─────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0D1B2A;
    border-right: 1px solid #1E3050;
}
[data-testid="stSidebar"] * { color: #C8D6E5 !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    letter-spacing: 0.3px;
    padding: 6px 0 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #1E3050 !important;
}

/* ── Page background ─────────────────── */
.stApp { background-color: #F4F6F9; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Page title ──────────────────────── */
.page-header {
    background: #0D1B2A;
    padding: 20px 28px;
    border-radius: 6px;
    margin-bottom: 24px;
    border-left: 4px solid #0D6E7A;
}
.page-header h1 {
    color: #FFFFFF;
    font-size: 22px;
    font-weight: 600;
    margin: 0 0 4px 0;
    letter-spacing: 0.3px;
}
.page-header p {
    color: #8BA3B8;
    font-size: 13px;
    margin: 0;
    font-weight: 400;
}

/* ── KPI Cards ───────────────────────── */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E0E6ED;
    border-radius: 6px;
    padding: 18px 20px;
    border-top: 3px solid #0D6E7A;
}
.kpi-card.danger  { border-top-color: #C0392B; }
.kpi-card.warning { border-top-color: #D68910; }
.kpi-card.success { border-top-color: #1E8449; }
.kpi-card.neutral { border-top-color: #2471A3; }

.kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: #7F8C8D;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 24px;
    font-weight: 500;
    color: #0D1B2A;
    line-height: 1.1;
}
.kpi-value.red    { color: #C0392B; }
.kpi-value.green  { color: #1E8449; }
.kpi-value.orange { color: #D68910; }
.kpi-value.blue   { color: #2471A3; }
.kpi-sub {
    font-size: 11px;
    color: #95A5A6;
    margin-top: 4px;
}

/* ── Alerts ──────────────────────────── */
.alert {
    padding: 13px 16px;
    border-radius: 4px;
    margin-bottom: 14px;
    font-size: 13px;
    font-weight: 500;
    border-left: 4px solid;
    line-height: 1.5;
}
.alert-danger  { background: #FDEDEC; border-color: #C0392B; color: #922B21; }
.alert-warning { background: #FDFAF2; border-color: #D68910; color: #9A7D0A; }
.alert-success { background: #EAF5EA; border-color: #1E8449; color: #186A3B; }
.alert-info    { background: #EBF5FB; border-color: #2471A3; color: #1A5276; }

/* ── Section titles ──────────────────── */
.section-title {
    font-size: 13px;
    font-weight: 600;
    color: #0D6E7A;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding-bottom: 8px;
    border-bottom: 1px solid #D5E8EE;
    margin-bottom: 16px;
    margin-top: 8px;
}

/* ── Table ───────────────────────────── */
[data-testid="stDataFrame"] thead th {
    background-color: #0D1B2A !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 12px !important;
}

/* ── Form ────────────────────────────── */
[data-testid="stForm"] {
    background: #FFFFFF;
    border: 1px solid #E0E6ED;
    border-radius: 6px;
    padding: 20px 20px 16px;
}

/* ── Buttons ─────────────────────────── */
.stButton > button {
    background-color: #0D1B2A;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.3px;
    padding: 10px 22px;
    transition: background-color 0.15s;
}
.stButton > button:hover { background-color: #0D6E7A; }

/* ── Sidebar branding ─────────────────── */
.sidebar-brand {
    padding: 12px 0 16px;
    border-bottom: 1px solid #1E3050;
    margin-bottom: 20px;
}
.sidebar-brand .company {
    font-size: 13px;
    font-weight: 600;
    color: #FFFFFF !important;
    letter-spacing: 0.3px;
}
.sidebar-brand .subtitle {
    font-size: 11px;
    color: #5D7A96 !important;
    margin-top: 2px;
}
.sidebar-info {
    background: #152232;
    border-radius: 4px;
    padding: 10px 12px;
    margin-top: 16px;
    font-size: 11px;
}
.sidebar-info .label { color: #5D7A96 !important; }
.sidebar-info .value { color: #C8D6E5 !important; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  DATA PATHS & I/O
# ─────────────────────────────────────────────────────────────────────────────
def get_paths():
    base = os.path.dirname(os.path.abspath(__file__))
    return (
        os.path.join(base, "transactions.csv"),
        os.path.join(base, "echeances.csv"),
    )

@st.cache_data(ttl=5)
def load_transactions():
    path, _ = get_paths()
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=["date"])
    else:
        df = pd.DataFrame(columns=["date","type","categorie","description","montant"])
        df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["montant_signe"] = df.apply(
        lambda r: r["montant"] if r["type"] == "entree" else -abs(r["montant"]), axis=1
    )
    df["solde_cumule"] = SOLDE_INITIAL + df["montant_signe"].cumsum()
    return df

@st.cache_data(ttl=5)
def load_echeances():
    _, path = get_paths()
    if os.path.exists(path):
        df = pd.read_csv(path, parse_dates=["date"])
    else:
        df = pd.DataFrame(columns=["date","type","partie","description","montant","statut"])
        df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)

def save_transactions(df):
    path, _ = get_paths()
    df.drop(columns=["montant_signe","solde_cumule"], errors="ignore").to_csv(
        path, index=False, date_format="%Y-%m-%d")
    load_transactions.clear()

def save_echeances(df):
    _, path = get_paths()
    df.to_csv(path, index=False, date_format="%Y-%m-%d")
    load_echeances.clear()

# ─────────────────────────────────────────────────────────────────────────────
#  CHART HELPERS
# ─────────────────────────────────────────────────────────────────────────────
CHART_BG = "#FFFFFF"
C_NAVY   = "#0D1B2A"
C_TEAL   = "#0D6E7A"
C_GREEN  = "#1E8449"
C_RED    = "#C0392B"
C_ORANGE = "#D68910"
C_LGRAY  = "#ECF0F1"

def fig_style(fig, ax):
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_BG)
    for sp in ax.spines.values():
        sp.set_color("#D5DCE4")
        sp.set_linewidth(0.6)
    ax.tick_params(colors="#5D6D7E", labelsize=8.5)
    ax.grid(axis="y", linestyle=":", color="#D5DCE4", alpha=0.7)
    ax.set_axisbelow(True)
    return fig, ax

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="company">ATLAS ENGINEERING SERVICES</div>
        <div class="subtitle">Gestion de Trésorerie</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Dashboard", "Flux de Trésorerie", "Echéancier", "Prévision 8 Semaines"],
        label_visibility="collapsed",
    )
    st.markdown("""<div class="sidebar-info">
        <div class="label">Seuil critique</div>
        <div class="value">10 000 MAD</div>
        <div class="label" style="margin-top:8px">Solde initial</div>
        <div class="value">87 100 MAD</div>
        <div class="label" style="margin-top:8px">Exercice</div>
        <div class="value">Jan – Juin 2025</div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 1 — DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "Dashboard":
    st.markdown("""
    <div class="page-header">
        <h1>Dashboard — Vue d'ensemble</h1>
        <p>Situation de trésorerie en temps réel · Atlas Engineering Services</p>
    </div>
    """, unsafe_allow_html=True)

    df   = load_transactions()
    ech  = load_echeances()

    # ── Slicer de date ───────────────
    if not df.empty:
        date_min = df["date"].min().date()
        date_max = df["date"].max().date()
    else:
        date_min = date_max = date.today()

    with st.expander("Filtrer par période", expanded=False):
        col_d1, col_d2, col_d3 = st.columns([2, 2, 3])
        with col_d1:
            filtre_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max, key="dash_debut")
        with col_d2:
            filtre_fin   = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max, key="dash_fin")
        with col_d3:
            presets = st.selectbox("Raccourci", ["Personnalisé", "Mois en cours", "Mois précédent", "Trimestre en cours", "Toute la période"], key="dash_preset")

    # Appliquer les raccourcis
    today_d = date.today()
    if presets == "Mois en cours":
        filtre_debut = today_d.replace(day=1)
        filtre_fin   = today_d
    elif presets == "Mois précédent":
        premier_ce_mois = today_d.replace(day=1)
        dernier_mois = premier_ce_mois - timedelta(days=1)
        filtre_debut = dernier_mois.replace(day=1)
        filtre_fin   = dernier_mois
    elif presets == "Trimestre en cours":
        trim_debut_mois = ((today_d.month - 1) // 3) * 3 + 1
        filtre_debut = today_d.replace(month=trim_debut_mois, day=1)
        filtre_fin   = today_d
    elif presets == "Toute la période":
        filtre_debut = date_min
        filtre_fin   = date_max

    # Filtrer les transactions selon la période
    if not df.empty:
        df_f = df[(df["date"].dt.date >= filtre_debut) & (df["date"].dt.date <= filtre_fin)].copy()
    else:
        df_f = df.copy()

    # Calculs sur la période filtrée
    # Le solde affiché = solde cumulé à la fin de la période filtrée
    if not df_f.empty:
        solde   = df_f["solde_cumule"].iloc[-1]
    elif not df.empty:
        # Si le filtre exclut tout, prendre le solde au dernier jour avant filtre_debut
        df_avant = df[df["date"].dt.date < filtre_debut]
        solde = df_avant["solde_cumule"].iloc[-1] if not df_avant.empty else SOLDE_INITIAL
    else:
        solde = SOLDE_INITIAL

    entrees = df_f[df_f["type"]=="entree"]["montant"].sum()
    sorties = df_f[df_f["type"]=="sortie"]["montant"].sum()
    flux_net = entrees - sorties

    # Retards : uniquement les clients (pas les fournisseurs)
    retards_client = ech[(ech["statut"]=="en_retard") & (ech["type"]=="client")]
    nb_retards = len(retards_client)
    mont_retards = retards_client["montant"].sum()

    # A encaisser : uniquement clients
    a_enc = ech[ech["statut"]=="a_encaisser"]["montant"].sum()

    # ── Période affichée ────────────
    if filtre_debut != date_min or filtre_fin != date_max:
        st.markdown(
            f'<div class="alert alert-info">Période affichée : du {filtre_debut.strftime("%d/%m/%Y")} au {filtre_fin.strftime("%d/%m/%Y")} — {len(df_f)} transaction(s)</div>',
            unsafe_allow_html=True)

    # ── Alerts ──────────────────────
    solde_reel = df["solde_cumule"].iloc[-1] if not df.empty else SOLDE_INITIAL
    if solde_reel < SEUIL_CRITIQUE:
        st.markdown(f'<div class="alert alert-danger">Alerte critique — Le solde actuel ({solde_reel:,.0f} MAD) est inférieur au seuil critique de {SEUIL_CRITIQUE:,.0f} MAD.</div>', unsafe_allow_html=True)
    elif solde_reel < SEUIL_CRITIQUE * 2:
        st.markdown(f'<div class="alert alert-warning">Attention — Le solde actuel ({solde_reel:,.0f} MAD) est proche du seuil critique.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert alert-success">Situation saine — Le solde actuel ({solde_reel:,.0f} MAD) est au-dessus du seuil critique de {SEUIL_CRITIQUE:,.0f} MAD.</div>', unsafe_allow_html=True)
    if nb_retards > 0:
        st.markdown(f'<div class="alert alert-warning">{nb_retards} facture(s) client en retard — Montant total à récupérer : {mont_retards:,.0f} MAD. Relances à effectuer.</div>', unsafe_allow_html=True)

    # ── KPI Cards ───────────────────
    col_cls = "danger" if solde < SEUIL_CRITIQUE else ("warning" if solde < SEUIL_CRITIQUE*2 else "success")
    val_cls = "red"    if solde < SEUIL_CRITIQUE else ("orange" if solde < SEUIL_CRITIQUE*2 else "green")
    flux_cls = "success" if flux_net >= 0 else "danger"
    flux_val_cls = "green" if flux_net >= 0 else "red"
    periode_label = f"{filtre_debut.strftime('%d/%m')} – {filtre_fin.strftime('%d/%m/%Y')}"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card {col_cls}">
        <div class="kpi-label">Solde en fin de période</div>
        <div class="kpi-value {val_cls}">{solde:,.0f}</div>
        <div class="kpi-sub">MAD · Seuil : {SEUIL_CRITIQUE:,} MAD</div>
      </div>
      <div class="kpi-card success">
        <div class="kpi-label">Total Entrées</div>
        <div class="kpi-value green">{entrees:,.0f}</div>
        <div class="kpi-sub">MAD · {periode_label}</div>
      </div>
      <div class="kpi-card danger">
        <div class="kpi-label">Total Sorties</div>
        <div class="kpi-value red">{sorties:,.0f}</div>
        <div class="kpi-sub">MAD · {periode_label}</div>
      </div>
      <div class="kpi-card {flux_cls}">
        <div class="kpi-label">Flux Net Période</div>
        <div class="kpi-value {flux_val_cls}">{flux_net:+,.0f}</div>
        <div class="kpi-sub">MAD · Entrées – Sorties</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts ───────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-title">Evolution du solde de trésorerie</div>', unsafe_allow_html=True)
        if not df_f.empty:
            fig, ax = plt.subplots(figsize=(9, 3.6))
            fig, ax = fig_style(fig, ax)
            ax.fill_between(df_f["date"], df_f["solde_cumule"], alpha=0.12, color=C_TEAL)
            ax.plot(df_f["date"], df_f["solde_cumule"], color=C_TEAL, linewidth=2, zorder=3)
            ax.axhline(SEUIL_CRITIQUE, color=C_RED, linestyle="--",
                       linewidth=1.2, label=f"Seuil critique ({SEUIL_CRITIQUE:,} MAD)")
            import matplotlib.dates as mdates
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
            ax.set_ylabel("MAD", fontsize=8.5, color="#5D6D7E")
            ax.yaxis.set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
            plt.xticks(rotation=30, fontsize=8.5)
            ax.legend(fontsize=8.5, framealpha=0, loc="upper left")
            plt.tight_layout(pad=0.8)
            st.pyplot(fig); plt.close()
        else:
            st.info("Aucune transaction sur cette période.")

    with col2:
        st.markdown('<div class="section-title">Entrées vs Sorties par mois</div>', unsafe_allow_html=True)
        if not df_f.empty:
            df_m = df_f.copy()
            df_m["mois"] = df_m["date"].dt.to_period("M")
            gp = df_m.groupby(["mois","type"])["montant"].sum().unstack(fill_value=0)
            labels = [str(m) for m in gp.index]
            x = np.arange(len(labels)); w = 0.38
            fig2, ax2 = plt.subplots(figsize=(5, 3.6))
            fig2, ax2 = fig_style(fig2, ax2)
            e_vals = gp.get("entree", pd.Series(0, index=gp.index))
            s_vals = gp.get("sortie", pd.Series(0, index=gp.index))
            ax2.bar(x - w/2, e_vals, width=w, color=C_GREEN, alpha=0.85, label="Entrées")
            ax2.bar(x + w/2, s_vals, width=w, color=C_RED,   alpha=0.85, label="Sorties")
            ax2.set_xticks(x); ax2.set_xticklabels(labels, rotation=30, fontsize=8.5)
            ax2.yaxis.set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda v, _: f"{v/1000:.0f}k"))
            ax2.legend(fontsize=8.5, framealpha=0)
            plt.tight_layout(pad=0.8)
            st.pyplot(fig2); plt.close()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 2 — FLUX DE TRESORERIE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Flux de Trésorerie":
    st.markdown("""
    <div class="page-header">
        <h1>Flux de Trésorerie</h1>
        <p>Enregistrement et suivi des entrées et sorties · Solde cumulé automatique</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_transactions()

    # ── Table ────────────────────────
    st.markdown('<div class="section-title">Historique des transactions</div>', unsafe_allow_html=True)

    CATS_ENTREE = ["Honoraires clients", "Acompte client", "Remboursement", "Subvention", "Divers"]
    CATS_SORTIE = ["Salaires", "Charges sociales", "Loyer", "Sous-traitance",
                   "Impôts & taxes", "Charges d'exploitation", "Fournitures", "Autres charges"]

    if not df.empty:
        affichage = df[["date","type","categorie","description","montant","montant_signe","solde_cumule"]].copy()
        affichage["date"] = affichage["date"].dt.strftime("%d/%m/%Y")
        affichage.columns = ["Date","Type","Categorie","Description",
                             "Montant brut (MAD)","Montant signe (MAD)","Solde cumule (MAD)"]

        col_f1, col_f2, col_f3 = st.columns([2,2,3])
        with col_f1:
            f_type = st.selectbox("Filtrer par type", ["Tous","entree","sortie"])
        with col_f2:
            all_cats = ["Toutes"] + sorted(df["categorie"].dropna().unique().tolist())
            f_cat = st.selectbox("Filtrer par categorie", all_cats)
        with col_f3:
            f_search = st.text_input("Rechercher dans la description", "")

        view = affichage.copy()
        if f_type != "Tous": view = view[view["Type"] == f_type]
        if f_cat != "Toutes": view = view[view["Categorie"] == f_cat]
        if f_search: view = view[view["Description"].str.contains(f_search, case=False, na=False)]

        st.dataframe(
            view.style
            .map(lambda v: "color: #1E8449; font-weight:500" if v == "entree"
                      else ("color: #C0392B; font-weight:500" if v == "sortie" else ""),
                      subset=["Type"])
            .format({"Montant brut (MAD)": "{:,.0f}",
                     "Montant signe (MAD)": "{:,.0f}",
                     "Solde cumule (MAD)": "{:,.0f}"}),
            use_container_width=True, height=300,
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Transactions affichées", len(view))
        c2.metric("Total entrees",  f'{view[view["Type"]=="entree"]["Montant brut (MAD)"].sum():,.0f} MAD')
        c3.metric("Total sorties",  f'{view[view["Type"]=="sortie"]["Montant brut (MAD)"].sum():,.0f} MAD')
    else:
        st.info("Aucune transaction enregistrée.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Form ─────────────────────────
    st.markdown('<div class="section-title">Ajouter une transaction</div>', unsafe_allow_html=True)
    with st.form("form_tx", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            f_date = st.date_input("Date", value=date.today())
            f_typ  = st.selectbox("Type", ["entree","sortie"])
        with c2:
            cats = CATS_ENTREE if f_typ == "entree" else CATS_SORTIE
            f_cat_new = st.selectbox("Categorie", cats)
            f_mont = st.number_input("Montant (MAD)", min_value=0.0, step=100.0, format="%.2f")
        with c3:
            f_desc = st.text_input("Description")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Enregistrer la transaction",
                                               use_container_width=True)
        if submitted:
            if f_mont <= 0:
                st.error("Le montant doit être supérieur à 0.")
            elif not f_desc.strip():
                st.error("La description est obligatoire.")
            else:
                df_raw = df.drop(columns=["montant_signe","solde_cumule"], errors="ignore")
                new = pd.DataFrame([{"date": pd.Timestamp(f_date), "type": f_typ,
                                     "categorie": f_cat_new, "description": f_desc.strip(),
                                     "montant": f_mont}])
                save_transactions(pd.concat([df_raw, new], ignore_index=True))
                st.success(f"Transaction enregistree : {f_desc} — {f_mont:,.0f} MAD")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Import CSV ───────────────────
    st.markdown('<div class="section-title">Importer un fichier CSV</div>', unsafe_allow_html=True)

    with st.expander("Importer / Remplacer les transactions via CSV", expanded=False):
        st.markdown("""
        <div class="alert alert-info">
        Le fichier CSV doit contenir les colonnes : <strong>date, type, categorie, description, montant</strong><br>
        • <strong>date</strong> : format YYYY-MM-DD &nbsp;|&nbsp; <strong>type</strong> : <code>entree</code> ou <code>sortie</code> &nbsp;|&nbsp; <strong>montant</strong> : nombre positif
        </div>
        """, unsafe_allow_html=True)

        col_imp1, col_imp2 = st.columns([3, 2])
        with col_imp1:
            uploaded_csv = st.file_uploader("Choisir un fichier CSV", type=["csv"], key="csv_uploader")
        with col_imp2:
            import_mode = st.radio(
                "Mode d'import",
                ["Fusionner (ajouter aux existantes)", "Remplacer (écraser tout)"],
                key="import_mode"
            )

        if uploaded_csv is not None:
            try:
                df_import = pd.read_csv(uploaded_csv, parse_dates=["date"])

                # Validate required columns
                required_cols = {"date", "type", "categorie", "description", "montant"}
                missing = required_cols - set(df_import.columns)
                if missing:
                    st.error(f"Colonnes manquantes dans le fichier : {', '.join(missing)}")
                else:
                    # Validate type values
                    invalid_types = df_import[~df_import["type"].isin(["entree", "sortie"])]
                    # Validate montant positive
                    invalid_mont = df_import[df_import["montant"] <= 0]

                    # Show preview
                    st.markdown("**Apercu du fichier importé :**")
                    preview = df_import.copy()
                    preview["date"] = preview["date"].dt.strftime("%d/%m/%Y")
                    st.dataframe(preview.head(10), use_container_width=True, height=220)

                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    col_stat1.metric("Lignes détectées", len(df_import))
                    col_stat2.metric("Entrées", len(df_import[df_import["type"]=="entree"]))
                    col_stat3.metric("Sorties", len(df_import[df_import["type"]=="sortie"]))

                    if not invalid_types.empty:
                        st.warning(f"{len(invalid_types)} ligne(s) avec type invalide (ni 'entree' ni 'sortie') — ces lignes seront ignorées.")
                        df_import = df_import[df_import["type"].isin(["entree", "sortie"])]

                    if not invalid_mont.empty:
                        st.warning(f"{len(invalid_mont)} ligne(s) avec montant nul ou négatif — ces lignes seront ignorées.")
                        df_import = df_import[df_import["montant"] > 0]

                    # Keep only required columns
                    df_import = df_import[["date", "type", "categorie", "description", "montant"]].copy()
                    df_import["date"] = pd.to_datetime(df_import["date"])

                    col_btn1, col_btn2 = st.columns([2, 3])
                    with col_btn1:
                        if st.button("Confirmer l'import", type="primary", use_container_width=True):
                            df_existing = load_transactions().drop(
                                columns=["montant_signe", "solde_cumule"], errors="ignore")

                            if import_mode.startswith("Fusionner"):
                                df_final = pd.concat([df_existing, df_import], ignore_index=True)
                                df_final = df_final.sort_values("date").reset_index(drop=True)
                                # Deduplicate: same date + description + montant
                                before = len(df_final)
                                df_final = df_final.drop_duplicates(
                                    subset=["date", "description", "montant"], keep="first")
                                dupes = before - len(df_final)
                                save_transactions(df_final)
                                msg = f"{len(df_import)} transaction(s) importée(s)"
                                if dupes > 0:
                                    msg += f" · {dupes} doublon(s) ignoré(s)"
                                st.success(msg)
                            else:
                                save_transactions(df_import.sort_values("date").reset_index(drop=True))
                                st.success(f"Données remplacées — {len(df_import)} transaction(s) chargées.")

                            st.rerun()
                    with col_btn2:
                        # Download template
                        template = pd.DataFrame([
                            {"date": "2026-01-05", "type": "entree", "categorie": "Honoraires clients",
                             "description": "Exemple facture client", "montant": 50000},
                            {"date": "2026-01-10", "type": "sortie", "categorie": "Salaires",
                             "description": "Exemple salaires", "montant": 35000},
                        ])
                        st.download_button(
                            "Télécharger le modèle CSV",
                            data=template.to_csv(index=False),
                            file_name="modele_transactions.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

            except Exception as ex:
                st.error(f"Erreur lors de la lecture du fichier : {ex}")

        else:
            # Show download template button even without file
            template = pd.DataFrame([
                {"date": "2026-01-05", "type": "entree", "categorie": "Honoraires clients",
                 "description": "Exemple facture client", "montant": 50000},
                {"date": "2026-01-10", "type": "sortie", "categorie": "Salaires",
                 "description": "Exemple salaires", "montant": 35000},
            ])
            st.download_button(
                "Télécharger le modèle CSV",
                data=template.to_csv(index=False),
                file_name="modele_transactions.csv",
                mime="text/csv",
            )

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 3 — ECHEANCIER
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Echéancier":
    st.markdown("""
    <div class="page-header">
        <h1>Echéancier</h1>
        <p>Suivi des créances clients et charges à payer · Alertes retards</p>
    </div>
    """, unsafe_allow_html=True)

    ech = load_echeances()

    a_enc = ech[ech["statut"]=="a_encaisser"]["montant"].sum()
    a_pay = ech[ech["statut"]=="a_payer"]["montant"].sum()
    en_ret= ech[ech["statut"]=="en_retard"]["montant"].sum()
    nb_ret= (ech["statut"]=="en_retard").sum()

    if nb_ret > 0:
        st.markdown(f'<div class="alert alert-danger">{nb_ret} echéance(s) en retard — Montant total en souffrance : {en_ret:,.0f} MAD. Relances clients à déclencher immédiatement.</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card success">
        <div class="kpi-label">A Encaisser</div>
        <div class="kpi-value green">{a_enc:,.0f}</div>
        <div class="kpi-sub">MAD · Créances clients</div>
      </div>
      <div class="kpi-card warning">
        <div class="kpi-label">A Payer</div>
        <div class="kpi-value orange">{a_pay:,.0f}</div>
        <div class="kpi-sub">MAD · Charges fournisseurs</div>
      </div>
      <div class="kpi-card danger">
        <div class="kpi-label">En Retard</div>
        <div class="kpi-value red">{en_ret:,.0f}</div>
        <div class="kpi-sub">MAD · {nb_ret} facture(s)</div>
      </div>
      <div class="kpi-card neutral">
        <div class="kpi-label">Solde Net Previsionnel</div>
        <div class="kpi-value blue">{(a_enc - a_pay):,.0f}</div>
        <div class="kpi-sub">MAD · Encaisser – Payer</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Liste des échéances</div>', unsafe_allow_html=True)

    col_f, _ = st.columns([2, 4])
    with col_f:
        filtre = st.selectbox("Filtrer par statut", ["Tous","a_encaisser","a_payer","en_retard"])

    vue = ech if filtre == "Tous" else ech[ech["statut"] == filtre]

    if not vue.empty:
        disp = vue.copy()
        disp["date"] = disp["date"].dt.strftime("%d/%m/%Y")
        disp.columns = ["Date","Type","Partie","Description","Montant (MAD)","Statut"]
        st.dataframe(
            disp.style
            .map(lambda v:
                "color: #1E8449; font-weight:600" if v == "a_encaisser"
                else ("color: #D68910; font-weight:600" if v == "a_payer"
                else ("color: #C0392B; font-weight:600; background-color:#FDEDEC"
                      if v == "en_retard" else "")),
                subset=["Statut"])
            .format({"Montant (MAD)": "{:,.0f}"}),
            use_container_width=True, height=280,
        )
    else:
        st.info("Aucune échéance pour ce filtre.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Ajouter une échéance</div>', unsafe_allow_html=True)

    with st.form("form_ech", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            e_date   = st.date_input("Date d'échéance", value=date.today())
            e_type   = st.selectbox("Type", ["client","fournisseur"])
        with c2:
            e_partie = st.text_input("Partie (client / fournisseur)")
            e_mont   = st.number_input("Montant (MAD)", min_value=0.0, step=100.0, format="%.2f")
        with c3:
            e_statut = st.selectbox("Statut", ["a_encaisser","a_payer","en_retard"])
            e_desc   = st.text_input("Description")
        sub_e = st.form_submit_button("Enregistrer l'échéance", use_container_width=True)
        if sub_e:
            if e_mont <= 0 or not e_partie.strip() or not e_desc.strip():
                st.error("Tous les champs sont obligatoires et le montant doit être > 0.")
            else:
                new_e = pd.DataFrame([{"date": pd.Timestamp(e_date), "type": e_type,
                                       "partie": e_partie.strip(), "description": e_desc.strip(),
                                       "montant": e_mont, "statut": e_statut}])
                save_echeances(pd.concat([ech, new_e], ignore_index=True))
                st.success(f"Echéance enregistrée : {e_desc} — {e_mont:,.0f} MAD")
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 4 — PREVISION 8 SEMAINES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "Prévision 8 Semaines":
    st.markdown("""
    <div class="page-header">
        <h1>Prévision de Trésorerie — 8 Semaines</h1>
        <p>Projection du solde prévisionnel · Détection précoce des tensions de liquidité</p>
    </div>
    """, unsafe_allow_html=True)

    df_tx  = load_transactions()
    df_ech = load_echeances()

    solde_actuel = df_tx["solde_cumule"].iloc[-1] if not df_tx.empty else SOLDE_INITIAL
    today        = date.today()

    # Retards alert — clients uniquement
    retards = df_ech[(df_ech["statut"] == "en_retard") & (df_ech["type"] == "client")]
    if not retards.empty:
        st.markdown(
            f'<div class="alert alert-danger">{len(retards)} facture(s) client en retard '
            f'({retards["montant"].sum():,.0f} MAD) — Ces montants ne sont pas intégrés '
            f'dans la prévision. Leur encaissement permettrait d\'améliorer significativement '
            f'la position de trésorerie.</div>', unsafe_allow_html=True)

    # Build weekly forecast
    semaines = [today + timedelta(weeks=w) for w in range(9)]
    df_fut = df_ech[df_ech["statut"].isin(["a_encaisser","a_payer"])].copy()
    df_fut["date_d"] = df_fut["date"].dt.date

    soldes_prev = [solde_actuel]
    entrees_sem = []
    sorties_sem = []

    for i in range(8):
        d0, d1 = semaines[i], semaines[i+1]
        mask   = (df_fut["date_d"] >= d0) & (df_fut["date_d"] < d1)
        p      = df_fut[mask]
        e = p[p["statut"]=="a_encaisser"]["montant"].sum()
        s = p[p["statut"]=="a_payer"]["montant"].sum()
        entrees_sem.append(e)
        sorties_sem.append(s)
        soldes_prev.append(soldes_prev[-1] + e - s)

    min_prev = min(soldes_prev)
    alerte_semaines = [i for i, v in enumerate(soldes_prev) if v < SEUIL_CRITIQUE]

    # Alerts
    if alerte_semaines:
        prm = alerte_semaines[0]
        st.markdown(
            f'<div class="alert alert-danger">Le solde prévisionnel passera sous le seuil critique '
            f'à la semaine S+{prm} ({soldes_prev[prm]:,.0f} MAD). '
            f'Anticipez les encaissements ou reportez certaines sorties.</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="alert alert-success">Le solde reste au-dessus du seuil critique '
            f'sur l\'ensemble des 8 prochaines semaines. Situation prévisionnelle favorable.</div>',
            unsafe_allow_html=True)

    # KPIs
    css_min = "danger" if min_prev < SEUIL_CRITIQUE else ("warning" if min_prev < SEUIL_CRITIQUE*3 else "success")
    val_min = "red"    if min_prev < SEUIL_CRITIQUE else ("orange" if min_prev < SEUIL_CRITIQUE*3 else "green")
    css_fin = "success" if soldes_prev[-1] > solde_actuel else "warning"
    val_fin = "green"   if soldes_prev[-1] > solde_actuel else "orange"

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card neutral">
        <div class="kpi-label">Solde Actuel</div>
        <div class="kpi-value blue">{solde_actuel:,.0f}</div>
        <div class="kpi-sub">MAD · Point de départ</div>
      </div>
      <div class="kpi-card {css_min}">
        <div class="kpi-label">Solde Minimum Prévu</div>
        <div class="kpi-value {val_min}">{min_prev:,.0f}</div>
        <div class="kpi-sub">MAD · Pire semaine</div>
      </div>
      <div class="kpi-card {css_fin}">
        <div class="kpi-label">Solde Final S+8</div>
        <div class="kpi-value {val_fin}">{soldes_prev[-1]:,.0f}</div>
        <div class="kpi-sub">MAD · Fin de période</div>
      </div>
      <div class="kpi-card {'danger' if alerte_semaines else 'success'}">
        <div class="kpi-label">Semaines en Alerte</div>
        <div class="kpi-value {'red' if alerte_semaines else 'green'}">{len(alerte_semaines)}</div>
        <div class="kpi-sub">Semaines sous seuil critique</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Chart
    st.markdown('<div class="section-title">Graphique du solde prévisionnel</div>', unsafe_allow_html=True)

    labels_sem = ["Aujourd'hui"] + [f"S+{i+1}\n{semaines[i+1].strftime('%d/%m')}" for i in range(8)]
    dot_colors = [C_RED if v < SEUIL_CRITIQUE else
                  (C_ORANGE if v < SEUIL_CRITIQUE*3 else C_TEAL)
                  for v in soldes_prev]

    fig, ax = plt.subplots(figsize=(12, 4.2))
    fig, ax = fig_style(fig, ax)

    x = np.arange(len(labels_sem))

    # Zone de remplissage sous la courbe
    ax.fill_between(x, soldes_prev, alpha=0.08, color=C_TEAL, zorder=1)

    # Ligne principale
    ax.plot(x, soldes_prev, "-", color=C_TEAL, linewidth=2.2, zorder=2)

    # Points colorés selon le statut
    for i, (val, col) in enumerate(zip(soldes_prev, dot_colors)):
        ax.scatter(i, val, color=col, s=60, zorder=4)

    ax.axhline(SEUIL_CRITIQUE, color=C_RED, linestyle="--",
               linewidth=1.3, zorder=3)

    for i, val in enumerate(soldes_prev):
        ax.annotate(f"{val/1000:.1f}k",
                    xy=(i, val), xytext=(0, 9), textcoords="offset points",
                    ha="center", fontsize=8, color=C_NAVY, fontweight="500")

    ax.set_xticks(x)
    ax.set_xticklabels(labels_sem, fontsize=8.5)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylabel("MAD", fontsize=8.5, color="#5D6D7E")

    ax.legend(handles=[
        plt.Line2D([0],[0], color=C_TEAL, linewidth=2.2, label="Solde prévisionnel"),
        plt.Line2D([0],[0], color=C_RED, linestyle="--", linewidth=1.3, label=f"Seuil critique ({SEUIL_CRITIQUE:,} MAD)"),
        plt.scatter([],[], color=C_TEAL,   s=50, label="Satisfaisant"),
        plt.scatter([],[], color=C_ORANGE, s=50, label="Faible"),
        plt.scatter([],[], color=C_RED,    s=50, label="Alerte"),
    ], fontsize=8.5, framealpha=0, ncol=3, loc="upper right")

    plt.tight_layout(pad=0.8)
    st.pyplot(fig); plt.close()

    # Detail table
    st.markdown('<div class="section-title">Détail semaine par semaine</div>', unsafe_allow_html=True)

    rows = []
    for i in range(8):
        d0, d1 = semaines[i], semaines[i+1]
        statut = ("ALERTE"    if soldes_prev[i+1] < SEUIL_CRITIQUE else
                  "ATTENTION" if soldes_prev[i+1] < SEUIL_CRITIQUE*3 else "OK")
        rows.append({
            "Semaine":              f"S+{i+1}  ({d0.strftime('%d/%m')} – {d1.strftime('%d/%m')})",
            "Entrees prev. (MAD)":  entrees_sem[i],
            "Sorties prev. (MAD)":  sorties_sem[i],
            "Flux net (MAD)":       entrees_sem[i] - sorties_sem[i],
            "Solde debut (MAD)":    soldes_prev[i],
            "Solde fin (MAD)":      soldes_prev[i+1],
            "Statut":               statut,
        })

    df_prev = pd.DataFrame(rows)

    def color_statut(val):
        if val == "ALERTE":    return "color: #C0392B; font-weight:600; background:#FDEDEC"
        if val == "ATTENTION": return "color: #D68910; font-weight:600; background:#FDFAF2"
        return "color: #1E8449; font-weight:600; background:#EAF5EA"

    def color_flux(val):
        if isinstance(val, (int, float)):
            return "color: #1E8449" if val >= 0 else "color: #C0392B"
        return ""

    st.dataframe(
        df_prev.style
        .map(color_statut, subset=["Statut"])
        .map(color_flux,   subset=["Flux net (MAD)"])
        .format({c: "{:,.0f}" for c in df_prev.columns if "(MAD)" in c}),
        use_container_width=True, hide_index=True,
    )
