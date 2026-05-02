import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import io

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CLAPTALES | Market Research Dashboard",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Theme / CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.brand-header {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    color: white;
}
.brand-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
}
.brand-header p { margin: 0; opacity: 0.85; font-size: 0.95rem; }

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    border: 1px solid #F0F0F0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    height: 100%;
}
.metric-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; }
.metric-value { font-size: 2rem; font-weight: 600; color: #1A1A1A; line-height: 1.1; }
.metric-sub { font-size: 0.78rem; color: #999; margin-top: 4px; }
.metric-trend-up { color: #2ECC71; font-size: 0.8rem; font-weight: 500; }
.metric-trend-dn { color: #E74C3C; font-size: 0.8rem; font-weight: 500; }

.insight-box {
    background: #FFF8F0;
    border-left: 4px solid #FF8E53;
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1.1rem;
    margin: 0.75rem 0 1.25rem 0;
    font-size: 0.88rem;
    color: #5A3E2B;
    line-height: 1.5;
}
.conclusion-box {
    background: #F0FFF4;
    border-left: 4px solid #2ECC71;
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1.1rem;
    margin: 0.75rem 0 0.5rem 0;
    font-size: 0.88rem;
    color: #1A4731;
    line-height: 1.5;
}
.warning-box {
    background: #FFF5F5;
    border-left: 4px solid #E74C3C;
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1.1rem;
    margin: 0.75rem 0 0.5rem 0;
    font-size: 0.88rem;
    color: #5A1A1A;
    line-height: 1.5;
}
.section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: #1A1A1A;
    margin: 1.5rem 0 0.25rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #FF8E53;
    display: inline-block;
}
.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 2px;
}
.tag-green { background: #D4EDDA; color: #155724; }
.tag-red   { background: #F8D7DA; color: #721C24; }
.tag-amber { background: #FFF3CD; color: #856404; }
.tag-blue  { background: #D1ECF1; color: #0C5460; }

[data-testid="stSidebar"] { background: #FAFAFA; border-right: 1px solid #F0F0F0; }
div[data-testid="stMetric"] { background: white; border-radius: 12px; padding: 1rem; border: 1px solid #F0F0F0; }
</style>
""", unsafe_allow_html=True)

# ─── Column mapping ─────────────────────────────────────────────────────────────
COLUMN_MAP = {
    "product": ["product name","title","product title","asin title","name","product"],
    "brand":   ["brand","brand name","manufacturer","seller"],
    "price":   ["price","sale price","buy box price","current price","selling price","buy box: current price"],
    "rating":  ["rating","star rating","avg rating","average rating","review rating","ratings"],
    "reviews": ["reviews","number of reviews","review count","total reviews","ratings total","number of ratings"],
    "bsr":     ["bsr","best seller rank","sales rank","rank","best sellers rank"],
    "monthly_sales": ["monthly sales","estimated monthly sales","est. monthly sales","sales/month","monthly units"],
    "monthly_revenue":["monthly revenue","estimated monthly revenue","est. monthly revenue","revenue/month","monthly sales revenue"],
    "category":["category","main category","product category","department"],
}

def detect_col(df, key):
    aliases = COLUMN_MAP[key]
    for col in df.columns:
        if col.strip().lower() in aliases:
            return col
    return None

def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return None

def clean_numeric(series):
    if series.dtype == object:
        series = series.astype(str).str.replace(r'[₹$,\s]', '', regex=True)
        series = pd.to_numeric(series, errors='coerce')
    return series

# ─── Sample data ────────────────────────────────────────────────────────────────
def get_sample_data():
    np.random.seed(42)
    brands = ['FunSkool','Hasbro','Mattel','Funskool','Lego','Toyzone','Miss&Chief','OK Play','Ratnas','Simba']
    categories = ['Action Figures','Puzzles','Board Games','Soft Toys','Educational Toys','Outdoor Toys']
    data = []
    for i in range(80):
        brand = np.random.choice(brands, p=[0.18,0.14,0.12,0.11,0.10,0.09,0.08,0.08,0.06,0.04])
        cat   = np.random.choice(categories)
        price = np.random.choice([299,399,499,599,799,999,1299,1499,1999,2499,2999])
        rating = round(np.clip(np.random.normal(4.1, 0.4), 1, 5), 1)
        reviews = int(np.random.exponential(8000))
        bsr = int(np.random.exponential(3000)) + 100
        monthly_sales = int(np.random.exponential(400))
        monthly_revenue = monthly_sales * price
        data.append(dict(
            product=f"Toy Product {i+1} - {cat[:4]}",
            brand=brand, category=cat, price=price,
            rating=rating, reviews=reviews, bsr=bsr,
            monthly_sales=monthly_sales, monthly_revenue=monthly_revenue,
        ))
    return pd.DataFrame(data)

# ─── Plotly theme ───────────────────────────────────────────────────────────────
COLORS = ["#FF6B6B","#FF8E53","#FFC75F","#2ECC71","#3498DB","#9B59B6","#1ABC9C","#E74C3C","#F39C12","#2980B9"]
PLOT_LAYOUT = dict(
    font_family="DM Sans",
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=16, r=16, t=36, b=16),
    title_font_size=14,
    title_font_color="#1A1A1A",
    legend=dict(font_size=11),
    colorway=COLORS,
)

def style_fig(fig, title=""):
    fig.update_layout(**PLOT_LAYOUT, title=title)
    fig.update_xaxes(showgrid=False, linecolor="#F0F0F0", tickfont_size=11)
    fig.update_yaxes(showgrid=True, gridcolor="#F7F7F7", linecolor="#F0F0F0", tickfont_size=11)
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧸 CLAPTALES")
    st.markdown("**Market Research Dashboard**")
    st.divider()

    uploaded = st.file_uploader(
        "Upload your data export",
        type=["csv","xlsx"],
        help="Supports Helium10, Jungle Scout, or any standard product CSV/Excel export"
    )

    st.divider()
    st.markdown("**Filters**")
    use_sample = not bool(uploaded)

    if use_sample:
        st.info("📊 Showing sample toy market data. Upload your file above to analyze your real data.")

    # placeholder filters — populated after data loads
    cat_filter    = None
    price_filter  = None
    rating_filter = None

# ═══════════════════════════════════════════════════════════════════════════════
#  LOAD DATA
# ═══════════════════════════════════════════════════════════════════════════════
if uploaded:
    raw = load_data(uploaded)
else:
    raw = get_sample_data()

if raw is None:
    st.stop()

# ─── Map columns ────────────────────────────────────────────────────────────────
df = raw.copy()
col = {k: detect_col(df, k) for k in COLUMN_MAP}

# Rename detected cols to standard names for simplicity
rename = {v: k for k, v in col.items() if v and v != k}
df = df.rename(columns=rename)

# Ensure numeric
for num_col in ["price","rating","reviews","bsr","monthly_sales","monthly_revenue"]:
    if num_col in df.columns:
        df[num_col] = clean_numeric(df[num_col])

# Fill missing standard cols with NaN if not detected
for c in ["product","brand","price","rating","reviews","bsr","monthly_sales","monthly_revenue","category"]:
    if c not in df.columns:
        df[c] = np.nan

df = df.dropna(subset=["price","rating"]).reset_index(drop=True)

# ─── Sidebar filters (now that data is loaded) ──────────────────────────────────
with st.sidebar:
    if "category" in df.columns and df["category"].notna().any():
        cats = ["All"] + sorted(df["category"].dropna().unique().tolist())
        cat_sel = st.selectbox("Category", cats)
    else:
        cat_sel = "All"

    price_min, price_max = int(df["price"].min()), int(df["price"].max())
    price_range = st.slider("Price range (₹)", price_min, price_max, (price_min, price_max))

    rating_min = st.slider("Minimum rating", 1.0, 5.0, 3.5, 0.1)

# ─── Apply filters ──────────────────────────────────────────────────────────────
fdf = df.copy()
if cat_sel != "All":
    fdf = fdf[fdf["category"] == cat_sel]
fdf = fdf[(fdf["price"] >= price_range[0]) & (fdf["price"] <= price_range[1])]
fdf = fdf[fdf["rating"] >= rating_min]

# ═══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="brand-header">
  <h1>🧸 CLAPTALES Market Intelligence</h1>
  <p>Amazon Toy Market Research Dashboard — helping the team find the right products to launch next</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Market Overview",
    "🎯 Product Opportunity",
    "💰 Pricing Strategy",
    "🏆 Competitor Intel",
    "🚀 Launch Recommendations",
])

# ╔═══════════════════════════════════════════════════════════════════╗
# ║  TAB 1 — MARKET OVERVIEW                                         ║
# ╚═══════════════════════════════════════════════════════════════════╝
with tabs[0]:
    st.markdown('<div class="section-header">Market Snapshot</div>', unsafe_allow_html=True)

    # ── KPI cards ──────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)

    total_products = len(fdf)
    avg_price      = fdf["price"].mean()
    avg_rating     = fdf["rating"].mean()
    total_rev      = fdf["monthly_revenue"].sum() if fdf["monthly_revenue"].notna().any() else 0
    top_brand      = fdf["brand"].value_counts().idxmax() if fdf["brand"].notna().any() else "N/A"

    with k1:
        st.metric("Products Tracked", f"{total_products:,}")
    with k2:
        st.metric("Avg Market Price", f"₹{avg_price:,.0f}")
    with k3:
        st.metric("Avg Rating", f"{avg_rating:.1f} ★")
    with k4:
        est = f"₹{total_rev/100000:.1f}L/mo" if total_rev > 0 else "N/A"
        st.metric("Est. Market Revenue", est)
    with k5:
        st.metric("Market Leader", top_brand)

    st.markdown("""<div class="insight-box">
    📌 <b>What this tells us:</b> These numbers represent the toy market landscape on Amazon India right now.
    Use this as your baseline — any product CLAPTALES launches should be benchmarked against these averages.
    </div>""", unsafe_allow_html=True)

    # ── Category breakdown ──────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Category Distribution</div>', unsafe_allow_html=True)
        if fdf["category"].notna().any():
            cat_counts = fdf["category"].value_counts().reset_index()
            cat_counts.columns = ["Category","Count"]
            fig = px.pie(cat_counts, values="Count", names="Category",
                         color_discrete_sequence=COLORS, hole=0.45)
            fig = style_fig(fig)
            fig.update_traces(textposition="outside", textinfo="label+percent")
            st.plotly_chart(fig, use_container_width=True)

            top_cat = cat_counts.iloc[0]["Category"]
            top_pct = round(cat_counts.iloc[0]["Count"] / cat_counts["Count"].sum() * 100)
            st.markdown(f"""<div class="conclusion-box">
            ✅ <b>Conclusion:</b> <b>{top_cat}</b> dominates with {top_pct}% of listings —
            this is the most competitive space. For CLAPTALES, entering a category with 10–20%
            share gives room to grow without fighting giants from day one.
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Category column not detected in your data.")

    with col2:
        st.markdown('<div class="section-header">Monthly Revenue by Category</div>', unsafe_allow_html=True)
        if fdf["monthly_revenue"].notna().any() and fdf["category"].notna().any():
            rev_cat = fdf.groupby("category")["monthly_revenue"].sum().reset_index()
            rev_cat.columns = ["Category","Revenue"]
            rev_cat = rev_cat.sort_values("Revenue", ascending=True)
            fig = px.bar(rev_cat, x="Revenue", y="Category", orientation="h",
                         color_discrete_sequence=["#FF8E53"])
            fig = style_fig(fig, "")
            fig.update_traces(marker_line_width=0)
            fig.update_layout(xaxis_tickformat=",.0f", xaxis_title="₹ Monthly Revenue")
            st.plotly_chart(fig, use_container_width=True)

            best_rev_cat = rev_cat.iloc[-1]["Category"]
            st.markdown(f"""<div class="conclusion-box">
            ✅ <b>Conclusion:</b> <b>{best_rev_cat}</b> generates the highest monthly revenue —
            meaning customers are spending real money here. High revenue + manageable competition = sweet spot for CLAPTALES.
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Monthly revenue data not available.")

    # ── Rating distribution ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Overall Rating Distribution</div>', unsafe_allow_html=True)
    fig = px.histogram(fdf, x="rating", nbins=20, color_discrete_sequence=["#3498DB"])
    fig = style_fig(fig)
    fig.update_layout(bargap=0.1, xaxis_title="Rating", yaxis_title="Number of products")
    st.plotly_chart(fig, use_container_width=True)

    pct_low = round(len(fdf[fdf["rating"] < 3.5]) / len(fdf) * 100)
    st.markdown(f"""<div class="insight-box">
    📌 <b>Market quality signal:</b> {pct_low}% of products are rated below 3.5 stars —
    this means customers are dissatisfied with many existing toys. 
    If CLAPTALES can consistently deliver 4.2+ rated products, we stand out immediately.
    </div>""", unsafe_allow_html=True)


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  TAB 2 — PRODUCT OPPORTUNITY                                     ║
# ╚═══════════════════════════════════════════════════════════════════╝
with tabs[1]:
    st.markdown('<div class="section-header">Finding the White Space</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight-box">
    📌 <b>What we're looking for:</b> Products with <b>high demand</b> (many reviews, high sales)
    but <b>low quality competition</b> (average ratings below 4.0). These gaps are where CLAPTALES can enter and win.
    </div>""", unsafe_allow_html=True)

    # ── Opportunity matrix: rating vs reviews ───────────────────────────
    st.markdown('<div class="section-header">Opportunity Matrix — Demand vs Quality</div>', unsafe_allow_html=True)

    plot_df = fdf.dropna(subset=["reviews","rating","price"]).copy()
    plot_df["reviews_k"] = plot_df["reviews"] / 1000

    # Quadrant logic
    med_reviews = plot_df["reviews"].median()
    med_rating  = 4.0

    def quadrant(row):
        hi_demand  = row["reviews"] >= med_reviews
        hi_quality = row["rating"]  >= med_rating
        if hi_demand and hi_quality:     return "🔴 Tough (high demand, well rated)"
        if hi_demand and not hi_quality: return "🟢 Opportunity (high demand, poor quality)"
        if not hi_demand and hi_quality: return "🟡 Niche (low demand, well rated)"
        return "⚪ Avoid (low demand, poor quality)"

    plot_df["quadrant"] = plot_df.apply(quadrant, axis=1)

    color_map = {
        "🔴 Tough (high demand, well rated)": "#E74C3C",
        "🟢 Opportunity (high demand, poor quality)": "#2ECC71",
        "🟡 Niche (low demand, well rated)": "#F39C12",
        "⚪ Avoid (low demand, poor quality)": "#BDC3C7",
    }

    fig = px.scatter(
        plot_df, x="reviews_k", y="rating",
        color="quadrant", color_discrete_map=color_map,
        size="price", size_max=22,
        hover_data={"product": True, "brand": True, "price": True,
                    "reviews_k": False, "reviews": True, "rating": True, "quadrant": False},
        labels={"reviews_k":"Reviews (thousands)","rating":"Star Rating"},
    )
    fig.add_hline(y=med_rating, line_dash="dash", line_color="#999", line_width=1)
    fig.add_vline(x=med_reviews/1000, line_dash="dash", line_color="#999", line_width=1)
    fig = style_fig(fig)
    fig.update_layout(height=420, legend_title_text="Quadrant")
    st.plotly_chart(fig, use_container_width=True)

    opp_count = len(plot_df[plot_df["quadrant"].str.startswith("🟢")])
    st.markdown(f"""<div class="conclusion-box">
    ✅ <b>Conclusion for CLAPTALES:</b> There are <b>{opp_count} products</b> in the green "Opportunity" zone —
    high customer demand but competitors delivering poor quality. These are the exact product types CLAPTALES should study and launch better versions of.
    </div>""", unsafe_allow_html=True)

    # ── Top opportunity products ─────────────────────────────────────────
    st.markdown('<div class="section-header">Top Opportunity Products to Study</div>', unsafe_allow_html=True)
    opp_df = plot_df[plot_df["quadrant"].str.startswith("🟢")].sort_values("reviews", ascending=False)

    if len(opp_df) > 0:
        show_cols = [c for c in ["product","brand","category","price","rating","reviews","monthly_sales"] if c in opp_df.columns]
        display = opp_df[show_cols].head(15).copy()
        display["price"] = display["price"].apply(lambda x: f"₹{x:,.0f}")
        display["reviews"] = display["reviews"].apply(lambda x: f"{x:,.0f}")
        if "monthly_sales" in display.columns:
            display["monthly_sales"] = display["monthly_sales"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No opportunity products found with current filters — try widening the filters.")

    # ── Demand heatmap by category & price band ──────────────────────────
    if fdf["category"].notna().any():
        st.markdown('<div class="section-header">Demand Heatmap — Category × Price Band</div>', unsafe_allow_html=True)
        fdf2 = fdf.copy()
        fdf2["price_band"] = pd.cut(fdf2["price"],
            bins=[0,499,999,1999,4999,99999],
            labels=["Under ₹500","₹500–999","₹1,000–1,999","₹2,000–4,999","₹5,000+"])
        heat = fdf2.groupby(["category","price_band"], observed=True)["reviews"].mean().reset_index()
        heat_pivot = heat.pivot(index="category", columns="price_band", values="reviews").fillna(0)
        fig = px.imshow(heat_pivot, color_continuous_scale="Oranges",
                        labels=dict(color="Avg Reviews"),
                        aspect="auto")
        fig = style_fig(fig)
        fig.update_layout(xaxis_title="Price Band", yaxis_title="", coloraxis_colorbar_title="Avg Reviews")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""<div class="insight-box">
        📌 <b>How to read this:</b> Darker orange = more customer demand (more reviews) in that category + price combination.
        These are the highest-traffic pockets of the market — ideal entry points for CLAPTALES new products.
        </div>""", unsafe_allow_html=True)


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  TAB 3 — PRICING STRATEGY                                        ║
# ╚═══════════════════════════════════════════════════════════════════╝
with tabs[2]:
    st.markdown('<div class="section-header">Where Should CLAPTALES Price?</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight-box">
    📌 <b>Goal:</b> Find the price points that attract the most buyers and generate the best revenue — not too cheap (destroys margins), not too expensive (kills volume).
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Price band volume
        fdf3 = fdf.copy()
        fdf3["price_band"] = pd.cut(fdf3["price"],
            bins=[0,499,999,1999,4999,99999],
            labels=["<₹500","₹500–999","₹1k–2k","₹2k–5k","₹5k+"])
        band_count = fdf3["price_band"].value_counts().sort_index().reset_index()
        band_count.columns = ["Price Band","Products"]
        fig = px.bar(band_count, x="Price Band", y="Products",
                     color_discrete_sequence=["#FF6B6B"], text="Products")
        fig = style_fig(fig, "Products per Price Band")
        fig.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Revenue by price band
        if fdf["monthly_revenue"].notna().any():
            fdf3["price_band"] = pd.cut(fdf3["price"],
                bins=[0,499,999,1999,4999,99999],
                labels=["<₹500","₹500–999","₹1k–2k","₹2k–5k","₹5k+"])
            band_rev = fdf3.groupby("price_band", observed=True)["monthly_revenue"].sum().reset_index()
            band_rev.columns = ["Price Band","Revenue"]
            fig = px.bar(band_rev, x="Price Band", y="Revenue",
                         color_discrete_sequence=["#2ECC71"], text_auto=".2s")
            fig = style_fig(fig, "Monthly Revenue per Price Band")
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(yaxis_tickformat=",.0f", yaxis_title="₹ Monthly Revenue")
            st.plotly_chart(fig, use_container_width=True)

    # Sweet spot
    sweetspot = fdf3.groupby("price_band", observed=True).agg(
        products=("price","count"),
        avg_rating=("rating","mean"),
        avg_reviews=("reviews","mean"),
        total_revenue=("monthly_revenue","sum"),
    ).reset_index()
    sweetspot["score"] = (
        sweetspot["avg_reviews"] / sweetspot["avg_reviews"].max() * 0.4 +
        sweetspot["avg_rating"]  / 5 * 0.3 +
        (sweetspot["total_revenue"] / sweetspot["total_revenue"].max() * 0.3 if sweetspot["total_revenue"].sum()>0 else 0)
    )
    best_band = sweetspot.sort_values("score", ascending=False).iloc[0]["price_band"]

    st.markdown(f"""<div class="conclusion-box">
    ✅ <b>Recommended price range for CLAPTALES:</b> <b>{best_band}</b> — this band shows the best
    combination of customer demand (review volume), product quality (ratings), and total revenue.
    Launching here maximises chances of early traction while remaining competitive.
    </div>""", unsafe_allow_html=True)

    # Price vs Rating scatter
    st.markdown('<div class="section-header">Does Higher Price = Better Rating?</div>', unsafe_allow_html=True)
    fig = px.scatter(fdf, x="price", y="rating",
                     trendline="lowess",
                     color="category" if fdf["category"].notna().any() else None,
                     color_discrete_sequence=COLORS,
                     hover_data=["brand","reviews"] if "brand" in fdf.columns else None,
                     labels={"price":"Price (₹)","rating":"Star Rating"})
    fig = style_fig(fig)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    corr = fdf[["price","rating"]].corr().iloc[0,1]
    direction = "slight positive" if corr > 0.1 else ("slight negative" if corr < -0.1 else "no meaningful")
    st.markdown(f"""<div class="insight-box">
    📌 <b>Finding:</b> There is a <b>{direction} correlation</b> (r={corr:.2f}) between price and rating.
    This means customers don't automatically rate expensive toys higher — <b>quality and value matter more than price.</b>
    CLAPTALES should compete on product quality, not just pricing.
    </div>""", unsafe_allow_html=True)


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  TAB 4 — COMPETITOR INTEL                                        ║
# ╚═══════════════════════════════════════════════════════════════════╝
with tabs[3]:
    st.markdown('<div class="section-header">Who Are We Up Against?</div>', unsafe_allow_html=True)

    if not fdf["brand"].notna().any():
        st.info("Brand column not detected in your data.")
    else:
        brand_stats = fdf.groupby("brand").agg(
            listings=("price","count"),
            avg_price=("price","mean"),
            avg_rating=("rating","mean"),
            avg_reviews=("reviews","mean"),
            total_revenue=("monthly_revenue","sum"),
        ).reset_index()
        brand_stats = brand_stats[brand_stats["listings"] >= 2].sort_values("listings", ascending=False)

        # ── Brand listing share ──────────────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            top_brands = brand_stats.head(8)
            fig = px.bar(top_brands.sort_values("listings"), x="listings", y="brand",
                         orientation="h", color_discrete_sequence=["#3498DB"],
                         text="listings")
            fig = style_fig(fig, "Listings per Brand (Top 8)")
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(yaxis_title="", xaxis_title="Number of Products")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(brand_stats.head(12),
                             x="avg_price", y="avg_rating",
                             size="listings", size_max=30,
                             color="brand", color_discrete_sequence=COLORS,
                             text="brand",
                             labels={"avg_price":"Avg Price (₹)","avg_rating":"Avg Rating","listings":"Listings"})
            fig = style_fig(fig, "Brand Positioning Map")
            fig.update_traces(textposition="top center", textfont_size=9)
            fig.update_layout(showlegend=False, height=360)
            fig.add_hline(y=4.0, line_dash="dot", line_color="#ccc")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""<div class="insight-box">
        📌 <b>How to read the positioning map:</b> Brands in the <b>top-right</b> are expensive AND well-rated — premium competitors.
        Brands in the <b>bottom-right</b> are expensive but poorly rated — vulnerable to disruption.
        CLAPTALES should aim for <b>top-left to top-right</b>: quality products at accessible prices.
        </div>""", unsafe_allow_html=True)

        # ── Competitor table ────────────────────────────────────────────────
        st.markdown('<div class="section-header">Full Competitor Scorecard</div>', unsafe_allow_html=True)
        display_brands = brand_stats.head(15).copy()
        display_brands["avg_price"]   = display_brands["avg_price"].apply(lambda x: f"₹{x:,.0f}")
        display_brands["avg_rating"]  = display_brands["avg_rating"].apply(lambda x: f"{x:.1f} ★")
        display_brands["avg_reviews"] = display_brands["avg_reviews"].apply(lambda x: f"{x:,.0f}")
        if display_brands["total_revenue"].sum() > 0:
            display_brands["total_revenue"] = display_brands["total_revenue"].apply(
                lambda x: f"₹{x/100000:.1f}L/mo" if x > 0 else "N/A")
        display_brands.columns = ["Brand","Listings","Avg Price","Avg Rating","Avg Reviews","Est. Monthly Revenue"]
        if display_brands["Est. Monthly Revenue"].eq("N/A").all():
            display_brands = display_brands.drop(columns=["Est. Monthly Revenue"])
        st.dataframe(display_brands, use_container_width=True, hide_index=True)

        # ── Weakest competitor ratings (attack opportunities) ────────────────
        st.markdown('<div class="section-header">Brands with Lowest Ratings (Attack Opportunities)</div>', unsafe_allow_html=True)
        weak = brand_stats[brand_stats["avg_rating"] < 4.0].sort_values("avg_reviews", ascending=False)
        if len(weak):
            st.markdown(f"""<div class="warning-box">
            ⚠️ <b>These {len(weak)} brands have high demand but poor ratings</b> — customers are stuck with them because there's no better alternative.
            If CLAPTALES launches a better-quality version of their top products, we can capture their customer base.
            </div>""", unsafe_allow_html=True)
            for _, row in weak.head(5).iterrows():
                st.markdown(f"- **{row['brand']}** — {row['listings']} listings, avg rating {row['avg_rating']:.1f}★, avg {row['avg_reviews']:,.0f} reviews")
        else:
            st.success("Most brands in this dataset maintain ratings above 4.0 — competition is quality-focused.")


# ╔═══════════════════════════════════════════════════════════════════╗
# ║  TAB 5 — LAUNCH RECOMMENDATIONS                                  ║
# ╚═══════════════════════════════════════════════════════════════════╝
with tabs[4]:
    st.markdown('<div class="section-header">🚀 What Should CLAPTALES Launch Next?</div>', unsafe_allow_html=True)
    st.markdown("""<div class="insight-box">
    📌 This section synthesises everything above into clear recommendations for the management team.
    Updated automatically whenever you upload new data.
    </div>""", unsafe_allow_html=True)

    # ── Compute scores per category ──────────────────────────────────────
    if fdf["category"].notna().any():
        cat_summary = fdf.groupby("category").agg(
            products=("price","count"),
            avg_price=("price","mean"),
            avg_rating=("rating","mean"),
            avg_reviews=("reviews","mean"),
            total_rev=("monthly_revenue","sum"),
        ).reset_index()

        # Opportunity score: high demand, low rating (easier to beat), decent revenue
        rev_max = cat_summary["total_rev"].max() if cat_summary["total_rev"].max() > 0 else 1
        cat_summary["opportunity_score"] = (
            (cat_summary["avg_reviews"] / cat_summary["avg_reviews"].max()) * 40 +
            ((5 - cat_summary["avg_rating"]) / 5) * 30 +
            (cat_summary["total_rev"] / rev_max) * 30
        ).round(1)
        cat_summary = cat_summary.sort_values("opportunity_score", ascending=False)

        # Score bar
        fig = px.bar(cat_summary, x="opportunity_score", y="category", orientation="h",
                     color="opportunity_score", color_continuous_scale=["#FFC75F","#FF8E53","#FF6B6B"],
                     text="opportunity_score")
        fig = style_fig(fig, "Category Opportunity Score (higher = better entry point for CLAPTALES)")
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(yaxis_title="", xaxis_title="Opportunity Score (0–100)",
                          coloraxis_showscale=False, height=320)
        st.plotly_chart(fig, use_container_width=True)

        # Top 3 recommendations
        st.markdown('<div class="section-header">Top 3 Category Recommendations</div>', unsafe_allow_html=True)
        medals = ["🥇","🥈","🥉"]
        rec_cols = st.columns(3)
        for i, (_, row) in enumerate(cat_summary.head(3).iterrows()):
            with rec_cols[i]:
                score_color = "#2ECC71" if row["opportunity_score"] > 65 else "#F39C12"
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid {score_color};">
                  <div style="font-size:1.6rem">{medals[i]}</div>
                  <div style="font-size:1.1rem;font-weight:600;margin:8px 0 4px">{row['category']}</div>
                  <div style="font-size:1.5rem;font-weight:600;color:{score_color}">{row['opportunity_score']:.0f}<span style="font-size:0.8rem;color:#999"> / 100</span></div>
                  <hr style="border:none;border-top:1px solid #F0F0F0;margin:10px 0">
                  <div style="font-size:0.8rem;color:#666">
                    Avg price: <b>₹{row['avg_price']:,.0f}</b><br>
                    Avg rating: <b>{row['avg_rating']:.1f} ★</b><br>
                    Avg reviews: <b>{row['avg_reviews']:,.0f}</b>
                  </div>
                </div>""", unsafe_allow_html=True)

    # ── Final action plan ────────────────────────────────────────────────
    st.markdown("")
    st.markdown('<div class="section-header">Management Action Plan</div>', unsafe_allow_html=True)

    sweet_price_low, sweet_price_high = int(fdf["price"].quantile(0.35)), int(fdf["price"].quantile(0.65))
    quality_bar = round(fdf["rating"].quantile(0.75), 1)

    st.markdown(f"""
<div class="conclusion-box">
<b>1. Price to win</b><br>
Enter the <b>₹{sweet_price_low:,} – ₹{sweet_price_high:,}</b> range — this is where most purchasing decisions happen in this market.
Avoid going below ₹{sweet_price_low:,} (margin risk) or above ₹{sweet_price_high:,} (volume risk) for your first products.
</div>

<div class="conclusion-box">
<b>2. Quality is non-negotiable</b><br>
The market average rating is {avg_rating:.1f}★. Top 25% of products are rated {quality_bar}★ or above.
CLAPTALES must target <b>{quality_bar}★ at launch</b> — anything below will not organically rank or earn repeat buyers.
</div>

<div class="conclusion-box">
<b>3. Attack weak competitors first</b><br>
Identify brands with 3.5★ or below that still have 1,000+ reviews — these customers are unhappy but have no better option.
Study their 1-star reviews to understand exactly what to fix. Build CLAPTALES products around those pain points.
</div>

<div class="conclusion-box">
<b>4. Don't spread thin — go deep on one category first</b><br>
Pick the top-scoring category from above, launch 2–3 tightly related SKUs, dominate that niche before expanding.
Amazon's algorithm rewards sellers who own a category, not those who scatter across many.
</div>
""", unsafe_allow_html=True)

    # ── Download summary ─────────────────────────────────────────────────
    st.divider()
    st.markdown("**Export filtered data**")
    export_df = fdf[[c for c in ["product","brand","category","price","rating","reviews","monthly_sales","monthly_revenue","bsr"] if c in fdf.columns]]
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download filtered data as CSV",
        data=csv_bytes,
        file_name="claptales_market_research.csv",
        mime="text/csv",
    )

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#BBB;font-size:0.78rem'>CLAPTALES Market Research Dashboard • Built for internal use • Data from Helium10 / Jungle Scout</div>",
    unsafe_allow_html=True
)
