import pandas as pd
import networkx as nx
import dash
from dash import Dash, html, dcc, Output, Input, callback
from dash.dependencies import Output, Input
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc


dash.register_page(__name__, order = 2)

# Load data
df = pd.read_csv('/home/sjmpythonanywhere/mysite/pac_vendor_agg.csv')
#df = pd.read_csv('~/Desktop/scam_pacs/data/processed/pac_vendor_agg.csv')

example_cmtes = [
    "FREEDOM AND PROSPERITY FUND",
    "RETIRED DEMS",
    "STOP MAGA PAC",
    "ELECT DEMS NOW",
    "STOP PROJECT 2026",
    "REPUBLICANS ARE CORRUPT ACTION FUND",
    "GOD, FAMILY, & COUNTRY PAC",
    "GOD, GUNS, LIFE PAC",
    "USA FREEDOM FUND",
    "COMMON SENSE FOR AMERICA",
    "HOPE SPRINGS FROM FIELD PAC",
    "SUPPORT AMERICA'S POLICE PAC",
    "UNITED VETERANS ALLIANCE OF AMERICA PAC",
    "SUPPORT OUR FIREFIGHTERS AND PARAMEDICS PAC",
    "AMERICAN POLICE AND TROOPERS COALITION PAC",
    "POLICE COALITION OF AMERICA PAC",
    "AMERICAN VETERANS SUPPORT GROUP PAC",
    "POLICE AND TROOPER SUPPORT PAC",
    "CONSTITUTIONAL LEADERSHIP PAC",
    "UNITED BREAST CANCER SUPPORT PAC",
    "FIREFIGHTERS COALITION OF AMERICA PAC",
    "AMERICAN VETERANS INITIATIVE PAC",
    "VETERANS AID PAC",
    "AUTISM HEAR US NOW",
    "LAW ENFORCEMENT FOR A SAFER AMERICA PAC",
    "AMERICAN ALLIANCE FOR DISABLED CHILDREN PAC",
    "AMERICAN COALITION FOR CRISIS RELIEF PAC",
    "HONORING AMERICAN LAW ENFORCEMENT PAC",
    "AMERICAN HEALTH COMMITTEE PAC"
    ]

# Limit to a random 100 committees for performance reasons
random_100 = df.committee_name.sample(100).tolist()

# Filter the base df to the examples and random sample
df = df[df['committee_name'].isin(random_100) | df['committee_name'].isin(example_cmtes)]

# Define a function to filter the data based on the input variables
def filter_data(df, percent_value, flag_selected, numeric_value, categories_selected, committees_selected):
    """
    A function to filter the dataset based on user inputs in the app

    ARGS:
    df: the dataframe to filter

    percent_value: a user entered percent value used to filter based on % unitemized
    flag_selected: a user entered boolean value used to exclude or include union pacs
    numeric_value: a user entered boolean value used to filter out committees based on the number of vendors they have
    categories_selected: a user entered value used to filter to specific PAC designations
    committees_selected: a user entered value used to filter to specific PACs based on committee name

    """
    # Create a copy of the data frame to filter
    filtered_df = df.copy()

    # Filter based on pct_unitemized
    filtered_df = filtered_df[filtered_df["pct_unitem"] >= percent_value]

    # Filter based on is_union_pac
    if "TRUE" in flag_selected:
        filtered_df = filtered_df[filtered_df["is_union_pac"] == False]

    # Filter based on n_unique_vendors
    filtered_df = filtered_df[filtered_df["n_unique_vendors"] <= numeric_value]

    # Filter based on cmte_designation if user input exists
    if categories_selected:
        filtered_df = filtered_df[filtered_df["committee_designation_full"].isin(categories_selected)]

    # Filter based on cmte_name if user input exists
    if committees_selected:
        filtered_df = filtered_df[filtered_df["committee_name"].isin(committees_selected)]

    # order resulting df based on committee id and total spend by vendor
    filtered_df = filtered_df.sort_values(by = ['committee_id','ttl_spend'], ascending = [True,  False])

    return filtered_df

# Define a function to update the visualization based on the updated data
def update_viz(filtered_df):
    """
    A function to regenerate the cytoscape elements based on the filtered dataset

    ARGS:
    filtered_df: the filtered dataframe

    """
    # Create a df of just unique committees and their features to create committee nodes
    cmte_unique = (filtered_df[['committee_id',
                                'committee_name',
                                'committee_state',
                                'committee_type_full',
                                'committee_designation_full',
                                'organization_type_full',
                                'treasurer_name',
                                'individual_unitemized_contributions',
                                'receipts',
                                'pct_indiv',
                                'pct_unitem',
                                'n_unique_vendors',
                                'is_union_pac']]
                   .copy()
                   .drop_duplicates()

    )

    # Create a df of just unique vendors and their features to create vendor nodes
    vendor_unique = (filtered_df[['vendor_full',
                                  'exp_cat',
                                  'n_unique_filers']]
                    .copy()
                    .drop_duplicates()

    )

    # Create tuples from cmte_unique
    cmtes = [tuple(row) for row in cmte_unique.itertuples(index = False)]

    # Create tuples from vendor_unique
    vendors = [tuple(row) for row in vendor_unique.itertuples(index = False)]

    # Create edges with pct_ttl_spend as weight
    edges = [
        (row.committee_name, row.vendor_full, float(row.pct_ttl_spend))
        for _, row in filtered_df.iterrows()
    ]

    # Initialize network graph object
    G = nx.Graph()

    # Add nodes from cmte_unique as type = 'Filer'
    G.add_nodes_from(cmte_unique['committee_name'], type = 'Filer')

    # Add nodes from vendor_unique as type = 'Vendor'
    G.add_nodes_from(vendor_unique['vendor_full'], type = 'Vendor')

    # Add weighted edges
    G.add_weighted_edges_from(edges)


    # Set node attributes from tuples
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


    nx.set_node_attributes(G, committee_id_dict, 'committee_id')
    nx.set_node_attributes(G, committee_state_dict, 'committee_state')
    nx.set_node_attributes(G, committee_type_dict, 'committee_type')
    nx.set_node_attributes(G, committee_designation_dict, 'committee_designation')
    nx.set_node_attributes(G, organization_type_dict, 'organization_type')
    nx.set_node_attributes(G, treasurer_name_dict, 'treasurer_name')
    nx.set_node_attributes(G, individual_unitemized_contributions_dict, 'unitemized_contributions')
    nx.set_node_attributes(G, receipts_dict, 'receipts')
    nx.set_node_attributes(G, pct_indiv_dict, 'pct_receipts_from_individuals')
    nx.set_node_attributes(G, pct_unitem_dict, 'pct_receipts_from_unitemized')
    nx.set_node_attributes(G, n_unique_vendors_dict, 'n_unique_vendors')
    nx.set_node_attributes(G, is_union_pac_dict, 'is_union_pac')


    nx.set_node_attributes(G, vendor_exp_cat_dict, 'exp_cat')
    nx.set_node_attributes(G, vendor_unique_filers_dict, 'n_unique_filers')


    # Convert networkX to cytoscape:
    cyto_data = nx.cytoscape_data(G)
    elements = cyto_data['elements'] ['nodes'] + cyto_data['elements']['edges']

    return elements

###### Build app

cyto.load_extra_layouts()

# commented out because now a page and not the app itself
#app = Dash(__name__)
#server = app.server

heading = html.H1("Federal PAC Spending Network")
subheading = html.H2("2023 - 2024 Election Cycle")
intro_text = html.Div([
    html.P([
    dcc.Markdown("Per the proposed [SCAM PACT Act](https://www.congress.gov/bill/118th-congress/house-bill/6893/text):"),
    html.Span("Congress affirms the Federal Election Commission’s description of scam PACs as unauthorized committees that mislead contributors by “[soliciting] contributions with the promise of supporting candidates, but then ",style = {'font-style':'italic'}),
    html.Span("disclose minimal or no candidate support activities while engaging in significant and continuous fundraising. ", style = {'font-style':'italic','font-weight':'bold'}),
    html.Span("This fundraising predominantly funds personal compensation for the committees’ organizers. In many cases, all funds raised by this subset of political committees are provided to ", style = {'font-style':'italic'}), 
    html.Span("fundraising vendors, direct mail vendors, and consultants in which the political committees’ officers appear to have financial interests.”", style = {'font-style':'italic','font-weight':'bold'})
    ]),
    
    html.P(["The visualization below displays ~100 PACs and their vendors from the 2024 election cycle. The PACs are represented by ",
           html.Span("the blue nodes", style={"color": "#003D52", "font-weight": "bold"}),
           ", while vendors are the green nodes."]),
    html.P([
        html.Span("Candidate committees and other political committees are light green", style={"color": "#BADDC9", "font-weight": "bold"}),
        " , while ",
        html.Span("operational vendors are dark green.", style={"color": "#265436", "font-weight": "bold"})
    ]),
    html.P([
        html.Span("Independent expenditure spending is aggregated for each PAC and is represented by the "),
        html.Span("golden yellow node.", style={"color": "#EDAA1C", "font-weight": "bold"})
    ]),
    html.P([
        html.Span("If you select one of the nodes, the edges will become "),
        html.Span("weighted ", style = {'font-weight':'extra-bold'}),
        html.Span("by the percent of total spending a PAC spent with a vendor."),]),
    html.P("Use the filters on the left side to adjust the visible PACs to help expand or narrow your search."),


    html.P([
        html.Span("Can you find any potential Scam PACs from this data?", style = {'size': 16, 'font-weight':'bold'})
    ])
])

# Define sidebar with filter components
side_bar = html.Div(
        style={
            "width": "320px",
            "minWidth": "320px",
            "flexShrink": 0,
            "padding": "20px",
            "background-color": "#f8f9fa",
            "border-right": "1px solid #ddd",
            "overflow-y": "auto",
            'height': '100vh'
        },
        children = [

            html.H3("Filters", style={"marginBottom": "20px"}),
            dbc.Accordion(
                [
            # Slider for % unitemized
                    dbc.AccordionItem(
                        [
                            html.P("Limit the visible PACs based on the percent of their total receipts that were rasied from small-dollar donors. We are generally more interested in PACs that have a higher % unitemized."),
                        ],
                        title = "Minimum % of Receipts from Unitemized Contributions"
                    ),
                ],
                start_collapsed=True,
            ),
            #html.Label("Minimum % of Receipts from Unitemized Contributions"),
            dcc.Slider(
                id = 'percent-slider',
                min = .25,
                max = 1.00,
                step = .05,
                marks = {round(i/4 + 0.25, 2): f"{int((i/4 + 0.25)*100)}%" for i in range(4)},
                value = .80
            ),
            html.Br(),

            # Check box for is_union_pac
            dbc.Accordion(
                [
            # Slider for % unitemized
                    dbc.AccordionItem(
                        [
                            html.P("Check this box to exclude PACs that are formally registered as Union, Trade, or Membership PACs"),
                        ],
                        title = "Exclude Union, Trade and Membership PACs?"
                    ),
                ],
                start_collapsed=True,
            ),
            dcc.Checklist(
                id="flag-toggle",
                options=[{"label": "Exclude?", "value": "TRUE"}],
                value = []
            ),
            html.Br(),

            # Numeric input for n_unique_vendors
            dbc.Accordion(
                [
            # Slider for % unitemized
                    dbc.AccordionItem(
                        [
                            html.P("This filter limits PACs to those who have X vendors or fewer. Typically, PACs with many vendors are giving money to many candidates and are therefore unlikely to be Scam PACs."),
                        ],
                        title = "Maximum Number of Vendors"
                    ),
                ],
                start_collapsed=True,
            ),
            dcc.Input(
                id="numeric-input",
                type="number",
                value=100,
                style={"width": "100%"}
            ),
            html.Br(), html.Br(),

            # Multi-select dropdown for cmte designation
            dbc.Accordion(
                [
            # Slider for % unitemized
                    dbc.AccordionItem(
                        [
                            html.P("Filter PACs based on their official FEC designations."),
                        ],
                        title = "Select PAC designations"
                    ),
                ]
            ),
            dcc.Dropdown(
                id="category-dropdown",
                options=[{"label": c, "value": c} for c in df["committee_designation_full"].dropna().unique()],
                multi=True,
                placeholder= "Select a PAC designation"
            ),
            # Multi-select dropdown for committee name
            dbc.Accordion(
                [
            # Slider for % unitemized
                    dbc.AccordionItem(
                        [
                            html.P("Filter to just one, or a selection of specific PACs by committee name."),
                        ],
                        title = "Select Filing Committee"
                    ),
                ],
                start_collapsed=True,
            ),
            dcc.Dropdown(
                id="cmte-dropdown",
                options=[{"label": c, "value": c} for c in df["committee_name"].dropna().unique()],
                multi=True,
                placeholder= "Select a PAC"
            ),
        ], className= 'col-2'
    )

# Define cytoscape html div
main_viz = html.Div([
        cyto.Cytoscape(
            id = 'network',
            minZoom = 0.2,
            maxZoom = 4,
            elements = [],
            style={'width': '100%', 'height': '1000px'},
            layout={'name': 'cose'},
            selectedNodeData = None,
            stylesheet=[]
            )
        ], className= 'col', style = {'height':'100vh', 'overflow':'hidden',
            'flex': "1"}
    )

# Define app layout
layout = html.Div(
    children = [heading, subheading,intro_text,
    html.Div(
        style={
            "display": "flex",
            "flexDirection": "row",
            "height": "100vh",
            "overflow": "hidden"
        },
        children = [ side_bar, main_viz], className='row'
        )
    ]
)

# Define app callbacks to update vizualization based on filter components
@callback(Output(component_id='network',component_property='elements'),
              [Input('percent-slider', 'value'),
                Input('flag-toggle', 'value'),
                Input('numeric-input', 'value'),
                Input('category-dropdown', 'value'),
                Input('cmte-dropdown', 'value')]
              )

def update_elements(percent_value, flag_selected, numeric_value, categories_selected, committees_selected):

    # Use filter_data function to filter dataframe based on user inputs
    filtered_df = filter_data(df, percent_value, flag_selected, numeric_value, categories_selected, committees_selected)

    # Update visualization based on updated dataframe
    elements = update_viz(filtered_df)

    return elements


# Define app callbacks to update vizualization based on user click actions
@callback(Output(component_id='network',component_property='stylesheet'),
              [Input(component_id='network', component_property='selectedNodeData'),
               Input(component_id='network',component_property='elements')])

def update_edge_color(snd, elements):
    # Base stylesheet (normal colors)
    base_styles = [
            {
                'selector': 'edge',
                'style': {
                    'line-color': '#B8B19D',
                    'width': .25,
                    'line-opacity': .25
                }
            },
            {'selector': 'node',
                'style': {
                    'label': 'data(name)'
                }

            },

            {
                'selector': 'node[type = "Filer"]',
                'style': {
                    'width': 10,
                    'height': 10,
                    'background-color': '#384056',
                    'label': 'data(name)',
                    'font-size': 3,
                    'font-weight': 'bold',
                    'text-color': 'rgb(255,0,0)'
                }
            },
            {
                'selector': 'node[name = "INDEPENDENT EXPENDITURE"]',
                'style': {
                    'width': 7,
                    'height': 7,
                    'background-color': '#EDAA1C',
                    'label': 'data(name)',
                    'font-size': 3,
                    'font-weight': 'bold',
                    'text-color': 'rgb(255,0,0)'
                }
            },
            {
                'selector':'[exp_cat = "Other"]',
                'style':{
                    'width': 3.5,
                    'height': 3.5,
                    'background-color': '#265436',
                    'label': 'data(name)',
                    'font-size': 2
                }
            },
            {
                'selector':'[exp_cat = "Transfer to affiliated committee"]',
                'style':{
                    'width': 3.5,
                    'height': 3.5,
                    'background-color': '#799A84',
                    'label': 'data(name)',
                    'font-size': 2
                }
            },
            {
                'selector':'[exp_cat = "Contribution to Candidate or Committee"]',
                'style':{
                    'width': 3.5,
                    'height': 3.5,
                    'background-color': '#BADDC9',
                    'label': 'data(name)',
                    'font-size': 2
                }
            }
        ]

    if not snd:
        return base_styles

    selected_node = snd[0]['id']

    highlight_styles = [
        # highlight edges connected to selected node
        {
            'selector': f'edge[source = "{selected_node}"], edge[target = "{selected_node}"]',
            'style': {
                'line-color': '#5D6770',
                'width': 'data(weight)',
            }
        },
        # mute other connections
        {
            'selector': f'edge[source != "{selected_node}"][target != "{selected_node}"]',
            'style': {
                'line-color': '#DDD',
                'width': .25,
                'opacity': 0.25
            }
        }
    ]

    return base_styles + highlight_styles
