from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

def format_value(value):
    if pd.isna(value): return "$0.0M"
    return f"${value/1_000_000:.1f}M"

def layout(df):
    return html.Div([
        html.H4("🔍 Product Analysis", className="mb-4"),
        
        # Filters
        dbc.Row([
            dbc.Col([
                html.Label("Year:", className="fw-bold"),
                dcc.Dropdown(
                    id='p3-year',
                    options=[{'label': 'All Years', 'value': 'All'}] +
                           [{'label': str(y), 'value': y} for y in sorted(df['Year'].unique(), reverse=True)],
                    value='All',
                    clearable=False
                )
            ], width=3),
            dbc.Col([
                html.Label("Quarter:", className="fw-bold"),
                dcc.Dropdown(
                    id='p3-quarter',
                    options=[
                        {'label': 'All Quarters', 'value': 'All'},
                        {'label': 'Q1', 'value': '1'},
                        {'label': 'Q2', 'value': '2'},
                        {'label': 'Q3', 'value': '3'},
                        {'label': 'Q4', 'value': '4'}
                    ],
                    value='All',
                    clearable=False
                )
            ], width=3),
            dbc.Col([
                html.Label("Flow:", className="fw-bold"),
                dcc.Dropdown(
                    id='p3-flow',
                    options=[
                        {'label': 'Exports', 'value': 'E'},
                        {'label': 'Imports', 'value': 'I'},
                        {'label': 'Re-exports', 'value': 'R'}
                    ],
                    value='E',
                    clearable=False
                )
            ], width=3),
            dbc.Col([
                html.Label("Product Classification:", className="fw-bold"),
                dcc.Dropdown(
                    id='p3-classification',
                    options=[
                        {'label': 'HS2 (2-digit)', 'value': 'HS2'},
                        {'label': 'HS4 (4-digit)', 'value': 'HS4'},
                        {'label': 'HS6 (6-digit)', 'value': 'HS6'},
                        {'label': 'HS8 (8-digit)', 'value': 'HS8'},
                        {'label': 'SITC', 'value': 'SITC'}
                    ],
                    value='HS2',
                    clearable=False
                )
            ], width=3)
        ], className="mb-4"),
        
        html.Hr(),
        
        # Table 1: Top 10 Products with Year-Quarter Performance
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(id='p3-table1-title')),
                    dbc.CardBody([
                        html.Div(id='p3-table1')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        # Table 2: Product Classification Mapping
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📋 Product Classification Mapping - All Levels")),
                    dbc.CardBody([
                        html.P("This table shows how the top 10 products map across all classification systems.",
                              className="text-muted mb-3"),
                        html.Div(id='p3-table2')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ])
    ])

def register_callbacks(app, df):
    
    @callback(
        Output('p3-table1-title', 'children'),
        Output('p3-table1', 'children'),
        Output('p3-table2', 'children'),
        Input('selected-trade-type', 'children'),
        Input('p3-year', 'value'),
        Input('p3-quarter', 'value'),
        Input('p3-flow', 'value'),
        Input('p3-classification', 'value')
    )
    def update_page3(trade_type, year, quarter, flow, classification):
        
        try:
            # Filter data
            fdf = df[df['TradeType'] == trade_type].copy()
            fdf = fdf[fdf['Flow'] == flow].copy()
            
            # Clean classification codes - remove decimals, handle non-numeric values
            def clean_code(x):
                try:
        # Try to convert to number and remove decimals
                    return str(int(float(x)))
                except (ValueError, TypeError):
        # If not a number, just return as string without decimals
                  return str(x).replace('.0', '').strip() if pd.notna(x) else ''

            fdf['HS2'] = fdf['HS2'].apply(clean_code)
            fdf['HS4'] = fdf['HS4'].apply(clean_code)
            fdf['HS6'] = fdf['HS6'].apply(clean_code)
            fdf['HS8'] = fdf['HS8'].apply(clean_code)
            fdf['SITC'] = fdf['SITC'].apply(clean_code)
            
            # Clean descriptions - remove extra whitespace
            for col in ['HS2_Description', 'HS4_Description', 'HS6_Description', 'HS8_Description', 'SITC_Description']:
                if col in fdf.columns:
                    fdf[col] = fdf[col].astype(str).str.strip()
            
            # Apply year/quarter filter for sorting
            sort_df = fdf.copy()
            if year != 'All':
                sort_df = sort_df[sort_df['Year'] == year]
            if quarter != 'All':
                sort_df = sort_df[sort_df['Quarter'] == quarter]
            
            if len(sort_df) == 0:
                return "No Data", dbc.Alert("No data available for selected filters", color="warning"), html.Div()
            
            # Get description column
            desc_col = f'{classification}_Description'
            
            # Check if classification and description columns exist
            if classification not in fdf.columns or desc_col not in fdf.columns:
                return "Error", dbc.Alert(f"Classification {classification} not found in data", color="danger"), html.Div()
            
            # Get top 10 products by selected classification
            top10_agg = sort_df.groupby([classification, desc_col])['CValue'].sum().reset_index()
            top10_agg = top10_agg.sort_values('CValue', ascending=False).head(10)
            
            if len(top10_agg) == 0:
                return "No Data", dbc.Alert("No products found for selected filters", color="warning"), html.Div()
            
            top10_codes = top10_agg[classification].tolist()
            
            # TABLE 1: Year-Quarter Performance for Top 10
            # Determine which years to display (last 3 years)
            available_years = sorted(fdf['Year'].unique(), reverse=True)[:3]
            
            if year != 'All':
                display_years = [year]
            else:
                display_years = available_years
            
            # Filter data for top 10 products and display years
            top10_df = fdf[fdf[classification].isin(top10_codes) & fdf['Year'].isin(display_years)].copy()
            
            if quarter != 'All':
                top10_df = top10_df[top10_df['Quarter'] == quarter]
            
            if len(top10_df) == 0:
                return "No Data", dbc.Alert("No data for year-quarter performance", color="warning"), html.Div()
            
            # Create Year-Quarter column
            top10_df['YearQuarter'] = top10_df['Year'].astype(str) + '-Q' + top10_df['Quarter'].astype(str)
            
            # Aggregate by classification and year-quarter
            agg_df = top10_df.groupby([classification, desc_col, 'YearQuarter'])['CValue'].sum().reset_index()
            
            # Pivot table: Rows = Products, Columns = Year-Quarters
            pivot = agg_df.pivot_table(
                index=[classification, desc_col],
                columns='YearQuarter',
                values='CValue',
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            
            # Get year-quarter columns and sort them
            yq_cols = [col for col in pivot.columns if '-Q' in str(col)]
            
            # Sort year-quarter columns chronologically
            def sort_yq(yq):
                try:
                    parts = yq.split('-Q')
                    return (int(parts[0]), int(parts[1]))
                except:
                    return (0, 0)
            
            yq_cols_sorted = sorted(yq_cols, key=sort_yq)
            
            # Calculate total for sorting products
            pivot['Total'] = pivot[yq_cols].sum(axis=1)
            pivot = pivot.sort_values('Total', ascending=False).drop('Total', axis=1)
            
            # Format values for display
            for col in yq_cols_sorted:
                pivot[f'{col}_fmt'] = pivot[col].apply(lambda x: f"${x/1_000_000:.1f}M" if x > 0 else "-")
            
            # Create table columns
            table1_cols = [
                {'name': classification, 'id': classification},
                {'name': 'Product Description', 'id': desc_col}
            ]
            
            for col in yq_cols_sorted:
                table1_cols.append({'name': col, 'id': f'{col}_fmt'})
            
            # Prepare data for display
            display_data = pivot[[classification, desc_col] + [f'{col}_fmt' for col in yq_cols_sorted]].to_dict('records')
            
            table1 = dash_table.DataTable(
                data=display_data,
                columns=table1_cols,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px',
                    'fontFamily': 'Arial',
                    'fontSize': '13px',
                    'minWidth': '100px'
                },
                style_cell_conditional=[
                    {'if': {'column_id': classification}, 'width': '120px', 'textAlign': 'center', 'fontWeight': 'bold'},
                    {'if': {'column_id': desc_col}, 'width': '300px', 'fontWeight': '500'}
                ],
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'fontSize': '14px'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
                    {'if': {'row_index': 0}, 'backgroundColor': '#fff3cd', 'fontWeight': 'bold'}
                ],
                export_format='xlsx',
                export_headers='display',
                page_size=10
            )
            
# TABLE 2: Classification Mapping
            # Get all records for top 10 products to show ALL their classification mappings
            mapping_df = fdf[fdf[classification].isin(top10_codes)].copy()
            
            # Get unique combinations across all classification levels
            mapping_cols = [
                'HS2', 'HS2_Description',
                'HS4', 'HS4_Description',
                'HS6', 'HS6_Description',
                'HS8', 'HS8_Description',
                'SITC', 'SITC_Description'
            ]
            
            # Ensure all columns exist
            available_cols = [col for col in mapping_cols if col in mapping_df.columns]
            
            # Group to get unique classification combinations for the top 10
            # Keep all unique combinations without limiting
            mapping_agg = mapping_df[available_cols].drop_duplicates()
            
            # Sort by the selected classification to group related products together
            mapping_agg = mapping_agg.sort_values(by=[classification] + [available_cols[0]])
            
            # Add rank/grouping indicator to show which products from top 10
            # Create a mapping of selected classification to see all its related codes
            mapping_agg['Rank'] = mapping_agg[classification].apply(
                lambda x: top10_codes.index(x) + 1 if x in top10_codes else 999
            )
            mapping_agg = mapping_agg.sort_values('Rank').drop('Rank', axis=1)
            
            table2_cols = []
            for i in range(0, len(available_cols), 2):
                code_col = available_cols[i]
                desc_col_map = available_cols[i+1] if i+1 < len(available_cols) else None
                
                table2_cols.append({'name': code_col, 'id': code_col})
                if desc_col_map:
                    table2_cols.append({'name': f'{code_col.replace("_", " ")} Desc', 'id': desc_col_map})
            
            # Highlight rows that match top 10 in selected classification
            style_conditions = [
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}
            ]
            
            # Add highlighting for top 10 products
            for idx, code in enumerate(top10_codes):
                style_conditions.append({
                    'if': {
                        'filter_query': f'{{{classification}}} = "{code}"',
                    },
                    'backgroundColor': '#fff3cd' if idx == 0 else '#e7f3ff',
                    'fontWeight': 'bold' if idx < 3 else 'normal'
                })
            
            table2 = dash_table.DataTable(
                data=mapping_agg.to_dict('records'),
                columns=table2_cols,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontFamily': 'Arial',
                    'fontSize': '12px',
                    'minWidth': '90px',
                    'maxWidth': '250px',
                    'whiteSpace': 'normal'
                },
                style_cell_conditional=[
                    {'if': {'column_id': col}, 'width': '100px', 'textAlign': 'center', 'fontWeight': 'bold'} 
                    for col in ['HS2', 'HS4', 'HS6', 'HS8', 'SITC']
                ],
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'fontSize': '13px'
                },
                style_data_conditional=style_conditions,
                page_size=50,  # Increased to show more mappings
                export_format='xlsx',
                export_headers='display',
                filter_action='native',
                sort_action='native'
            )
            
            # Create title
            flow_names = {'E': 'Exports', 'I': 'Imports', 'R': 'Re-exports'}
            flow_name = flow_names.get(flow, flow)
            
            year_text = f"{year}" if year != 'All' else "All Years"
            quarter_text = f"Q{quarter}" if quarter != 'All' else "All Quarters"
            
            table1_title = f"Top 10 {flow_name} Products by {classification} - {year_text}, {quarter_text}"
            
            return table1_title, table1, table2
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return "Error", dbc.Alert(error_msg, color="danger"), html.Div()