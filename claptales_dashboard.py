import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CLAPTALES | Market Research",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Serif+Display&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.brand-header {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    border-radius: 16px; padding: 1.75rem 2rem; margin-bottom: 1.5rem; color: white;
}
.brand-header h1 { font-family: 'DM Serif Display', serif; font-size: 2rem; margin: 0 0 4px; }
.brand-header p  { margin: 0; opacity: 0.88; font-size: 0.9rem; }
.insight  { background:#FFF8F0; border-left:4px solid #FF8E53; border-radius:0 8px 8px 0; padding:.8rem 1rem; margin:.6rem 0 1rem; font-size:.85rem; color:#5A3E2B; line-height:1.55; }
.conclude { background:#F0FFF4; border-left:4px solid #2ECC71; border-radius:0 8px 8px 0; padding:.8rem 1rem; margin:.5rem 0; font-size:.85rem; color:#1A4731; line-height:1.55; }
.warn     { background:#FFF5F5; border-left:4px solid #E74C3C; border-radius:0 8px 8px 0; padding:.8rem 1rem; margin:.5rem 0; font-size:.85rem; color:#5A1A1A; line-height:1.55; }
.sec { font-size:1.05rem; font-weight:600; color:#1A1A1A; margin:1.2rem 0 .3rem; padding-bottom:.4rem; border-bottom:2px solid #FF8E53; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
COLORS = ["#FF6B6B","#FF8E53","#FFC75F","#2ECC71","#3498DB","#9B59B6","#1ABC9C","#E74C3C","#F39C12","#2980B9"]

def style_fig(fig):
    fig.update_layout(
        font_family="DM Sans", plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=12, r=12, t=36, b=12), colorway=COLORS,
        legend=dict(font_size=11), title_font_size=13,
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

# ── Exact Jungle Scout column map ─────────────────────────────────────────────
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

# ── Sample data ───────────────────────────────────────────────────────────────
def sample_data():
    np.random.seed(42)
    brands = ['FunSkool','Hasbro','Mattel','Lego','Toyzone','Miss&Chief','OK Play','Ratnas','Simba','Funskool']
    subcats = ['Action Figures','Puzzles','Board Games','Soft Toys','Educational Toys','Outdoor Toys','Clay & Dough','Brain Teasers','Building Blocks','Art & Craft']
    rows = []
    for i in range(120):
        brand = np.random.choice(brands, p=[.18,.14,.12,.10,.09,.08,.08,.07,.07,.07])
        sub   = np.random.choice(subcats)
        price = np.random.choice([199,299,399,499,599,799,999,1299,1499,1999,2499,2999])
        rating= round(np.clip(np.random.normal(4.1,.45),1,5),1)
        reviews=int(np.random.exponential(6000))
        bsr   = int(np.random.exponential(4000))+50
        sales = int(np.random.exponential(350))
        rows.append(dict(
            title=f"Sample Toy {i+1} - {sub[:6]}",
            brand=brand, category="Toys & Games", subcategory=sub,
            bsr=bsr, price=price, asin_sales=sales,
            asin_revenue=sales*price, reviews=reviews, rating=rating,
            price_trend=round(np.random.uniform(-30,10),1),
            sales_trend=round(np.random.uniform(-20,80),1),
            fulfillment=np.random.choice(['FBA','FBM'],p=[.72,.28]),
            sellers=np.random.randint(1,6),
            listing_age=np.random.randint(6,200),
            sales_to_rev=round(sales/max(reviews,1),3),
        ))
    return pd.DataFrame(rows)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧸 CLAPTALES")
    st.markdown("**Market Research Dashboard**")
    st.divider()
    uploaded = st.file_uploader("Upload Jungle Scout / Helium10 export", type=["csv","xlsx"])
    st.divider()
    st.markdown("**Filters**")

# ── Load & map ────────────────────────────────────────────────────────────────
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
              "fulfillment","sellers","listing_age","sales_to_rev"]:
        if c not in df.columns:
            df[c] = np.nan
    missing = [c for c in ["price","rating"] if df[c].isna().all()]
    if missing:
        st.error(f"Could not detect required columns: **{', '.join(missing)}**")
        st.markdown("**Columns found in your file:**")
        st.code(", ".join(raw.columns.tolist()))
        st.info("Rename columns to match: `Price`, `Reviews Rating`, `Review Count`, `ASIN Sales`, `ASIN Revenue`, `BSR`, `Brand`, `Subcategory`")
        st.stop()
    df = df.dropna(subset=["price","rating"]).reset_index(drop=True)
    if len(df) == 0:
        st.error("No valid rows found. Check that Price and Reviews Rating columns contain numbers.")
        st.stop()
    using_sample = False
else:
    df = sample_data()
    using_sample = True

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    if using_sample:
        st.info("📊 Sample data shown. Upload your Jungle Scout CSV to analyse real data.")
    subcat_opts = ["All"] + sorted(df["subcategory"].dropna().unique().tolist()) if df["subcategory"].notna().any() else ["All"]
    subcat_sel  = st.selectbox("Subcategory", subcat_opts)
    p_min, p_max = int(df["price"].min()), int(df["price"].max())
    if p_min == p_max: p_max = p_min + 1
    price_range  = st.slider("Price range (₹)", p_min, p_max, (p_min, p_max))
    rating_min   = st.slider("Min rating", 1.0, 5.0, 3.0, 0.1)
    ful_opts     = ["All"] + sorted(df["fulfillment"].dropna().unique().tolist()) if df["fulfillment"].notna().any() else ["All"]
    ful_sel      = st.selectbox("Fulfillment", ful_opts)

# ── Apply filters ─────────────────────────────────────────────────────────────
fdf = df.copy()
if subcat_sel != "All": fdf = fdf[fdf["subcategory"] == subcat_sel]
fdf = fdf[(fdf["price"] >= price_range[0]) & (fdf["price"] <= price_range[1])]
fdf = fdf[fdf["rating"] >= rating_min]
if ful_sel != "All":    fdf = fdf[fdf["fulfillment"] == ful_sel]

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="brand-header">
  <h1>🧸 CLAPTALES Market Intelligence</h1>
  <p>Amazon India Toy Market · Jungle Scout data · Helps the team decide what to build next</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Overview",
    "🎯 Opportunity Finder",
    "💰 Pricing Strategy",
    "🏆 Competitor Intel",
    "🚀 Launch Decision",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKET OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="sec">Market Snapshot</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    total_rev = fdf["asin_revenue"].fillna(0).sum()
    c1.metric("Products tracked",     f"{len(fdf):,}")
    c2.metric("Avg price",            f"₹{fdf['price'].mean():,.0f}")
    c3.metric("Avg rating",           f"{fdf['rating'].mean():.1f} ★")
    c4.metric("Est. monthly revenue", f"₹{total_rev/100000:.1f}L" if total_rev > 0 else "N/A")
    c5.metric("Median BSR",           f"{fdf['bsr'].median():,.0f}" if fdf['bsr'].notna().any() else "N/A")

    st.markdown("""<div class="insight">📌 <b>How to read this:</b> These numbers are your market baseline.
    Any product CLAPTALES launches should beat the average price-to-rating ratio shown here.</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sec">Revenue by Subcategory</div>', unsafe_allow_html=True)
        if fdf["subcategory"].notna().any() and fdf["asin_revenue"].notna().any():
            sub_rev = fdf.groupby("subcategory")["asin_revenue"].sum().reset_index()
            sub_rev.columns = ["Subcategory","Revenue"]
            sub_rev = sub_rev.sort_values("Revenue", ascending=True).tail(10)
            fig = px.bar(sub_rev, x="Revenue", y="Subcategory", orientation="h",
                         color_discrete_sequence=["#FF8E53"], text_auto=".2s")
            fig = style_fig(fig)
            fig.update_traces(marker_line_width=0, textposition="outside")
            fig.update_layout(yaxis_title="", xaxis_title="₹ Monthly Revenue", height=340)
            st.plotly_chart(fig, use_container_width=True)
            best = sub_rev.iloc[-1]["Subcategory"]
            st.markdown(f"""<div class="conclude">✅ <b>{best}</b> generates the most monthly revenue —
            customers are actively spending here. High priority for CLAPTALES to evaluate.</div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="sec">Fulfillment Split (FBA vs FBM)</div>', unsafe_allow_html=True)
        if fdf["fulfillment"].notna().any():
            ful = fdf["fulfillment"].value_counts().reset_index()
            ful.columns = ["Type","Count"]
            fig = px.pie(ful, values="Count", names="Type", hole=0.5,
                         color_discrete_sequence=["#3498DB","#FF6B6B","#2ECC71"])
            fig = style_fig(fig)
            fig.update_traces(textposition="outside", textinfo="label+percent")
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            fba_pct = round(fdf[fdf["fulfillment"]=="FBA"].shape[0] / len(fdf) * 100)
            st.markdown(f"""<div class="conclude">✅ <b>{fba_pct}% of products use FBA.</b>
            CLAPTALES should also use FBA for faster delivery and better search ranking.</div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Rating Distribution</div>', unsafe_allow_html=True)
    fig = px.histogram(fdf, x="rating", nbins=18, color_discrete_sequence=["#3498DB"])
    fig = style_fig(fig)
    fig.update_layout(bargap=0.08, xaxis_title="Star Rating", yaxis_title="Products", height=260)
    st.plotly_chart(fig, use_container_width=True)
    pct_low = round(len(fdf[fdf["rating"] < 3.5]) / max(len(fdf),1) * 100)
    st.markdown(f"""<div class="insight">📌 <b>{pct_low}% of products rated below 3.5★.</b>
    Customers are frequently disappointed. If CLAPTALES delivers 4.2★+ consistently, we stand out immediately.</div>""", unsafe_allow_html=True)

    if fdf["sales_trend"].notna().any():
        st.markdown('<div class="sec">90-Day Sales Trend by Subcategory</div>', unsafe_allow_html=True)
        trend = fdf.groupby("subcategory")["sales_trend"].mean().reset_index()
        trend.columns = ["Subcategory","Avg Trend (%)"]
        trend = trend.sort_values("Avg Trend (%)", ascending=False).head(12)
        trend["color"] = trend["Avg Trend (%)"].apply(lambda x: "#2ECC71" if x >= 0 else "#E74C3C")
        fig = px.bar(trend, x="Subcategory", y="Avg Trend (%)",
                     color="color", color_discrete_map="identity", text_auto=".1f")
        fig = style_fig(fig)
        fig.update_layout(showlegend=False, xaxis_tickangle=-35, height=300)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
        growing = trend[trend["Avg Trend (%)"] > 0]["Subcategory"].tolist()
        if growing:
            st.markdown(f"""<div class="conclude">✅ Growing subcategories right now: <b>{', '.join(growing[:4])}</b>.
            Entering a growing market means demand is already pulling — easier to get early sales.</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — OPPORTUNITY FINDER
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec">Finding the White Space</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight">📌 We are looking for subcategories with high sales volume
    but weak average ratings — customers want the product but no one is delivering quality.
    These are CLAPTALES best entry points.</div>""", unsafe_allow_html=True)

    pdf = fdf.dropna(subset=["reviews","rating","price"]).copy()
    med_rev = pdf["reviews"].median()

    def quadrant(row):
        hi   = row["reviews"] >= med_rev
        good = row["rating"]  >= 4.0
        if hi and not good: return "🟢 Opportunity"
        if hi and good:     return "🔴 Competitive"
        if not hi and good: return "🟡 Niche"
        return "⚪ Low priority"

    pdf["zone"] = pdf.apply(quadrant, axis=1)
    color_map = {"🟢 Opportunity":"#2ECC71","🔴 Competitive":"#E74C3C",
                 "🟡 Niche":"#F39C12","⚪ Low priority":"#BDC3C7"}

    st.markdown('<div class="sec">Opportunity Matrix — Reviews vs Rating</div>', unsafe_allow_html=True)
    hover = {c: True for c in ["title","brand","subcategory","price","reviews","rating"] if c in pdf.columns}
    hover["zone"] = False
    fig = px.scatter(pdf, x="reviews", y="rating", color="zone",
                     color_discrete_map=color_map, size="price", size_max=20,
                     hover_data=hover,
                     labels={"reviews":"Review Count","rating":"Star Rating"})
    fig.add_hline(y=4.0, line_dash="dash", line_color="#aaa", line_width=1,
                  annotation_text="4.0★ quality bar", annotation_position="top right")
    fig.add_vline(x=med_rev, line_dash="dash", line_color="#aaa", line_width=1,
                  annotation_text="median reviews", annotation_position="top right")
    fig = style_fig(fig)
    fig.update_layout(height=420, legend_title_text="Zone")
    st.plotly_chart(fig, use_container_width=True)

    n_opp = len(pdf[pdf["zone"]=="🟢 Opportunity"])
    st.markdown(f"""<div class="conclude">✅ <b>{n_opp} products</b> in the Opportunity zone —
    high demand, poor quality competition. Study these: read their 1-star reviews to understand
    what customers hate. Build CLAPTALES products that fix those exact problems.</div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Top Opportunity Products to Study</div>', unsafe_allow_html=True)
    opp = pdf[pdf["zone"]=="🟢 Opportunity"].sort_values("reviews", ascending=False)
    if len(opp):
        show = [c for c in ["title","brand","subcategory","price","rating","reviews","asin_sales","sales_trend"] if c in opp.columns]
        disp = opp[show].head(20).copy()
        disp["price"]   = disp["price"].apply(lambda x: f"₹{x:,.0f}")
        disp["reviews"] = disp["reviews"].apply(lambda x: f"{int(x):,}")
        if "asin_sales"   in disp: disp["asin_sales"]   = disp["asin_sales"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        if "sales_trend"  in disp: disp["sales_trend"]  = disp["sales_trend"].apply(lambda x: f"{x:+.0f}%" if pd.notna(x) else "—")
        disp.columns = [c.replace("_"," ").title() for c in disp.columns]
        st.dataframe(disp, use_container_width=True, hide_index=True)
    else:
        st.info("No opportunity products found with current filters.")

    if fdf["subcategory"].notna().any():
        st.markdown('<div class="sec">Subcategory Opportunity Score</div>', unsafe_allow_html=True)
        heat = fdf.groupby("subcategory").agg(
            avg_rating=("rating","mean"),
            avg_reviews=("reviews","mean"),
        ).reset_index()
        heat["score"] = (
            (heat["avg_reviews"] / heat["avg_reviews"].max()) * 50 +
            ((5 - heat["avg_rating"]) / 5) * 50
        ).round(1)
        heat = heat.sort_values("score", ascending=False)
        fig = px.bar(heat, x="score", y="subcategory", orientation="h",
                     color="score", color_continuous_scale=["#FFC75F","#FF8E53","#FF6B6B"],
                     text="score")
        fig = style_fig(fig)
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(yaxis_title="", xaxis_title="Opportunity Score (0–100)",
                          coloraxis_showscale=False, height=max(300, len(heat)*32))
        st.plotly_chart(fig, use_container_width=True)
        top3 = heat.head(3)["subcategory"].tolist()
        st.markdown(f"""<div class="conclude">✅ Best subcategories to enter: <b>{', '.join(top3)}</b>.
        High demand + weak competition = easiest place to launch and win early reviews.</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PRICING STRATEGY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec">Where Should CLAPTALES Price?</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight">📌 Goal: Find the price range that drives most sales and revenue —
    not so cheap it kills margins, not so expensive it kills volume.</div>""", unsafe_allow_html=True)

    fdf2 = fdf.copy()
    fdf2["band"] = pd.cut(fdf2["price"],
        bins=[0,299,499,999,1999,4999,99999],
        labels=["<₹300","₹300–499","₹500–999","₹1k–2k","₹2k–5k","₹5k+"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="sec">Products per Price Band</div>', unsafe_allow_html=True)
        bc = fdf2["band"].value_counts().sort_index().reset_index()
        bc.columns = ["Band","Count"]
        fig = px.bar(bc, x="Band", y="Count", color_discrete_sequence=["#FF6B6B"], text="Count")
        fig = style_fig(fig)
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(xaxis_title="", yaxis_title="Products", height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="sec">Monthly Revenue per Price Band</div>', unsafe_allow_html=True)
        if fdf2["asin_revenue"].notna().any():
            br = fdf2.groupby("band", observed=True)["asin_revenue"].sum().reset_index()
            br.columns = ["Band","Revenue"]
            fig = px.bar(br, x="Band", y="Revenue", color_discrete_sequence=["#2ECC71"], text_auto=".2s")
            fig = style_fig(fig)
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(xaxis_title="", yaxis_title="₹ Revenue", height=280)
            st.plotly_chart(fig, use_container_width=True)

    band_summary = fdf2.groupby("band", observed=True).agg(
        count=("price","count"),
        avg_rating=("rating","mean"),
        avg_reviews=("reviews","mean"),
        total_rev=("asin_revenue","sum"),
    ).reset_index().dropna()

    if len(band_summary):
        rev_max = band_summary["total_rev"].max() or 1
        band_summary["score"] = (
            (band_summary["avg_reviews"] / band_summary["avg_reviews"].max()) * 40 +
            (band_summary["avg_rating"]  / 5) * 30 +
            (band_summary["total_rev"]   / rev_max) * 30
        )
        best_band = band_summary.sort_values("score", ascending=False).iloc[0]["band"]
        st.markdown(f"""<div class="conclude">✅ <b>Recommended entry price for CLAPTALES: {best_band}</b> —
        best combination of demand, quality, and revenue. Launch here first before moving to premium pricing.</div>""", unsafe_allow_html=True)

    if fdf["price_trend"].notna().any():
        st.markdown('<div class="sec">Price Trend (90 Days) — Is the Market Going Up or Down?</div>', unsafe_allow_html=True)
        fig = px.histogram(fdf, x="price_trend", nbins=20, color_discrete_sequence=["#9B59B6"])
        fig = style_fig(fig)
        fig.update_layout(bargap=0.08, xaxis_title="Price Change % (90 days)", yaxis_title="Products", height=250)
        fig.add_vline(x=0, line_color="#E74C3C", line_width=1.5)
        st.plotly_chart(fig, use_container_width=True)
        declining = round((fdf["price_trend"] < 0).sum() / len(fdf) * 100)
        st.markdown(f"""<div class="insight">📌 <b>{declining}% of products had price drops in 90 days.</b>
        Sellers are competing on price. CLAPTALES should compete on quality and branding instead.</div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Does Higher Price = Better Rating?</div>', unsafe_allow_html=True)
    fig = px.scatter(fdf.dropna(subset=["price","rating"]), x="price", y="rating",
                     trendline="lowess",
                     color="subcategory" if fdf["subcategory"].notna().any() else None,
                     color_discrete_sequence=COLORS,
                     hover_data=["brand","reviews"] if "brand" in fdf.columns else None,
                     labels={"price":"Price (₹)","rating":"Rating"})
    fig = style_fig(fig)
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)
    corr = fdf[["price","rating"]].corr().iloc[0,1]
    direction = "weak positive" if corr > 0.1 else ("weak negative" if corr < -0.1 else "no meaningful")
    st.markdown(f"""<div class="insight">📌 There is a <b>{direction} correlation</b> (r={corr:.2f}) between price and rating.
    Customers do not rate expensive toys higher automatically — <b>quality matters more than price tag.</b></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — COMPETITOR INTEL
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec">Who Are We Up Against?</div>', unsafe_allow_html=True)
    if not fdf["brand"].notna().any():
        st.info("Brand column not detected in your file.")
    else:
        bs = fdf.groupby("brand").agg(
            listings=("price","count"),
            avg_price=("price","mean"),
            avg_rating=("rating","mean"),
            avg_reviews=("reviews","mean"),
            total_sales=("asin_sales","sum"),
            total_rev=("asin_revenue","sum"),
        ).reset_index()
        bs = bs[bs["listings"] >= 2].sort_values("listings", ascending=False)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="sec">Top Brands by Listing Count</div>', unsafe_allow_html=True)
            top8 = bs.head(8).sort_values("listings")
            fig = px.bar(top8, x="listings", y="brand", orientation="h",
                         color_discrete_sequence=["#3498DB"], text="listings")
            fig = style_fig(fig)
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(yaxis_title="", xaxis_title="Listings", height=320)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="sec">Brand Positioning Map</div>', unsafe_allow_html=True)
            fig = px.scatter(bs.head(14), x="avg_price", y="avg_rating",
                             size="listings", size_max=32,
                             color="brand", color_discrete_sequence=COLORS, text="brand",
                             labels={"avg_price":"Avg Price (₹)","avg_rating":"Avg Rating"})
            fig = style_fig(fig)
            fig.update_traces(textposition="top center", textfont_size=9)
            fig.update_layout(showlegend=False, height=340)
            fig.add_hline(y=4.0, line_dash="dot", line_color="#ddd", annotation_text="4.0★ quality bar")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""<div class="insight">📌 <b>Positioning map:</b> Top-right = premium & well-rated (hard to beat).
        Bottom-right = expensive but poorly rated (vulnerable). CLAPTALES should aim for
        mid-price, high-quality — top-left to top-centre of this chart.</div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec">Competitor Scorecard</div>', unsafe_allow_html=True)
        disp = bs.head(15).copy()
        disp["avg_price"]   = disp["avg_price"].apply(lambda x: f"₹{x:,.0f}")
        disp["avg_rating"]  = disp["avg_rating"].apply(lambda x: f"{x:.1f} ★")
        disp["avg_reviews"] = disp["avg_reviews"].apply(lambda x: f"{x:,.0f}")
        disp["total_sales"] = disp["total_sales"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "—")
        disp["total_rev"]   = disp["total_rev"].apply(lambda x: f"₹{x/100000:.1f}L/mo" if x > 0 else "—")
        disp.columns = ["Brand","Listings","Avg Price","Avg Rating","Avg Reviews","Monthly Sales","Monthly Revenue"]
        st.dataframe(disp, use_container_width=True, hide_index=True)

        weak = bs[(bs["avg_rating"] < 4.0) & (bs["avg_reviews"] > bs["avg_reviews"].median())]
        if len(weak):
            st.markdown('<div class="sec">Brands to Disrupt</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="warn">⚠️ <b>{len(weak)} brands</b> have high demand but poor ratings.
            Their customers are stuck with them. CLAPTALES can capture this market share by launching
            a better-quality alternative.</div>""", unsafe_allow_html=True)
            for _, r in weak.sort_values("avg_reviews", ascending=False).head(6).iterrows():
                st.markdown(f"- **{r['brand']}** — {r['listings']} listings · {r['avg_rating']:.1f}★ · {r['avg_reviews']:,.0f} avg reviews")

        if fdf["sellers"].notna().any():
            st.markdown('<div class="sec">Competition Intensity — Active Sellers per Product</div>', unsafe_allow_html=True)
            fig = px.histogram(fdf, x="sellers", nbins=10, color_discrete_sequence=["#9B59B6"])
            fig = style_fig(fig)
            fig.update_layout(bargap=0.1, xaxis_title="Active Sellers", yaxis_title="Products", height=240)
            st.plotly_chart(fig, use_container_width=True)
            low_comp_pct = round(len(fdf[fdf["sellers"] <= 2]) / len(fdf) * 100)
            st.markdown(f"""<div class="conclude">✅ <b>{low_comp_pct}% of products have 2 or fewer active sellers.</b>
            Low seller count = easier to win the Buy Box and rank on page 1.</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — LAUNCH DECISION
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec">🚀 What Should CLAPTALES Launch Next?</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight">📌 This page synthesises all data into a clear recommendation
    for the management team. Updates automatically when you upload new data.</div>""", unsafe_allow_html=True)

    if fdf["subcategory"].notna().any():
        sc = fdf.groupby("subcategory").agg(
            products=("price","count"),
            avg_price=("price","mean"),
            avg_rating=("rating","mean"),
            avg_reviews=("reviews","mean"),
            total_rev=("asin_revenue","sum"),
            avg_sales_trend=("sales_trend","mean"),
        ).reset_index()
        rev_max    = sc["total_rev"].max() or 1
        trend_norm = ((sc["avg_sales_trend"].fillna(0) + 100) / 200).clip(0,1)
        sc["score"] = (
            (sc["avg_reviews"] / sc["avg_reviews"].max()) * 35 +
            ((5 - sc["avg_rating"]) / 5) * 25 +
            (sc["total_rev"] / rev_max) * 25 +
            trend_norm * 15
        ).round(1)
        sc = sc.sort_values("score", ascending=False)

        fig = px.bar(sc, x="score", y="subcategory", orientation="h",
                     color="score", color_continuous_scale=["#FFC75F","#FF8E53","#FF6B6B"],
                     text="score")
        fig = style_fig(fig)
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(yaxis_title="", xaxis_title="Launch Opportunity Score (0–100)",
                          coloraxis_showscale=False, height=max(300, len(sc)*30))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="sec">Top 3 Subcategories to Enter</div>', unsafe_allow_html=True)
        medals = ["🥇","🥈","🥉"]
        borders = ["#FFD700","#C0C0C0","#CD7F32"]
        cols = st.columns(3)
        for i, (_, row) in enumerate(sc.head(3).iterrows()):
            with cols[i]:
                trend_txt = f"{row['avg_sales_trend']:+.0f}% sales trend" if pd.notna(row["avg_sales_trend"]) else ""
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:1.2rem;border:1px solid #F0F0F0;border-top:4px solid {borders[i]};">
                  <div style="font-size:1.5rem">{medals[i]}</div>
                  <div style="font-size:1rem;font-weight:600;margin:8px 0 6px;color:#1A1A1A">{row['subcategory']}</div>
                  <div style="font-size:1.6rem;font-weight:600;color:#FF6B6B">{row['score']:.0f}<span style="font-size:.8rem;color:#999"> /100</span></div>
                  <hr style="border:none;border-top:1px solid #F5F5F5;margin:10px 0">
                  <div style="font-size:.8rem;color:#666;line-height:1.8">
                    Avg price: <b>₹{row['avg_price']:,.0f}</b><br>
                    Avg rating: <b>{row['avg_rating']:.1f}★</b><br>
                    Avg reviews: <b>{row['avg_reviews']:,.0f}</b><br>
                    {trend_txt}
                  </div>
                </div>""", unsafe_allow_html=True)

    p25 = int(fdf["price"].quantile(0.30))
    p75 = int(fdf["price"].quantile(0.65))
    quality_bar = round(fdf["rating"].quantile(0.75), 1)
    avg_rat = fdf["rating"].mean()
    fba_pct = round(fdf[fdf["fulfillment"]=="FBA"].shape[0] / max(len(fdf),1) * 100) if fdf["fulfillment"].notna().any() else 72

    st.markdown("")
    st.markdown('<div class="sec">Management Action Plan</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="conclude"><b>1. Price to win early traction</b><br>
Enter the <b>₹{p25:,} – ₹{p75:,}</b> range — this is where most buying decisions happen.
Below ₹{p25:,} signals low quality; above ₹{p75:,} reduces volume for an unproven brand.
Once CLAPTALES builds reviews and trust, premium pricing becomes possible.</div>

<div class="conclude"><b>2. Quality is your biggest moat</b><br>
Market avg rating is {avg_rat:.1f}★. Top 25% hit {quality_bar}★+.
<b>Target {quality_bar}★ minimum at launch.</b> Strong ratings drive organic ranking,
repeat purchases, and word-of-mouth — all of which reduce marketing cost over time.</div>

<div class="conclude"><b>3. Go after weak competitors first</b><br>
Find brands with ratings below 4.0 and high review counts in the Competitor Intel tab.
Read their 1-star reviews — those complaints are your product brief.
Build the version that fixes every complaint, price it similarly, and launch.</div>

<div class="conclude"><b>4. Use FBA from day one</b><br>
{fba_pct}% of successful competitors use FBA. It improves delivery, search ranking, and trust.
The fulfilment cost is worth it — organic ranking lift alone justifies it for a new brand.</div>

<div class="conclude"><b>5. Go deep before going wide</b><br>
Pick the top-scoring subcategory, launch 2–3 closely related SKUs, dominate that niche first.
Amazon rewards category depth — 5 strong products in one subcategory outrank 20 scattered ones.</div>
""", unsafe_allow_html=True)

    st.divider()
    export_cols = [c for c in ["title","brand","subcategory","price","rating","reviews",
                               "asin_sales","asin_revenue","bsr","sales_trend",
                               "price_trend","fulfillment","sellers","listing_age"] if c in fdf.columns]
    csv = fdf[export_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download filtered dataset as CSV", data=csv,
                       file_name="claptales_research_filtered.csv", mime="text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("<div style='text-align:center;color:#CCC;font-size:.75rem'>CLAPTALES Market Intelligence · Amazon India · Jungle Scout · Internal use only</div>",
            unsafe_allow_html=True)
