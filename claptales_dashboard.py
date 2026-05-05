import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CLAPTALES | Market Intelligence",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Serif+Display&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Header */
.brand-header {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    border-radius: 16px; padding: 1.6rem 2rem; margin-bottom: 1.5rem; color: white;
}
.brand-header h1 { font-family:'DM Serif Display',serif; font-size:2rem; margin:0 0 4px; }
.brand-header p  { margin:0; opacity:.88; font-size:.88rem; }

/* KPI card */
.kpi {
    background:white; border-radius:12px; padding:1.1rem 1.3rem;
    border:1px solid #F0F0F0; box-shadow:0 2px 8px rgba(0,0,0,.04);
}
.kpi-label { font-size:.72rem; color:#999; text-transform:uppercase; letter-spacing:.06em; margin-bottom:4px; }
.kpi-val   { font-size:1.8rem; font-weight:600; color:#1A1A1A; line-height:1.1; }
.kpi-sub   { font-size:.75rem; color:#aaa; margin-top:3px; }

/* Callout boxes */
.insight  { background:#FFF8F0; border-left:4px solid #FF8E53; border-radius:0 8px 8px 0;
            padding:.75rem 1rem; margin:.5rem 0 1rem; font-size:.84rem; color:#5A3E2B; line-height:1.55; }
.conclude { background:#F0FFF4; border-left:4px solid #2ECC71; border-radius:0 8px 8px 0;
            padding:.75rem 1rem; margin:.4rem 0; font-size:.84rem; color:#1A4731; line-height:1.55; }
.warn     { background:#FFF5F5; border-left:4px solid #E74C3C; border-radius:0 8px 8px 0;
            padding:.75rem 1rem; margin:.4rem 0; font-size:.84rem; color:#5A1A1A; line-height:1.55; }

/* Section title */
.sec { font-size:1rem; font-weight:600; color:#1A1A1A; margin:1.1rem 0 .3rem;
       padding-bottom:.35rem; border-bottom:2px solid #FF8E53; display:inline-block; }

/* Product card */
.prod-card {
    background:white; border:1px solid #EFEFEF; border-radius:14px;
    padding:14px; margin-bottom:14px; height:100%;
    transition: box-shadow .2s;
}

/* Divider */
hr.light { border:none; border-top:1px solid #F0F0F0; margin:1rem 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
COLORS = ["#FF6B6B","#FF8E53","#FFC75F","#2ECC71","#3498DB","#9B59B6","#1ABC9C","#E74C3C","#F39C12","#2980B9"]

def style_fig(fig, height=320):
    fig.update_layout(
        font_family="DM Sans", plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=12, r=12, t=32, b=12), colorway=COLORS,
        legend=dict(font_size=11), title_font_size=13, height=height,
    )
    fig.update_xaxes(showgrid=False, linecolor="#F0F0F0", tickfont_size=11)
    fig.update_yaxes(showgrid=True, gridcolor="#F7F7F7", linecolor="#F0F0F0", tickfont_size=11)
    return fig

def load_file(f):
    try:
        df = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return None

def to_num(s):
    if s.dtype != object: return s
    return pd.to_numeric(s.astype(str).str.replace(r'[₹$,%\s]','',regex=True), errors='coerce')

def kpi(label, value, sub=""):
    return f"""<div class="kpi">
      <div class="kpi-label">{label}</div>
      <div class="kpi-val">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

def demand_badge(score):
    if score >= 0.6: return ("🔥 High Demand","#FF6B6B","#FFF0F0")
    if score >= 0.3: return ("📈 Growing",    "#FF8E53","#FFF5EE")
    return                  ("💤 Low Demand", "#888",   "#F5F5F5")

# ══════════════════════════════════════════════════════════════════════════════
# COLUMN MAPPING  (exact Jungle Scout column names)
# ══════════════════════════════════════════════════════════════════════════════
COL = {
    "title":        ["title","product name","product title","asin title","name"],
    "brand":        ["brand","brand name","manufacturer"],
    "category":     ["category","main category","product category","department"],
    "subcategory":  ["subcategory","sub category","sub-category"],
    "bsr":          ["bsr","best seller rank","sales rank","subcategory bsr"],
    "price":        ["price","sale price","buy box price","current price","selling price"],
    "asin_sales":   ["asin sales","monthly sales","estimated monthly sales","est. monthly sales"],
    "asin_revenue": ["asin revenue","monthly revenue","estimated monthly revenue"],
    "reviews":      ["review count","reviews","number of reviews","total reviews"],
    "rating":       ["reviews rating","rating","star rating","avg rating","average rating"],
    "price_trend":  ["price trend (90 days) (%)","price trend","price change (%)"],
    "sales_trend":  ["sales trend (90 days) (%)","sales trend","sales change (%)"],
    "fulfillment":  ["fulfillment","fulfillment type","fba/fbm"],
    "sellers":      ["number of active sellers","active sellers","seller count"],
    "listing_age":  ["listing age (months)","listing age","age (months)"],
    "sales_to_rev": ["sales to reviews","sales/reviews ratio"],
    "url":          ["url","product url","amazon url","product link","link","asin url"],
    "image_url":    ["image url","image","image link","product image","thumbnail","img url","photo url"],
}

def detect(df, key):
    aliases = COL[key]
    for col in df.columns:
        if col.strip().lower() in aliases:
            return col
    for col in df.columns:
        cl = col.strip().lower()
        for a in aliases:
            if a in cl or cl in a:
                return col
    return None

# ══════════════════════════════════════════════════════════════════════════════
# SAMPLE DATA  (shown when no file is uploaded)
# ══════════════════════════════════════════════════════════════════════════════
def sample_data():
    np.random.seed(42)
    brands  = ['FunSkool','Hasbro','Mattel','Lego','Toyzone','Miss&Chief','OK Play','Ratnas','Simba','Funskool']
    cats    = ['Toys & Games','Baby Products']
    subcats = {
        'Toys & Games': ['Board Games','Building Sets','Puzzles','Action Figures','Art & Craft','Outdoor Toys'],
        'Baby Products': ['Baby Toys','Soft Toys','Educational Toys','Bath Toys','Rattles','Teethers'],
    }
    rows = []
    for i in range(150):
        cat   = np.random.choice(cats, p=[.6,.4])
        sub   = np.random.choice(subcats[cat])
        brand = np.random.choice(brands, p=[.18,.14,.12,.10,.09,.08,.08,.07,.07,.07])
        price = np.random.choice([199,299,399,499,599,799,999,1299,1499,1999,2499])
        rating= round(np.clip(np.random.normal(4.1,.45),1,5),1)
        revs  = int(np.random.exponential(6000))
        bsr   = int(np.random.exponential(4000))+50
        sales = int(np.random.exponential(350))
        rows.append(dict(
            title=f"Sample {sub} Product {i+1}",
            brand=brand, category=cat, subcategory=sub,
            bsr=bsr, price=price, asin_sales=sales,
            asin_revenue=float(sales*price), reviews=revs, rating=rating,
            price_trend=round(np.random.uniform(-30,10),1),
            sales_trend=round(np.random.uniform(-20,80),1),
            fulfillment=np.random.choice(['FBA','FBM'],p=[.72,.28]),
            sellers=np.random.randint(1,6),
            listing_age=np.random.randint(6,200),
            sales_to_rev=round(sales/max(revs,1),3),
            url="https://www.amazon.in",
            image_url="",
        ))
    return pd.DataFrame(rows)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  — upload + filters
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧸 CLAPTALES")
    st.markdown("**Market Intelligence Platform**")
    st.divider()
    uploaded = st.file_uploader("Upload Jungle Scout / Helium10 export", type=["csv","xlsx"])
    st.divider()
    st.markdown("**Filters**")

# ══════════════════════════════════════════════════════════════════════════════
# LOAD + MAP COLUMNS
# ══════════════════════════════════════════════════════════════════════════════
if uploaded:
    raw = load_file(uploaded)
    if raw is None: st.stop()
    df = raw.copy()
    rename = {}
    for k in COL:
        found = detect(df, k)
        if found and found != k:
            rename[found] = k
    df = df.rename(columns=rename)
    for c in ["bsr","price","asin_sales","asin_revenue","reviews","rating",
              "price_trend","sales_trend","sellers","listing_age","sales_to_rev"]:
        if c in df.columns:
            df[c] = to_num(df[c])
    for c in ["title","brand","category","subcategory","bsr","price","asin_sales",
              "asin_revenue","reviews","rating","price_trend","sales_trend",
              "fulfillment","sellers","listing_age","sales_to_rev","url","image_url"]:
        if c not in df.columns:
            df[c] = np.nan
    missing = [c for c in ["price","rating"] if df[c].isna().all()]
    if missing:
        st.error(f"Could not detect required columns: **{', '.join(missing)}**")
        st.markdown("**Columns in your file:**")
        st.code(", ".join(raw.columns.tolist()))
        st.stop()
    df = df.dropna(subset=["price","rating"]).reset_index(drop=True)
    if len(df) == 0:
        st.error("No valid rows found — check Price and Rating columns contain numbers.")
        st.stop()
    using_sample = False
else:
    df = sample_data()
    using_sample = True

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    if using_sample:
        st.info("📊 Sample data — upload your Jungle Scout CSV for real analysis.")
    cat_opts   = ["All"] + sorted(df["category"].dropna().unique().tolist())   if df["category"].notna().any()   else ["All"]
    cat_sel    = st.selectbox("Category", cat_opts)
    subcat_opts= ["All"] + sorted(df["subcategory"].dropna().unique().tolist()) if df["subcategory"].notna().any() else ["All"]
    subcat_sel = st.selectbox("Subcategory", subcat_opts)
    p_min, p_max = int(df["price"].min()), int(df["price"].max())
    if p_min == p_max: p_max = p_min + 1
    price_range  = st.slider("Price (₹)", p_min, p_max, (p_min, p_max))
    rating_min   = st.slider("Min rating", 1.0, 5.0, 3.0, 0.1)
    ful_opts     = ["All"] + sorted(df["fulfillment"].dropna().unique().tolist()) if df["fulfillment"].notna().any() else ["All"]
    ful_sel      = st.selectbox("Fulfillment", ful_opts)

# ── Apply filters ─────────────────────────────────────────────────────────────
fdf = df.copy()
if cat_sel    != "All": fdf = fdf[fdf["category"]    == cat_sel]
if subcat_sel != "All": fdf = fdf[fdf["subcategory"] == subcat_sel]
fdf = fdf[(fdf["price"] >= price_range[0]) & (fdf["price"] <= price_range[1])]
fdf = fdf[fdf["rating"] >= rating_min]
if ful_sel    != "All": fdf = fdf[fdf["fulfillment"] == ful_sel]

# ══════════════════════════════════════════════════════════════════════════════
# SHARED SCORING HELPER
# ══════════════════════════════════════════════════════════════════════════════
def score_df(grp, group_col):
    """Score any grouped dataframe by revenue, sales, reviews, trend."""
    s = grp.copy()
    rev_max  = s["total_revenue"].max() or 1
    sal_max  = s["avg_sales"].max()     or 1
    rev_max2 = s["avg_reviews"].max()   or 1
    s["score"] = (
        (s["total_revenue"].fillna(0) / rev_max)  * 40 +
        (s["avg_sales"].fillna(0)     / sal_max)  * 25 +
        (s["avg_reviews"].fillna(0)   / rev_max2) * 20 +
        ((s["avg_sales_trend"].fillna(0) + 100) / 200).clip(0,1) * 15
    ).round(1)
    return s.sort_values("score", ascending=False)

def score_products(prod_df):
    prod_df = prod_df.copy()
    prod_df["asin_revenue"] = pd.to_numeric(prod_df["asin_revenue"], errors="coerce").fillna(0)
    prod_df["asin_sales"]   = pd.to_numeric(prod_df["asin_sales"],   errors="coerce").fillna(0)
    prod_df["reviews"]      = pd.to_numeric(prod_df["reviews"],      errors="coerce").fillna(0)
    rev_p = prod_df["asin_revenue"].max() or 1
    rev_r = prod_df["reviews"].max()      or 1
    sal_p = prod_df["asin_sales"].max()   or 1
    prod_df["prod_score"] = (
        (prod_df["asin_revenue"] / rev_p) * 40 +
        (prod_df["reviews"]      / rev_r) * 35 +
        (prod_df["asin_sales"]   / sal_p) * 25
    ).round(3)
    return prod_df.sort_values("prod_score", ascending=False).reset_index(drop=True)

def agg_group(df, group_col):
    return df.groupby(group_col).agg(
        products   =("price",        "count"),
        avg_price  =("price",        "mean"),
        avg_rating =("rating",       "mean"),
        avg_reviews=("reviews",      "mean"),
        total_revenue=("asin_revenue","sum"),
        avg_sales  =("asin_sales",   "mean"),
        avg_sales_trend=("sales_trend","mean"),
    ).reset_index()

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL PAGE HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="brand-header">
  <h1>🧸 CLAPTALES Market Intelligence</h1>
  <p>Amazon India · Jungle Scout data · Know the market. Build the right product.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TOP-LEVEL KPIs  (always visible above tabs)
# ══════════════════════════════════════════════════════════════════════════════
total_rev  = fdf["asin_revenue"].fillna(0).sum()
fba_pct    = round(fdf[fdf["fulfillment"]=="FBA"].shape[0] / max(len(fdf),1) * 100) if fdf["fulfillment"].notna().any() else 0
top_brand  = fdf["brand"].value_counts().idxmax() if fdf["brand"].notna().any() else "—"
pct_high   = round(len(fdf[fdf["rating"] >= 4.2]) / max(len(fdf),1) * 100)

k1,k2,k3,k4,k5 = st.columns(5)
k1.markdown(kpi("Products tracked",   f"{len(fdf):,}",       f"{fdf['subcategory'].nunique()} subcategories"), unsafe_allow_html=True)
k2.markdown(kpi("Avg market price",   f"₹{fdf['price'].mean():,.0f}", f"range ₹{int(fdf['price'].min()):,}–₹{int(fdf['price'].max()):,}"), unsafe_allow_html=True)
k3.markdown(kpi("Avg rating",         f"{fdf['rating'].mean():.1f}★", f"{pct_high}% hit 4.2★+"), unsafe_allow_html=True)
k4.markdown(kpi("Est. market revenue",f"₹{total_rev/100000:.1f}L/mo"  if total_rev > 0 else "N/A", "monthly across all products"), unsafe_allow_html=True)
k5.markdown(kpi("FBA adoption",       f"{fba_pct}%",          f"market leader: {top_brand}"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS  — 3 focused tabs
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "📊 Market Overview",
    "🏆 Competitor Intel",
    "🛍️ Products to Launch",
])

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 1 — MARKET OVERVIEW                                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
with tab1:
    col_l, col_r = st.columns(2)

    # ── Revenue by subcategory ────────────────────────────────────────────
    with col_l:
        st.markdown('<div class="sec">Monthly Revenue by Subcategory</div>', unsafe_allow_html=True)
        if fdf["subcategory"].notna().any() and fdf["asin_revenue"].notna().any():
            sub_rev = fdf.groupby("subcategory")["asin_revenue"].sum().reset_index()
            sub_rev.columns = ["Subcategory","Revenue"]
            sub_rev = sub_rev[sub_rev["Revenue"] > 0].sort_values("Revenue", ascending=True).tail(12)
            fig = px.bar(sub_rev, x="Revenue", y="Subcategory", orientation="h",
                         color="Revenue", color_continuous_scale=["#FFC75F","#FF8E53","#FF6B6B"],
                         text=sub_rev["Revenue"].apply(lambda x: f"₹{x/100000:.1f}L"),
                         labels={"Revenue":"₹ Monthly Revenue","Subcategory":""})
            fig = style_fig(fig, height=max(280, len(sub_rev)*34))
            fig.update_traces(marker_line_width=0, textposition="outside")
            fig.update_layout(coloraxis_showscale=False, xaxis_tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)
            best_rev_sub = sub_rev.iloc[-1]["Subcategory"]
            st.markdown(f"""<div class="conclude">✅ <b>{best_rev_sub}</b> generates the most monthly revenue.
            This is where real purchasing is happening — top priority for CLAPTALES to evaluate.</div>""",
            unsafe_allow_html=True)
        else:
            st.info("Revenue data not available.")

    # ── 90-day sales trend by subcategory ────────────────────────────────
    with col_r:
        st.markdown('<div class="sec">90-Day Sales Trend by Subcategory</div>', unsafe_allow_html=True)
        if fdf["sales_trend"].notna().any() and fdf["subcategory"].notna().any():
            trend = fdf.groupby("subcategory")["sales_trend"].mean().reset_index()
            trend.columns = ["Subcategory","Trend"]
            trend = trend[trend["Subcategory"].notna() & (trend["Subcategory"] != "")]
            trend = trend.sort_values("Trend", ascending=False).head(12)
            trend["color"] = trend["Trend"].apply(lambda x: "#2ECC71" if x >= 0 else "#E74C3C")
            fig = px.bar(trend, x="Subcategory", y="Trend",
                         color="color", color_discrete_map="identity",
                         text=trend["Trend"].apply(lambda x: f"{x:+.0f}%"),
                         labels={"Subcategory":"","Trend":"Sales Change %"})
            fig = style_fig(fig, height=max(280, len(trend)*34))
            fig.update_layout(showlegend=False, xaxis_tickangle=-35, yaxis_title="Sales Change % (90d)")
            fig.update_traces(marker_line_width=0, textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
            growing = trend[trend["Trend"] > 0]["Subcategory"].tolist()
            if growing:
                st.markdown(f"""<div class="conclude">✅ Growing right now: <b>{', '.join(growing[:3])}</b>.
                Entering a growing subcategory means demand is already pulling — easier to get early sales.</div>""",
                unsafe_allow_html=True)
        else:
            st.info("Sales trend data not available.")

    st.markdown("<hr class='light'>", unsafe_allow_html=True)

    # ── Opportunity matrix ────────────────────────────────────────────────
    st.markdown('<div class="sec">Opportunity Matrix — Where is Demand Unmet?</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight">📌 <b>Green zone = your entry point.</b>
    High reviews (proven demand) but low ratings (poor quality from competitors).
    These are subcategories where CLAPTALES can launch a better product and win.</div>""",
    unsafe_allow_html=True)

    opp_df = fdf.dropna(subset=["reviews","rating","price"]).copy()
    med_rev = opp_df["reviews"].median()

    def quadrant(row):
        hi   = row["reviews"] >= med_rev
        good = row["rating"]  >= 4.0
        if hi and not good: return "🟢 Opportunity"
        if hi and good:     return "🔴 Competitive"
        if not hi and good: return "🟡 Niche"
        return "⚪ Low priority"

    opp_df["zone"] = opp_df.apply(quadrant, axis=1)
    color_map = {"🟢 Opportunity":"#2ECC71","🔴 Competitive":"#E74C3C",
                 "🟡 Niche":"#F39C12","⚪ Low priority":"#BDC3C7"}

    hover_cols = {c: True for c in ["title","brand","subcategory","price","reviews","rating"]
                  if c in opp_df.columns and opp_df[c].notna().any()}
    hover_cols["zone"] = False

    fig = px.scatter(opp_df, x="reviews", y="rating", color="zone",
                     color_discrete_map=color_map, size="price", size_max=22,
                     hover_data=hover_cols,
                     labels={"reviews":"Review Count","rating":"Star Rating"})
    fig.add_hline(y=4.0, line_dash="dash", line_color="#bbb", line_width=1,
                  annotation_text="4.0★ quality bar", annotation_position="top right")
    fig.add_vline(x=med_rev, line_dash="dash", line_color="#bbb", line_width=1,
                  annotation_text="median reviews", annotation_position="top right")
    fig = style_fig(fig, height=420)
    fig.update_layout(legend_title_text="Zone")
    st.plotly_chart(fig, use_container_width=True)

    n_opp = len(opp_df[opp_df["zone"]=="🟢 Opportunity"])
    st.markdown(f"""<div class="conclude">✅ <b>{n_opp} products</b> sit in the Opportunity zone —
    high demand, weak competition. These are the exact product types to study and launch better versions of.
    See the <b>🛍️ Products to Launch</b> tab for a full breakdown.</div>""",
    unsafe_allow_html=True)

    st.markdown("<hr class='light'>", unsafe_allow_html=True)

    # ── Price band vs revenue ─────────────────────────────────────────────
    st.markdown('<div class="sec">Which Price Range Drives the Most Revenue?</div>', unsafe_allow_html=True)
    fdf2 = fdf.copy()
    fdf2["band"] = pd.cut(fdf2["price"],
        bins=[0,299,499,999,1999,4999,99999],
        labels=["<₹300","₹300–499","₹500–999","₹1k–2k","₹2k–5k","₹5k+"])

    col_a, col_b = st.columns(2)
    with col_a:
        bc = fdf2["band"].value_counts().sort_index().reset_index()
        bc.columns = ["Band","Count"]
        fig = px.bar(bc, x="Band", y="Count", color_discrete_sequence=["#3498DB"],
                     text="Count", labels={"Band":"","Count":"Products"})
        fig = style_fig(fig, height=260)
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        if fdf2["asin_revenue"].notna().any():
            br = fdf2.groupby("band", observed=True)["asin_revenue"].sum().reset_index()
            br.columns = ["Band","Revenue"]
            fig = px.bar(br, x="Band", y="Revenue", color_discrete_sequence=["#2ECC71"],
                         text=br["Revenue"].apply(lambda x: f"₹{x/100000:.1f}L"),
                         labels={"Band":"","Revenue":"₹ Monthly Revenue"})
            fig = style_fig(fig, height=260)
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(yaxis_tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

    band_sum = fdf2.groupby("band", observed=True).agg(
        count=("price","count"), avg_rating=("rating","mean"),
        avg_reviews=("reviews","mean"), total_rev=("asin_revenue","sum"),
    ).reset_index().dropna()
    if len(band_sum):
        rev_mx = band_sum["total_rev"].max() or 1
        band_sum["sc"] = (
            (band_sum["avg_reviews"] / (band_sum["avg_reviews"].max() or 1)) * 40 +
            (band_sum["avg_rating"]  / 5) * 30 +
            (band_sum["total_rev"]   / rev_mx) * 30
        )
        best_band = band_sum.sort_values("sc", ascending=False).iloc[0]["band"]
        p25 = int(fdf["price"].quantile(.30)); p75 = int(fdf["price"].quantile(.65))
        st.markdown(f"""<div class="conclude">✅ Sweet spot: <b>{best_band}</b> — best balance of volume, ratings, and revenue.
        CLAPTALES should launch in the <b>₹{p25:,}–₹{p75:,}</b> range for maximum early traction.</div>""",
        unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 2 — COMPETITOR INTEL                                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
with tab2:
    if not fdf["brand"].notna().any():
        st.info("Brand column not detected in your file.")
    else:
        bs = fdf.groupby("brand").agg(
            listings      =("price","count"),
            avg_price     =("price","mean"),
            avg_rating    =("rating","mean"),
            avg_reviews   =("reviews","mean"),
            total_sales   =("asin_sales","sum"),
            total_rev     =("asin_revenue","sum"),
        ).reset_index()
        bs = bs[bs["listings"] >= 2].sort_values("listings", ascending=False)

        col_l, col_r = st.columns(2)

        # ── Listings per brand ────────────────────────────────────────────
        with col_l:
            st.markdown('<div class="sec">Market Share by Brand</div>', unsafe_allow_html=True)
            top8 = bs.head(8).sort_values("listings")
            fig = px.bar(top8, x="listings", y="brand", orientation="h",
                         color="listings", color_continuous_scale=["#93C5FD","#3498DB"],
                         text="listings", labels={"listings":"Listings","brand":""})
            fig = style_fig(fig, height=300)
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False, xaxis_title="Number of listings")
            st.plotly_chart(fig, use_container_width=True)

        # ── Positioning map ───────────────────────────────────────────────
        with col_r:
            st.markdown('<div class="sec">Brand Positioning — Price vs Quality</div>', unsafe_allow_html=True)
            fig = px.scatter(bs.head(14), x="avg_price", y="avg_rating",
                             size="listings", size_max=32,
                             color="brand", color_discrete_sequence=COLORS, text="brand",
                             labels={"avg_price":"Avg Price (₹)","avg_rating":"Avg Rating"})
            fig = style_fig(fig, height=300)
            fig.update_traces(textposition="top center", textfont_size=9)
            fig.update_layout(showlegend=False)
            fig.add_hline(y=4.0, line_dash="dot", line_color="#ddd",
                          annotation_text="4.0★ quality bar", annotation_font_size=10)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""<div class="insight">📌 <b>Reading the map:</b>
        Top-right = premium + well-rated (hard to beat).
        Bottom-right = expensive but poor quality (<b>most vulnerable</b> to disruption).
        CLAPTALES should target the mid-price, high-quality quadrant — top-left to top-centre.</div>""",
        unsafe_allow_html=True)

        st.markdown("<hr class='light'>", unsafe_allow_html=True)

        # ── Scorecard ─────────────────────────────────────────────────────
        st.markdown('<div class="sec">Full Competitor Scorecard</div>', unsafe_allow_html=True)
        disp = bs.head(20).copy()
        disp["avg_price"]   = disp["avg_price"].apply(lambda x: f"₹{x:,.0f}")
        disp["avg_rating"]  = disp["avg_rating"].apply(lambda x: f"{x:.1f} ★")
        disp["avg_reviews"] = disp["avg_reviews"].apply(lambda x: f"{x:,.0f}")
        disp["total_sales"] = disp["total_sales"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        disp["total_rev"]   = disp["total_rev"].apply(lambda x: f"₹{x/100000:.1f}L/mo" if x > 0 else "—")
        disp.columns = ["Brand","Listings","Avg Price","Avg Rating","Avg Reviews","Monthly Sales","Monthly Revenue"]
        st.dataframe(disp, use_container_width=True, hide_index=True)

        # ── Brands to disrupt ─────────────────────────────────────────────
        weak = bs[(bs["avg_rating"] < 4.0) & (bs["avg_reviews"] > bs["avg_reviews"].median())]
        if len(weak):
            st.markdown("<hr class='light'>", unsafe_allow_html=True)
            st.markdown('<div class="sec">🎯 Brands to Disrupt</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="warn">⚠️ <b>{len(weak)} brands</b> have high demand but ratings below 4.0.
            Their customers are unhappy but have nowhere better to go.
            CLAPTALES can take this market share by launching a higher-quality alternative.</div>""",
            unsafe_allow_html=True)
            for _, r in weak.sort_values("avg_reviews", ascending=False).head(6).iterrows():
                rev_line = f"₹{r['total_rev']/100000:.1f}L/mo revenue" if r["total_rev"] > 0 else ""
                st.markdown(f"- **{r['brand']}** — {r['listings']} listings · {r['avg_rating']:.1f}★ avg · {r['avg_reviews']:,.0f} avg reviews · {rev_line}")

        # ── Active sellers ────────────────────────────────────────────────
        if fdf["sellers"].notna().any():
            st.markdown("<hr class='light'>", unsafe_allow_html=True)
            st.markdown('<div class="sec">Competition Intensity — Sellers per Product</div>', unsafe_allow_html=True)
            fig = px.histogram(fdf, x="sellers", nbins=10, color_discrete_sequence=["#9B59B6"],
                               labels={"sellers":"Active Sellers per Product","count":"Products"})
            fig = style_fig(fig, height=220)
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)
            low_pct = round(len(fdf[fdf["sellers"] <= 2]) / len(fdf) * 100)
            st.markdown(f"""<div class="conclude">✅ <b>{low_pct}% of products have ≤2 active sellers</b> —
            low competition means CLAPTALES can win the Buy Box and rank on page 1 faster.</div>""",
            unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 3 — PRODUCTS TO LAUNCH                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
with tab3:
    st.markdown("""<div class="insight">📌 <b>How this works:</b>
    We score every category and subcategory by revenue, sales volume, review demand, and growth trend —
    then surface the top 2 categories → top 3 subcategories each → top 3 products per subcategory,
    with images and direct Amazon links.</div>""", unsafe_allow_html=True)

    # ── Score categories ──────────────────────────────────────────────────
    cat_grp = agg_group(fdf[fdf["asin_revenue"].fillna(0) > 0], "category") \
              if fdf["asin_revenue"].notna().any() and (fdf["asin_revenue"].fillna(0) > 0).any() \
              else agg_group(fdf, "category")
    cat_grp = score_df(cat_grp, "category")
    top2_cats = cat_grp.head(2)["category"].tolist()
    if not top2_cats:
        st.warning("Not enough category data to generate recommendations.")
        st.stop()

    # ── Render each category ──────────────────────────────────────────────
    for cat_idx, cat_name in enumerate(top2_cats):
        cat_rank_label = ["🥇 Best Category","🥈 Runner-up Category"][cat_idx]
        cat_row = cat_grp[cat_grp["category"] == cat_name].iloc[0]

        # Category header strip
        st.markdown(f"""
        <div style="background:{'linear-gradient(135deg,#FF6B6B,#FF8E53)' if cat_idx==0 else 'linear-gradient(135deg,#3498DB,#2980B9)'};
                    border-radius:12px;padding:1rem 1.5rem;color:white;margin:1.2rem 0 .8rem;
                    display:flex;align-items:center;gap:1rem">
          <div style="font-size:1.8rem">{'🏆' if cat_idx==0 else '🎖️'}</div>
          <div>
            <div style="font-size:.72rem;opacity:.8;text-transform:uppercase;letter-spacing:.08em">{cat_rank_label}</div>
            <div style="font-size:1.3rem;font-weight:700">{cat_name}</div>
            <div style="font-size:.8rem;opacity:.9">
              Score {cat_row['score']:.0f}/100 &nbsp;·&nbsp;
              ₹{cat_row['total_revenue']/100000:.1f}L monthly revenue &nbsp;·&nbsp;
              {cat_row['avg_rating']:.1f}★ avg rating
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Score subcategories within this category ───────────────────────
        cat_df = fdf[fdf["category"] == cat_name].copy()
        sub_grp = agg_group(cat_df[cat_df["asin_revenue"].fillna(0) > 0], "subcategory") \
                  if (cat_df["asin_revenue"].fillna(0) > 0).any() \
                  else agg_group(cat_df, "subcategory")
        sub_grp = score_df(sub_grp, "subcategory")
        top3_subs = sub_grp.head(3)["subcategory"].tolist()

        if not top3_subs:
            st.info(f"No subcategory data available for {cat_name}.")
            continue

        # ── One expander per subcategory ───────────────────────────────────
        sub_medals = ["🥇","🥈","🥉"]
        sub_borders = ["#FFD700","#C0C0C0","#CD7F32"]

        for sub_idx, sub_name in enumerate(top3_subs):
            sub_row = sub_grp[sub_grp["subcategory"] == sub_name].iloc[0]
            trend_badge = f"{sub_row['avg_sales_trend']:+.0f}% trend" if pd.notna(sub_row.get("avg_sales_trend")) else ""

            with st.expander(
                f"{sub_medals[sub_idx]} {sub_name}  ·  Score {sub_row['score']:.0f}/100  ·  "
                f"₹{sub_row['total_revenue']/100000:.1f}L/mo  ·  {sub_row['avg_rating']:.1f}★  ·  {trend_badge}",
                expanded=(sub_idx == 0 and cat_idx == 0)   # auto-open only the very first one
            ):
                # Sub-level stats row
                s1,s2,s3,s4 = st.columns(4)
                s1.metric("Avg Price",    f"₹{sub_row['avg_price']:,.0f}")
                s2.metric("Avg Rating",   f"{sub_row['avg_rating']:.1f} ★")
                s3.metric("Avg Reviews",  f"{sub_row['avg_reviews']:,.0f}")
                s4.metric("Monthly Rev",  f"₹{sub_row['total_revenue']/100000:.1f}L")

                # ── Top 3 products ─────────────────────────────────────────
                sub_prods = cat_df[cat_df["subcategory"] == sub_name].copy()
                sub_prods = score_products(sub_prods).head(3)

                if len(sub_prods) == 0:
                    st.info("No products found for this subcategory.")
                    continue

                st.markdown(f"**Top {len(sub_prods)} in-demand products to study:**")
                prod_cols = st.columns(min(3, len(sub_prods)))

                for p_idx, (_, prod) in enumerate(sub_prods.iterrows()):
                    with prod_cols[p_idx]:
                        badge_text, badge_color, badge_bg = demand_badge(prod["prod_score"])

                        img_url  = (str(prod["image_url"])
                                    if "image_url" in prod.index
                                    and pd.notna(prod["image_url"])
                                    and str(prod["image_url"]).startswith("http")
                                    else "")
                        prod_url = (str(prod["url"])
                                    if "url" in prod.index
                                    and pd.notna(prod["url"])
                                    and str(prod["url"]).startswith("http")
                                    else "")

                        raw_title = str(prod["title"]) if "title" in prod.index and pd.notna(prod.get("title")) else "Unnamed"
                        title     = (raw_title[:55]+"…") if len(raw_title) > 55 else raw_title
                        brand     = str(prod.get("brand","—"))
                        price     = f"₹{prod['price']:,.0f}"   if pd.notna(prod.get("price"))  else "—"
                        rating    = f"{prod['rating']:.1f}★"   if pd.notna(prod.get("rating")) else "—"
                        reviews   = f"{int(prod['reviews']):,}" if prod["reviews"] > 0          else "—"
                        sales     = f"{int(prod['asin_sales']):,}/mo" if prod["asin_sales"] > 0  else "—"
                        revenue   = f"₹{prod['asin_revenue']/100000:.2f}L/mo" if prod["asin_revenue"] > 0 else "—"
                        s_trend   = prod.get("sales_trend", None)
                        trend_txt = f"{s_trend:+.0f}% trend" if pd.notna(s_trend) else ""
                        t_color   = "#2ECC71" if (pd.notna(s_trend) and s_trend >= 0) else "#E74C3C"

                        img_html = (
                            f'<img src="{img_url}" style="width:100%;height:130px;object-fit:contain;'
                            f'border-radius:8px;background:#FAFAFA;padding:6px;">'
                            if img_url else
                            '<div style="height:130px;background:#F5F5F5;border-radius:8px;'
                            'display:flex;align-items:center;justify-content:center;'
                            'color:#CCC;font-size:2.5rem">🧸</div>'
                        )
                        link_btn = (
                            f'<a href="{prod_url}" target="_blank" style="display:block;text-align:center;'
                            f'background:#FF6B6B;color:white;padding:7px;border-radius:8px;'
                            f'font-size:.76rem;font-weight:600;text-decoration:none;margin-top:8px">'
                            f'View on Amazon →</a>'
                            if prod_url else ""
                        )

                        st.markdown(f"""
                        <div style="background:white;border:1px solid #EFEFEF;border-radius:12px;
                                    padding:12px;height:100%;border-top:3px solid {badge_color}">
                          {img_html}
                          <div style="margin-top:9px">
                            <span style="background:{badge_bg};color:{badge_color};font-size:.68rem;
                                         font-weight:600;padding:2px 8px;border-radius:99px">{badge_text}</span>
                            <div style="font-size:.81rem;font-weight:600;color:#1A1A1A;
                                         margin:7px 0 2px;line-height:1.35">{title}</div>
                            <div style="font-size:.73rem;color:#999;margin-bottom:9px">{brand}</div>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:.74rem;color:#444">
                              <div>Price<br><b style="color:#1A1A1A">{price}</b></div>
                              <div>Rating<br><b style="color:#1A1A1A">{rating}</b></div>
                              <div>Reviews<br><b style="color:#1A1A1A">{reviews}</b></div>
                              <div>Sales/mo<br><b style="color:#1A1A1A">{sales}</b></div>
                              <div style="grid-column:span 2">Revenue<br>
                                <b style="color:#1A1A1A">{revenue}</b>
                                <span style="color:{t_color};font-size:.68rem;margin-left:4px">{trend_txt}</span>
                              </div>
                            </div>
                          </div>
                          {link_btn}
                        </div>""", unsafe_allow_html=True)

                # Revenue + trend mini-chart
                chart_prods = sub_prods[sub_prods["asin_revenue"] > 0].copy()
                if len(chart_prods) > 1:
                    chart_prods["short"] = chart_prods["title"].apply(
                        lambda x: (str(x)[:28]+"…") if len(str(x)) > 28 else str(x))
                    fig_p = px.bar(chart_prods.sort_values("asin_revenue", ascending=True),
                                   x="asin_revenue", y="short", orientation="h",
                                   color="sales_trend" if chart_prods["sales_trend"].notna().any() else None,
                                   color_continuous_scale=["#E74C3C","#FFC75F","#2ECC71"],
                                   text=chart_prods.sort_values("asin_revenue", ascending=True)["asin_revenue"]
                                        .apply(lambda x: f"₹{x/100000:.1f}L"),
                                   labels={"asin_revenue":"Revenue/mo","short":"",
                                           "sales_trend":"Trend %"})
                    fig_p.update_traces(textposition="outside", marker_line_width=0)
                    fig_p.update_layout(font_family="DM Sans", plot_bgcolor="white", paper_bgcolor="white",
                                        margin=dict(l=8,r=8,t=8,b=8),
                                        coloraxis_colorbar_title="Trend %",
                                        coloraxis_showscale=False,
                                        xaxis_tickformat=",.0f",
                                        height=max(160, len(chart_prods)*55))
                    st.plotly_chart(fig_p, use_container_width=True)

        # Category-level action note
        p_low = int(fdf["price"].quantile(.30))
        p_hi  = int(fdf["price"].quantile(.65))
        quality_bar = round(fdf["rating"].quantile(.75), 1)
        st.markdown(f"""<div class="conclude" style="margin-top:.8rem">
        <b>Action for {cat_name}:</b> Enter at <b>₹{p_low:,}–₹{p_hi:,}</b> ·
        Target <b>{quality_bar}★+</b> product quality · Use <b>FBA</b> from day one ·
        Study the 1★ reviews of the products above — those pain points are your product brief.
        </div>""", unsafe_allow_html=True)

        if cat_idx < len(top2_cats) - 1:
            st.markdown("<hr class='light'>", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#CCC;font-size:.72rem'>"
    "CLAPTALES Market Intelligence · Amazon India · Jungle Scout data · Internal use only"
    "</div>",
    unsafe_allow_html=True
)
