from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def format_value(value):
    if pd.isna(value) or value == 0:
        return "$0.0M"
    return f"${value/1_000_000:.1f}M"


def layout(df):
    # Build transport mode options from Via column
    via_options = [{'label': 'All Modes', 'value': 'All'}]
    if not df.empty and 'Via' in df.columns:
        for v in sorted(df['Via'].dropna().unique()):
            via_options.append({'label': str(v), 'value': str(v)})

    return html.Div([

        # ── Filters ──────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Year:", className="fw-bold"),
                dcc.Dropdown(
                    id='p5-year',
                    options=[{'label': 'All Years', 'value': 'All'}] +
                            [{'label': str(y), 'value': y}
                             for y in sorted(df['Year'].unique(), reverse=True)],
                    value='All',
                    clearable=False
                )
            ], width=3),
            dbc.Col([
                html.Label("Quarter:", className="fw-bold"),
                dcc.Dropdown(
                    id='p5-quarter',
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
                    id='p5-flow',
                    options=[
                        {'label': 'All Flows', 'value': 'All'},
                        {'label': 'Exports', 'value': 'E'},
                        {'label': 'Imports', 'value': 'I'},
                        {'label': 'Re-exports', 'value': 'R'}
                    ],
                    value='All',
                    clearable=False
                )
            ], width=3),
            dbc.Col([
                html.Label("Transport Mode:", className="fw-bold"),
                dcc.Dropdown(
                    id='p5-mode',
                    options=via_options,
                    value='All',
                    clearable=False
                )
            ], width=3),
        ], className="mb-4"),

        html.Hr(),

        # ── KPI Cards ────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col(html.Div(id='p5-kpi-total'), width=4),
            dbc.Col(html.Div(id='p5-kpi-dominant'), width=4),
            dbc.Col(html.Div(id='p5-kpi-busiest'), width=4),
        ], className="mb-4"),

        html.Hr(),

        # ── Chart 1: Transport Mode Trends Over Time ─────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📈 Transport Mode Trends Over Time (US$ Million)", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='p5-trend-chart', style={'height': '450px'})
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),

        # ── Chart 2: Donut + Clustered Bar side by side ───────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🍩 Distribution of Trade Value by Transport Mode", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='p5-donut-chart', style={'height': '420px'})
                    ])
                ], className="shadow-sm")
            ], width=5),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🏢 Trade by Customs Office / Border Post", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='p5-border-chart', style={'height': '420px'})
                    ])
                ], className="shadow-sm")
            ], width=7),
        ], className="mb-4"),

        # ── Pivot Table ───────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📋 Pivot Table — Transport Mode vs Year-Quarter (US$ Million)", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id='p5-pivot-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),

        # ── Key Insights ──────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("💡 Key Insights", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id='p5-key-insights')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),
    ])


def register_callbacks(app, df):

    @callback(
        Output('p5-kpi-total', 'children'),
        Output('p5-kpi-dominant', 'children'),
        Output('p5-kpi-busiest', 'children'),
        Output('p5-trend-chart', 'figure'),
        Output('p5-donut-chart', 'figure'),
        Output('p5-border-chart', 'figure'),
        Output('p5-pivot-table', 'children'),
        Output('p5-key-insights', 'children'),
        Input('selected-trade-type', 'children'),
        Input('p5-year', 'value'),
        Input('p5-quarter', 'value'),
        Input('p5-flow', 'value'),
        Input('p5-mode', 'value'),
    )
    def update_page5(trade_type, year, quarter, flow, mode):

        # ── Empty figure helper ───────────────────────────────────────────────
        def empty_fig(msg="No data available"):
            fig = go.Figure()
            fig.add_annotation(text=msg, xref="paper", yref="paper",
                               x=0.5, y=0.5, showarrow=False, font=dict(size=14))
            fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
            return fig

        def kpi_card(title, value, subtitle, color="primary", icon=""):
            return dbc.Card(dbc.CardBody([
                html.H6(f"{icon} {title}", className="text-muted mb-2", style={'fontSize': '0.85rem'}),
                html.H3(value, className=f"text-{color} mb-0", style={'fontSize': '1.6rem'}),
                html.Small(subtitle, className="text-muted")
            ]), className="shadow-sm h-100")

        try:
            # ── Base filter ───────────────────────────────────────────────────
            fdf = df[df['TradeType'] == trade_type].copy()

            if year != 'All':
                fdf = fdf[fdf['Year'] == year]
            if quarter != 'All':
                fdf = fdf[fdf['Quarter'] == quarter]
            if flow != 'All':
                fdf = fdf[fdf['Flow'] == flow]
            if mode != 'All':
                fdf = fdf[fdf['Via'] == mode]

            if len(fdf) == 0:
                no_data = dbc.Alert("No data available for the selected filters.", color="warning")
                empty = empty_fig()
                return (no_data, no_data, no_data,
                        empty, empty, empty,
                        no_data, no_data)

            flow_names = {'E': 'Exports', 'I': 'Imports', 'R': 'Re-exports'}

            # ── KPI 1: Total Trade Value ──────────────────────────────────────
            total_trade = fdf['CValue'].sum()
            kpi_total = kpi_card(
                "Total Trade Value",
                format_value(total_trade),
                f"{trade_type.replace('Trade', ' Trade')} | {flow_names.get(flow, 'All Flows')}",
                "primary", "💰"
            )

            # ── KPI 2: Dominant Transport Mode ────────────────────────────────
            mode_agg = fdf.groupby('Via')['CValue'].sum()
            if len(mode_agg) > 0:
                dominant_mode = mode_agg.idxmax()
                dominant_val = mode_agg.max()
                dominant_pct = (dominant_val / total_trade * 100) if total_trade > 0 else 0
                kpi_dominant = kpi_card(
                    "Dominant Transport Mode",
                    str(dominant_mode),
                    f"{dominant_pct:.1f}% of total trade value",
                    "success", "🚚"
                )
            else:
                kpi_dominant = kpi_card("Dominant Transport Mode", "N/A", "No data", "secondary", "🚚")

            # ── KPI 3: Busiest Customs Office ─────────────────────────────────
            border_agg = fdf.groupby('Borders')['CValue'].sum()
            if len(border_agg) > 0:
                busiest_border = border_agg.idxmax()
                busiest_val = border_agg.max()
                busiest_pct = (busiest_val / total_trade * 100) if total_trade > 0 else 0
                kpi_busiest = kpi_card(
                    "Busiest Customs Office",
                    str(busiest_border),
                    f"{busiest_pct:.1f}% of total trade value",
                    "warning", "🏢"
                )
            else:
                kpi_busiest = kpi_card("Busiest Customs Office", "N/A", "No data", "secondary", "🏢")

            # ── CHART 1: Trends Over Time ─────────────────────────────────────
            # Use full df filtered only by trade type + flow + mode (not year/quarter)
            # so the trend shows all available year-quarters
            trend_base = df[df['TradeType'] == trade_type].copy()
            if flow != 'All':
                trend_base = trend_base[trend_base['Flow'] == flow]
            if mode != 'All':
                trend_base = trend_base[trend_base['Via'] == mode]

            trend_agg = trend_base.groupby(['Year', 'Quarter', 'Via'])['CValue'].sum().reset_index()
            trend_agg['CValue_M'] = trend_agg['CValue'] / 1_000_000
            trend_agg['YQ'] = trend_agg['Year'].astype(str) + '-Q' + trend_agg['Quarter'].astype(str)
            trend_agg = trend_agg.sort_values(['Year', 'Quarter'])

            all_yq = trend_agg['YQ'].unique()

            fig_trend = go.Figure()
            via_values = trend_agg['Via'].unique()
            colors_trend = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

            for i, v in enumerate(via_values):
                vd = trend_agg[trend_agg['Via'] == v]
                fig_trend.add_trace(go.Bar(
                    name=str(v),
                    x=vd['YQ'],
                    y=vd['CValue_M'],
                    marker_color=colors_trend[i % len(colors_trend)]
                ))

            # Add total line on secondary axis
            total_trend = trend_agg.groupby('YQ')['CValue_M'].sum().reset_index()
            fig_trend.add_trace(go.Scatter(
                name='Total Trade',
                x=total_trend['YQ'],
                y=total_trend['CValue_M'],
                mode='lines+markers',
                line=dict(color='#ffc107', width=3),
                marker=dict(size=7),
                yaxis='y2'
            ))

            fig_trend.update_layout(
                barmode='group',
                height=450,
                xaxis=dict(title="Year-Quarter", categoryorder='array', categoryarray=list(all_yq)),
                yaxis=dict(title="Trade Value (US$ Million)"),
                yaxis2=dict(title="Total Trade (US$ Million)", overlaying='y', side='right'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )

            # ── CHART 2: Donut ────────────────────────────────────────────────
            donut_agg = fdf.groupby('Via')['CValue'].sum().reset_index()
            donut_agg['CValue_M'] = donut_agg['CValue'] / 1_000_000

            fig_donut = px.pie(
                donut_agg,
                values='CValue_M',
                names='Via',
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_donut.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Value: $%{value:.1f}M<br>Share: %{percent}<extra></extra>'
            )
            fig_donut.update_layout(height=420, showlegend=True,
                                    legend=dict(orientation="h", yanchor="bottom", y=-0.2))

            # ── CHART 3: Clustered Bar — Trade by Border/Customs Office ────────
            border_flow_agg = fdf.groupby(['Borders', 'Flow'])['CValue'].sum().reset_index()
            border_flow_agg['CValue_M'] = border_flow_agg['CValue'] / 1_000_000
            border_flow_agg['Flow_Name'] = border_flow_agg['Flow'].map(flow_names)

            # Sort borders by total value
            border_order = border_flow_agg.groupby('Borders')['CValue_M'].sum().sort_values(ascending=False).index.tolist()

            fig_border = go.Figure()
            color_map = {'Exports': '#28a745', 'Imports': '#dc3545', 'Re-exports': '#17a2b8'}

            for fn, clr in color_map.items():
                fd = border_flow_agg[border_flow_agg['Flow_Name'] == fn]
                if len(fd) > 0:
                    fig_border.add_trace(go.Bar(
                        name=fn,
                        x=fd['Borders'],
                        y=fd['CValue_M'],
                        marker_color=clr,
                        text=fd['CValue_M'].apply(lambda x: f"${x:.1f}M"),
                        textposition='outside'
                    ))

            fig_border.update_layout(
                barmode='group',
                height=420,
                xaxis=dict(title="Border / Customs Office", categoryorder='array', categoryarray=border_order),
                yaxis=dict(title="Trade Value (US$ Million)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )

            # ── PIVOT TABLE ───────────────────────────────────────────────────
            pivot_base = fdf.copy()
            pivot_base['YQ'] = pivot_base['Year'].astype(str) + '-Q' + pivot_base['Quarter'].astype(str)
            pivot_agg = pivot_base.groupby(['Via', 'YQ'])['CValue'].sum().reset_index()
            pivot_agg['CValue_M'] = pivot_agg['CValue'] / 1_000_000

            pivot_table = pivot_agg.pivot_table(
                index='Via',
                columns='YQ',
                values='CValue_M',
                fill_value=0
            ).reset_index()
            pivot_table.columns.name = None

            # Sort YQ columns chronologically
            yq_cols = [c for c in pivot_table.columns if c != 'Via']
            def sort_yq(yq):
                try:
                    parts = yq.split('-Q')
                    return (int(parts[0]), int(parts[1]))
                except:
                    return (0, 0)
            yq_cols_sorted = sorted(yq_cols, key=sort_yq)

            # Add total column
            pivot_table['Total'] = pivot_table[yq_cols_sorted].sum(axis=1)
            pivot_table = pivot_table.sort_values('Total', ascending=False)

            # Format for display
            for col in yq_cols_sorted + ['Total']:
                pivot_table[f'{col}_fmt'] = pivot_table[col].apply(lambda x: f"${x:.1f}M")

            table_cols = [{'name': 'Transport Mode', 'id': 'Via'}]
            for col in yq_cols_sorted:
                table_cols.append({'name': col, 'id': f'{col}_fmt'})
            table_cols.append({'name': 'Total (US$ M)', 'id': 'Total_fmt'})

            display_cols = ['Via'] + [f'{c}_fmt' for c in yq_cols_sorted] + ['Total_fmt']
            pivot_display = pivot_table[display_cols].to_dict('records')

            pivot_dt = dash_table.DataTable(
                data=pivot_display,
                columns=table_cols,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'padding': '12px',
                    'fontFamily': 'Arial',
                    'fontSize': '13px',
                    'minWidth': '110px'
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'Via'}, 'textAlign': 'left',
                     'fontWeight': 'bold', 'width': '160px'},
                    {'if': {'column_id': 'Total_fmt'}, 'fontWeight': 'bold',
                     'backgroundColor': '#fff3cd'}
                ],
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
                    {'if': {'row_index': 0}, 'backgroundColor': '#e8f5e9', 'fontWeight': 'bold'}
                ],
                export_format='xlsx',
                export_headers='display'
            )

            # ── KEY INSIGHTS ──────────────────────────────────────────────────
            # Transport Infrastructure
            air_val = fdf[fdf['Via'].astype(str).str.lower() == 'air']['CValue'].sum()
            land_val = fdf[fdf['Via'].astype(str).str.lower() != 'air']['CValue'].sum()
            air_pct = (air_val / total_trade * 100) if total_trade > 0 else 0
            land_pct = (land_val / total_trade * 100) if total_trade > 0 else 0

            # Border Efficiency
            top3_borders = border_agg.sort_values(ascending=False).head(3)
            top3_pct = (top3_borders.sum() / total_trade * 100) if total_trade > 0 else 0

            # Trade Diversification
            n_modes = fdf['Via'].nunique()
            n_borders = fdf['Borders'].nunique()

            insights = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("🚚 Transport Infrastructure", className="text-success fw-bold mb-2"),
                            html.P([
                                f"Land transport dominates with ",
                                html.Strong(f"{land_pct:.1f}%"),
                                f" of total trade value ({format_value(land_val)}), while Air accounts for ",
                                html.Strong(f"{air_pct:.1f}%"),
                                f" ({format_value(air_val)}). ",
                                f"The dominant route is ",
                                html.Strong(f"{dominant_mode}"),
                                f", contributing {dominant_pct:.1f}% of total trade."
                            ], className="text-muted small mb-0")
                        ])
                    ], className="shadow-sm h-100", style={'border-left': '4px solid #28a745'})
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("🏢 Border Efficiency", className="text-warning fw-bold mb-2"),
                            html.P([
                                f"The busiest customs office is ",
                                html.Strong(f"{busiest_border}"),
                                f" ({busiest_pct:.1f}% of total trade). ",
                                f"The top 3 border posts — ",
                                html.Strong(', '.join(top3_borders.index.tolist())),
                                f" — collectively handle ",
                                html.Strong(f"{top3_pct:.1f}%"),
                                f" of all trade activity."
                            ], className="text-muted small mb-0")
                        ])
                    ], className="shadow-sm h-100", style={'border-left': '4px solid #ffc107'})
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📊 Trade Diversification", className="text-primary fw-bold mb-2"),
                            html.P([
                                f"Trade is spread across ",
                                html.Strong(f"{n_modes} transport mode(s)"),
                                f" and ",
                                html.Strong(f"{n_borders} border/customs office(s)"),
                                f". ",
                                f"Total trade value stands at ",
                                html.Strong(format_value(total_trade)),
                                f" for the selected period and filters."
                            ], className="text-muted small mb-0")
                        ])
                    ], className="shadow-sm h-100", style={'border-left': '4px solid #007bff'})
                ], width=4),
            ])

            return (kpi_total, kpi_dominant, kpi_busiest,
                    fig_trend, fig_donut, fig_border,
                    pivot_dt, insights)

        except Exception as e:
            error = dbc.Alert(f"Error loading page: {str(e)}", color="danger")
            empty = empty_fig("Error loading chart")
            return (error, error, error,
                    empty, empty, empty,
                    error, error)