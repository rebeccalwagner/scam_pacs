import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, name="Recent Updates", path="/Updates")

# ── Screenshot metadata ───────────────────────────────────────────────────────
# Add an entry here for each screenshot in your assets/ folder.
# Dash serves assets/ automatically, so just use the filename.

SCREENSHOTS = [
    {
        "filename": "original_pipeline.png",
        "title": "Scam PAC Explorer - Original Pipeline",
        "caption": "Diagram for the original scam PAC explorer using only local resources",
        "text": "The original explorer leveraged local compute power and random sampling to deliver an explorer that did not capture the full extent of the scam PAC network. A series of 5 Jupyter notebooks were manually executed to access the FEC API to download filings and financials, join and clean the data and create a network visualization. Then a large file was loaded into memory which required random sampling. This version is not scalable, not reproducible and not automated",
    },
    {
        "filename": "data_pipeline.png",
        "title": "Scam PAC Explorer - Updated Data Pipeline",
        "caption": "Diagram highlighting the scam PAC explorer's data pipeline leveraging cloud and distributed computing",
        "text": "The updated data pipeline requires some manual execution to access the FEC API as the Databricks free tier does not allow external connections. Once the API is accessed manually, the files are written to Amazon S3 buckets which are read into Databricks for automated aggregation and standardization as Parquet files. These files are connected to Hugging Face through a serverless DuckDB layer that removes the need for random sampling.",
    },
    {
        "filename": "infastructure.png",
        "title": "Scam PAC Explorer - Full Infrastructure",
        "caption": "Full infrastructure for the updated scam PACs explorer including s3, Databricks, DuckDB and Hugging Face Spaces",
        "text": "The updated infrastructure has four layers. First, the local compute layer to access the FEC API for data collection. The Amazon S3 layer holds raw and process Parquet files. The Databricks layer interacts with S3 in a read/write capacity to clean and standardize data. Finally, the public facing Dash app is located on Hugging Face Spaces which displays data through the serverless DuckDB. Journalists, activits and others are welcome to explore the network of PACs to research potential scam PACS.",
    },
    # Add more screenshots here as needed
]


# ── Helper: single screenshot card ───────────────────────────────────────────

def screenshot_card(item: dict) -> dbc.Row:
    return dbc.Row(
        dbc.Col(
            dbc.Card([

                # ── Title + caption ABOVE image ──
                dbc.CardHeader([
                    html.H4(item["title"], className="mb-1 fw-semibold"),
                    html.P(item["caption"], className="text-muted small mb-0"),
                ]),

                # ── Centered, constrained image ──
                html.Div(
                    dbc.CardImg(
                        src=f"/assets/{item['filename']}",
                        style={
                            "maxWidth": "800px",   # constrain size
                            "width": "100%",       # responsive scaling
                            "margin": "0 auto",    # center horizontally
                            "display": "block",
                        },
                    ),
                    style={"textAlign": "center", "padding": "20px"},
                ),

                # ── Text BELOW image ──
                dbc.CardBody([
                    html.P(
                        item.get("text", ""),
                        style={"lineHeight": "1.6"},
                    ) if item.get("text") else None,
                ]),

            ], className="shadow-sm"),

            width=12
        ),
        className="mb-5"
    )


# ── Page layout ───────────────────────────────────────────────────────────────
layout = dbc.Container([

    # Header at very top
    html.H1('Recent Updates', className="mb-4"),

    dcc.Markdown("""
    The original scam PAC explorer was built using only local compute resources 
    which limited the ability to truly explore all 7,157 PACs from the 2023-2024 
    election cycle through forced random sampling.

    By updating the infrastructure and data pipelines to leverage Amazon S3 
    storage, Databricks, and DuckDB, the system is now scalable, shareable, 
    and reproducible.
    """, className="mb-5"),

    html.Div([
    screenshot_card(item) for item in SCREENSHOTS
])

], fluid=True)