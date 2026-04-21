import duckdb
import pandas as pd
import networkx as nx
import dash
from dash import Dash, html, dcc, Output, Input, callback
from dash.dependencies import Output, Input
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import os

dash.register_page(__name__, order=2)

# --- DuckDB / S3 setup ---
S3_PARQUET_PATH = "s3://scam-pacs/processed/pac_vendor_agg.parquet"

def get_conn():
    """
    Create a DuckDB connection with S3 credentials loaded from environment variables.
    Expected env vars: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION (optional, defaults to us-east-1)
    """
    conn = duckdb.connect()
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    conn.execute(f"""
        SET s3_access_key_id='{os.environ.get("AWS_ACCESS_KEY_ID", "")}';
        SET s3_secret_access_key='{os.environ.get("AWS_SECRET_ACCESS_KEY", "")}';
        SET s3_region='{os.environ.get("AWS_REGION", "us-east-1")}';
    """)
    return conn


def load_dropdown_options():
    """
    Query S3 once at startup for the distinct values needed to populate
    the category and committee dropdowns. Much cheaper than loading the
    full 94 MB CSV — returns only two small result sets.
    """
    conn = get_conn()

    designations = conn.execute(f"""
        SELECT DISTINCT committee_designation_full
        FROM read_parquet('{S3_PARQUET_PATH}')
        WHERE committee_designation_full IS NOT NULL
        ORDER BY committee_designation_full
    """).df()["committee_designation_full"].tolist()

    committees = conn.execute(f"""
        SELECT DISTINCT committee_name
        FROM read_parquet('{S3_PARQUET_PATH}')
        WHERE committee_name IS NOT NULL
        ORDER BY committee_name
    """).df()["committee_name"].tolist()

    conn.close()
    return designations, committees


# Load only the dropdown option lists at startup (tiny queries, not the full dataset)
designation_options, committee_options = load_dropdown_options()


# --- Data fetching ---

def fetch_filtered_data(percent_value, flag_selected, numeric_value, categories_selected, committees_selected):
    """
    Query only the rows that match the current filter state directly from
    S3 Parquet via DuckDB. Replaces the old in-memory filter_data() approach.

    Returns a pandas DataFrame of matching rows, capped at 500 PAC-vendor
    pairs to keep Cytoscape rendering fast.
    """
    conn = get_conn()

    # Build parameterised WHERE clauses
    conditions = [
        f"pct_unitem >= {float(percent_value)}",
        f"n_unique_vendors <= {int(numeric_value)}",
    ]

    if flag_selected and "TRUE" in flag_selected:
        conditions.append("is_union_pac = FALSE")

    if categories_selected:
        quoted = ", ".join(f"'{c}'" for c in categories_selected)
        conditions.append(f"committee_designation_full IN ({quoted})")

    if committees_selected:
        quoted = ", ".join(f"'{c}'" for c in committees_selected)
        conditions.append(f"committee_name IN ({quoted})")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT *
        FROM read_parquet('{S3_PARQUET_PATH}')
        WHERE {where_clause}
        ORDER BY committee_id ASC, ttl_spend DESC
        LIMIT 500
    """

    df = conn.execute(query).df()
    conn.close()
    return df


# --- Visualization builder (unchanged from original) ---

def update_viz(filtered_df):
    """
    Regenerate the Cytoscape elements based on the filtered dataset.
    """
    cmte_unique = (
        filtered_df[[
            "committee_id",
            "committee_name",
            "committee_state",
            "committee_type_full",
            "committee_designation_full",
            "organization_type_full",
            "treasurer_name",
            "individual_unitemized_contributions",
            "receipts",
            "pct_indiv",
            "pct_unitem",
            "n_unique_vendors",
            "is_union_pac",
        ]]
        .copy()
        .drop_duplicates()
    )

    vendor_unique = (
        filtered_df[["vendor_full", "exp_cat", "n_unique_filers"]]
        .copy()
        .drop_duplicates()
    )

    cmtes = [tuple(row) for row in cmte_unique.itertuples(index=False)]
    vendors = [tuple(row) for row in vendor_unique.itertuples(index=False)]

    edges = [
        (row.committee_name, row.vendor_full, float(row.pct_ttl_spend))
        for _, row in filtered_df.iterrows()
    ]

    G = nx.Graph()
    G.add_nodes_from(cmte_unique["committee_name"], type="Filer")
    G.add_nodes_from(vendor_unique["vendor_full"], type="Vendor")
    G.add_weighted_edges_from(edges)

    committee_id_dict = {}
    committee_state_dict = {}
    committee_type_dict = {}
    committee_designation_dict = {}
    organization_type_dict = {}
    treasurer_name_dict = {}
    individual_unitemized_contributions_dict = {}
    receipts_dict = {}
    pct_indiv_dict = {}
    pct_unitem_dict = {}
    n_unique_vendors_dict = {}
    is_union_pac_dict = {}

    for cmte in cmtes:
        committee_id_dict[cmte[1]] = cmte[0]
        committee_state_dict[cmte[1]] = cmte[2]
        committee_type_dict[cmte[1]] = cmte[3]
        committee_designation_dict[cmte[1]] = cmte[4]
        organization_type_dict[cmte[1]] = cmte[5]
        treasurer_name_dict[cmte[1]] = cmte[6]
        individual_unitemized_contributions_dict[cmte[1]] = cmte[7]
        receipts_dict[cmte[1]] = cmte[8]
        pct_indiv_dict[cmte[1]] = cmte[9]
        pct_unitem_dict[cmte[1]] = cmte[10]
        n_unique_vendors_dict[cmte[1]] = cmte[11]
        is_union_pac_dict[cmte[1]] = cmte[12]

    vendor_exp_cat_dict = {}
    vendor_unique_filers_dict = {}

    for vendor in vendors:
        vendor_exp_cat_dict[vendor[0]] = vendor[1]
        vendor_unique_filers_dict[vendor[0]] = vendor[2]

    nx.set_node_attributes(G, committee_id_dict, "committee_id")
    nx.set_node_attributes(G, committee_state_dict, "committee_state")
    nx.set_node_attributes(G, committee_type_dict, "committee_type")
    nx.set_node_attributes(G, committee_designation_dict, "committee_designation")
    nx.set_node_attributes(G, organization_type_dict, "organization_type")
    nx.set_node_attributes(G, treasurer_name_dict, "treasurer_name")
    nx.set_node_attributes(G, individual_unitemized_contributions_dict, "unitemized_contributions")
    nx.set_node_attributes(G, receipts_dict, "receipts")
    nx.set_node_attributes(G, pct_indiv_dict, "pct_receipts_from_individuals")
    nx.set_node_attributes(G, pct_unitem_dict, "pct_receipts_from_unitemized")
    nx.set_node_attributes(G, n_unique_vendors_dict, "n_unique_vendors")
    nx.set_node_attributes(G, is_union_pac_dict, "is_union_pac")
    nx.set_node_attributes(G, vendor_exp_cat_dict, "exp_cat")
    nx.set_node_attributes(G, vendor_unique_filers_dict, "n_unique_filers")

    cyto_data = nx.cytoscape_data(G)
    elements = cyto_data["elements"]["nodes"] + cyto_data["elements"]["edges"]
    return elements


###### Build app layout

cyto.load_extra_layouts()

heading = html.H1("Federal PAC Spending Network")
subheading = html.H2("2023 - 2024 Election Cycle")

intro_text = html.Div([
    html.P([
        dcc.Markdown("Per the proposed [SCAM PACT Act](https://www.congress.gov/bill/118th-congress/house-bill/6893/text):"),
        html.Span(
            "Congress affirms the Federal Election Commission\u2019s description of scam PACs as unauthorized committees that mislead contributors by \u201c[soliciting] contributions with the promise of supporting candidates, but then ",
            style={"font-style": "italic"},
        ),
        html.Span(
            "disclose minimal or no candidate support activities while engaging in significant and continuous fundraising. ",
            style={"font-style": "italic", "font-weight": "bold"},
        ),
        html.Span(
            "This fundraising predominantly funds personal compensation for the committees\u2019 organizers. In many cases, all funds raised by this subset of political committees are provided to ",
            style={"font-style": "italic"},
        ),
        html.Span(
            "fundraising vendors, direct mail vendors, and consultants in which the political committees\u2019 officers appear to have financial interests.\u201d",
            style={"font-style": "italic", "font-weight": "bold"},
        ),
    ]),

    html.P([
        "The visualization below displays PACs and their vendors from the 2024 election cycle. The PACs are represented by ",
        html.Span("the blue nodes", style={"color": "#003D52", "font-weight": "bold"}),
        ", while vendors are the green nodes.",
    ]),
    html.P([
        html.Span("Candidate committees and other political committees are light green", style={"color": "#BADDC9", "font-weight": "bold"}),
        " , while ",
        html.Span("operational vendors are dark green.", style={"color": "#265436", "font-weight": "bold"}),
    ]),
    html.P([
        html.Span("Independent expenditure spending is aggregated for each PAC and is represented by the "),
        html.Span("golden yellow node.", style={"color": "#EDAA1C", "font-weight": "bold"}),
    ]),
    html.P([
        html.Span("If you select one of the nodes, the edges will become "),
        html.Span("weighted ", style={"font-weight": "extra-bold"}),
        html.Span("by the percent of total spending a PAC spent with a vendor."),
    ]),
    html.P("Use the filters on the left side to adjust the visible PACs to help expand or narrow your search."),
    html.P([
        html.Span("Can you find any potential Scam PACs from this data?", style={"size": 16, "font-weight": "bold"})
    ]),
])

# Sidebar with filter components
side_bar = html.Div(
    style={
        "width": "320px",
        "minWidth": "320px",
        "flexShrink": 0,
        "padding": "20px",
        "background-color": "#f8f9fa",
        "border-right": "1px solid #ddd",
        "overflow-y": "auto",
        "height": "100vh",
    },
    children=[
        html.H3("Filters", style={"marginBottom": "20px"}),

        # % unitemized slider
        dbc.Accordion(
            [dbc.AccordionItem(
                [html.P("Limit the visible PACs based on the percent of their total receipts that were raised from small-dollar donors. We are generally more interested in PACs that have a higher % unitemized.")],
                title="Minimum % of Receipts from Unitemized Contributions",
            )],
            start_collapsed=True,
        ),
        dcc.Slider(
            id="percent-slider",
            min=0.25,
            max=1.00,
            step=0.05,
            marks={round(i / 4 + 0.25, 2): f"{int((i / 4 + 0.25) * 100)}%" for i in range(4)},
            value=0.80,
        ),
        html.Br(),

        # Union PAC exclude toggle
        dbc.Accordion(
            [dbc.AccordionItem(
                [html.P("Check this box to exclude PACs that are formally registered as Union, Trade, or Membership PACs")],
                title="Exclude Union, Trade and Membership PACs?",
            )],
            start_collapsed=True,
        ),
        dcc.Checklist(
            id="flag-toggle",
            options=[{"label": "Exclude?", "value": "TRUE"}],
            value=[],
        ),
        html.Br(),

        # Max vendors input
        dbc.Accordion(
            [dbc.AccordionItem(
                [html.P("This filter limits PACs to those who have X vendors or fewer. Typically, PACs with many vendors are giving money to many candidates and are therefore unlikely to be Scam PACs.")],
                title="Maximum Number of Vendors",
            )],
            start_collapsed=True,
        ),
        dcc.Input(
            id="numeric-input",
            type="number",
            value=100,
            style={"width": "100%"},
        ),
        html.Br(), html.Br(),

        # PAC designation dropdown — populated from S3 at startup
        dbc.Accordion(
            [dbc.AccordionItem(
                [html.P("Filter PACs based on their official FEC designations.")],
                title="Select PAC designations",
            )]
        ),
        dcc.Dropdown(
            id="category-dropdown",
            options=[{"label": c, "value": c} for c in designation_options],
            multi=True,
            placeholder="Select a PAC designation",
        ),

        # Committee name dropdown — populated from S3 at startup
        dbc.Accordion(
            [dbc.AccordionItem(
                [html.P("Filter to just one, or a selection of specific PACs by committee name.")],
                title="Select Filing Committee",
            )],
            start_collapsed=True,
        ),
        dcc.Dropdown(
            id="cmte-dropdown",
            options=[{"label": c, "value": c} for c in committee_options],
            multi=True,
            placeholder="Select a PAC",
        ),
    ],
    className="col-2",
)

# Main Cytoscape panel
main_viz = html.Div(
    [cyto.Cytoscape(
        id="network",
        minZoom=0.2,
        maxZoom=4,
        elements=[],
        style={"width": "100%", "height": "1000px"},
        layout={"name": "cose"},
        selectedNodeData=None,
        stylesheet=[],
    )],
    className="col",
    style={"height": "100vh", "overflow": "hidden", "flex": "1"},
)

layout = html.Div(
    children=[
        heading, subheading, intro_text,
        html.Div(
            style={
                "display": "flex",
                "flexDirection": "row",
                "height": "100vh",
                "overflow": "hidden",
            },
            children=[side_bar, main_viz],
            className="row",
        ),
    ]
)


# --- Callbacks ---

@callback(
    Output(component_id="network", component_property="elements"),
    [
        Input("percent-slider", "value"),
        Input("flag-toggle", "value"),
        Input("numeric-input", "value"),
        Input("category-dropdown", "value"),
        Input("cmte-dropdown", "value"),
    ],
)
def update_elements(percent_value, flag_selected, numeric_value, categories_selected, committees_selected):
    # Query only matching rows from S3 — no more in-memory 94 MB CSV
    filtered_df = fetch_filtered_data(
        percent_value, flag_selected, numeric_value, categories_selected, committees_selected
    )
    return update_viz(filtered_df)


@callback(
    Output(component_id="network", component_property="stylesheet"),
    [
        Input(component_id="network", component_property="selectedNodeData"),
        Input(component_id="network", component_property="elements"),
    ],
)
def update_edge_color(snd, elements):
    base_styles = [
        {
            "selector": "edge",
            "style": {"line-color": "#B8B19D", "width": 0.25, "line-opacity": 0.25},
        },
        {"selector": "node", "style": {"label": "data(name)"}},
        {
            "selector": 'node[type = "Filer"]',
            "style": {
                "width": 10,
                "height": 10,
                "background-color": "#384056",
                "label": "data(name)",
                "font-size": 3,
                "font-weight": "bold",
                "text-color": "rgb(255,0,0)",
            },
        },
        {
            "selector": 'node[name = "INDEPENDENT EXPENDITURE"]',
            "style": {
                "width": 7,
                "height": 7,
                "background-color": "#EDAA1C",
                "label": "data(name)",
                "font-size": 3,
                "font-weight": "bold",
                "text-color": "rgb(255,0,0)",
            },
        },
        {
            "selector": '[exp_cat = "Other"]',
            "style": {
                "width": 3.5,
                "height": 3.5,
                "background-color": "#265436",
                "label": "data(name)",
                "font-size": 2,
            },
        },
        {
            "selector": '[exp_cat = "Transfer to affiliated committee"]',
            "style": {
                "width": 3.5,
                "height": 3.5,
                "background-color": "#799A84",
                "label": "data(name)",
                "font-size": 2,
            },
        },
        {
            "selector": '[exp_cat = "Contribution to Candidate or Committee"]',
            "style": {
                "width": 3.5,
                "height": 3.5,
                "background-color": "#BADDC9",
                "label": "data(name)",
                "font-size": 2,
            },
        },
    ]

    if not snd:
        return base_styles

    selected_node = snd[0]["id"]

    highlight_styles = [
        {
            "selector": f'edge[source = "{selected_node}"], edge[target = "{selected_node}"]',
            "style": {"line-color": "#5D6770", "width": "data(weight)"},
        },
        {
            "selector": f'edge[source != "{selected_node}"][target != "{selected_node}"]',
            "style": {"line-color": "#DDD", "width": 0.25, "opacity": 0.25},
        },
    ]

    return base_styles + highlight_styles
