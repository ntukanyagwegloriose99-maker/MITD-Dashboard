from dash import html, dcc, callback, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pages.country_mapping import *

def format_value(value):
    if pd.isna(value): return "$0.0M"
    return f"${value/1_000_000:.1f}M"

def layout(df):
    return html.Div([
        # Partner Type Radio Buttons
        html.H5("Select Partner Type:", className="mb-3"),
        dbc.RadioItems(
            id='p2-partner-type',
            options=[
                {'label': ' Trade by Continent', 'value': 'continent'},
                {'label': ' Regional Blocks', 'value': 'regional'}
            ],
            value='continent',
            inline=True,
            className="mb-4"
        ),
        
        # Filters Row
        dbc.Row([
            dbc.Col([
                html.Label("Year:", className="fw-bold"),
                dcc.Dropdown(id='p2-year', options=[{'label': 'All Years', 'value': 'All'}] + 
                    [{'label': str(y), 'value': y} for y in sorted(df['Year'].unique(), reverse=True)],
                    value='All', clearable=False)
            ], width=3),
            dbc.Col([
                html.Label("Quarter:", className="fw-bold"),
                dcc.Dropdown(id='p2-quarter', options=[
                    {'label': 'All Quarters', 'value': 'All'},
                    {'label': 'Q1', 'value': '1'}, {'label': 'Q2', 'value': '2'},
                    {'label': 'Q3', 'value': '3'}, {'label': 'Q4', 'value': '4'}
                ], value='All', clearable=False)
            ], width=3),
            dbc.Col([
                html.Label("Flow:", className="fw-bold"),
                dcc.Dropdown(id='p2-flow', options=[
                    {'label': 'All Flows', 'value': 'All'},
                    {'label': 'Exports', 'value': 'E'},
                    {'label': 'Imports', 'value': 'I'},
                    {'label': 'Re-exports', 'value': 'R'}
                ], value='All', clearable=False)
            ], width=3),
            dbc.Col(html.Div(id='p2-conditional-filter'), width=3)
        ], className="mb-4"),
        
        html.Hr(),
        
        # Hidden stores
        dcc.Store(id='p2-cont-store', data='All'),
        dcc.Store(id='p2-reg-store', data='COMESA'),
        
        # Map Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5(id='p2-map-title')),
                    dbc.CardBody([dcc.Graph(id='p2-map', style={'height': '500px'})])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
        
        # Chart and Table Section
        html.Div(id='p2-charts-tables')
    ])

def register_callbacks(app, df):
    df['Continent'] = df['Partner_Country'].apply(get_continent)
    
    # Show conditional filter
    @callback(
        Output('p2-conditional-filter', 'children'),
        Input('p2-partner-type', 'value')
    )
    def show_conditional_filter(ptype):
        if ptype == 'continent':
            return html.Div([
                html.Label("Continent:", className="fw-bold"),
                dcc.Dropdown(id='p2-cont-dd', options=[
                    {'label': 'All Continents', 'value': 'All'},
                    {'label': 'AFRICA', 'value': 'AFRICA'},
                    {'label': 'AMERICA', 'value': 'AMERICA'},
                    {'label': 'ASIA', 'value': 'ASIA'},
                    {'label': 'EUROPE', 'value': 'EUROPE'},
                    {'label': 'OCEANIA', 'value': 'OCEANIA'}
                ], value='All', clearable=False)
            ])
        else:
            return html.Div([
                html.Label("Regional Block:", className="fw-bold"),
                dcc.Dropdown(id='p2-reg-dd', options=[
                    {'label': 'CEPGL', 'value': 'CEPGL'},
                    {'label': 'COMESA', 'value': 'COMESA'},
                    {'label': 'COMMONWEALTH', 'value': 'COMMONWEALTH'},
                    {'label': 'ECOWAS', 'value': 'ECOWAS'},
                    {'label': 'SADC', 'value': 'SADC'},
                    {'label': 'EU', 'value': 'EU'},
                    {'label': 'EAC', 'value': 'EAC'},
                    {'label': 'EAC Partner States', 'value': 'EAC_PARTNERS'}
                ], value='COMESA', clearable=False)
            ])
    
    # Store updates
    @callback(Output('p2-cont-store', 'data'), Input('p2-cont-dd', 'value'), prevent_initial_call=True)
    def store_cont(v): return v if v else 'All'
    
    @callback(Output('p2-reg-store', 'data'), Input('p2-reg-dd', 'value'), prevent_initial_call=True)
    def store_reg(v): return v if v else 'COMESA'
    
    # Main update
    @callback(
        Output('p2-map-title', 'children'),
        Output('p2-map', 'figure'),
        Output('p2-charts-tables', 'children'),
        Input('selected-trade-type', 'children'),
        Input('p2-partner-type', 'value'),
        Input('p2-year', 'value'),
        Input('p2-quarter', 'value'),
        Input('p2-flow', 'value'),
        Input('p2-cont-store', 'data'),
        Input('p2-reg-store', 'data')
    )
    def update_all(ttype, ptype, yr, qtr, flw, cont, reg):
        # Filter
        fdf = df[df['TradeType'] == ttype].copy()
        if yr != 'All': fdf = fdf[fdf['Year'] == yr]
        if qtr != 'All': fdf = fdf[fdf['Quarter'] == qtr]
        if flw != 'All': fdf = fdf[fdf['Flow'] == flw]
        
        # Geographic filter
        if ptype == 'continent':
            if cont != 'All': fdf = fdf[fdf['Continent'] == cont]
            title = f"Trade Map - {cont if cont != 'All' else 'All Continents'}"
        else:
            if reg == 'EAC': fdf = fdf[fdf['Partner_Country'].isin(EAC_COUNTRIES)]
            elif reg == 'EAC_PARTNERS': fdf = fdf[fdf['Partner_Country'].isin(EAC_PARTNER_STATES)]
            elif reg == 'COMESA': fdf = fdf[fdf['Partner_Country'].isin(COMESA_COUNTRIES)]
            elif reg == 'SADC': fdf = fdf[fdf['Partner_Country'].isin(SADC_COUNTRIES)]
            elif reg == 'ECOWAS': fdf = fdf[fdf['Partner_Country'].isin(ECOWAS_COUNTRIES)]
            elif reg == 'CEPGL': fdf = fdf[fdf['Partner_Country'].isin(CEPGL_COUNTRIES)]
            elif reg == 'COMMONWEALTH': fdf = fdf[fdf['Partner_Country'].isin(COMMONWEALTH_COUNTRIES)]
            elif reg == 'EU': fdf = fdf[fdf['Partner_Country'].isin(EU_COUNTRIES)]
            title = f"Trade Map - {reg.replace('_', ' ')}"
        
        if len(fdf) == 0:
            empty = go.Figure()
            empty.add_annotation(text="No data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return title, empty, dbc.Alert("No data available", color="warning")
        
        # Map
        mdata = fdf.groupby('Partner_Country')['CValue'].sum().reset_index()
        fig_map = px.choropleth(mdata, locations='Partner_Country', locationmode='country names',
                               color='CValue', color_continuous_scale='Viridis')
        fig_map.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=500)
        
        # Charts based on selection
        if ptype == 'regional' and reg == 'EAC':
            charts = build_eac_line_chart(fdf)
        elif ptype == 'regional' and reg == 'EAC_PARTNERS':
            charts = build_eac_partners_combo(fdf, flw)
        else:
            charts = build_standard_chart(fdf)
        
        return title, fig_map, charts

def build_standard_chart(fdf):
    """Clustered bar (flows) + line (total trade) for last 3 years"""
    years = sorted(fdf['Year'].unique(), reverse=True)[:3]
    three_df = fdf[fdf['Year'].isin(years)].copy()
    
    agg = three_df.groupby(['Year', 'Quarter', 'Flow'])['CValue'].sum().reset_index()
    agg['CValue_M'] = agg['CValue'] / 1_000_000
    agg['YQ'] = agg['Year'].astype(str) + '-Q' + agg['Quarter'].astype(str)
    agg = agg.sort_values(['Year', 'Quarter'])
    
    total = agg.groupby('YQ')['CValue_M'].sum().reset_index()
    total.rename(columns={'CValue_M': 'Total'}, inplace=True)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    for fc, fn, clr in [('E','Exports','#28a745'), ('I','Imports','#dc3545'), ('R','Re-exports','#17a2b8')]:
        fd = agg[agg['Flow']==fc]
        if len(fd)>0:
            fig.add_trace(go.Bar(name=fn, x=fd['YQ'], y=fd['CValue_M'], marker_color=clr), secondary_y=False)
    
    fig.add_trace(go.Scatter(name='Total Trade', x=total['YQ'], y=total['Total'],
                            mode='lines+markers', line=dict(color='#ffc107', width=3)), secondary_y=True)
    
    fig.update_xaxes(title_text="Year-Quarter")
    fig.update_yaxes(title_text="Flow Value (US$ M)", secondary_y=False)
    fig.update_yaxes(title_text="Total Trade (US$ M)", secondary_y=True)
    fig.update_layout(barmode='group', height=500)
    
    # Annex table
    annex = agg.pivot_table(index=['Year','Quarter'], columns='Flow', values='CValue_M', fill_value=0).reset_index()
    annex.columns.name = None
    for c in ['E','I','R']:
        if c in annex.columns:
            annex[f'{c}_f'] = annex[c].apply(lambda x: f"{x:.1f}")
    
    tbl = dash_table.DataTable(
        data=annex.to_dict('records'),
        columns=[{'name':'Year','id':'Year'},{'name':'Quarter','id':'Quarter'},
                {'name':'Exports(M)','id':'E_f'},{'name':'Imports(M)','id':'I_f'},{'name':'Re-exports(M)','id':'R_f'}],
        style_cell={'textAlign':'center','padding':'10px'},
        style_header={'backgroundColor':'#2c3e50','color':'white','fontWeight':'bold'},
        export_format='xlsx'
    )
    
    return html.Div([
        dbc.Row([dbc.Col([dbc.Card([dbc.CardHeader(html.H5("Performance - Last 3 Years")),
                                   dbc.CardBody([dcc.Graph(figure=fig)])],className="shadow-sm")],width=12)],className="mb-4"),
        dbc.Row([dbc.Col([dbc.Card([dbc.CardHeader(html.H5("📋 Annex Table")),
                                   dbc.CardBody([tbl])],className="shadow-sm")],width=12)])
    ])

def build_eac_line_chart(fdf):
    """EAC: Line chart with flows"""
    agg = fdf.groupby(['Year','Quarter','Flow'])['CValue'].sum().reset_index()
    agg['CValue_M'] = agg['CValue']/1_000_000
    agg['YQ'] = agg['Year'].astype(str)+'-Q'+agg['Quarter'].astype(str)
    agg = agg.sort_values(['Year','Quarter'])
    
    fig = px.line(agg, x='YQ', y='CValue_M', color='Flow', markers=True,
                 color_discrete_map={'E':'#28a745','I':'#dc3545','R':'#17a2b8'})
    fig.update_layout(height=500, xaxis_title="Year-Quarter", yaxis_title="Trade Value (US$ M)")
    
    annex = agg.pivot_table(index=['Year','Quarter'], columns='Flow', values='CValue_M', fill_value=0).reset_index()
    annex.columns.name = None
    for c in ['E','I','R']:
        if c in annex.columns: annex[f'{c}_f'] = annex[c].apply(lambda x: f"{x:.1f}")
    
    tbl = dash_table.DataTable(
        data=annex.to_dict('records'),
        columns=[{'name':'Year','id':'Year'},{'name':'Quarter','id':'Quarter'},
                {'name':'Exports(M)','id':'E_f'},{'name':'Imports(M)','id':'I_f'},{'name':'Re-exports(M)','id':'R_f'}],
        style_cell={'textAlign':'center','padding':'10px'},
        style_header={'backgroundColor':'#2c3e50','color':'white','fontWeight':'bold'},
        export_format='xlsx'
    )
    
    return html.Div([
        dbc.Row([dbc.Col([dbc.Card([dbc.CardHeader(html.H5("EAC Trade Trends")),
                                   dbc.CardBody([dcc.Graph(figure=fig)])],className="shadow-sm")],width=12)],className="mb-4"),
        dbc.Row([dbc.Col([dbc.Card([dbc.CardHeader(html.H5("📋 Annex Table")),
                                   dbc.CardBody([tbl])],className="shadow-sm")],width=12)])
    ])

def build_eac_partners_combo(fdf, flw):
    """EAC Partners: Bars for 5 countries, line for total EAC (7)"""
    if flw == 'All':
        return dbc.Alert("Please select a specific flow (Exports, Imports, or Re-exports)", color="info")
    
    flow_df = fdf[fdf['Flow']==flw].copy()
    
    # 5 partners
    partners = flow_df[flow_df['Partner_Country'].isin(EAC_PARTNER_STATES)]
    pagg = partners.groupby(['Year','Quarter','Partner_Country'])['CValue'].sum().reset_index()
    pagg['CValue_M'] = pagg['CValue']/1_000_000
    pagg['YQ'] = pagg['Year'].astype(str)+'-Q'+pagg['Quarter'].astype(str)
    
    # 7 EAC total
    eac = flow_df[flow_df['Partner_Country'].isin(EAC_COUNTRIES)]
    eagg = eac.groupby(['Year','Quarter'])['CValue'].sum().reset_index()
    eagg['CValue_M'] = eagg['CValue']/1_000_000
    eagg['YQ'] = eagg['Year'].astype(str)+'-Q'+eagg['Quarter'].astype(str)
    
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    
    colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd']
    for i, c in enumerate(EAC_PARTNER_STATES):
        cd = pagg[pagg['Partner_Country']==c]
        if len(cd)>0:
            fig.add_trace(go.Bar(name=c, x=cd['YQ'], y=cd['CValue_M'], marker_color=colors[i]), secondary_y=False)
    
    fig.add_trace(go.Scatter(name='Total EAC', x=eagg['YQ'], y=eagg['CValue_M'],
                            mode='lines+markers', line=dict(color='#ffc107', width=3)), secondary_y=True)
    
    fig.update_xaxes(title_text="Year-Quarter")
    fig.update_yaxes(title_text="Partner States (US$ M)", secondary_y=False)
    fig.update_yaxes(title_text="Total EAC (US$ M)", secondary_y=True)
    fig.update_layout(barmode='group', height=500)
    
    return dbc.Row([dbc.Col([dbc.Card([dbc.CardHeader(html.H5("EAC Partner States vs Total EAC")),
                                      dbc.CardBody([dcc.Graph(figure=fig)])],className="shadow-sm")],width=12)])