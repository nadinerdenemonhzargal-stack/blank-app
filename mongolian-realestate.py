"""
Монгол Үл Хөдлөх Хөрөнгийн Үнэ Тооцоолуур
Streamlit аппликейшн - шууд ажиллуулахад бэлэн

Суулгах: pip install streamlit plotly
Ажиллуулах: streamlit run mongolian_realestate.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ─── Хуудасны тохиргоо ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Монгол Үл Хөдлөх Хөрөнгийн Үнэ",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS загвар ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Mongolian&family=Inter:wght@300;400;600;700&display=swap');

  html, body, [class*="css"] {
      font-family: 'Inter', sans-serif;
  }

  /* Арын өнгө */
  .stApp {
      background: linear-gradient(135deg, #0f1923 0%, #1a2a3a 60%, #0d1f2d 100%);
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #162130 0%, #1e2f40 100%);
      border-right: 1px solid rgba(99, 179, 237, 0.15);
  }

  /* Metric card */
  .metric-card {
      background: linear-gradient(135deg, rgba(99,179,237,0.12), rgba(49,130,206,0.08));
      border: 1px solid rgba(99, 179, 237, 0.25);
      border-radius: 16px;
      padding: 24px 20px;
      text-align: center;
      backdrop-filter: blur(8px);
  }
  .metric-card .label {
      font-size: 0.78rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #90cdf4;
      margin-bottom: 8px;
  }
  .metric-card .value {
      font-size: 1.9rem;
      font-weight: 700;
      color: #ebf8ff;
      line-height: 1.1;
  }
  .metric-card .sub {
      font-size: 0.8rem;
      color: #63b3ed;
      margin-top: 6px;
  }

  /* Insight хайрцаг */
  .insight-box {
      background: linear-gradient(135deg, rgba(236,201,75,0.10), rgba(183,121,31,0.08));
      border: 1px solid rgba(236,201,75,0.30);
      border-radius: 14px;
      padding: 20px 22px;
  }
  .insight-title {
      font-size: 0.78rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #f6e05e;
      margin-bottom: 10px;
  }
  .insight-text {
      color: #fefcbf;
      font-size: 0.97rem;
      line-height: 1.7;
  }

  /* Range card */
  .range-card {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.10);
      border-radius: 12px;
      padding: 18px;
      text-align: center;
  }
  .range-label { color: #a0aec0; font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase; }
  .range-val   { font-size: 1.35rem; font-weight: 600; margin-top: 6px; }
  .range-low   { color: #fc8181; }
  .range-high  { color: #68d391; }

  /* Хэсгийн гарчиг */
  .section-title {
      font-size: 0.72rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #63b3ed;
      padding-bottom: 6px;
      border-bottom: 1px solid rgba(99,179,237,0.20);
      margin-bottom: 16px;
  }

  h1 { color: #ebf8ff !important; }
  h2, h3 { color: #bee3f8 !important; }
  label, .stSlider label { color: #a0d8f1 !important; }

  div[data-testid="stMetric"] label { color: #90cdf4 !important; }
  div[data-testid="stMetric"] div   { color: #ebf8ff !important; }
</style>
""", unsafe_allow_html=True)

# ─── Константууд ─────────────────────────────────────────────────────────────
BASE_PRICE_PER_SQM = 3_500_000  # төгрөг / м²

LOCATION_INDEX = {
    "Зайсан / Хан-Уул":     1.30,
    "Хотын төв (БГД/СБД)":  1.45,
    "Яармаг":                0.90,
    "БЗД":                   0.95,
    "СХД":                   0.85,
}

CONSTRUCTION_INDEX = {
    "Бүрэн цутгамал":  1.15,
    "Угсармал":         1.00,
    "Тоосгон":          0.88,
}

# ─── SIDEBAR – Оролтын өгөгдлүүд ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ Тооцооллын параметрүүд")
    st.markdown("---")

    # 1. Талбай
    st.markdown('<div class="section-title">📐 Талбай</div>', unsafe_allow_html=True)
    area = st.slider("Нийт талбай (м²)", min_value=10, max_value=500, value=60, step=5)

    st.markdown("---")

    # 2. Байршил
    st.markdown('<div class="section-title">📍 Байршил</div>', unsafe_allow_html=True)
    location = st.selectbox("Бүс сонгох", list(LOCATION_INDEX.keys()))

    st.markdown("---")

    # 3. Давхар
    st.markdown('<div class="section-title">🏢 Давхар</div>', unsafe_allow_html=True)
    total_floors = st.number_input("Барилгын нийт давхар", min_value=2, max_value=30, value=9, step=1)
    floor        = st.slider("Тухайн давхар", min_value=1, max_value=int(total_floors), value=4)

    floor_discount = False
    if floor == 1 or floor == total_floors:
        floor_discount = True
        st.info("⚠️ 1-р эсвэл хамгийн дээд давхар → үнэ **5%** хямдарна.")

    st.markdown("---")

    # 4. Инфляци
    st.markdown('<div class="section-title">📈 Инфляцийн түвшин</div>', unsafe_allow_html=True)
    inflation = st.slider("Жилийн инфляци (%)", min_value=0.0, max_value=25.0, value=11.0, step=0.5)

    st.markdown("---")

    # 5. Барилгын хийц
    st.markdown('<div class="section-title">🧱 Барилгын хийц</div>', unsafe_allow_html=True)
    construction = st.radio("Хийц сонгох", list(CONSTRUCTION_INDEX.keys()))

    st.markdown("---")
    st.caption("© 2025 · Монгол Үл Хөдлөх Хөрөнгийн Тооцоолуур")

# ─── ТООЦООЛОЛ ────────────────────────────────────────────────────────────────
loc_idx   = LOCATION_INDEX[location]
const_idx = CONSTRUCTION_INDEX[construction]
floor_mul = 0.95 if floor_discount else 1.0

# Суурь дүн (инфляцигүй)
base_total = BASE_PRICE_PER_SQM * area * loc_idx * const_idx * floor_mul

# Инфляцийн нэмэгдэл
inflation_addition = base_total * (inflation / 100)

# Нийт үнэ
total_price = base_total + inflation_addition

# Зах зээлийн хэлбэлзэл ±5%
price_low  = total_price * 0.95
price_high = total_price * 1.05

# м² үнэ
price_per_sqm = total_price / area

# Хөрөнгө оруулалтын таамаглал — 8% жилийн өсөлт, 3 жил
growth_rate = 0.08
price_3yr   = total_price * ((1 + growth_rate) ** 3)

# ─── УТИЛИТ функц ─────────────────────────────────────────────────────────────
def fmt(n: float) -> str:
    """Тоог сая.X хэлбэрт хөрвүүлнэ"""
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f} сая ₮"
    return f"{n:,.0f} ₮"

# ─── MAIN DASHBOARD ───────────────────────────────────────────────────────────
st.markdown("# 🏠 Монгол Үл Хөдлөх Хөрөнгийн Үнэ Тооцоолуур")
st.markdown("*Зах зээлийн дундаж үнийн индекс дээр үндэслэсэн баримжаа тооцоолол*")
st.markdown("---")

# ── Metric Cards ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">💰 Нийт баримжаа үнэ</div>
        <div class="value">{fmt(total_price)}</div>
        <div class="sub">{area} м² · {location}</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">📏 1 м² үнэ</div>
        <div class="value">{fmt(price_per_sqm)}</div>
        <div class="sub">Байршил + Хийц тооцсон</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">📊 Байршлын индекс</div>
        <div class="value">×{loc_idx:.2f}</div>
        <div class="sub">Суурь үнэтэй харьцуулсан</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Зах зээлийн дээд/доод үнэ ────────────────────────────────────────────────
st.markdown('<div class="section-title">📉 Зах зээлийн үнийн хэлбэлзэл (±5%)</div>', unsafe_allow_html=True)
rc1, rc2, rc3 = st.columns(3)

with rc1:
    st.markdown(f"""
    <div class="range-card">
        <div class="range-label">Доод үнэ (–5%)</div>
        <div class="range-val range-low">{fmt(price_low)}</div>
    </div>""", unsafe_allow_html=True)

with rc2:
    st.markdown(f"""
    <div class="range-card">
        <div class="range-label">Баримжаа үнэ</div>
        <div class="range-val" style="color:#90cdf4">{fmt(total_price)}</div>
    </div>""", unsafe_allow_html=True)

with rc3:
    st.markdown(f"""
    <div class="range-card">
        <div class="range-label">Дээд үнэ (+5%)</div>
        <div class="range-val range-high">{fmt(price_high)}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Графикууд ─────────────────────────────────────────────────────────────────
chart_col, insight_col = st.columns([3, 2])

with chart_col:
    st.markdown('<div class="section-title">📊 Үнийн бүтцийн задаргаа</div>', unsafe_allow_html=True)

    # Pie chart өгөгдөл
    base_raw        = BASE_PRICE_PER_SQM * area  # байршил, хийцгүй суурь
    location_add    = base_raw * (loc_idx - 1)
    construction_add= base_raw * loc_idx * (const_idx - 1)
    floor_effect    = -base_raw * loc_idx * const_idx * 0.05 if floor_discount else 0
    inflation_part  = inflation_addition

    labels  = ["Суурь үнэ", "Байршлын нэмэгдэл", "Хийцийн нөлөө", "Инфляцийн нөлөө"]
    values  = [base_raw, location_add, construction_add, inflation_part]
    colors  = ["#3182ce", "#38a169", "#d69e2e", "#e53e3e"]

    # Сөрөг утгатай бол (хийц хямд бол) тусгай тайлбар
    if construction_add < 0:
        labels[2] = "Хийцийн хөнгөлөлт"
        values[2] = abs(construction_add)
        colors[2] = "#805ad5"

    fig_pie = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(colors=colors, line=dict(color="#0f1923", width=2)),
        textinfo="label+percent",
        textfont=dict(size=13, color="#ebf8ff"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} ₮<br>%{percent}<extra></extra>",
    ))

    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font=dict(color="#ebf8ff"),
        margin=dict(t=20, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(
            font=dict(color="#a0d8f1", size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        annotations=[dict(
            text=f"<b>{fmt(total_price)}</b>",
            x=0.5, y=0.5, font_size=13,
            showarrow=False, font_color="#ebf8ff",
        )],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Bar chart — байршил харьцуулалт
    st.markdown('<div class="section-title" style="margin-top:8px">🗺️ Байршлуудын үнийн харьцуулалт</div>',
                unsafe_allow_html=True)

    loc_names  = list(LOCATION_INDEX.keys())
    loc_prices = [BASE_PRICE_PER_SQM * area * v * const_idx * floor_mul * (1 + inflation / 100)
                  for v in LOCATION_INDEX.values()]
    bar_colors = ["#63b3ed" if n != location else "#f6e05e" for n in loc_names]

    fig_bar = go.Figure(go.Bar(
        x=loc_names,
        y=loc_prices,
        marker_color=bar_colors,
        text=[f"{v/1_000_000:.1f}M" for v in loc_prices],
        textposition="outside",
        textfont=dict(color="#ebf8ff", size=12),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} ₮<extra></extra>",
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font=dict(color="#a0d8f1"),
        margin=dict(t=30, b=10, l=10, r=10),
        xaxis=dict(tickfont=dict(size=11, color="#a0d8f1"), showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(99,179,237,0.10)",
                   tickfont=dict(color="#718096")),
        bargap=0.3,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with insight_col:
    st.markdown('<div class="section-title">💡 Хөрөнгө оруулалтын таамаглал</div>', unsafe_allow_html=True)

    # 3 жилийн хөгжлийн таамаглал — жил бүрийн утга
    years  = [0, 1, 2, 3]
    prices = [total_price * ((1 + growth_rate) ** y) for y in years]

    fig_line = go.Figure(go.Scatter(
        x=[f"{y} жил" for y in years],
        y=prices,
        mode="lines+markers+text",
        line=dict(color="#f6e05e", width=3),
        marker=dict(size=9, color="#f6e05e", line=dict(color="#0f1923", width=2)),
        text=[f"{p/1_000_000:.1f}M" for p in prices],
        textposition="top center",
        textfont=dict(color="#fefcbf", size=12),
        fill="tozeroy",
        fillcolor="rgba(246,224,94,0.07)",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} ₮<extra></extra>",
    ))
    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font=dict(color="#a0d8f1"),
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, tickfont=dict(color="#a0d8f1")),
        yaxis=dict(showgrid=True, gridcolor="rgba(246,224,94,0.08)",
                   tickfont=dict(color="#718096")),
        height=220,
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Insight текст хайрцаг
    gain = price_3yr - total_price
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">📌 3 жилийн таамаглал (8% өсөлт/жил)</div>
        <div class="insight-text">
            Хэрэв энэ үл хөдлөх хөрөнгийн үнэ жилд <b>8%</b>-иар өсвөл:
            <br><br>
            🏁 <b>Өнөөдрийн үнэ:</b> {fmt(total_price)}<br>
            📅 <b>3 жилийн дараа:</b> {fmt(price_3yr)}<br>
            📈 <b>Нийт өөрчлөлт:</b> +{fmt(gain)}
            <br><br>
            <span style="font-size:0.85rem; color:#b7791f;">
            ⚠️ Энэ нь зөвхөн баримжаа таамаглал бөгөөд зах зээлийн нөхцөлөөс хамаарна.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Нэмэлт мэдээлэл хайрцаг
    st.markdown(f"""
    <div class="insight-box" style="border-color:rgba(99,179,237,0.30); background:linear-gradient(135deg,rgba(99,179,237,0.08),rgba(49,130,206,0.05));">
        <div class="insight-title" style="color:#90cdf4;">📋 Тооцооллын дэлгэрэнгүй</div>
        <div class="insight-text" style="color:#bee3f8; font-size:0.88rem;">
            🔹 Суурь үнэ (м²): {BASE_PRICE_PER_SQM:,} ₮<br>
            🔹 Байршлын индекс: ×{loc_idx:.2f} ({location})<br>
            🔹 Хийцийн индекс: ×{const_idx:.2f} ({construction})<br>
            🔹 Давхрын хасалт: {"–5%" if floor_discount else "үгүй"}<br>
            🔹 Инфляци: {inflation}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "📌 Анхааруулга: Энэхүү тооцоолуур нь зах зээлийн дундаж үзүүлэлтэд үндэслэсэн "
    "баримжаа мэдээлэл өгдөг бөгөөд мэргэжлийн үнэлгээний орлуулалт биш болно. "
    "Бодит гүйлгээ хийхдээ мэргэжлийн үнэлгээч болон хуулийн зөвлөхтэй зөвлөлдөнө үү."
)
