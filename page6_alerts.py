from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def format_value(value):
    if pd.isna(value) or value == 0:
        return "$0.0M"
    return f"${value/1_000_000:.1f}M"


def format_change(value):
    """Format percentage change"""
    if pd.isna(value):
        return "N/A"
    return f"{value:+.1f}%"


def layout(df):
    return html.Div([
        
        # ── Page Description ──────────────────────────────────────────────────
        dbc.Alert([
            html.H5(" Internal Analytical Support Tool", className="alert-heading mb-2"),
            html.P([
                "This page facilitates internal data checks by automatically flagging irregular trade fluctuations ",
                "that require a review by analysts."
            ], className="mb-0")
        ], color="info", className="mb-4"),

        # ── Filters ───────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Year:", className="fw-bold"),
                dcc.Dropdown(
                    id='p6-year',
                    options=[{'label': str(y), 'value': y}
                             for y in sorted(df['Year'].unique(), reverse=True)],
                    value=df['Year'].max(),
                    clearable=False
                )
            ], width=3),
            dbc.Col([
                html.Label("Quarter:", className="fw-bold"),
                dcc.Dropdown(
                    id='p6-quarter',
                    options=[
                        {'label': 'Q1', 'value': '1'},
                        {'label': 'Q2', 'value': '2'},
                        {'label': 'Q3', 'value': '3'},
                        {'label': 'Q4', 'value': '4'}
                    ],
                    value='4',
                    clearable=False
                )
            ], width=3),
            dbc.Col([
                html.Label("Flow:", className="fw-bold"),
                dcc.Dropdown(
                    id='p6-flow',
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
                html.Label("Analysis Level:", className="fw-bold"),
                dcc.Dropdown(
                    id='p6-analysis',
                    options=[
                        {'label': 'By SITC (Product)', 'value': 'sitc'},
                        {'label': 'By Country', 'value': 'country'}
                    ],
                    value='sitc',
                    clearable=False
                )
            ], width=3),
        ], className="mb-4"),

        html.Hr(),

        # ── KPI Cards: Alert Summary ──────────────────────────────────────────
        dbc.Row([
            dbc.Col(html.Div(id='p6-kpi-total'), width=3),
            dbc.Col(html.Div(id='p6-kpi-increases'), width=3),
            dbc.Col(html.Div(id='p6-kpi-decreases'), width=3),
            dbc.Col(html.Div(id='p6-kpi-normal'), width=3),
        ], className="mb-4"),

        html.Hr(),

        # ── Table: Unusual Trade Movements ────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📊 Unusual Trade Movements", className="mb-0")),
                    dbc.CardBody([
                        html.P([
                            "Alert Logic: Flags items where ",
                            html.Strong("BOTH"),
                            " QoQ change AND YoY change are extreme (> +40% or < -40%)."
                        ], className="text-muted small mb-3"),
                        html.Div(id='p6-movements-table')
                    ])
                ], className="shadow-sm")
            ], width=12)
        ], className="mb-4"),

        # ── Charts Row ────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("🔴 Alert Distribution Overview", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='p6-pie-chart', style={'height': '380px'})
                    ])
                ], className="shadow-sm")
            ], width=5),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📈 Top 5 Increases vs Top 5 Decreases", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id='p6-bar-chart', style={'height': '380px'})
                    ])
                ], className="shadow-sm")
            ], width=7),
        ], className="mb-4"),

        # ── Data Validation Checklist ─────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📝 Data Validation Checklist", className="mb-0")),
                    dbc.CardBody([
                        html.P("For flagged items, analysts should verify:", className="fw-bold text-primary mb-2"),
                        html.Ul([
                            html.Li("Is this a real economic event? (New market access, policy change, seasonal variation)"),
                            html.Li("Check for data quality issues: Misclassification, late declarations, duplicates, unit errors"),
                            html.Li("Compare with customs documentation and supporting data sources"),
                            html.Li("Verify HS code accuracy and partner country codes"),
                            html.Li("Review historical patterns for this product-country combination"),
                            html.Li("Contact reporting entities if necessary for clarification")
                        ], className="mb-3"),
                        html.P([
                            html.Strong("Note: "),
                            "This page facilitates internal data checks by automatically flagging irregular trade ",
                            "fluctuations that require a review by analysts."
                        ], className="text-muted small mb-0")
                    ])
                ], className="shadow-sm", style={'border-left': '4px solid #ffc107'})
            ], width=12)
        ])
    ])


def register_callbacks(app, df):

    @callback(
        Output('p6-kpi-total', 'children'),
        Output('p6-kpi-increases', 'children'),
        Output('p6-kpi-decreases', 'children'),
        Output('p6-kpi-normal', 'children'),
        Output('p6-movements-table', 'children'),
        Output('p6-pie-chart', 'figure'),
        Output('p6-bar-chart', 'figure'),
        Input('selected-trade-type', 'children'),
        Input('p6-year', 'value'),
        Input('p6-quarter', 'value'),
        Input('p6-flow', 'value'),
        Input('p6-analysis', 'value'),
    )
    def update_page6(trade_type, year, quarter, flow, analysis):

        def empty_fig(msg="No data available"):
            fig = go.Figure()
            fig.add_annotation(text=msg, xref="paper", yref="paper",
                               x=0.5, y=0.5, showarrow=False, font=dict(size=14))
            fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
            return fig

        def kpi_card(title, value, subtitle, color="primary", icon=""):
            return dbc.Card(dbc.CardBody([
                html.H6(f"{icon} {title}", className="text-muted mb-2", style={'fontSize': '0.85rem'}),
                html.H3(str(value), className=f"text-{color} mb-0", style={'fontSize': '1.8rem'}),
                html.Small(subtitle, className="text-muted")
            ]), className="shadow-sm h-100")

        try:
            # ── Base Filter ───────────────────────────────────────────────────
            fdf = df[df['TradeType'] == trade_type].copy()
            fdf = fdf[fdf['Flow'] == flow].copy()

            if len(fdf) == 0:
                no_data = dbc.Alert("No data available for selected filters.", color="warning")
                empty = empty_fig()
                return (no_data, no_data, no_data, no_data, no_data, empty, empty)

            # ── Determine Dimension ───────────────────────────────────────────
            if analysis == 'sitc':
                dim_col = 'SITC_Description'
                dim_label = 'Product (SITC)'
            else:
                dim_col = 'Partner_Country'
                dim_label = 'Country'

            # Clean dimension
            fdf[dim_col] = fdf[dim_col].fillna('Unknown').astype(str).str.strip()

            # ── Calculate periods ─────────────────────────────────────────────
            current_year = int(year)
            current_quarter = str(quarter)

            # Previous quarter (wrap around)
            if current_quarter == '1':
                prev_quarter = '4'
                prev_quarter_year = current_year - 1
            else:
                prev_quarter = str(int(current_quarter) - 1)
                prev_quarter_year = current_year

            # Same quarter previous year
            prev_year_quarter = current_quarter
            prev_year_year = current_year - 1

            # ── Aggregate data ────────────────────────────────────────────────
            # Current period
            current_df = fdf[(fdf['Year'] == current_year) & (fdf['Quarter'] == current_quarter)]
            current_agg = current_df.groupby(dim_col)['CValue'].sum().reset_index()
            current_agg.rename(columns={'CValue': 'Current_Value'}, inplace=True)

            # Previous quarter
            prev_q_df = fdf[(fdf['Year'] == prev_quarter_year) & (fdf['Quarter'] == prev_quarter)]
            prev_q_agg = prev_q_df.groupby(dim_col)['CValue'].sum().reset_index()
            prev_q_agg.rename(columns={'CValue': 'PrevQ_Value'}, inplace=True)

            # Previous year same quarter
            prev_y_df = fdf[(fdf['Year'] == prev_year_year) & (fdf['Quarter'] == prev_year_quarter)]
            prev_y_agg = prev_y_df.groupby(dim_col)['CValue'].sum().reset_index()
            prev_y_agg.rename(columns={'CValue': 'PrevY_Value'}, inplace=True)

            # ── Merge all periods ─────────────────────────────────────────────
            merged = current_agg.merge(prev_q_agg, on=dim_col, how='left')
            merged = merged.merge(prev_y_agg, on=dim_col, how='left')

            # Fill missing with 0
            merged['PrevQ_Value'] = merged['PrevQ_Value'].fillna(0)
            merged['PrevY_Value'] = merged['PrevY_Value'].fillna(0)

            # ── Calculate changes ─────────────────────────────────────────────
            merged['QoQ_Change'] = ((merged['Current_Value'] - merged['PrevQ_Value']) / 
                                    merged['PrevQ_Value'] * 100).replace([float('inf'), -float('inf')], 0)
            merged['YoY_Change'] = ((merged['Current_Value'] - merged['PrevY_Value']) / 
                                    merged['PrevY_Value'] * 100).replace([float('inf'), -float('inf')], 0)

            # Handle division by zero
            merged.loc[merged['PrevQ_Value'] == 0, 'QoQ_Change'] = 0
            merged.loc[merged['PrevY_Value'] == 0, 'YoY_Change'] = 0

            # ── Alert Logic (BOTH must be extreme) ───────────────────────────
            def determine_alert(row):
                qoq = row['QoQ_Change']
                yoy = row['YoY_Change']

                # Both must be extreme
                qoq_extreme = (qoq > 40) or (qoq < -40)
                yoy_extreme = (yoy > 40) or (yoy < -40)

                if qoq_extreme and yoy_extreme:
                    if qoq > 40 and yoy > 40:
                        return '🔴 Extreme Increase'
                    elif qoq < -40 and yoy < -40:
                        return '🟠 Extreme Decrease'
                    else:
                        return '🟡 Mixed Signal'
                else:
                    return '🟢 Normal Movement'

            merged['Alert'] = merged.apply(determine_alert, axis=1)

            # ── Alert Counts ──────────────────────────────────────────────────
            total_alerts = len(merged)
            increases = len(merged[merged['Alert'] == '🔴 Extreme Increase'])
            decreases = len(merged[merged['Alert'] == '🟠 Extreme Decrease'])
            normal = len(merged[merged['Alert'] == '🟢 Normal Movement'])

            # KPIs
            kpi_total = kpi_card("Total Items Analyzed", total_alerts, 
                                f"{dim_label} analyzed", "primary", "📊")
            kpi_increases = kpi_card("Unusual Increases", increases, 
                                    "Extreme upward movements", "danger", "📈")
            kpi_decreases = kpi_card("Unusual Decreases", decreases, 
                                    "Extreme downward movements", "warning", "📉")
            kpi_normal = kpi_card("Normal Movements", normal, 
                                 "Within expected range", "success", "✅")

            # ── Table: Sort by Alert Severity ────────────────────────────────
            alert_order = {
                '🔴 Extreme Increase': 1,
                '🟠 Extreme Decrease': 2,
                '🟡 Mixed Signal': 3,
                '🟢 Normal Movement': 4
            }
            merged['Alert_Order'] = merged['Alert'].map(alert_order)
            merged = merged.sort_values('Alert_Order')

            # Format for display
            merged['Current_fmt'] = merged['Current_Value'].apply(format_value)
            merged['PrevQ_fmt'] = merged['PrevQ_Value'].apply(format_value)
            merged['PrevY_fmt'] = merged['PrevY_Value'].apply(format_value)
            merged['QoQ_fmt'] = merged['QoQ_Change'].apply(format_change)

            flow_names = {'E': 'Exports', 'I': 'Imports', 'R': 'Re-exports'}
            flow_name = flow_names[flow]

            table_data = merged[[dim_col, 'Current_fmt', 'PrevQ_fmt', 'PrevY_fmt', 'QoQ_fmt', 'Alert']].to_dict('records')

            movements_table = dash_table.DataTable(
                data=table_data,
                columns=[
                    {'name': dim_label, 'id': dim_col},
                    {'name': f'Current ({year}-Q{quarter})', 'id': 'Current_fmt'},
                    {'name': f'Prev Quarter ({prev_quarter_year}-Q{prev_quarter})', 'id': 'PrevQ_fmt'},
                    {'name': f'Prev Year ({prev_year_year}-Q{prev_year_quarter})', 'id': 'PrevY_fmt'},
                    {'name': '% Change (QoQ)', 'id': 'QoQ_fmt'},
                    {'name': 'Alert', 'id': 'Alert'}
                ],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px',
                    'fontFamily': 'Arial',
                    'fontSize': '13px',
                    'minWidth': '120px'
                },
                style_cell_conditional=[
                    {'if': {'column_id': dim_col}, 'fontWeight': 'bold', 'width': '200px'},
                    {'if': {'column_id': 'Alert'}, 'fontWeight': 'bold', 'textAlign': 'center'}
                ],
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
                    {'if': {'filter_query': '{Alert} = "🔴 Extreme Increase"'}, 
                     'backgroundColor': '#f8d7da', 'color': '#721c24'},
                    {'if': {'filter_query': '{Alert} = "🟠 Extreme Decrease"'}, 
                     'backgroundColor': '#fff3cd', 'color': '#856404'},
                    {'if': {'filter_query': '{Alert} = "🟢 Normal Movement"'}, 
                     'backgroundColor': '#d4edda', 'color': '#155724'},
                ],
                page_size=20,
                export_format='xlsx',
                export_headers='display',
                filter_action='native',
                sort_action='native'
            )

            # ── Pie Chart: Alert Distribution ─────────────────────────────────
            alert_counts = merged['Alert'].value_counts().reset_index()
            alert_counts.columns = ['Alert', 'Count']

            color_map_pie = {
                '🔴 Extreme Increase': '#dc3545',
                '🟠 Extreme Decrease': '#ffc107',
                '🟡 Mixed Signal': '#6c757d',
                '🟢 Normal Movement': '#28a745'
            }

            fig_pie = px.pie(
                alert_counts,
                values='Count',
                names='Alert',
                hole=0.4,
                color='Alert',
                color_discrete_map=color_map_pie
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=380, showlegend=True,
                                 legend=dict(orientation="h", yanchor="bottom", y=-0.2))

            # ── Bar Chart: Top 5 Increases vs Top 5 Decreases ────────────────
            increases_df = merged[merged['Alert'] == '🔴 Extreme Increase'].nlargest(5, 'QoQ_Change')
            decreases_df = merged[merged['Alert'] == '🟠 Extreme Decrease'].nsmallest(5, 'QoQ_Change')

            fig_bar = go.Figure()

            if len(increases_df) > 0:
                fig_bar.add_trace(go.Bar(
                    name='Increases',
                    y=increases_df[dim_col],
                    x=increases_df['QoQ_Change'],
                    orientation='h',
                    marker_color='#dc3545',
                    text=increases_df['QoQ_Change'].apply(lambda x: f"+{x:.1f}%"),
                    textposition='outside'
                ))

            if len(decreases_df) > 0:
                fig_bar.add_trace(go.Bar(
                    name='Decreases',
                    y=decreases_df[dim_col],
                    x=decreases_df['QoQ_Change'],
                    orientation='h',
                    marker_color='#ffc107',
                    text=decreases_df['QoQ_Change'].apply(lambda x: f"{x:.1f}%"),
                    textposition='outside'
                ))

            fig_bar.update_layout(
                barmode='overlay',
                height=380,
                xaxis=dict(title="% Change (QoQ)", zeroline=True, zerolinewidth=2, zerolinecolor='black'),
                yaxis=dict(title=""),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='y unified'
            )

            return (kpi_total, kpi_increases, kpi_decreases, kpi_normal,
                    movements_table, fig_pie, fig_bar)

        except Exception as e:
            error = dbc.Alert(f"Error loading page: {str(e)}", color="danger")
            empty = empty_fig("Error loading chart")
            return (error, error, error, error, error, empty, empty)