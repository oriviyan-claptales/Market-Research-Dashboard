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
            url="https://www.amazon.in",
            image_url="",
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
              "fulfillment","sellers","listing_age","sales_to_rev","url","image_url"]:
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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Market Overview",
    "🎯 Opportunity Finder",
    "💰 Pricing Strategy",
    "🏆 Competitor Intel",
    "🚀 Launch Decision",
    "🛍️ Products to Launch",
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

    # Rating quality KPI inline — no chart needed, covered by scatter in Tab 2
    pct_low = round(len(fdf[fdf["rating"] < 3.5]) / max(len(fdf),1) * 100)
    pct_high = round(len(fdf[fdf["rating"] >= 4.2]) / max(len(fdf),1) * 100)
    st.markdown(f"""<div class="insight">📌 <b>Quality gap:</b> {pct_low}% of products are rated below 3.5★
    while only {pct_high}% hit 4.2★+. If CLAPTALES consistently delivers 4.2★+,
    we land in the top tier of this market automatically.</div>""", unsafe_allow_html=True)

    if fdf["sales_trend"].notna().any():
        st.markdown('<div class="sec">90-Day Sales Trend by Subcategory</div>', unsafe_allow_html=True)
        trend = fdf.groupby("subcategory")["sales_trend"].mean().reset_index()
        trend.columns = ["Subcategory","Avg Trend (%)"]
        trend = trend[trend["Subcategory"].notna() & (trend["Subcategory"] != "")]
        trend = trend.sort_values("Avg Trend (%)", ascending=False).head(12)
        trend["color"] = trend["Avg Trend (%)"].apply(lambda x: "#2ECC71" if x >= 0 else "#E74C3C")
        fig = px.bar(trend, x="Subcategory", y="Avg Trend (%)",
                     color="color", color_discrete_map="identity", text_auto=".1f",
                     labels={"Subcategory":"","Avg Trend (%)":"Sales Change % (90 days)"})
        fig = style_fig(fig)
        fig.update_layout(showlegend=False, xaxis_tickangle=-35, height=300,
                          xaxis_title="", yaxis_title="Sales Change % (90 days)")
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
    hover_cols = {c: True for c in ["title","brand","subcategory","price","reviews","rating"]
                  if c in pdf.columns and pdf[c].notna().any()}
    hover_cols["zone"] = False
    fig = px.scatter(pdf, x="reviews", y="rating", color="zone",
                     color_discrete_map=color_map, size="price", size_max=20,
                     hover_data=hover_cols,
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
        declining = round((fdf["price_trend"] < 0).sum() / len(fdf) * 100)
        rising = 100 - declining
        st.markdown(f"""<div class="insight">📌 <b>Price pressure signal:</b> {declining}% of products had price drops
        in the last 90 days — sellers are racing to the bottom.
        CLAPTALES should compete on <b>quality and brand trust</b>, not price cuts.
        The {rising}% with stable/rising prices are the premium brands worth benchmarking.</div>""", unsafe_allow_html=True)

    corr = fdf[["price","rating"]].corr().iloc[0,1]
    direction = "weak positive" if corr > 0.1 else ("weak negative" if corr < -0.1 else "no meaningful")
    st.markdown(f'''<div class="insight">📌 <b>Price ≠ quality:</b> There is a {direction} correlation (r={corr:.2f})
    between price and rating. Customers do not reward expensive toys with better reviews —
    <b>what you build matters more than what you charge.</b></div>''', unsafe_allow_html=True)


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


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — PRODUCTS TO LAUNCH
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="sec">🛍️ Step-by-Step Product Launch Finder</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight">📌 This section drills from <b>Category → Subcategory → Products</b>
    to show CLAPTALES the exact products it should study and launch versions of —
    with images and direct Amazon links.</div>""", unsafe_allow_html=True)

    # ── STEP 1: Best Category ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Step 1 — Best Category")

    cat_stats = fdf.groupby("category").agg(
        products=("price","count"),
        avg_rating=("rating","mean"),
        avg_reviews=("reviews","mean"),
        total_revenue=("asin_revenue","sum"),
        avg_sales=("asin_sales","mean"),
        avg_sales_trend=("sales_trend","mean"),
    ).reset_index()

    cat_stats = cat_stats[cat_stats["total_revenue"].fillna(0) > 0] if cat_stats["total_revenue"].notna().any() else cat_stats
    if len(cat_stats) == 0:
        cat_stats = fdf.groupby("category").agg(products=("price","count"), avg_rating=("rating","mean"),
            avg_reviews=("reviews","mean"), total_revenue=("asin_revenue","sum"),
            avg_sales=("asin_sales","mean"), avg_sales_trend=("sales_trend","mean")).reset_index()

    rev_max = cat_stats["total_revenue"].max() or 1
    cat_stats["score"] = (
        (cat_stats["avg_reviews"].fillna(0) / max(cat_stats["avg_reviews"].max(), 1)) * 30 +
        (cat_stats["total_revenue"].fillna(0) / rev_max) * 35 +
        (cat_stats["avg_sales"].fillna(0) / max(cat_stats["avg_sales"].max(), 1)) * 20 +
        ((cat_stats["avg_sales_trend"].fillna(0) + 100) / 200).clip(0, 1) * 15
    ).round(1)
    cat_stats = cat_stats.sort_values("score", ascending=False)
    best_cat = cat_stats.iloc[0]["category"]

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FF6B6B,#FF8E53);border-radius:14px;padding:1.4rem;color:white;text-align:center">
          <div style="font-size:2rem">🏆</div>
          <div style="font-size:.75rem;opacity:.85;text-transform:uppercase;letter-spacing:.08em;margin:6px 0 4px">Best Category</div>
          <div style="font-size:1.4rem;font-weight:700">{best_cat}</div>
          <div style="font-size:.8rem;opacity:.9;margin-top:6px">Score: {cat_stats.iloc[0]["score"]:.0f}/100</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.metric("Avg Monthly Revenue", f"₹{cat_stats.iloc[0]['total_revenue']/max(cat_stats.iloc[0]['products'],1)/100000:.2f}L per product" if cat_stats.iloc[0]['total_revenue'] > 0 else "N/A")
        st.metric("Avg Rating", f"{cat_stats.iloc[0]['avg_rating']:.1f} ★")
    with col3:
        st.metric("Avg Reviews", f"{cat_stats.iloc[0]['avg_reviews']:,.0f}")
        st.metric("Products Tracked", f"{int(cat_stats.iloc[0]['products'])}")

    if len(cat_stats) > 1:
        fig_cat = px.bar(cat_stats.sort_values("score"), x="score", y="category",
                         orientation="h", color="score",
                         color_continuous_scale=["#FFC75F","#FF8E53","#FF6B6B"],
                         text="score", labels={"score":"Opportunity Score","category":""})
        fig_cat.update_traces(marker_line_width=0, textposition="outside")
        fig_cat.update_layout(font_family="DM Sans", plot_bgcolor="white", paper_bgcolor="white",
                              margin=dict(l=10,r=10,t=10,b=10), coloraxis_showscale=False,
                              xaxis_title="Score", height=max(180, len(cat_stats)*45))
        st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown(f"""<div class="conclude">✅ <b>{best_cat}</b> is the strongest category —
    highest combination of revenue, sales volume, and growth trend.
    All further analysis focuses here.</div>""", unsafe_allow_html=True)

    # ── STEP 2: Best Subcategory ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Step 2 — Best Subcategory within " + best_cat)

    cat_df = fdf[fdf["category"] == best_cat].copy() if "category" in fdf.columns else fdf.copy()

    if "subcategory" in cat_df.columns and cat_df["subcategory"].notna().any():
        sub_stats = cat_df.groupby("subcategory").agg(
            products=("price","count"),
            avg_price=("price","mean"),
            avg_rating=("rating","mean"),
            avg_reviews=("reviews","mean"),
            total_revenue=("asin_revenue","sum"),
            avg_sales=("asin_sales","mean"),
            avg_sales_trend=("sales_trend","mean"),
        ).reset_index()

        sub_stats = sub_stats[sub_stats["total_revenue"].fillna(0) > 0]
        if len(sub_stats) == 0:
            sub_stats = cat_df.groupby("subcategory").agg(products=("price","count"),
                avg_price=("price","mean"), avg_rating=("rating","mean"),
                avg_reviews=("reviews","mean"), total_revenue=("asin_revenue","sum"),
                avg_sales=("asin_sales","mean"), avg_sales_trend=("sales_trend","mean")).reset_index()

        rev_max2 = sub_stats["total_revenue"].max() or 1
        sub_stats["score"] = (
            (sub_stats["avg_reviews"].fillna(0) / max(sub_stats["avg_reviews"].max(), 1)) * 30 +
            (sub_stats["total_revenue"].fillna(0) / rev_max2) * 35 +
            (sub_stats["avg_sales"].fillna(0) / max(sub_stats["avg_sales"].max(), 1)) * 20 +
            ((sub_stats["avg_sales_trend"].fillna(0) + 100) / 200).clip(0, 1) * 15
        ).round(1)
        sub_stats = sub_stats.sort_values("score", ascending=False)
        best_sub = sub_stats.iloc[0]["subcategory"]

        # Top 3 subcategory cards
        medals = ["🥇","🥈","🥉"]
        borders = ["#FFD700","#C0C0C0","#CD7F32"]
        sub_cols = st.columns(min(3, len(sub_stats)))
        for i, (_, row) in enumerate(sub_stats.head(3).iterrows()):
            with sub_cols[i]:
                trend_txt = f"{row['avg_sales_trend']:+.0f}% sales trend" if pd.notna(row.get("avg_sales_trend")) else ""
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:1.1rem;border:1px solid #F0F0F0;
                            border-top:4px solid {borders[i]};height:100%">
                  <div style="font-size:1.4rem">{medals[i]}</div>
                  <div style="font-size:.95rem;font-weight:600;margin:6px 0 4px;color:#1A1A1A">{row['subcategory']}</div>
                  <div style="font-size:1.5rem;font-weight:700;color:#FF6B6B">{row['score']:.0f}
                    <span style="font-size:.75rem;color:#999">/100</span></div>
                  <hr style="border:none;border-top:1px solid #F5F5F5;margin:8px 0">
                  <div style="font-size:.78rem;color:#666;line-height:1.8">
                    Avg price: <b>₹{row['avg_price']:,.0f}</b><br>
                    Avg rating: <b>{row['avg_rating']:.1f}★</b><br>
                    Avg reviews: <b>{row['avg_reviews']:,.0f}</b><br>
                    Monthly revenue: <b>₹{row['total_revenue']/100000:.1f}L</b><br>
                    {trend_txt}
                  </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Subcategory comparison chart
        fig_sub = px.bar(sub_stats.head(10).sort_values("score"), x="score", y="subcategory",
                         orientation="h", color="score",
                         color_continuous_scale=["#FFC75F","#FF8E53","#FF6B6B"],
                         text="score", labels={"score":"Score","subcategory":""})
        fig_sub.update_traces(marker_line_width=0, textposition="outside")
        fig_sub.update_layout(font_family="DM Sans", plot_bgcolor="white", paper_bgcolor="white",
                              margin=dict(l=10,r=10,t=10,b=10), coloraxis_showscale=False,
                              height=max(200, min(len(sub_stats),10)*38))
        st.plotly_chart(fig_sub, use_container_width=True)

        st.markdown(f"""<div class="conclude">✅ <b>{best_sub}</b> is the top subcategory —
        highest revenue, demand, and growth momentum within {best_cat}.
        Products to launch should target this subcategory first.</div>""", unsafe_allow_html=True)

    else:
        best_sub = None
        st.info("Subcategory data not available.")

    # ── STEP 3: Products to Launch ───────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"### Step 3 — 🔥 In-Demand Products in **{best_sub or best_cat}**")
    st.markdown("""<div class="insight">📌 These are the highest-performing products competitors are already selling.
    Study them — their reviews, pricing, images, and descriptions — to build a better CLAPTALES version.</div>""", unsafe_allow_html=True)

    if best_sub and "subcategory" in cat_df.columns:
        prod_df = cat_df[cat_df["subcategory"] == best_sub].copy()
    else:
        prod_df = cat_df.copy()

    # Score products: revenue + reviews + sales trend
    prod_df["asin_revenue"] = pd.to_numeric(prod_df["asin_revenue"], errors="coerce").fillna(0)
    prod_df["asin_sales"]   = pd.to_numeric(prod_df["asin_sales"], errors="coerce").fillna(0)
    prod_df["reviews"]      = pd.to_numeric(prod_df["reviews"], errors="coerce").fillna(0)
    rev_p = prod_df["asin_revenue"].max() or 1
    rev_r = prod_df["reviews"].max() or 1
    sal_p = prod_df["asin_sales"].max() or 1
    prod_df["prod_score"] = (
        (prod_df["asin_revenue"] / rev_p) * 40 +
        (prod_df["reviews"] / rev_r) * 35 +
        (prod_df["asin_sales"] / sal_p) * 25
    ).round(2)
    prod_df = prod_df.sort_values("prod_score", ascending=False).reset_index(drop=True)

    # ── Product cards with images ─────────────────────────────────────────
    st.markdown(f"**Showing top {min(12, len(prod_df))} products · Sorted by demand score**")

    # Demand badge helper
    def demand_badge(score):
        if score >= 0.6:   return ("🔥 High Demand", "#FF6B6B", "#FFF0F0")
        if score >= 0.3:   return ("📈 Growing",     "#FF8E53", "#FFF5EE")
        return                    ("💤 Low Demand",  "#999",    "#F5F5F5")

    cols_per_row = 3
    top_prods = prod_df.head(12)
    for row_start in range(0, len(top_prods), cols_per_row):
        cols = st.columns(cols_per_row)
        for col_idx, (_, prod) in enumerate(top_prods.iloc[row_start:row_start+cols_per_row].iterrows()):
            with cols[col_idx]:
                badge_text, badge_color, badge_bg = demand_badge(prod["prod_score"])
                img_url  = str(prod["image_url"]) if "image_url" in prod.index and pd.notna(prod["image_url"]) and str(prod["image_url"]).startswith("http") else ""
                prod_url = str(prod["url"]) if "url" in prod.index and pd.notna(prod["url"]) and str(prod["url"]).startswith("http") else ""
                raw_title = str(prod["title"]) if "title" in prod.index and pd.notna(prod.get("title")) else "Unnamed Product"
                title    = (raw_title[:58] + "…") if len(raw_title) > 58 else raw_title
                brand    = str(prod.get("brand","—"))
                price    = f"₹{prod['price']:,.0f}" if pd.notna(prod.get("price")) else "—"
                rating   = f"{prod['rating']:.1f}★" if pd.notna(prod.get("rating")) else "—"
                reviews  = f"{int(prod['reviews']):,}" if prod["reviews"] > 0 else "—"
                sales    = f"{int(prod['asin_sales']):,}/mo" if prod["asin_sales"] > 0 else "—"
                revenue  = f"₹{prod['asin_revenue']/100000:.2f}L/mo" if prod["asin_revenue"] > 0 else "—"
                trend    = prod.get("sales_trend", None)
                trend_txt = f"{trend:+.0f}% trend" if pd.notna(trend) else ""
                trend_color = "#2ECC71" if (pd.notna(trend) and trend >= 0) else "#E74C3C"

                img_html = (f'<img src="{img_url}" style="width:100%;height:140px;object-fit:contain;border-radius:8px;background:#FAFAFA;padding:8px;">'
                            if img_url else
                            '<div style="height:140px;background:#F5F5F5;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#CCC;font-size:2rem">🧸</div>')

                link_btn = f'<a href="{prod_url}" target="_blank" style="display:block;text-align:center;background:#FF6B6B;color:white;padding:7px;border-radius:8px;font-size:.78rem;font-weight:600;text-decoration:none;margin-top:8px">View on Amazon →</a>' if prod_url else ""

                st.markdown(f"""
                <div style="background:white;border:1px solid #F0F0F0;border-radius:14px;padding:12px;margin-bottom:12px;height:100%">
                  {img_html}
                  <div style="margin-top:10px">
                    <span style="background:{badge_bg};color:{badge_color};font-size:.7rem;font-weight:600;padding:2px 8px;border-radius:99px">{badge_text}</span>
                    <div style="font-size:.82rem;font-weight:600;color:#1A1A1A;margin:7px 0 2px;line-height:1.35">{title}</div>
                    <div style="font-size:.75rem;color:#888;margin-bottom:8px">{brand}</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:.75rem">
                      <div><span style="color:#999">Price</span><br><b>{price}</b></div>
                      <div><span style="color:#999">Rating</span><br><b>{rating}</b></div>
                      <div><span style="color:#999">Reviews</span><br><b>{reviews}</b></div>
                      <div><span style="color:#999">Sales/mo</span><br><b>{sales}</b></div>
                      <div style="grid-column:span 2"><span style="color:#999">Revenue</span><br><b>{revenue}</b> <span style="color:{trend_color};font-size:.7rem">{trend_txt}</span></div>
                    </div>
                  </div>
                  {link_btn}
                </div>""", unsafe_allow_html=True)

    # ── Summary insight table ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sec">Product Intelligence Summary</div>', unsafe_allow_html=True)

    summary = top_prods[[c for c in ["title","brand","price","rating","reviews","asin_sales","asin_revenue","sales_trend","prod_score"] if c in top_prods.columns]].copy()
    summary["asin_revenue"] = summary["asin_revenue"].apply(lambda x: f"₹{x/100000:.2f}L" if x > 0 else "—")
    summary["price"]        = summary["price"].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "—")
    summary["rating"]       = summary["rating"].apply(lambda x: f"{x:.1f}★" if pd.notna(x) else "—")
    summary["reviews"]      = summary["reviews"].apply(lambda x: f"{int(x):,}" if x > 0 else "—")
    summary["asin_sales"]   = summary["asin_sales"].apply(lambda x: f"{int(x):,}" if x > 0 else "—")
    summary["sales_trend"]  = summary["sales_trend"].apply(lambda x: f"{x:+.0f}%" if pd.notna(x) else "—")
    summary["prod_score"]   = summary["prod_score"].apply(lambda x: f"{x:.2f}")
    summary.columns         = [c.replace("_"," ").replace("asin","").title().strip() for c in summary.columns]
    st.dataframe(summary, use_container_width=True, hide_index=True)

    # ── Revenue + Sales trend bar ─────────────────────────────────────────
    st.markdown('<div class="sec">Revenue & Sales Trend — Top Products</div>', unsafe_allow_html=True)
    chart_df = top_prods[top_prods["asin_revenue"] > 0].head(10).copy()
    chart_df["short_title"] = chart_df["title"].apply(lambda x: str(x)[:30]+"…" if len(str(x))>30 else str(x))

    if len(chart_df):
        fig_p = px.bar(chart_df.sort_values("asin_revenue", ascending=True),
                       x="asin_revenue", y="short_title", orientation="h",
                       color="sales_trend",
                       color_continuous_scale=["#E74C3C","#FFC75F","#2ECC71"],
                       text=chart_df.sort_values("asin_revenue", ascending=True)["asin_revenue"].apply(lambda x: f"₹{x/100000:.1f}L"),
                       labels={"asin_revenue":"Monthly Revenue (₹)","short_title":"","sales_trend":"Sales Trend %"})
        fig_p.update_traces(textposition="outside", marker_line_width=0)
        fig_p.update_layout(font_family="DM Sans", plot_bgcolor="white", paper_bgcolor="white",
                            margin=dict(l=10,r=10,t=10,b=10),
                            coloraxis_colorbar_title="Trend %",
                            xaxis_tickformat=",.0f",
                            height=max(300, len(chart_df)*42))
        st.plotly_chart(fig_p, use_container_width=True)
        st.markdown("""<div class="insight">📌 <b>Color = sales trend:</b> Green = growing fast, Red = declining.
        CLAPTALES should prioritise products that are both high revenue AND green — they show growing demand
        with proven monetisation.</div>""", unsafe_allow_html=True)

    # ── Final CLAPTALES recommendation ───────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="sec">🎯 Final Recommendation for CLAPTALES</div>', unsafe_allow_html=True)

    top1 = top_prods.iloc[0] if len(top_prods) else None
    avg_price_sub = prod_df["price"].mean()
    growing_prods = prod_df[prod_df["sales_trend"].fillna(0) > 0]
    pct_growing = round(len(growing_prods) / max(len(prod_df),1) * 100)

    if top1 is not None:
        st.markdown(f"""
<div class="conclude"><b>Launch category:</b> {best_cat} → <b>{best_sub or "Top subcategory"}</b><br>
This is where the money is. Highest revenue, clearest demand signal, active growth.</div>

<div class="conclude"><b>Study this product first:</b> {str(top1.get('title',''))[:80]}...<br>
Brand: {top1.get('brand','—')} · Price: ₹{top1['price']:,.0f} · Rating: {top1['rating']:.1f}★ · {int(top1['reviews']):,} reviews<br>
Read every 1-star and 2-star review. Those pain points are your product brief.</div>

<div class="conclude"><b>Price your launch at:</b> ₹{int(avg_price_sub*0.85):,} – ₹{int(avg_price_sub):,}<br>
Slightly below the subcategory average (₹{avg_price_sub:,.0f}) to drive initial velocity.
Once you have 50+ reviews, raise to market rate.</div>

<div class="conclude"><b>Growth signal:</b> {pct_growing}% of products in this subcategory show positive 90-day sales trends.<br>
The market is actively growing — good timing to enter now before it becomes crowded.</div>

<div class="conclude"><b>What to do next:</b><br>
1. Click "View on Amazon →" on the top 3 product cards above<br>
2. Read reviews (especially 1★ and 2★) to find quality gaps<br>
3. Note packaging, number of images, and variation counts of top sellers<br>
4. Build a CLAPTALES product that fixes their weaknesses at a competitive price</div>
""", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("<div style='text-align:center;color:#CCC;font-size:.75rem'>CLAPTALES Market Intelligence · Amazon India · Jungle Scout · Internal use only</div>",
            unsafe_allow_html=True)
