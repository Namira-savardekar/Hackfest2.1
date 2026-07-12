import streamlit as st
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
import io
import google.genai as genai

# -----------------------------------------------------------------------------
# 🎨 DYNAMIC STRUCTURAL HIGH-CONTRAST GLOW THEME
# -----------------------------------------------------------------------------
st.set_page_config(page_title="CatalogAI Enterprise Suite", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Full Application Base Layout */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #0e1117 !important;
    }
    
    /* Standard Text Target Visibility overrides */
    .stMarkdown, p, span, h1, h2, h3, h4, h5, h6 {
        color: #f3f4f6 !important;
    }

    /* 📂 PERFECT DARK STYLE UPLOAD CONTAINER FIX (Screenshot 2 Fix) */
    div[data-testid="stFileUploader"] {
        background-color: #161b22 !important;
        border: 2px dashed #00dfd8 !important;
        border-radius: 12px;
        padding: 20px !important;
    }
    div[data-testid="stFileUploader"] [data-testid="stUploadDropzone"] {
        background-color: #161b22 !important;
        border: none !important;
    }
    /* Explicit Label text for drag and drop descriptor */
    div[data-testid="stFileUploader"] label p {
        color: #00dfd8 !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    
    /* 🔴 THE UPLOAD ACTION BUTTON: STAYS RED */
    div[data-testid="stFileUploader"] button {
        background-color: #ff0000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 20px !important;
        font-weight: bold !important;
        box-shadow: 0px 4px 10px rgba(255, 0, 0, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    /* 🟢 UPLOAD HOVER DETECTOR STATE */
    div[data-testid="stFileUploader"] button:hover {
        background-color: #00ff00 !important;
        color: #000000 !important;
        box-shadow: 0px 4px 15px rgba(0, 255, 0, 0.6) !important;
    }

    /* 🎯 GLOBAL WORKBENCH WORKSPACE BUTTON STYLING (SHINY NEON STYLE - Screenshot 1 Fix) */
    div.stButton > button {
        background: linear-gradient(135deg, #7928ca 0%, #ff007f 100%) !important;
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 15px rgba(121, 40, 202, 0.4) !important;
        text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.6) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        width: 100% !important;
        display: block !important;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        box-shadow: 0 6px 20px rgba(255, 0, 127, 0.6) !important;
        transform: translateY(-2px);
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }

    /* Sidebar controls contrast enhancements */
    div[data-testid="stSidebar"] div[data-testid="stTextInput"] input,
    div[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border: 2px solid #7928ca !important;
        border-radius: 8px !important;
    }
    div[data-testid="stSidebar"] label {
        color: #00dfd8 !important;
        font-weight: bold !important;
    }
    
    /* Main Layout Branding Items */
    .main-title-container { text-align: center; padding: 15px 0; }
    .main-title {
        font-size: 45px; font-weight: 900;
        background: linear-gradient(90deg, #ff007f 0%, #7928ca 40%, #00dfd8 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    .neon-pulse-line {
        height: 4px; width: 200px; background: linear-gradient(90deg, #ff007f, #00dfd8); 
        margin: 10px auto 20px auto; border-radius: 10px;
    }
    
    /* Segment block wrappers */
    .kpi-card-pink { background: #161b22; padding: 20px; border-radius: 14px; border-top: 5px solid #ff007f; }
    .kpi-card-yellow { background: #161b22; padding: 20px; border-radius: 14px; border-top: 5px solid #f59e0b; }
    .kpi-card-cyan { background: #161b22; padding: 20px; border-radius: 14px; border-top: 5px solid #00dfd8; }
    .product-box {
        background: #11141a; padding: 25px; border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.06); border-left: 6px solid #7928ca; margin-bottom: 25px;
    }
    .table-header-title {
        background: linear-gradient(135deg, #1f2937, #111827); padding: 12px 20px; 
        border-radius: 8px; border-left: 5px solid #00dfd8; margin-bottom: 15px;
        font-weight: 800; font-size: 20px; color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-title-container">
    <div class="main-title">⚡ CatalogAI Enterprise Suite ⚡</div>
    <div style="color: #9ca3af; font-size: 15px; margin-top: 5px;">Instantly transform flat B2B supply reports into high-converting digital catalogs and visual assets.</div>
    <div class="neon-pulse-line"></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 🤖 BACKEND UTILITIES DATA MATRIX
# -----------------------------------------------------------------------------
GOOGLE_API_KEY = "AQ.Ab8RN6LJiaXdHWlgF3iOMvL0CbQ25-d0QhBUO5G0klffby4X2Q"
try:
    client = genai.Client(api_key=API_KEY)
except Exception:
    client = None

product_images = {
    "milk": "images/milk.jpg", "paneer": "images/paneer.jpg",
    "egg": "images/egg.jpg", "water": "images/water.jpg",
    "snacks": "images/snacks.jpg", "curd": "images/curd.jpg"
}

def get_product_image(product_name):
    p_lower = str(product_name).lower()
    for key, path in product_images.items():
        if key in p_lower:
            return path
    return None

def create_placeholder_image(label_text="Product Asset Ready"):
    img = Image.new('RGB', (400, 400), color='#161b22')
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 390, 390], outline="#00dfd8", width=3)
    d.text((90, 185), "✨ CATALOG VISUAL READY", fill='#ffffff')
    return img

def create_marketing_poster(product_name, category, price):
    canvas = Image.new('RGB', (600, 600), color='#0e1117')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([20, 20, 580, 580], outline="#ff007f", width=4)
    draw.text((50, 55), "EXCLUSIVE DEALS", fill="#f59e0b")
    
    words = product_name.upper().split()
    lines = []
    current_line = []
    for word in words:
        if len(" ".join(current_line + [word])) <= 22:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    
    y_offset = 110
    for line in lines[:3]: 
        draw.text((50, y_offset), line, fill="white")
        y_offset += 45
        
    draw.text((50, 270), f"Category: {category}", fill="#93c5fd")
    draw.rectangle([50, 330, 390, 420], fill="#ef4444")
    draw.text((75, 355), f"SPECIAL PRICE: INR {price}/-", fill="white")
    return canvas

def generate_ai_description(product_name, category):
    prompt = f"Write a premium 2-line commercial description for '{product_name}' under '{category}'."
    if client and API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        try:
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            return response.text.strip()
        except Exception:
            pass
    return f"Premium industry-standard inventory listing for {product_name} in {category} segment."

# -----------------------------------------------------------------------------
# 📑 FRONTEND RUNTIME LAYER
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader("📂 Drag & Drop Inventory or Sales PDF Report Here", type=["pdf"], key="catalog_pdf_uploader_master")

if uploaded_file is not None:
    st.success("✅ Document uploaded and parsed successfully!")
    
    all_data = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table:
                    all_data.append(row)

    if all_data:
        all_data = all_data[1:]
        headers = ["Product Code", "Batch ID", "Product Name", "Category", "UOM", "Quantity", "Sales Amount", "Purchase Amount", "Profit"]
        df = pd.DataFrame(all_data, columns=headers)

        numeric_cols = ["Quantity", "Sales Amount", "Purchase Amount", "Profit"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Operational Metrics
        st.markdown("### 📊 Live Operations Metrics")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="kpi-card-pink"><div>📋 Active SKU Inventory</div><div style="color: #fff; font-size: 24px; font-weight: bold;">{len(df):,} Items</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card-yellow"><div>💰 Gross Document Revenue</div><div style="color: #fff; font-size: 24px; font-weight: bold;">₹ {df["Sales Amount"].sum():,.2f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card-cyan"><div>📈 Net Realized Yield</div><div style="color: #fff; font-size: 24px; font-weight: bold;">₹ {df["Profit"].sum():,.2f}</div></div>', unsafe_allow_html=True)

        # Sidebar Filters Matrix
        st.sidebar.markdown("### 🎯 Analytics Panel")
        search = st.sidebar.text_input("🔍 Search SKU Name", key="global_search_sku")
        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[filtered_df["Product Name"].str.contains(search, case=False, na=False)]

        category_list = sorted(filtered_df["Category"].dropna().unique())
        category = st.sidebar.selectbox("📂 Department Filters", ["All"] + list(category_list), key="category_selectbox")
        if category != "All":
            filtered_df = filtered_df[filtered_df["Category"] == category]

        # Table Section
        st.write("---")
        st.markdown('<div class="table-header-title">📋 Catalog Database Master Index</div>', unsafe_allow_html=True)
        st.dataframe(filtered_df, use_container_width=True)

        # -----------------------------------------------------------------------------
        # 💎 THE CONTENT STUDIO GENERATOR WORKBENCH
        # -----------------------------------------------------------------------------
        st.write("---")
        st.markdown("### 💎 Content Studio Workbench")

        unique_products = filtered_df["Product Name"].dropna().unique()
        
        if len(unique_products) > 0:
            selected_product = st.selectbox("Choose a target SKU to generate assets:", unique_products, key="selected_product_dropdown")
            selected_row = filtered_df[filtered_df["Product Name"] == selected_product].iloc[0]

            clean_name = " ".join(str(selected_row['Product Name']).split())
            clean_category = " ".join(str(selected_row['Category']).split())

            st.markdown('<div class="product-box">', unsafe_allow_html=True)
            left, right = st.columns([1, 2.2])

            with left:
                image_path = get_product_image(selected_product)
                if image_path and os.path.exists(image_path):
                    try: display_image = Image.open(image_path)
                    except Exception: display_image = create_placeholder_image(clean_name)
                else:
                    display_image = create_placeholder_image(clean_name)
                st.image(display_image, use_container_width=True)

            with right:
                st.markdown(f"<h2 style='color: #ff007f; margin-top: 0; font-weight:800;'>🛍️ {clean_name}</h2>", unsafe_allow_html=True)
                st.markdown(f"**Segment Class:** <span style='color:#00dfd8; font-weight:bold;'>{clean_category}</span>  |  **Stock Capacity:** <span style='color:#f59e0b; font-weight:bold;'>{selected_row['Quantity']} units</span>", unsafe_allow_html=True)
                
                sm1, sm2, sm3 = st.columns(3)
                sm1.metric("Retail Price (MRP)", f"₹ {selected_row['Sales Amount']:,}")
                sm2.metric("Procurement Cost", f"₹ {selected_row['Purchase Amount']:,}")
                sm3.metric("Net Margin Gain", f"₹ {selected_row['Profit']:,}")

                if "current_desc" not in st.session_state or st.session_state.get("last_prod") != clean_name:
                    st.session_state["current_desc"] = ""
                    st.session_state["last_prod"] = clean_name
                
                st.write("---")
                tab1, tab2, tab3 = st.tabs(["🔄 AI Description Engine", "📱 Omnichannel Copywriter", "🎨 Marketing Visual Studio"])
                
                with tab1:
                    if st.button("✨ Synthesize Automated E-commerce Copy", key=f"btn_desc_{clean_name}"):
                        st.session_state["current_desc"] = generate_ai_description(clean_name, clean_category)
                    if st.session_state["current_desc"]:
                        st.info(st.session_state["current_desc"])
                
                with tab2:
                    if st.button("💬 Generate WhatsApp Broadcast Script", key=f"btn_wa_{clean_name}"):
                        desc_text = st.session_state["current_desc"] if st.session_state["current_desc"] else "Special high priority offers live now!"
                        whatsapp_msg = f"""*🔥 LIVE OFFER: {clean_name.upper()}!*\n\n📦 *Item:* {clean_name}\n💰 *Price:* ₹ {selected_row['Sales Amount']:,}\n\n✨ *Insights:* {desc_text}"""
                        st.text_area("📋 Copyable Text Template:", value=whatsapp_msg, height=120)
                
                with tab3:
                    if st.button("🖼️ Render Automated Promotion Layout Card", key=f"btn_post_{clean_name}"):
                        poster_img = create_marketing_poster(clean_name, clean_category, selected_row['Sales Amount'])
                        buf = io.BytesIO()
                        poster_img.save(buf, format="PNG")
                        st.image(buf.getvalue(), width=310)
            st.markdown('</div>', unsafe_allow_html=True)

        # Business Intelligence System Graphs
        st.write("---")
        st.markdown("### 📊 Advanced Business Intelligence System")
        c_an1, c_an2 = st.columns(2)
        with c_an1:
            if st.button("📈 Initialize Product Revenue Distribution Breakdown", key="revenue_dist_btn"):
                top_products = filtered_df.groupby("Product Name")["Sales Amount"].sum().sort_values(ascending=False).head(8)
                fig, ax = plt.subplots(figsize=(6, 3.5))
                fig.patch.set_facecolor('#0e1117')
                ax.set_facecolor('#1f2937')
                ax.bar(range(len(top_products)), top_products.values, color="#ff007f")
                ax.tick_params(colors='white')
                ax.set_title("Top Operational Grossing Revenue Pipelines", color="white", weight="bold")
                ax.set_xticks(range(len(top_products)))
                ax.set_xticklabels(top_products.index, rotation=22, ha="right", color="white")
                st.pyplot(fig)
        
        with c_an2:
            if st.button("💰 Initialize Operational Net Margin Audit Layout", key="margin_audit_btn"):
                profit_data = filtered_df.groupby("Product Name")["Profit"].sum().sort_values(ascending=False).head(8)
                fig3, ax3 = plt.subplots(figsize=(6, 3.5))
                fig3.patch.set_facecolor('#0e1117')
                ax3.set_facecolor('#1f2937')
                ax3.bar(range(len(profit_data)), profit_data.values, color="#00dfd8")
                ax3.tick_params(colors='white')
                ax3.set_title("Top High Density Yield Matrix SKUs", color="white", weight="bold")
                ax3.set_xticks(range(len(profit_data)))
                ax3.set_xticklabels(profit_data.index, rotation=22, ha="right", color="white")
                st.pyplot(fig3)