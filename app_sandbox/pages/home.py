import dash
from dash import html, dcc

dash.register_page(__name__, path='/', order =0)

layout = html.Div(children=[
    html.H1(children='Scam PAC Explorer'),

    dcc.Markdown("""
        Welcome to the Scam PAC Explorer. This tool is meant as a resource to help journalists, activists, and regulators, better understand where to focus investigatory efforts to curb any potentially fraudulent
        behavior in the federal campaign finance ecosystem.
    """), 

    html.H2('Background'),

    dcc.Markdown("""
        With the development of digital political fundraising technologies, from credit card processing platforms,
        to increasingly advanced and easy to use email and SMS messaging services, it has never been easier to
        solicit political donations. These technological advances, alongside changes in US politics, have led to
        rapid growth in political donations. During this time period Political Action Committees (PACs) have
        experienced the most growth. Unsurprisingly, bad actors have taken advantage of this environment.
                    
        During the 2023-2024 election cycle, Scam PACs garnered increasing press attention including from the [Bulwark](https://www.thebulwark.com/p/actblue-boots-democratic-scam-pacs-harris-criticized), [OpenSecrets](https://www.opensecrets.org/news/2023/08/how-scam-pacs-line-their-pockets-by-deceiving-political-donors/), and [Campaign Legal Center](https://campaignlegal.org/update/clc-uncovers-two-scam-pacs-defrauding-donors). In December 2023, Representative Katie Porter (D-CA-47) proposed [a bill to regulate Scam PACs](https://www.congress.gov/bill/118th-congress/house-bill/6893/text).
        More recently, Adam Bonica, has [reported on a specific network](https://data4democracy.substack.com/p/the-mothership-vortex-an-investigation) of what he calls “spam PACs” and their negative impact on political organizing. 
                    
        This is not a new phenomenon. The Federal Election Commission (FEC) released [a memo](https://www.fec.gov/resources/about-fec/commissioners/weintraub/statements/2016-09_Memo–Scam-PACs.pdf) detailing the problem and suggesting solutions in 2016, and [again in 2021](https://www.fec.gov/resources/cms-content/documents/mtgdoc-21-23-A1.pdf).
            """),
    
    html.H2("What is a Scam PAC?"),

    dcc.Markdown("""
        Per the proposed [SCAM PACT Act](https://www.congress.gov/bill/118th-congress/house-bill/6893/text):
        > Congress affirms the Federal Election Commission’s description of scam PACs as unauthorized committees that mislead contributors by “[soliciting] contributions with the promise of supporting candidates, but then disclose minimal or no candidate support activities while engaging in significant and continuous fundraising. This fundraising predominantly funds personal compensation for the committees’ organizers. In many cases, all funds raised by this subset of political committees are provided to fundraising vendors, direct mail vendors, and consultants in which the political committees’ officers appear to have financial interests.
        
        So, indicators of Scam PACs include:
                 * A high percentage of funds raised coming from small-dollar donors (unitemized donations)
                 * A disproportionate amount of spending to vendors related to fundraising or direct mail services, or consultats
                 * A small proportion of spending on contributions to candidate committees or other PACs, or on independent expenditures
                 * The people who benefit from payments to vendors being the same people running the PAC, or friends or family

        You can get data on the first three indicators from the filings PACs are required to file with the FEC.
        
        """),


    html.H2('Data'),

    dcc.Markdown(
        """
        The data for this project comes from the [FEC's open API](https://api.open.fec.gov/developers/) and [bulk data store](https://www.fec.gov/data/browse-data/?tab=bulk-data). I pulled all F3x filings from PACs in the 2023-2024 election cycle, and combined and cleaned their schedule B and schedule E lineitems to be able to trace which vendors, campaigns and committees, they paid during the course of the election cycle. 
        Due to resource constraints, we are currently only including a random sample of ~100 PACs. 
    """
    ),

    html.H2('Future Work'),

    dcc.Markdown("""
        Future work includes:
                 
        * Further text mining to classify expenditures as fundraising or direct mail expenses
        * Improved text cleaning 
        * Performance imporvements to allow for visualization of the entire network
        """),

    html.H2('Questions or Feedback?'),

    dcc.Markdown(
        """
        Fill out [this form](https://docs.google.com/forms/d/e/1FAIpQLSedxTHRhUv3PYwyjvpo7VQwJOevb1-SV6EzTraL73w7vBpj_Q/viewform?usp=header) and I will review and respond. 
    """
    ),

])

