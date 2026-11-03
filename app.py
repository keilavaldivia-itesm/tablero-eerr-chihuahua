import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Tablero EERR", page_icon="🏆", layout="wide")

st.title("🏆 Tablero EERR - Tec Chihuahua AD26")

# Cargar datos
@st.cache_data
def cargar_datos():
    conexion = sqlite3.connect("rosters_eerr.db")
    df = pd.read_sql("SELECT * FROM roster_ad26", conexion)
    conexion.close()
    return df

df = cargar_datos()

if len(df) == 0:
    st.error("No hay datos. Ejecuta el pipeline primero.")
    st.stop()

# Sidebar
st.sidebar.title("🧭 Menú")
pagina = st.sidebar.radio("Selecciona:", ["📊 Resumen", "📋 Rosters", "🎓 Becas", "🍽️ Apoyos"])

st.sidebar.info(f"Total atletas: {len(df)}")

# ============================================
# PANTALLA 1: RESUMEN
# ============================================
if pagina == "📊 Resumen":
    st.header("📊 Resumen Ejecutivo")
    
    # Encontrar columnas automáticamente
    col_rama = [c for c in df.columns if 'rama' in c.lower()]
    col_equipo = [c for c in df.columns if 'equipo' in c.lower()]
    col_nivel = [c for c in df.columns if 'nivel' in c.lower()]
    col_beca = [c for c in df.columns if '% de beca' in c.lower() or 'beca' in c.lower()]
    
    col_rama = col_rama[0] if col_rama else None
    col_equipo = col_equipo[0] if col_equipo else None
    col_nivel = col_nivel[0] if col_nivel else None
    col_beca = col_beca[0] if col_beca else None
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Atletas", len(df))
    
    if col_rama:
        fem = len(df[df[col_rama].astype(str).str.contains('Femenil', na=False)])
        var = len(df[df[col_rama].astype(str).str.contains('Varonil', na=False)])
        c2.metric("👩 Femenil", fem)
        c3.metric("👨 Varonil", var)
    else:
        c2.metric("👩 Femenil", 0)
        c3.metric("👨 Varonil", 0)
    
    if col_beca:
        df[col_beca] = pd.to_numeric(df[col_beca], errors='coerce').fillna(0)
        c4.metric("🎓 Beca Promedio", f"{df[col_beca].mean():.1f}%")
    else:
        c4.metric("🎓 Beca Promedio", "N/A")
    
    st.markdown("---")
    
    # Gráficos
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("🏅 Por Equipo")
        if col_equipo:
            equipos = df[col_equipo].value_counts().head(10)
            fig1 = px.pie(values=equipos.values, names=equipos.index, hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col6:
        st.subheader("📈 Por Nivel")
        if col_nivel:
            niveles = df[col_nivel].astype(str).str.title().value_counts()
            fig2 = px.bar(x=niveles.index, y=niveles.values)
            st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🏆 Top 10 Equipos por Rama")
    if col_equipo and col_rama:
        top = df.groupby([col_equipo, col_rama]).size().reset_index(name='Total')
        top = top.sort_values('Total', ascending=False).head(10)
        fig3 = px.bar(top, x='Total', y=col_equipo, color=col_rama, orientation='h')
        st.plotly_chart(fig3, use_container_width=True)

# ============================================
# PANTALLA 2: ROSTERS
# ============================================
elif pagina == "📋 Rosters":
    st.header("📋 Rosters y Filtros")
    
    col_equipo = [c for c in df.columns if 'equipo' in c.lower()][0]
    col_rama = [c for c in df.columns if 'rama' in c.lower()][0]
    col_nivel = [c for c in df.columns if 'nivel' in c.lower()][0]
    col_nombre = [c for c in df.columns if 'nombre' in c.lower()][0]
    
    st.subheader("🔍 Filtros")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        equipos = sorted(df[col_equipo].dropna().unique())
        sel_equipos = st.multiselect("Equipo:", equipos, default=equipos[:5])
    
    with f2:
        ramas = sorted(df[col_rama].dropna().unique())
        sel_ramas = st.multiselect("Rama:", ramas, default=ramas)
    
    with f3:
        niveles = sorted(df[col_nivel].dropna().unique())
        sel_niveles = st.multiselect("Nivel:", niveles, default=niveles)
    
    buscador = st.text_input("🔎 Buscar por nombre:", "")
    
    df_f = df[
        (df[col_equipo].isin(sel_equipos)) &
        (df[col_rama].isin(sel_ramas)) &
        (df[col_nivel].isin(sel_niveles))
    ]
    
    if buscador:
        df_f = df_f[df_f[col_nombre].astype(str).str.contains(buscador, case=False, na=False)]
    
    st.markdown(f"**📊 Resultados:** {len(df_f)} atletas")
    
    cols_show = [col_nombre, col_nivel, col_equipo, col_rama]
    st.dataframe(df_f[cols_show], use_container_width=True, height=500)

# ============================================
# PANTALLA 3: BECAS
# ============================================
elif pagina == "🎓 Becas":
    st.header("🎓 Análisis de Becas")
    
    col_beca = [c for c in df.columns if '% de beca' in c.lower() or 'beca' in c.lower()][0]
    col_tipo = [c for c in df.columns if 'tipo' in c.lower() and 'beca' in c.lower()]
    col_tipo = col_tipo[0] if col_tipo else None
    col_equipo = [c for c in df.columns if 'equipo' in c.lower()][0]
    
    df[col_beca] = pd.to_numeric(df[col_beca], errors='coerce').fillna(0)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Beca Promedio", f"{df[col_beca].mean():.1f}%")
    c2.metric("Beca Mediana", f"{df[col_beca].median():.1f}%")
    c3.metric("Beca Máxima", f"{df[col_beca].max():.0f}%")
    c4.metric("Sin Beca", len(df[df[col_beca] == 0]))
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.subheader("📊 Distribución de Becas")
        fig1 = px.histogram(df, x=col_beca, nbins=20)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col6:
        if col_tipo:
            st.subheader("🥧 Tipos de Beca")
            df[col_tipo] = df[col_tipo].astype(str).str.title()
            tipos = df[col_tipo].value_counts()
            fig2 = px.pie(values=tipos.values, names=tipos.index, hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🏆 Beca Promedio por Equipo")
    beca_eq = df.groupby(col_equipo)[col_beca].mean().sort_values(ascending=False)
    fig3 = px.bar(x=beca_eq.values, y=beca_eq.index, orientation='h')
    st.plotly_chart(fig3, use_container_width=True)

# ============================================
# PANTALLA 4: APOYOS
# ============================================
elif pagina == "🍽️ Apoyos":
    st.header("🍽️ Análisis de Apoyos EERR")
    
    col_comida = [c for c in df.columns if 'comida' in c.lower() and 'apoyo' in c.lower()]
    col_comida = col_comida[0] if col_comida else None
    
    col_sost = [c for c in df.columns if 'sostenimiento' in c.lower()]
    col_sost = col_sost[0] if col_sost else None
    
    c1, c2, c3 = st.columns(3)
    
    if col_comida:
        df[col_comida] = df[col_comida].astype(str).str.title()
        con_comida = len(df[df[col_comida].str.contains('Si', na=False)])
        c1.metric("🍽️ Con Comida", con_comida)
    else:
        c1.metric("🍽️ Con Comida", "N/A")
    
    if col_sost:
        df[col_sost] = df[col_sost].astype(str).str.title()
        con_sost = len(df[df[col_sost].str.contains('Si', na=False)])
        c2.metric("💰 Con Sostenimiento", con_sost)
    else:
        c2.metric("💰 Con Sostenimiento", "N/A")
    
    c3.metric("👥 Total", len(df))
    
    st.markdown("---")
    
    col4, col5 = st.columns(2)
    
    with col4:
        if col_comida:
            st.subheader("🍽️ Apoyo de Comida")
            comida = df[col_comida].value_counts()
            fig1 = px.pie(values=comida.values, names=comida.index)
           