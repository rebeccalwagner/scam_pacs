import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, name="Screenshots", path="/screenshots")

# ── Screenshot metadata ───────────────────────────────────────────────────────
# Add an entry here for each screenshot in your assets/ folder.
# Dash serves assets/ automatically, so just use the filename.

SCREENSHOTS = [
    {
        "filename": "original_pipeline.png",
        "title": "Scam PAC Explorer - Original Pipeline",
        "caption": "Diagram for the original scam PAC explorer using only local resources",
    },
    {
        "filename": "data_pipeline.png",
        "title": "Scam PAC Explorer - Updated Data Pipeline",
        "caption": "Diagram highlighting the scam PAC explorer's data pipeline leveraging cloud and distributed computing",
    },
    {
        "filename": "infastructure.png",
        "title": "Scam PAC Explorer - Full Infastructure",
        "caption": "Full infastructure for the updated scam PACs explorer including s3, Databricks, DuckDB and Hugging Face Spaces",
    },
    # Add more screenshots here as needed
]


# ── Helper: single screenshot card ───────────────────────────────────────────

def screenshot_card(item: dict) -> dbc.Col:
    return dbc.Col(
        dbc.Card([
            dbc.CardImg(
                src=f"/assets/{item['filename']}",
                top=True,
                style={
                    "border-bottom": "1px solid #dee2e6",
                    "cursor": "pointer",
                },
            ),
            dbc.CardBody([
                html.H5(item["title"], className="card-title"),
                html.P(item["caption"], className="card-text text-muted"),
            ]),
        ],
        className="h-100 shadow-sm",
        ),
        xs=12, sm=12, md=6, lg=4,   # responsive: 1 col mobile, 2 tablet, 3 desktop
        className="mb-4",
    )


# ── Page layout ───────────────────────────────────────────────────────────────

layout = dbc.Container([

    dbc.Row(
        dbc.Col([
            html.H2("App Screenshots", className="mt-4 mb-1"),
            html.P(
                "A visual walkthrough of the Scam PAC Explorer interface.",
                className="text-muted mb-4",
            ),
            html.Hr(),
        ])
    ),

    dbc.Row(
        [screenshot_card(item) for item in SCREENSHOTS],
    ),

], fluid=True)