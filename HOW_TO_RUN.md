# CLAPTALES Dashboard — Setup Guide

## First-time setup (do this once)

Make sure Python is installed, then open your terminal and run:

```
pip install streamlit pandas plotly openpyxl xlrd
```

## Running the dashboard

```
streamlit run claptales_dashboard.py
```

It will open automatically in your browser at http://localhost:8501

## Using it

1. Open the dashboard in your browser
2. In the left sidebar, click **"Browse files"** and upload your Helium10 or Jungle Scout CSV/Excel export
3. Use the filters (category, price range, rating) to narrow down the data
4. Navigate the 5 tabs for different insights

## Supported column names (auto-detected)

The dashboard automatically detects these columns from your export:

| Your column | What it maps to |
|---|---|
| Product Name / Title / ASIN Title | Product name |
| Brand / Manufacturer | Brand |
| Price / Buy Box Price / Sale Price | Price |
| Rating / Star Rating / Avg Rating | Rating |
| Reviews / Number of Reviews | Review count |
| BSR / Best Seller Rank / Sales Rank | BSR |
| Monthly Sales / Est. Monthly Sales | Monthly units sold |
| Monthly Revenue / Est. Monthly Revenue | Monthly revenue |
| Category / Department | Category |

If your column names are slightly different, rename them in Excel before uploading.

## What each tab does

| Tab | Purpose |
|---|---|
| Market Overview | Overall market snapshot — size, rating quality, category split |
| Product Opportunity | Finds gaps where demand is high but competitors are weak |
| Pricing Strategy | Recommends where to price CLAPTALES products |
| Competitor Intel | Scores and maps every brand in the market |
| Launch Recommendations | Final action plan for management decisions |
