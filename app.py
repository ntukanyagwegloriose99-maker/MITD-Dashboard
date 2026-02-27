# Import required libraries
import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

# Import page modules
from pages import page1_executive,page2_countries,page3_products, page4_monthly, page5_transport, page6_alerts

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "MTID - Merchandise Trade Intelligence Dashboard"

# Load the real data
try:
    df = pd.read_csv('data/trade_data.csv')
    print("✅ Data loaded successfully!")
    print(f"📊 Shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    print(f"📅 Years: {sorted(df['Year'].unique())}")
    print(f"🔄 Trade Types: {df['TradeType'].unique()}")
    print(f"➡️ Flows: {df['Flow'].unique()}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    df = pd.DataFrame()

# Data validation and cleaning
if not df.empty:
    # Ensure proper data types
    df['Year'] = df['Year'].astype(int)
    df['Quarter'] = df['Quarter'].astype(str)
    df['Period'] = df['Period'].astype(str).str.zfill(2)  # Ensure 2 digits: 01, 02, etc.
    
    # Map Flow codes to readable names
    flow_mapping = {'E': 'Export', 'I': 'Import', 'R': 'Re-export'}
    df['Flow_Name'] = df['Flow'].map(flow_mapping)
    
    # Clean Via column - map transport modes
    df['Transport_Mode'] = df['Via'].apply(lambda x: 'Air' if x == 'Air' else 'Land')

# Sidebar Navigation
sidebar = html.Div([
    html.Div([
        html.H4("🌍 Merchandise Trade Intelligence Dashboard (MTID)", className="text-white text-center py-3"),
        html.Hr(className="bg-white"),
        
        # Trade Type Selection
        html.Div([
            html.P("Select Trade Type:", className="text-white-50 small mb-2 px-3"),
            dbc.RadioItems(
                id="trade-type-selector",
                options=[
                    {"label": " General Trade", "value": "GeneralTrade"},
                    {"label": " Special Trade", "value": "SpecialTrade"},
                ],
                value="GeneralTrade",
                className="px-3 mb-3",
                inline=False,
                style={'color': 'white'}
            )
        ]),
        
        html.Hr(className="bg-white"),
        
        # Page Navigation
        html.P("Navigation:", className="text-white-50 small mb-2 px-3"),
        dbc.Nav([
            dbc.NavLink("📊 Executive Overview", href="#", id="nav-page1", active=True, className="text-white"),
            dbc.NavLink("🌍 Partner Countries", href="#", id="nav-page2", className="text-white"),
            dbc.NavLink("📦 Product Analysis", href="#", id="nav-page3", className="text-white"),
            dbc.NavLink("📅 Monthly Trade Analysis ", href="#", id="nav-page4", className="text-white"),
            dbc.NavLink("🚢 Transport & Customs", href="#", id="nav-page5", className="text-white"),
            dbc.NavLink("🚨 Smart Alerts", href="#", id="nav-page6", className="text-white"),
            dbc.NavLink("📘 Metadata & Data", href="#", id="nav-page7", className="text-white"),
        ], vertical=True, pills=True),
    ], style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '250px',
        'padding': '0',
        'background-color': '#2c3e50'
    })
], style={'width': '250px'})

# Main Content Area
content = html.Div(id='page-content', style={
    'margin-left': '250px',
    'padding': '20px'
})

# App Layout
app.layout = html.Div([
    # Hidden div to store current page and trade type
    html.Div(id='current-page', style={'display': 'none'}, children='page1'),
    html.Div(id='selected-trade-type', style={'display': 'none'}, children='GeneralTrade'),
    
    # Sidebar and Content
    sidebar,
    content,
    
    # AI Chat Component
    #ai_chat.chat_interface()
])

# Callback: Update Trade Type Selection
@callback(
    Output('selected-trade-type', 'children'),
    Input('trade-type-selector', 'value')
)
def update_trade_type(trade_type):
    """Update selected trade type"""
    return trade_type

# Callback: Update Active Page
@callback(
    Output('current-page', 'children'),
    Output('nav-page1', 'active'),
    Output('nav-page2', 'active'),
    Output('nav-page3', 'active'),
    Output('nav-page4', 'active'),
    Output('nav-page5', 'active'),
    Output('nav-page6', 'active'),
    Output('nav-page7', 'active'),
    Input('nav-page1', 'n_clicks'),
    Input('nav-page2', 'n_clicks'),
    Input('nav-page3', 'n_clicks'),
    Input('nav-page4', 'n_clicks'),
    Input('nav-page5', 'n_clicks'),
    Input('nav-page6', 'n_clicks'),
    Input('nav-page7', 'n_clicks'),
)
def update_page(n1, n2, n3, n4, n5, n6, n7):
    """Update current page and navigation highlighting"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'page1', True, False, False, False, False, False, False
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Map button to page
    page_map = {
        'nav-page1': ('page1', True, False, False, False, False, False, False),
        'nav-page2': ('page2', False, True, False, False, False, False, False),
        'nav-page3': ('page3', False, False, True, False, False, False, False),
        'nav-page4': ('page4', False, False, False, True, False, False, False),
        'nav-page5': ('page5', False, False, False, False, True, False, False),
        'nav-page6': ('page6', False, False, False, False, False, True, False),
        'nav-page7': ('page7', False, False, False, False, False, False, True),
    }
    
    return page_map.get(button_id, ('page1', True, False, False, False, False, False, False))

# Callback: Display Page Content
@callback(
    Output('page-content', 'children'),
    Input('current-page', 'children'),
    Input('selected-trade-type', 'children')
)
def display_page(page, trade_type):
    """Display the selected page content"""
    
    # Header for all pages
    header = dbc.Row([
        dbc.Col([
            html.H2("National Institute of Statistics of Rwanda(NISR)", className="text-primary mb-0"),
            html.P("FORMAL EXTERNAL TRADE IN GOODS STATISTICS", className="text-muted")
        ], width=8),
        dbc.Col([
            html.P("Last Updated: January 2025", className="text-end text-muted mb-0"),
            html.P(f"Viewing: {trade_type.replace('Trade', ' Trade').upper()}", className="text-end fw-bold")
        ], width=4)
    ], className="mb-4")
    
    if page == 'page1':
        return html.Div([
            header,
            html.Hr(),
            html.H3("Executive Trade Overview", className="mb-4"),
            page1_executive.layout(df)
        ])
    
    elif page == 'page2':
      return html.Div([
        header,
        html.Hr(),
        html.H3("🌍 Trade by Partner Country", className="mb-4"),
        page2_countries.layout(df)
    ])
    
    elif page == 'page3':
        return html.Div([
        header,
        html.Hr(),
        page3_products.layout(df)
    ])
    
    elif page == 'page4':
        return html.Div([
        header,
        html.Hr(),
        page4_monthly.layout(df)
    ])
    
    elif page == 'page5':
        return html.Div([
            header,
            html.Hr(),
            html.H3("🚢 Transport Mode & Customs Insights", className="mb-4"),
            page5_transport.layout(df)
        ])
    
    elif page == 'page6':
        return html.Div([
            header,
            html.Hr(),
            html.H3("🚨 Smart Alerts - Data Validation Support", className="mb-4"),
            page6_alerts.layout(df)
        ])
    
    elif page == 'page7':
        return html.Div([
            header,
            html.Hr(),
            html.H3("📘 Metadata, Methodology & Raw Data", className="mb-4"),
            
            # Metadata Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("📋 Metadata & Data Source", className="mb-0")),
                        dbc.CardBody([
                            html.H6("Data Source", className="text-primary mb-2"),
                            html.P("EUROTRACE / ASYCUDA++ / Rwanda Revenue Authority (RRA)", className="mb-3"),
                            
                            html.H6("Scope", className="text-primary mb-2"),
                            html.P("Formal Merchandise Trade (General Trade and Special Trade)", className="mb-3"),
                            
                            html.H6("Coverage", className="text-primary mb-2"),
                            html.P("All merchandise goods crossing Rwanda's borders (imports, exports, and re-exports)", className="mb-3"),
                            
                            html.H6("Exclusions", className="text-primary mb-2"),
                            html.P("Trade in services, informal cross-border trade not captured by customs", className="mb-3"),
                            
                            html.H6("Publication Frequency", className="text-primary mb-2"),
                            html.P("Quarterly, with annual aggregations", className="mb-3"),
                            
                            html.H6("Classification System", className="text-primary mb-2"),
                            html.P("Harmonized System (HS) at 2, 4, 6, and 8-digit levels, plus SITC classification", className="mb-3"),
                            
                            html.H6("Currency", className="text-primary mb-2"),
                            html.P("All values reported in United States Dollars (USD)", className="mb-0"),
                        ])
                    ], className="shadow-sm mb-4")
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("🔬 Methodology", className="mb-0")),
                        dbc.CardBody([
                            html.H6("Data Collection", className="text-primary mb-2"),
                            html.P("Data is collected at customs border posts using ASYCUDA++ system", className="mb-3"),
                            
                            html.H6("Valuation Method", className="text-primary mb-2"),
                            html.P("FOB (Free on Board) for exports, CIF (Cost, Insurance, Freight) for imports", className="mb-3"),
                            
                            html.H6("Data Quality Control", className="text-primary mb-2"),
                            html.Ul([
                                html.Li("Automated validation checks in ASYCUDA++"),
                                html.Li("Manual review by customs officers"),
                                html.Li("Statistical validation by NISR analysts"),
                                html.Li("Cross-verification with partner country data (mirror statistics)")
                            ], className="mb-3"),
                            
                            html.H6("Confidentiality", className="text-primary mb-2"),
                            html.P("Individual trader information is protected. Only aggregated statistics are published.", className="mb-3"),
                            
                            html.H6("Contact Information", className="text-primary mb-2"),
                            html.P([
                                "National Institute of Statistics of Rwanda (NISR)",
                                html.Br(),
                                "Email: info@statistics.gov.rw",
                                html.Br(),
                                "Website: www.statistics.gov.rw"
                            ], className="mb-0"),
                        ])
                    ], className="shadow-sm mb-4")
                ], width=6),
            ]),
            
            html.Hr(),            
           
            # Data Dictionary
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("📖 Data Dictionary", className="mb-0")),
                        dbc.CardBody([
                            html.P("Explanation of all columns in the dataset:", className="fw-bold mb-3"),
                            
                            html.Table([
                                html.Thead([
                                    html.Tr([
                                        html.Th("Column Name", style={'width': '20%'}),
                                        html.Th("Type", style={'width': '15%'}),
                                        html.Th("Description", style={'width': '65%'})
                                    ])
                                ]),
                                html.Tbody([
                                    html.Tr([html.Td("Year"), html.Td("Numeric"), html.Td("Calendar year of the trade transaction")]),
                                    html.Tr([html.Td("Period"), html.Td("Text"), html.Td("Month when the trade occurred (01-12)")]),
                                    html.Tr([html.Td("Quarter"), html.Td("Text"), html.Td("Quarter of the year (1, 2, 3, 4)")]),
                                    html.Tr([html.Td("Flow"), html.Td("Categorical"), html.Td("Direction of trade: E (Export), I (Import), R (Re-export)")]),
                                    html.Tr([html.Td("TradeType"), html.Td("Categorical"), html.Td("GeneralTrade or SpecialTrade")]),
                                    html.Tr([html.Td("HS8"), html.Td("Text"), html.Td("8-digit Harmonized System code (most detailed product level)")]),
                                    html.Tr([html.Td("HS8_Description"), html.Td("Text"), html.Td("Description of the HS8 product")]),
                                    html.Tr([html.Td("HS6"), html.Td("Text"), html.Td("6-digit Harmonized System code")]),
                                    html.Tr([html.Td("HS6_Description"), html.Td("Text"), html.Td("Description of the HS6 product")]),
                                    html.Tr([html.Td("HS4"), html.Td("Text"), html.Td("4-digit Harmonized System code (product sub-category)")]),
                                    html.Tr([html.Td("HS4_Description"), html.Td("Text"), html.Td("Description of the HS4 product")]),
                                    html.Tr([html.Td("HS2"), html.Td("Text"), html.Td("2-digit Harmonized System code (broad product category)")]),
                                    html.Tr([html.Td("HS2_Description"), html.Td("Text"), html.Td("Description of the HS2 product")]),
                                    html.Tr([html.Td("SITC"), html.Td("Text"), html.Td("Standard International Trade Classification code")]),
                                    html.Tr([html.Td("SITC_Description"), html.Td("Text"), html.Td("Description of the SITC product")]),
                                    html.Tr([html.Td("Borders"), html.Td("Text"), html.Td("Border post / customs office where trade was recorded (e.g., Cyanika, Rusumo)")]),
                                    html.Tr([html.Td("Partner_Country"), html.Td("Text"), html.Td("Destination country (exports) or origin country (imports)")]),
                                    html.Tr([html.Td("Region"), html.Td("Text"), html.Td("Geographic/economic region of partner country")]),
                                    html.Tr([html.Td("CDuty"), html.Td("Numeric"), html.Td("Customs duties collected (in USD)")]),
                                    html.Tr([html.Td("CValue"), html.Td("Numeric"), html.Td("Monetary value of trade in US Dollars")]),
                                    html.Tr([html.Td("NetWeight"), html.Td("Numeric"), html.Td("Physical weight of goods traded (in kilograms)")]),
                                    html.Tr([html.Td("Via"), html.Td("Text"), html.Td("Mode of transport: Air, Dar, Mom, DRC, Bur (land routes)")]),
                                ])
                            ], className="table table-striped table-hover")
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ]),
        ])

# Register Page 1 callbacks
page1_executive.register_callbacks(app, df)
# Register Page 2 callbacks
page2_countries.register_callbacks(app, df)
# Register Page 3 callbacks
page3_products.register_callbacks(app, df)
# Register Page 4 callbacks
page4_monthly.register_callbacks(app, df)
# Register Page 5 callbacks
page5_transport.register_callbacks(app, df)
# Register Page 6 callbacks
page6_alerts.register_callbacks(app, df)

# Register AI Chat callbacks
#ai_chat.register_callbacks(app, df)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)