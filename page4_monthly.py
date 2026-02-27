from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

def format_value(value):
    if pd.isna(value) or value == 0: return "$0.0M"
    return f"${value/1_000_000:.1f}M"

def clean_code(x):
    try:
        return str(int(float(x)))
    except (ValueError, TypeError):
        return str(x).replace('.0', '').strip() if pd.notna(x) else ''

def layout(df):
    return html.Div([
        html.H4("📅 Monthly Trade Statistics", className="mb-4"),
        
        # Filters
        dbc.Row([
            dbc.Col([
                html.Label("Year:", className="fw-bold"),
                dcc.Dropdown(
                    id='p4-year',
                    options=[{'label': str(y), 'value': y} for y in sorted(df['Year'].unique(), reverse=True)],
                    value=df['Year'].max(),
                    clearable=False
                )
            ], width=4),
            dbc.Col([
                html.Label("Period (Month):", className="fw-bold"),
                dcc.Dropdown(
                    id='p4-period',
                    options=[
                        {'label': f'{i:02d} - {m}', 'value': f'{i:02d}'} 
                        for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June',
                                              'July', 'August', 'September', 'October', 'November', 'December'], 1)
                    ],
                    value='01',
                    clearable=False
                )
            ], width=4),
            dbc.Col([
                html.Label("Flow:", className="fw-bold"),
                dcc.Dropdown(
                    id='p4-flow',
                    options=[
                        {'label': 'Exports', 'value': 'E'},
                        {'label': 'Imports', 'value': 'I'},
                        {'label': 'Re-exports', 'value': 'R'}
                    ],
                    value='E',
                    clearable=False
                )
            ], width=4)
        ], className="mb-4"),
        
        html.Hr(),
        
        # Table 1: Summary Statistics
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📊 Summary - Total Trade Statistics")),
                    dbc.CardBody([
                        html.Div(id='p4-summary-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        # Table 2: Top 10 Products by SITC
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(id='p4-products-title')),
                    dbc.CardBody([
                        html.Div(id='p4-products-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        # Table 3: Top 10 Partners
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(id='p4-partners-title')),
                    dbc.CardBody([
                        html.Div(id='p4-partners-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ])

def register_callbacks(app, df):
    
    @callback(
        Output('p4-summary-table', 'children'),
        Output('p4-products-title', 'children'),
        Output('p4-products-table', 'children'),
        Output('p4-partners-title', 'children'),
        Output('p4-partners-table', 'children'),
        Input('selected-trade-type', 'children'),
        Input('p4-year', 'value'),
        Input('p4-period', 'value'),
        Input('p4-flow', 'value')
    )
    def update_page4(trade_type, year, period, flow):
        
        try:
            # Filter by trade type
            fdf = df[df['TradeType'] == trade_type].copy()
            
            # Clean SITC codes
            fdf['SITC'] = fdf['SITC'].apply(clean_code)
            fdf['SITC_Description'] = fdf['SITC_Description'].astype(str).str.strip()
            
            # Determine periods
            selected_year = int(year)
            selected_period = str(period)
            
            # Previous month in same year
            if selected_period == '01':
                prev_month_year = selected_year - 1
                prev_month_period = '12'
            else:
                prev_month_year = selected_year
                prev_month_period = f'{int(selected_period) - 1:02d}'
            
            # Same period previous year
            same_period_prev_year = selected_year - 1
            same_period_prev_period = selected_period
            
            # Period labels
            selected_label = f"{selected_year}-{selected_period}"
            prev_month_label = f"{prev_month_year}-{prev_month_period}"
            prev_year_label = f"{same_period_prev_year}-{same_period_prev_period}"
            
            # ========== TABLE 1: SUMMARY - ALL FLOWS ==========
            summary_data = []
            
            for flow_code, flow_name in [('E', 'Total Exports'), ('I', 'Total Imports'), ('R', 'Total Re-exports')]:
                # Selected period
                selected_val = fdf[(fdf['Year'] == selected_year) & 
                                  (fdf['Period'] == selected_period) & 
                                  (fdf['Flow'] == flow_code)]['CValue'].sum()
                
                # Previous month same year
                prev_month_val = fdf[(fdf['Year'] == prev_month_year) & 
                                    (fdf['Period'] == prev_month_period) & 
                                    (fdf['Flow'] == flow_code)]['CValue'].sum()
                
                # Same period previous year
                prev_year_val = fdf[(fdf['Year'] == same_period_prev_year) & 
                                   (fdf['Period'] == same_period_prev_period) & 
                                   (fdf['Flow'] == flow_code)]['CValue'].sum()
                
                summary_data.append({
                    'Metric': flow_name,
                    prev_year_label: format_value(prev_year_val),
                    prev_month_label: format_value(prev_month_val),
                    selected_label: format_value(selected_val)
                })
            
            summary_table = dash_table.DataTable(
                data=summary_data,
                columns=[
                    {'name': 'Trade Flow', 'id': 'Metric'},
                    {'name': f'Same Period Prev Year ({prev_year_label})', 'id': prev_year_label},
                    {'name': f'Previous Month ({prev_month_label})', 'id': prev_month_label},
                    {'name': f'Selected Period ({selected_label})', 'id': selected_label}
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '15px',
                    'fontFamily': 'Arial',
                    'fontSize': '14px'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'Metric'}, 'fontWeight': 'bold', 'width': '200px'}
                ],
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {'if': {'row_index': 0}, 'backgroundColor': '#d4edda'},
                    {'if': {'row_index': 1}, 'backgroundColor': '#f8d7da'},
                    {'if': {'row_index': 2}, 'backgroundColor': '#d1ecf1'}
                ]
            )
            
            # ========== TABLE 2: TOP 10 PRODUCTS BY SITC ==========
            flow_names = {'E': 'Exports', 'I': 'Imports', 'R': 'Re-exports'}
            flow_name = flow_names[flow]
            
            # Filter by selected flow
            flow_df = fdf[fdf['Flow'] == flow].copy()
            
            # Get top 10 by selected period
            selected_products = flow_df[(flow_df['Year'] == selected_year) & 
                                       (flow_df['Period'] == selected_period)]
            
            top10_sitc = selected_products.groupby(['SITC', 'SITC_Description'])['CValue'].sum().reset_index()
            top10_sitc = top10_sitc.sort_values('CValue', ascending=False).head(10)
            
            if len(top10_sitc) == 0:
                products_table = dbc.Alert("No data available for selected period", color="warning")
            else:
                top10_codes = top10_sitc['SITC'].tolist()
                
                products_data = []
                for _, row in top10_sitc.iterrows():
                    sitc_code = row['SITC']
                    sitc_desc = row['SITC_Description']
                    
                    # Selected period
                    sel_val = flow_df[(flow_df['Year'] == selected_year) & 
                                     (flow_df['Period'] == selected_period) & 
                                     (flow_df['SITC'] == sitc_code)]['CValue'].sum()
                    
                    # Previous month
                    prev_m_val = flow_df[(flow_df['Year'] == prev_month_year) & 
                                        (flow_df['Period'] == prev_month_period) & 
                                        (flow_df['SITC'] == sitc_code)]['CValue'].sum()
                    
                    # Previous year same period
                    prev_y_val = flow_df[(flow_df['Year'] == same_period_prev_year) & 
                                        (flow_df['Period'] == same_period_prev_period) & 
                                        (flow_df['SITC'] == sitc_code)]['CValue'].sum()
                    
                    products_data.append({
                        'SITC': sitc_code,
                        'SITC_Description': sitc_desc,
                        prev_year_label: format_value(prev_y_val),
                        prev_month_label: format_value(prev_m_val),
                        selected_label: format_value(sel_val)
                    })
                
                products_table = dash_table.DataTable(
                    data=products_data,
                    columns=[
                        {'name': 'SITC', 'id': 'SITC'},
                        {'name': 'Product Description', 'id': 'SITC_Description'},
                        {'name': prev_year_label, 'id': prev_year_label},
                        {'name': prev_month_label, 'id': prev_month_label},
                        {'name': selected_label, 'id': selected_label}
                    ],
                    style_cell={
                        'textAlign': 'left',
                        'padding': '12px',
                        'fontFamily': 'Arial',
                        'fontSize': '13px'
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': 'SITC'}, 'width': '100px', 'textAlign': 'center', 'fontWeight': 'bold'},
                        {'if': {'column_id': 'SITC_Description'}, 'width': '300px'}
                    ],
                    style_header={
                        'backgroundColor': '#2c3e50',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
                        {'if': {'row_index': 0}, 'backgroundColor': '#fff3cd', 'fontWeight': 'bold'}
                    ],
                    export_format='xlsx',
                    export_headers='display'
                )
            
            # ========== TABLE 3: TOP 10 PARTNERS ==========
            # Get top 10 partners by selected period
            selected_partners = flow_df[(flow_df['Year'] == selected_year) & 
                                       (flow_df['Period'] == selected_period)]
            
            top10_partners = selected_partners.groupby('Partner_Country')['CValue'].sum().reset_index()
            top10_partners = top10_partners.sort_values('CValue', ascending=False).head(10)
            
            if len(top10_partners) == 0:
                partners_table = dbc.Alert("No data available for selected period", color="warning")
            else:
                partners_data = []
                for _, row in top10_partners.iterrows():
                    country = row['Partner_Country']
                    
                    # Selected period
                    sel_val = flow_df[(flow_df['Year'] == selected_year) & 
                                     (flow_df['Period'] == selected_period) & 
                                     (flow_df['Partner_Country'] == country)]['CValue'].sum()
                    
                    # Previous month
                    prev_m_val = flow_df[(flow_df['Year'] == prev_month_year) & 
                                        (flow_df['Period'] == prev_month_period) & 
                                        (flow_df['Partner_Country'] == country)]['CValue'].sum()
                    
                    # Previous year same period
                    prev_y_val = flow_df[(flow_df['Year'] == same_period_prev_year) & 
                                        (flow_df['Period'] == same_period_prev_period) & 
                                        (flow_df['Partner_Country'] == country)]['CValue'].sum()
                    
                    partners_data.append({
                        'Partner_Country': country,
                        prev_year_label: format_value(prev_y_val),
                        prev_month_label: format_value(prev_m_val),
                        selected_label: format_value(sel_val)
                    })
                
                partners_table = dash_table.DataTable(
                    data=partners_data,
                    columns=[
                        {'name': 'Partner Country', 'id': 'Partner_Country'},
                        {'name': prev_year_label, 'id': prev_year_label},
                        {'name': prev_month_label, 'id': prev_month_label},
                        {'name': selected_label, 'id': selected_label}
                    ],
                    style_cell={
                        'textAlign': 'left',
                        'padding': '12px',
                        'fontFamily': 'Arial',
                        'fontSize': '13px'
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': 'Partner_Country'}, 'width': '250px', 'fontWeight': 'bold'}
                    ],
                    style_header={
                        'backgroundColor': '#2c3e50',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
                        {'if': {'row_index': 0}, 'backgroundColor': '#fff3cd', 'fontWeight': 'bold'}
                    ],
                    export_format='xlsx',
                    export_headers='display'
                )
            
            products_title = f"Top 10 {flow_name} Products by SITC - Sorted by {selected_label}"
            partners_title = f"Top 10 {flow_name} Partners - Sorted by {selected_label}"
            
            return summary_table, products_title, products_table, partners_title, partners_table
        
        except Exception as e:
            error = dbc.Alert(f"Error: {str(e)}", color="danger")
            return error, "Error", error, "Error", error