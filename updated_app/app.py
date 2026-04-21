from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc
	
# Configure Themes
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY
url_theme3 = dbc.themes.YETI


app = Dash(__name__, 
		   use_pages=True, 
		   external_stylesheets=[url_theme3, dbc.icons.FONT_AWESOME], 
		   pages_folder='pages')

# print_registry(exclude="layout")

header = dbc.NavbarSimple(
    [
        dbc.Nav([
            dbc.NavLink(page["name"], href=page["path"])
            for page in dash.page_registry.values() if page["module"] != "pages.not_found_404"
        ], pills = True, fill = True)
    ],
    brand=dbc.Row("Scam PAC Explorer"),
	brand_style={"margin-left": "0", "padding-left": "0"},
    dark=True,
    color="#003D52"
)



footer_style = {    
    'text-align': 'left',        
    'padding': '10px',             
    'background-color': '#003D52',   
	'color': '#F9F7F1',
	'font-style':'italic',
}
footer = html.Footer(children = [
	html.A(
		html.I(className = "fa-brands fa-github"),
		href = 'https://github.com/sarahmathey/scam_pacs',
		target = "_blank",
    ),
	"   Sarah Mathey 2025",
], style = footer_style)

app.layout = dbc.Container([header, dash.page_container, footer], className="dbc", fluid=True)

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=7860, debug=False)

