import dash
from dash import html, dcc

dash.register_page(__name__,  order=2)

layout = html.Div(children=[
    html.H1(children='Resources'),

    dcc.Markdown("""
        This project was completed with the help of the following online resources. 
    """), 

    html.H2('Network Visualization Techniques'),

   dcc.Markdown("""
        * [Lucas Durand's Building an Interactive Network Graph to Understand Communities, PyData NYC 2023](https://www.youtube.com/watch?v=3LwxyynEUwQ)
        * [Charming Data's Cytoscape series](https://www.youtube.com/watch?v=g8xBlilTV4w)
            """),
        
    html.H2('Dash Resources'),

    dcc.Markdown(
        """
        * [Dash Documentation](https://dash.plotly.com/)
        * [Dash Tutorial](https://open-resources.github.io/dash_curriculum/preface/about.html)
        * [Dash Bootstrap Components](https://www.dash-bootstrap-components.com/)
        * [Header, Footer, body with Dash](https://medium.com/@matthieu.ru/header-footer-body-with-dash-css-and-dash-html-component-d076b1881546#78c2)
        
    """
    ),

])
