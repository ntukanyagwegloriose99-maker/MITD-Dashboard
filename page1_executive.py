from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def format_value(value):
    """Format large numbers into millions"""
    if pd.isna(value):
        return "$0.0M"
    millions = value / 1_000_000
    return f"${millions:.1f}M"

def create_kpi_card(title, value, subtitle=None, color="primary"):
    """Create a KPI card component"""
    card_content = [
        html.H6(title, className="text-muted mb-2", style={'fontSize': '0.9rem'}),
        html.H3(format_value(value), className=f"text-{color} mb-0", style={'fontSize': '1.8rem'}),
    ]
    
    if subtitle:
        card_content.append(
            html.Small(subtitle, className="text-muted")
        )
    
    return dbc.Card(dbc.CardBody(card_content), className="shadow-sm h-100")

def layout(df):
    """Page 1 Layout - Executive Overview"""
    
    if df.empty:
        return dbc.Alert("No data available. Please check your data file.", color="danger")
    
    return html.Div([
        # Filters Section
        dbc.Row([
            dbc.Col([
                html.Label("Year:", className="fw-bold"),
                dcc.Dropdown(
                    id='p1-filter-year',
                    options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique(), reverse=True)],
                    value=df['Year'].max(),
                    clearable=False
                )
            ], width=4),
            dbc.Col([
                html.Label("Quarter:", className="fw-bold"),
                dcc.Dropdown(
                    id='p1-filter-quarter',
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
            ], width=4),
            dbc.Col([
                html.Label("Flow:", className="fw-bold"),
                dcc.Dropdown(
                    id='p1-filter-flow',
                    options=[
                        {'label': 'All Flows', 'value': 'All'},
                        {'label': 'Exports', 'value': 'E'},
                        {'label': 'Imports', 'value': 'I'},
                        {'label': 'Re-exports', 'value': 'R'}
                    ],
                    value='All',
                    clearable=False
                )
            ], width=4),
        ], className="mb-4"),
        
        html.Hr(),
        
        # 1. KPI Cards
        html.H5("📊 Key Performance Indicators", className="mb-3"),
        dbc.Row([
            dbc.Col(html.Div(id='p1-kpi-total-trade'), width=2),
            dbc.Col(html.Div(id='p1-kpi-exports'), width=2),
            dbc.Col(html.Div(id='p1-kpi-imports'), width=2),
            dbc.Col(html.Div(id='p1-kpi-reexports'), width=2),
            dbc.Col(html.Div(id='p1-kpi-balance'), width=2),
            dbc.Col(html.Div(id='p1-kpi-growth'), width=2),
        ], className="mb-4"),
        
        html.Hr(),
        
        # 2. 3-Year Quarterly Performance Chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Quarterly Performance - Last 3 Years (US$ Million)", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='p1-quarterly-performance', style={'height': '500px'})
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        # 3. Downloadable Annex Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📋 Annex Table - Quarterly Trade Data", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id='p1-annex-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        # Top 10 Trading Partners (Conditional based on flow)
        html.Div(id='p1-top-partners-section'),
        
        # NEW: Conditional Insights Section
        html.Div(id='p1-conditional-insights'),
        
        # 4. Trend Chart (Imports, Exports, Re-exports)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Trade Flow Trends - Selected Period", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='p1-trend-chart', style={'height': '400px'})
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        # 5. Pie Chart - Distribution
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Trade Flow Distribution", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='p1-pie-chart', style={'height': '400px'})
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
    ])

def register_callbacks(app, df):
    """Register callbacks for Page 1"""
    
    @callback(
        Output('p1-kpi-total-trade', 'children'),
        Output('p1-kpi-exports', 'children'),
        Output('p1-kpi-imports', 'children'),
        Output('p1-kpi-reexports', 'children'),
        Output('p1-kpi-balance', 'children'),
        Output('p1-kpi-growth', 'children'),
        Output('p1-quarterly-performance', 'figure'),
        Output('p1-annex-table', 'children'),
        Output('p1-top-partners-section', 'children'),
        Output('p1-conditional-insights', 'children'),
        Output('p1-trend-chart', 'figure'),
        Output('p1-pie-chart', 'figure'),
        Input('selected-trade-type', 'children'),
        Input('p1-filter-year', 'value'),
        Input('p1-filter-quarter', 'value'),
        Input('p1-filter-flow', 'value')
    )
    def update_page1(trade_type, selected_year, selected_quarter, selected_flow):
        """Update all Page 1 components"""
        
        if df.empty:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            empty_kpi = dbc.Alert("No data", color="secondary")
            return [empty_kpi]*6 + [empty_fig]*3 + [html.Div()]*2 + [empty_fig]
        
        # Filter by trade type
        filtered_df = df[df['TradeType'] == trade_type].copy()
        
        # Filter by year for KPIs
        year_df = filtered_df[filtered_df['Year'] == selected_year].copy()
        
        # Filter by quarter for KPIs
        if selected_quarter != 'All':
            quarter_df = year_df[year_df['Quarter'] == selected_quarter].copy()
        else:
            quarter_df = year_df.copy()
        
        # ========== 1. KPI CALCULATIONS ==========
        if selected_flow == 'All':
            exports = quarter_df[quarter_df['Flow'] == 'E']['CValue'].sum()
            imports = quarter_df[quarter_df['Flow'] == 'I']['CValue'].sum()
            reexports = quarter_df[quarter_df['Flow'] == 'R']['CValue'].sum()
        elif selected_flow == 'E':
            exports = quarter_df[quarter_df['Flow'] == 'E']['CValue'].sum()
            imports = 0
            reexports = 0
        elif selected_flow == 'I':
            exports = 0
            imports = quarter_df[quarter_df['Flow'] == 'I']['CValue'].sum()
            reexports = 0
        elif selected_flow == 'R':
            exports = 0
            imports = 0
            reexports = quarter_df[quarter_df['Flow'] == 'R']['CValue'].sum()
        
        total_trade = exports + imports + reexports
        balance = exports + reexports - imports
        
        # Growth Rate (YoY)
        prev_year = selected_year - 1
        if prev_year in filtered_df['Year'].values:
            prev_year_df = filtered_df[filtered_df['Year'] == prev_year].copy()
            if selected_quarter != 'All':
                prev_year_df = prev_year_df[prev_year_df['Quarter'] == selected_quarter]
            if selected_flow != 'All':
                prev_year_df = prev_year_df[prev_year_df['Flow'] == selected_flow]
            
            prev_total = prev_year_df['CValue'].sum()
            growth_rate = ((total_trade - prev_total) / prev_total * 100) if prev_total > 0 else 0
            growth_text = f"{growth_rate:+.1f}% YoY"
            growth_color = "success" if growth_rate >= 0 else "danger"
        else:
            growth_text = "N/A"
            growth_rate = 0
            growth_color = "secondary"
        
        # KPI Cards
        kpi_total = create_kpi_card("Total Trade", total_trade, "Sum of all flows", "primary")
        kpi_exports = create_kpi_card("Total Exports", exports, color="success")
        kpi_imports = create_kpi_card("Total Imports", imports, color="danger")
        kpi_reexports = create_kpi_card("Total Re-exports", reexports, color="info")
        
        balance_color = "success" if balance >= 0 else "danger"
        balance_status = "Surplus" if balance >= 0 else "Deficit"
        kpi_balance = create_kpi_card("Trade Balance", balance, balance_status, balance_color)
        
        kpi_growth = dbc.Card(dbc.CardBody([
            html.H6("Growth Rate", className="text-muted mb-2", style={'fontSize': '0.9rem'}),
            html.H3(growth_text, className=f"text-{growth_color} mb-0", style={'fontSize': '1.8rem'}),
            html.Small("Year-on-Year", className="text-muted")
        ]), className="shadow-sm h-100")
        
        # ========== 2. QUARTERLY PERFORMANCE (Last 3 Years) ==========
        available_years = sorted(filtered_df['Year'].unique(), reverse=True)[:3]
        three_year_df = filtered_df[filtered_df['Year'].isin(available_years)].copy()
        
        if selected_quarter != 'All':
            three_year_df = three_year_df[three_year_df['Quarter'] == selected_quarter].copy()
        
        if selected_flow != 'All':
            three_year_df = three_year_df[three_year_df['Flow'] == selected_flow].copy()
        
        quarterly_agg = three_year_df.groupby(['Year', 'Quarter', 'Flow'])['CValue'].sum().reset_index()
        quarterly_agg['CValue_M'] = quarterly_agg['CValue'] / 1_000_000
        quarterly_agg['YearQuarter'] = quarterly_agg['Year'].astype(str) + '-Q' + quarterly_agg['Quarter'].astype(str)
        quarterly_agg = quarterly_agg.sort_values(['Year', 'Quarter'])
        
        all_year_quarters = quarterly_agg['YearQuarter'].unique()
        
        exports_data = quarterly_agg[quarterly_agg['Flow'] == 'E'].copy()
        imports_data = quarterly_agg[quarterly_agg['Flow'] == 'I'].copy()
        reexports_data = quarterly_agg[quarterly_agg['Flow'] == 'R'].copy()
        
        balance_df = quarterly_agg.groupby(['YearQuarter']).apply(
            lambda x: (x[x['Flow'].isin(['E', 'R'])]['CValue'].sum() - x[x['Flow'] == 'I']['CValue'].sum()) / 1_000_000,
            include_groups=False
        ).reset_index(name='Balance_M')
        
        fig_quarterly = make_subplots(specs=[[{"secondary_y": True}]])
        
        if len(exports_data) > 0:
            fig_quarterly.add_trace(
                go.Bar(name='Exports', x=exports_data['YearQuarter'], y=exports_data['CValue_M'],
                       marker_color='#28a745', text=exports_data['CValue_M'].apply(lambda x: f"${x:.1f}M"),
                       textposition='outside'),
                secondary_y=False
            )
        
        if len(imports_data) > 0:
            fig_quarterly.add_trace(
                go.Bar(name='Imports', x=imports_data['YearQuarter'], y=imports_data['CValue_M'],
                       marker_color='#dc3545', text=imports_data['CValue_M'].apply(lambda x: f"${x:.1f}M"),
                       textposition='outside'),
                secondary_y=False
            )
        
        if len(reexports_data) > 0:
            fig_quarterly.add_trace(
                go.Bar(name='Re-exports', x=reexports_data['YearQuarter'], y=reexports_data['CValue_M'],
                       marker_color='#17a2b8', text=reexports_data['CValue_M'].apply(lambda x: f"${x:.1f}M"),
                       textposition='outside'),
                secondary_y=False
            )
        
        if selected_flow == 'All' and len(balance_df) > 0:
            fig_quarterly.add_trace(
                go.Scatter(name='Trade Balance', x=balance_df['YearQuarter'], y=balance_df['Balance_M'],
                          mode='lines+markers', line=dict(color='#ffc107', width=3), marker=dict(size=8),
                          text=balance_df['Balance_M'].apply(lambda x: f"${x:.1f}M"), textposition='top center'),
                secondary_y=True
            )
        
        fig_quarterly.update_xaxes(title_text="Year-Quarter", categoryorder='array', categoryarray=all_year_quarters)
        fig_quarterly.update_yaxes(title_text="Trade Value (US$ Million)", secondary_y=False)
        fig_quarterly.update_yaxes(title_text="Trade Balance (US$ Million)", secondary_y=True)
        fig_quarterly.update_layout(barmode='group', height=500, hovermode='x unified',
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        
        # ========== 3. ANNEX TABLE ==========
        annex_data = quarterly_agg.pivot_table(
            index=['Year', 'Quarter'], columns='Flow', values='CValue_M', fill_value=0
        ).reset_index()
        
        annex_data.columns.name = None
        if 'E' in annex_data.columns:
            annex_data.rename(columns={'E': 'Exports'}, inplace=True)
        else:
            annex_data['Exports'] = 0
        if 'I' in annex_data.columns:
            annex_data.rename(columns={'I': 'Imports'}, inplace=True)
        else:
            annex_data['Imports'] = 0
        if 'R' in annex_data.columns:
            annex_data.rename(columns={'R': 'Re-exports'}, inplace=True)
        else:
            annex_data['Re-exports'] = 0
        
        annex_data['Trade Balance'] = annex_data['Exports'] + annex_data['Re-exports'] - annex_data['Imports']
        
        for col in ['Exports', 'Imports', 'Re-exports', 'Trade Balance']:
            annex_data[f'{col}_formatted'] = annex_data[col].apply(lambda x: f"{x:.1f}")
        
        annex_table = dash_table.DataTable(
            data=annex_data.to_dict('records'),
            columns=[
                {'name': 'Year', 'id': 'Year'},
                {'name': 'Quarter', 'id': 'Quarter'},
                {'name': 'Exports (US$ M)', 'id': 'Exports_formatted'},
                {'name': 'Imports (US$ M)', 'id': 'Imports_formatted'},
                {'name': 'Re-exports (US$ M)', 'id': 'Re-exports_formatted'},
                {'name': 'Trade Balance (US$ M)', 'id': 'Trade Balance_formatted'},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '10px', 'fontFamily': 'Arial'},
            style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}],
            export_format='xlsx', export_headers='display', page_size=20
        )
        
        # ========== TOP 10 TRADING PARTNERS ==========
        top_partners_section = html.Div()
        
        if selected_flow != 'All':
            flow_df = quarter_df[quarter_df['Flow'] == selected_flow].copy()
            partners_agg = flow_df.groupby('Partner_Country')['CValue'].sum().reset_index()
            partners_agg = partners_agg.sort_values('CValue', ascending=False).head(10)
            partners_agg['CValue_M'] = partners_agg['CValue'] / 1_000_000
            partners_agg['CValue_formatted'] = partners_agg['CValue_M'].apply(lambda x: f"${x:.1f}M")
            partners_agg.insert(0, 'Rank', range(1, len(partners_agg) + 1))
            
            if selected_flow == 'E':
                table_title = "🌍 Top 10 Export Destinations"
                country_label = "Destination Country"
            elif selected_flow == 'I':
                table_title = "🌍 Top 10 Import Origins"
                country_label = "Origin Country"
            elif selected_flow == 'R':
                table_title = "🌍 Top 10 Re-export Destinations"
                country_label = "Destination Country"
            
            top_partners_section = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5(table_title, className="mb-0")),
                        dbc.CardBody([
                            dash_table.DataTable(
                                data=partners_agg.to_dict('records'),
                                columns=[
                                    {'name': 'Rank', 'id': 'Rank'},
                                    {'name': country_label, 'id': 'Partner_Country'},
                                    {'name': 'Trade Value (US$ M)', 'id': 'CValue_formatted'},
                                ],
                                style_table={'overflowX': 'auto'},
                                style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'Arial'},
                                style_cell_conditional=[{'if': {'column_id': 'Rank'}, 'width': '80px', 'textAlign': 'center'}],
                                style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold', 'textAlign': 'center'},
                                style_data_conditional=[
                                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
                                    {'if': {'row_index': 0}, 'backgroundColor': '#fff3cd', 'fontWeight': 'bold'}
                                ],
                                page_size=10
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ], className="mb-4")
        
        # ========== NEW: CONDITIONAL INSIGHTS ==========
        conditional_insights = html.Div()
        
        if selected_flow != 'All':
            # Get top 5 countries based on CURRENT SELECTION (same as Top 10 table)
            flow_df_for_top5 = quarter_df[quarter_df['Flow'] == selected_flow].copy()
            top5_countries = flow_df_for_top5.groupby('Partner_Country')['CValue'].sum().nlargest(5).index.tolist()
            
            # TOP 5 COUNTRIES QUARTERLY PERFORMANCE (3 YEARS)
            three_year_flow_df = filtered_df[filtered_df['Year'].isin(available_years)].copy()
            three_year_flow_df = three_year_flow_df[three_year_flow_df['Flow'] == selected_flow].copy()
            
            if selected_quarter != 'All':
                three_year_flow_df = three_year_flow_df[three_year_flow_df['Quarter'] == selected_quarter].copy()
            
            # Separate top 5 and rest
            three_year_flow_df['Country_Group'] = three_year_flow_df['Partner_Country'].apply(
                lambda x: x if x in top5_countries else 'Rest of World'
            )
            
            country_quarterly = three_year_flow_df.groupby(['Year', 'Quarter', 'Country_Group'])['CValue'].sum().reset_index()
            country_quarterly['CValue_M'] = country_quarterly['CValue'] / 1_000_000
            country_quarterly['YearQuarter'] = country_quarterly['Year'].astype(str) + '-Q' + country_quarterly['Quarter'].astype(str)
            country_quarterly = country_quarterly.sort_values(['Year', 'Quarter'])
            
            # Create chart
            fig_top5 = go.Figure()
            
            all_countries = top5_countries + ['Rest of World']
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            for idx, country in enumerate(all_countries):
                country_data = country_quarterly[country_quarterly['Country_Group'] == country]
                fig_top5.add_trace(go.Bar(
                    name=country,
                    x=country_data['YearQuarter'],
                    y=country_data['CValue_M'],
                    marker_color=colors[idx % len(colors)]
                ))
            
            fig_top5.update_layout(
                barmode='group',
                height=500,
                xaxis_title="Year-Quarter",
                yaxis_title="Trade Value (US$ Million)",
                legend_title="Country",
                hovermode='x unified'
            )
            
            # Annex table for top 5
            top5_annex = country_quarterly.pivot_table(
                index=['Year', 'Quarter'],
                columns='Country_Group',
                values='CValue_M',
                fill_value=0
            ).reset_index()
            
            # Format columns
            for col in top5_annex.columns:
                if col not in ['Year', 'Quarter']:
                    top5_annex[f'{col}_formatted'] = top5_annex[col].apply(lambda x: f"{x:.1f}")
            
            top5_table_columns = [{'name': 'Year', 'id': 'Year'}, {'name': 'Quarter', 'id': 'Quarter'}]
            for country in all_countries:
                if f'{country}_formatted' in top5_annex.columns:
                    top5_table_columns.append({'name': f'{country} (US$ M)', 'id': f'{country}_formatted'})
            
            top5_annex_table = dash_table.DataTable(
                data=top5_annex.to_dict('records'),
                columns=top5_table_columns,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '10px', 'fontFamily': 'Arial'},
                style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}],
                export_format='xlsx',
                export_headers='display'
            )
            
            flow_name = {'E': 'Exports', 'I': 'Imports', 'R': 'Re-exports'}[selected_flow]
            
            conditional_insights = html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5(f"Top 5 Countries - {flow_name} Quarterly Performance (Last 3 Years)", className="mb-0")),
                            dbc.CardBody([dcc.Graph(figure=fig_top5)])
                        ], className="shadow-sm")
                    ], width=12)
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5(f"📋 Annex Table - Top 5 Countries {flow_name}", className="mb-0")),
                            dbc.CardBody([top5_annex_table])
                        ], className="shadow-sm")
                    ], width=12)
                ], className="mb-4")
            ])
        
        else:
            # ANNUAL PERFORMANCE OF ALL FLOWS (ALL YEARS)
            annual_df = filtered_df.groupby(['Year', 'Flow'])['CValue'].sum().reset_index()
            annual_df['CValue_M'] = annual_df['CValue'] / 1_000_000
            
            # Calculate annual balance
            annual_balance = annual_df.pivot_table(
                index='Year',
                columns='Flow',
                values='CValue',
                fill_value=0
            )
            annual_balance['Balance'] = (
                annual_balance.get('E', 0) + 
                annual_balance.get('R', 0) - 
                annual_balance.get('I', 0)
            ) / 1_000_000
            annual_balance = annual_balance.reset_index()[['Year', 'Balance']]
            
            fig_annual = make_subplots(specs=[[{"secondary_y": True}]])
            
            exports_annual = annual_df[annual_df['Flow'] == 'E']
            imports_annual = annual_df[annual_df['Flow'] == 'I']
            reexports_annual = annual_df[annual_df['Flow'] == 'R']
            
            if len(exports_annual) > 0:
                fig_annual.add_trace(
                    go.Bar(name='Exports', x=exports_annual['Year'], y=exports_annual['CValue_M'],
                          marker_color='#28a745'),
                    secondary_y=False
                )
            
            if len(imports_annual) > 0:
                fig_annual.add_trace(
                    go.Bar(name='Imports', x=imports_annual['Year'], y=imports_annual['CValue_M'],
                          marker_color='#dc3545'),
                    secondary_y=False
                )
            
            if len(reexports_annual) > 0:
                fig_annual.add_trace(
                    go.Bar(name='Re-exports', x=reexports_annual['Year'], y=reexports_annual['CValue_M'],
                          marker_color='#17a2b8'),
                    secondary_y=False
                )
            
            fig_annual.add_trace(
                go.Scatter(name='Trade Balance', x=annual_balance['Year'], y=annual_balance['Balance'],
                          mode='lines+markers', line=dict(color='#ffc107', width=3), marker=dict(size=10)),
                secondary_y=True
            )
            
            fig_annual.update_xaxes(title_text="Year")
            fig_annual.update_yaxes(title_text="Trade Value (US$ Million)", secondary_y=False)
            fig_annual.update_yaxes(title_text="Trade Balance (US$ Million)", secondary_y=True)
            fig_annual.update_layout(
                barmode='group',
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            # Annual Annex Table
            annual_annex = annual_df.pivot_table(
                index='Year',
                columns='Flow',
                values='CValue_M',
                fill_value=0
            ).reset_index()
            
            annual_annex.columns.name = None
            if 'E' in annual_annex.columns:
                annual_annex['Exports'] = annual_annex['E']
            else:
                annual_annex['Exports'] = 0
            if 'I' in annual_annex.columns:
                annual_annex['Imports'] = annual_annex['I']
            else:
                annual_annex['Imports'] = 0
            if 'R' in annual_annex.columns:
                annual_annex['Re-exports'] = annual_annex['R']
            else:
                annual_annex['Re-exports'] = 0
            
            annual_annex['Trade Balance'] = annual_annex['Exports'] + annual_annex['Re-exports'] - annual_annex['Imports']
            
            for col in ['Exports', 'Imports', 'Re-exports', 'Trade Balance']:
                annual_annex[f'{col}_fmt'] = annual_annex[col].apply(lambda x: f"{x:.1f}")
            
            annual_table = dash_table.DataTable(
                data=annual_annex.to_dict('records'),
                columns=[
                    {'name': 'Year', 'id': 'Year'},
                    {'name': 'Exports (US$ M)', 'id': 'Exports_fmt'},
                    {'name': 'Imports (US$ M)', 'id': 'Imports_fmt'},
                    {'name': 'Re-exports (US$ M)', 'id': 'Re-exports_fmt'},
                    {'name': 'Trade Balance (US$ M)', 'id': 'Trade Balance_fmt'},
                ],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '10px', 'fontFamily': 'Arial'},
                style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'}],
                export_format='xlsx',
                export_headers='display'
            )
            
            conditional_insights = html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Annual Performance - All Flows (All Years)", className="mb-0")),
                            dbc.CardBody([dcc.Graph(figure=fig_annual)])
                        ], className="shadow-sm")
                    ], width=12)
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("📋 Annual Annex Table", className="mb-0")),
                            dbc.CardBody([annual_table])
                        ], className="shadow-sm")
                    ], width=12)
                ], className="mb-4")
            ])
        
      # ========== 4. TREND CHART ==========
        if selected_flow != 'All':
            trend_df = quarter_df[quarter_df['Flow'] == selected_flow].copy()
        else:
            trend_df = quarter_df.copy()
        
        trend_data = trend_df.groupby(['Quarter', 'Flow'])['CValue'].sum().reset_index()
        trend_data['CValue_M'] = trend_data['CValue'] / 1_000_000
        flow_names = {'E': 'Exports', 'I': 'Imports', 'R': 'Re-exports'}
        trend_data['Flow_Name'] = trend_data['Flow'].map(flow_names)
        
        fig_trend = px.line(
            trend_data, x='Quarter', y='CValue_M', color='Flow_Name', markers=True, title='',
            color_discrete_map={'Exports': '#28a745', 'Imports': '#dc3545', 'Re-exports': '#17a2b8'}
        )
        fig_trend.update_layout(
            xaxis_title="Quarter", 
            yaxis_title="Trade Value (US$ Million)",
            legend_title="Flow", 
            height=400
        )
        
        # ========== 5. PIE CHART ==========
        if selected_flow != 'All':
            pie_df = quarter_df[quarter_df['Flow'] == selected_flow].copy()
        else:
            pie_df = quarter_df.copy()
        
        pie_data = pie_df.groupby('Flow')['CValue'].sum().reset_index()
        pie_data['Flow_Name'] = pie_data['Flow'].map(flow_names)
        
        fig_pie = px.pie(
            pie_data, 
            values='CValue', 
            names='Flow_Name', 
            title='',
            color='Flow_Name',
            color_discrete_map={'Exports': '#28a745', 'Imports': '#dc3545', 'Re-exports': '#17a2b8'},
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=400)
        
        return (kpi_total, kpi_exports, kpi_imports, kpi_reexports, kpi_balance, kpi_growth,
                fig_quarterly, annex_table, top_partners_section, conditional_insights, fig_trend, fig_pie)