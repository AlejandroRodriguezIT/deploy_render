"""
Dashboard de Rankings de Equipos - TruMedia
Autor: Sistema de análisis TruMedia
Fecha: 2025

Panel interactivo con diagramas de Estilo y Rendimiento
Versión para despliegue en Render
"""

import os
import dash
from dash import dcc, html, callback, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS (usando variables de entorno para seguridad)
# ============================================================================

DB_USER = os.environ.get("DB_USER", "alen_depor")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "ik3QJOq6n")
DB_HOST = os.environ.get("DB_HOST", "82.165.192.201")
DB_NAME = os.environ.get("DB_NAME", "opta")
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

TABLA_RANKINGS = "team_stats_angel_ranking"
TABLA_PARTIDOS = "team_metricas_angel"

# ============================================================================
# CONFIGURACIÓN DE MÉTRICAS POR DIAGRAMA
# ============================================================================

# Diagrama de ESTILO GLOBAL (métricas de estilo de juego)
ESTILO_CONFIG = {
    'titulo_principal': 'ESTILO GLOBAL',
    'color_principal': '#FFD700',  # Amarillo/Dorado
    'metricas': [
        {'columna': 'Iniciativa de Juego', 'nombre': 'Iniciativa de Juego'},
        {'columna': '%Posesión', 'nombre': '% Posesión'},
        {'columna': 'Elaboración_Ofensiva', 'nombre': 'Elaboración Ofensiva'},
        {'columna': '% Finalizaciones rapidas', 'nombre': '% Finalizaciones rapidas'},
        {'columna': 'Ritmo_Circulación', 'nombre': 'Ritmo Circulación'},
        {'columna': '% Pases largos', 'nombre': '% Pases Largos'},
        {'columna': 'Centros intentados', 'nombre': 'Centros'},
        {'columna': '%Recuperacion_campo_contrario', 'nombre': '% Recup. Campo Contrario'},
        {'columna': '%Recuperaciones_rapidas', 'nombre': '% Recuperaciones Rápidas'},
        {'columna': 'Ritmo_Recuperación', 'nombre': 'Ritmo Recuperación'},
        {'columna': 'PPDA', 'nombre': 'PPDA'},
    ]
}

# Diagrama de RENDIMIENTO GLOBAL (métricas de rendimiento)
RENDIMIENTO_CONFIG = {
    'titulo_principal': 'RENDIMIENTO GLOBAL',
    'color_principal': '#00B050',  # Verde
    'metricas': [
        {'columna': 'Eficacia_Construcción_Ofensiva', 'nombre': 'Eficacia Construcción Of. (%)'},
        {'columna': 'Eficacia_Finalización', 'nombre': 'Eficacia Finalización (%)'},
        {'columna': 'Xg_Favor_NP', 'nombre': 'xG a Favor JD'},
        {'columna': 'Goal_global', 'nombre': 'Goles a Favor'},
        {'columna': 'Eficacia_Contención_Defensiva', 'nombre': 'Eficacia Contención Def. (%)'},
        {'columna': 'Eficacia_Evitación', 'nombre': 'Eficacia Evitación (%)'},
        {'columna': 'xG_Contra_NP', 'nombre': 'xG en Contra JD'},
        {'columna': 'Goal_global_rival', 'nombre': 'Goles en Contra'},
        {'columna': '% Duelos Aéreos', 'nombre': '% Duelos Aéreos'},
        {'columna': 'Goles_BP_Favor', 'nombre': 'Goles B.P. Favor'},
        {'columna': 'xG_BP_Favor', 'nombre': 'xG B.P. Favor'},
        {'columna': 'Goles_BP_Contra', 'nombre': 'Goles B.P. Contra'},
        {'columna': 'xG_BP_Contra', 'nombre': 'xG B.P. Contra'},
    ]
}


# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================

def cargar_datos_rankings():
    """Carga los datos de la tabla de rankings"""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        query = f"SELECT * FROM {TABLA_RANKINGS}"
        df = pd.read_sql(query, engine)
        engine.dispose()
        return df
    except Exception as e:
        print(f"Error al cargar datos rankings: {e}")
        return pd.DataFrame()


def cargar_datos_partidos():
    """Carga los datos de partidos individuales"""
    try:
        engine = create_engine(DATABASE_URL, echo=False)
        query = f"SELECT * FROM {TABLA_PARTIDOS} ORDER BY gameDate"
        df = pd.read_sql(query, engine)
        engine.dispose()
        return df
    except Exception as e:
        print(f"Error al cargar datos partidos: {e}")
        return pd.DataFrame()


# ============================================================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================================================

def get_color_by_ranking(ranking):
    """Retorna el color según la posición en el ranking"""
    if ranking <= 6:
        return '#00B050'  # Verde
    elif ranking <= 16:
        return '#FFD700'  # Amarillo
    else:
        return '#FF0000'  # Rojo


def crear_columna_no_disponible():
    """Crea una columna gris oscuro para métricas no disponibles"""
    slots = []
    for pos in range(1, 23):
        slot = html.Div(
            '',
            title=f"Datos no disponibles",
            style={
                'height': '20px',
                'backgroundColor': '#4a4a4a',
                'borderBottom': '1px solid #333',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
            }
        )
        slots.append(slot)
    
    return html.Div(slots, style={'display': 'flex', 'flexDirection': 'column'})


def crear_columna_ranking(df, metrica_col, equipo_seleccionado, disponible=True):
    """Crea una columna visual con 22 slots para representar el ranking"""
    if not disponible:
        return crear_columna_no_disponible()
    
    ranking_col = f"{metrica_col}_ranking"
    
    if ranking_col not in df.columns or metrica_col not in df.columns:
        return crear_columna_no_disponible()
    
    equipo_data = df[df['fullName'] == equipo_seleccionado]
    if equipo_data.empty:
        return crear_columna_no_disponible()
    
    ranking_equipo = int(equipo_data[ranking_col].values[0])
    color_equipo = get_color_by_ranking(ranking_equipo)
    
    slots = []
    for pos in range(1, 23):
        equipo_en_pos = df[df[ranking_col] == pos]
        
        if not equipo_en_pos.empty:
            nombre_equipo_pos = equipo_en_pos['fullName'].values[0]
            valor_metrica = equipo_en_pos[metrica_col].values[0]
            tooltip_text = f"#{pos} {nombre_equipo_pos}: {valor_metrica:.2f}"
        else:
            tooltip_text = f"Posición {pos}"
        
        if pos >= ranking_equipo:
            slot_color = color_equipo
        else:
            slot_color = '#E8E8E8'
        
        is_equipo_pos = (pos == ranking_equipo)
        
        slot = html.Div(
            '•' if is_equipo_pos else '',
            title=tooltip_text,
            style={
                'height': '20px',
                'backgroundColor': slot_color,
                'borderBottom': '1px solid #fff',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'color': '#000' if is_equipo_pos else 'transparent',
                'cursor': 'pointer',
                'transition': 'all 0.2s',
            }
        )
        slots.append(slot)
    
    return html.Div(slots, style={'display': 'flex', 'flexDirection': 'column'})


def crear_tabla_diagrama(df, config, equipo_seleccionado):
    """Crea la tabla visual del diagrama con métricas"""
    color_principal = config['color_principal']
    
    header_cells = [
        html.Th(
            'Pos',
            style={
                'backgroundColor': '#f0f0f0',
                'padding': '10px 5px',
                'fontSize': '12px',
                'fontWeight': 'bold',
                'textAlign': 'center',
                'width': '40px',
                'minWidth': '40px',
                'border': '1px solid #ccc',
            }
        )
    ]
    
    for metrica in config['metricas']:
        disponible = metrica.get('disponible', True)
        header_bg = '#f0f0f0' if disponible else '#4a4a4a'
        header_color = '#000' if disponible else '#999'
        
        header_cells.append(
            html.Th(
                metrica['nombre'],
                style={
                    'backgroundColor': header_bg,
                    'color': header_color,
                    'padding': '10px 5px',
                    'fontSize': '11px',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'width': '80px',
                    'minWidth': '80px',
                    'border': '1px solid #ccc',
                    'wordWrap': 'break-word',
                }
            )
        )
    
    body_rows = []
    for pos in range(1, 23):
        row_cells = [
            html.Td(
                str(pos),
                style={
                    'backgroundColor': '#f9f9f9',
                    'textAlign': 'center',
                    'fontSize': '11px',
                    'padding': '0',
                    'height': '20px',
                    'width': '40px',
                    'border': '1px solid #eee',
                }
            )
        ]
        
        for metrica in config['metricas']:
            disponible = metrica.get('disponible', True)
            metrica_col = metrica['columna']
            ranking_col = f"{metrica_col}_ranking"
            
            if not disponible or ranking_col not in df.columns or metrica_col not in df.columns:
                cell_style = {
                    'backgroundColor': '#4a4a4a',
                    'height': '20px',
                    'width': '80px',
                    'border': '1px solid #333',
                    'padding': '0',
                }
                tooltip = "Datos no disponibles"
                cell_content = ''
                is_equipo_pos = False
            else:
                equipo_data = df[df['fullName'] == equipo_seleccionado]
                if not equipo_data.empty:
                    ranking_equipo = int(equipo_data[ranking_col].values[0])
                    color_equipo = get_color_by_ranking(ranking_equipo)
                    
                    equipo_en_pos = df[df[ranking_col] == pos]
                    if not equipo_en_pos.empty:
                        nombre_equipo_pos = equipo_en_pos['fullName'].values[0]
                        valor_metrica = equipo_en_pos[metrica_col].values[0]
                        tooltip = f"#{pos} {nombre_equipo_pos}: {valor_metrica:.2f}"
                    else:
                        tooltip = f"Posición {pos}"
                    
                    if pos >= ranking_equipo:
                        cell_color = color_equipo
                    else:
                        cell_color = '#E8E8E8'
                    
                    is_equipo_pos = (pos == ranking_equipo)
                else:
                    cell_color = '#E8E8E8'
                    tooltip = f"Posición {pos}"
                    is_equipo_pos = False
                
                cell_style = {
                    'backgroundColor': cell_color,
                    'height': '20px',
                    'width': '80px',
                    'border': '1px solid #fff',
                    'padding': '0',
                    'textAlign': 'center',
                    'cursor': 'pointer',
                }
                cell_content = '•' if is_equipo_pos else ''
            
            row_cells.append(
                html.Td(
                    cell_content,
                    title=tooltip,
                    style=cell_style
                )
            )
        
        body_rows.append(html.Tr(row_cells))
    
    tabla = html.Table([
        html.Thead(html.Tr(header_cells)),
        html.Tbody(body_rows)
    ], style={
        'borderCollapse': 'collapse',
        'width': 'auto',
    })
    
    leyenda = html.Div([
        html.Span('■ 1-6', style={'color': '#00B050', 'marginRight': '15px', 'fontSize': '12px'}),
        html.Span('■ 7-16', style={'color': '#FFD700', 'marginRight': '15px', 'fontSize': '12px'}),
        html.Span('■ 17-22', style={'color': '#FF0000', 'fontSize': '12px'}),
    ], style={'textAlign': 'right', 'padding': '10px', 'marginTop': '10px'})
    
    return html.Div([
        tabla,
        leyenda,
    ], style={
        'overflow': 'auto',
        'maxWidth': '100%',
    })


# ============================================================================
# APLICACIÓN DASH
# ============================================================================

# Cargar datos iniciales
df_rankings = cargar_datos_rankings()
df_partidos = cargar_datos_partidos()

# Crear aplicación
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Necesario para Render/Gunicorn
app.title = "Dashboard Rankings - TruMedia"

# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Dashboard de Rankings de Equipos", 
                style={'textAlign': 'center', 'color': '#333', 'marginBottom': '10px'}),
        html.P("Segunda División 2024/2025 - Datos TruMedia", 
               style={'textAlign': 'center', 'color': '#666', 'fontSize': '14px'}),
    ], style={'padding': '20px', 'backgroundColor': '#f5f5f5'}),
    
    # Botones de navegación
    html.Div([
        html.Button(
            'DIAGRAMAS DE ESTILO',
            id='btn-estilo',
            n_clicks=0,
            style={
                'backgroundColor': '#FFD700',
                'color': '#000',
                'border': 'none',
                'padding': '15px 30px',
                'fontSize': '16px',
                'fontWeight': 'bold',
                'cursor': 'pointer',
                'marginRight': '20px',
                'borderRadius': '5px',
            }
        ),
        html.Button(
            'DIAGRAMAS DE RENDIMIENTO',
            id='btn-rendimiento',
            n_clicks=0,
            style={
                'backgroundColor': '#00B050',
                'color': '#fff',
                'border': 'none',
                'padding': '15px 30px',
                'fontSize': '16px',
                'fontWeight': 'bold',
                'cursor': 'pointer',
                'borderRadius': '5px',
            }
        ),
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    # Selector de equipo
    html.Div([
        html.Label('Seleccionar Equipo:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='selector-equipo',
            options=[{'label': equipo, 'value': equipo} for equipo in sorted(df_rankings['fullName'].unique())] if not df_rankings.empty else [],
            value=df_rankings['fullName'].iloc[0] if not df_rankings.empty else None,
            style={'width': '300px', 'display': 'inline-block'},
            clearable=False,
        ),
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    # Store para el diagrama activo
    dcc.Store(id='diagrama-activo', data='estilo'),
    
    # Contenedor del diagrama
    html.Div(id='contenedor-diagrama', style={'padding': '20px', 'overflowX': 'auto'}),
    
    # Separador
    html.Hr(style={'margin': '30px 0'}),
    
    # Sección del gráfico de barras
    html.Div([
        html.H3("Evolución por Partido", style={'textAlign': 'center', 'marginBottom': '20px'}),
        
        # Selector de métrica
        html.Div([
            html.Label('Seleccionar Métrica:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='selector-metrica',
                options=[],
                value=None,
                style={'width': '300px', 'display': 'inline-block'},
                clearable=False,
            ),
        ], style={'textAlign': 'center', 'marginBottom': '20px'}),
        
        # Gráfico de barras
        dcc.Graph(id='grafico-barras', style={'height': '400px'}),
        
    ], style={'padding': '20px'}),
    
    # Footer
    html.Div([
        html.P("© 2025 RC Deportivo de La Coruña - Departamento de Análisis", 
               style={'textAlign': 'center', 'color': '#999', 'fontSize': '12px', 'marginTop': '30px'}),
    ]),
    
], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1400px', 'margin': '0 auto'})


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('diagrama-activo', 'data'),
    Output('btn-estilo', 'style'),
    Output('btn-rendimiento', 'style'),
    Input('btn-estilo', 'n_clicks'),
    Input('btn-rendimiento', 'n_clicks'),
)
def cambiar_diagrama(clicks_estilo, clicks_rendimiento):
    ctx = dash.callback_context
    
    estilo_activo = {
        'backgroundColor': '#FFD700',
        'color': '#000',
        'border': '3px solid #000',
        'padding': '15px 30px',
        'fontSize': '16px',
        'fontWeight': 'bold',
        'cursor': 'pointer',
        'marginRight': '20px',
        'borderRadius': '5px',
    }
    
    estilo_inactivo = {
        'backgroundColor': '#FFD700',
        'color': '#000',
        'border': 'none',
        'padding': '15px 30px',
        'fontSize': '16px',
        'fontWeight': 'bold',
        'cursor': 'pointer',
        'marginRight': '20px',
        'borderRadius': '5px',
        'opacity': '0.7',
    }
    
    rendimiento_activo = {
        'backgroundColor': '#00B050',
        'color': '#fff',
        'border': '3px solid #000',
        'padding': '15px 30px',
        'fontSize': '16px',
        'fontWeight': 'bold',
        'cursor': 'pointer',
        'borderRadius': '5px',
    }
    
    rendimiento_inactivo = {
        'backgroundColor': '#00B050',
        'color': '#fff',
        'border': 'none',
        'padding': '15px 30px',
        'fontSize': '16px',
        'fontWeight': 'bold',
        'cursor': 'pointer',
        'borderRadius': '5px',
        'opacity': '0.7',
    }
    
    if not ctx.triggered:
        return 'estilo', estilo_activo, rendimiento_inactivo
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'btn-rendimiento':
        return 'rendimiento', estilo_inactivo, rendimiento_activo
    else:
        return 'estilo', estilo_activo, rendimiento_inactivo


@callback(
    Output('contenedor-diagrama', 'children'),
    Input('diagrama-activo', 'data'),
    Input('selector-equipo', 'value'),
)
def actualizar_diagrama(diagrama_activo, equipo_seleccionado):
    if not equipo_seleccionado or df_rankings.empty:
        return html.Div("Seleccione un equipo", style={'textAlign': 'center', 'padding': '50px'})
    
    if diagrama_activo == 'rendimiento':
        return crear_tabla_diagrama(df_rankings, RENDIMIENTO_CONFIG, equipo_seleccionado)
    else:
        return crear_tabla_diagrama(df_rankings, ESTILO_CONFIG, equipo_seleccionado)


@callback(
    Output('selector-metrica', 'options'),
    Output('selector-metrica', 'value'),
    Input('diagrama-activo', 'data'),
)
def actualizar_opciones_metrica(diagrama_activo):
    """Actualiza las opciones del selector de métricas según el diagrama activo"""
    if diagrama_activo == 'rendimiento':
        config = RENDIMIENTO_CONFIG
    else:
        config = ESTILO_CONFIG
    
    opciones = [
        {'label': m['nombre'], 'value': m['columna']}
        for m in config['metricas']
        if m.get('disponible', True)
    ]
    
    valor_default = opciones[0]['value'] if opciones else None
    
    return opciones, valor_default


@callback(
    Output('grafico-barras', 'figure'),
    Input('selector-equipo', 'value'),
    Input('selector-metrica', 'value'),
    Input('diagrama-activo', 'data'),
)
def actualizar_grafico_barras(equipo_seleccionado, metrica_seleccionada, diagrama_activo):
    """Genera el gráfico de barras con la evolución por partido"""
    if not equipo_seleccionado or not metrica_seleccionada or df_partidos.empty:
        return go.Figure()
    
    df_equipo = df_partidos[df_partidos['fullName'] == equipo_seleccionado].copy()
    
    if df_equipo.empty or metrica_seleccionada not in df_equipo.columns:
        return go.Figure().add_annotation(
            text="No hay datos disponibles para esta métrica",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
    
    df_equipo = df_equipo.sort_values('gameDate')
    
    if diagrama_activo == 'rendimiento':
        config = RENDIMIENTO_CONFIG
    else:
        config = ESTILO_CONFIG
    
    nombre_metrica = metrica_seleccionada
    for m in config['metricas']:
        if m['columna'] == metrica_seleccionada:
            nombre_metrica = m['nombre']
            break
    
    df_equipo['etiqueta'] = df_equipo.apply(
        lambda row: f"{row['oppFullName']}", axis=1
    )
    
    color_principal = '#FFD700' if diagrama_activo == 'estilo' else '#00B050'
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_equipo['etiqueta'],
        y=df_equipo[metrica_seleccionada],
        marker_color=color_principal,
        text=df_equipo[metrica_seleccionada].round(2),
        textposition='outside',
        hovertemplate=(
            '<b>%{x}</b><br>' +
            f'{nombre_metrica}: ' + '%{y:.2f}<br>' +
            '<extra></extra>'
        )
    ))
    
    fig.update_layout(
        title=dict(
            text=f'{nombre_metrica} - {equipo_seleccionado}',
            x=0.5,
            font=dict(size=18)
        ),
        xaxis=dict(
            title='Rival (ordenado por fecha)',
            tickangle=45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title=nombre_metrica,
        ),
        showlegend=False,
        margin=dict(b=120),
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    
    promedio = df_equipo[metrica_seleccionada].mean()
    fig.add_hline(
        y=promedio,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Promedio: {promedio:.2f}",
        annotation_position="top right"
    )
    
    return fig


# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host='0.0.0.0', port=port)
