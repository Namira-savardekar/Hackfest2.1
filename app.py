import streamlit as st
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
import io
import requests
import google.genai as genai
from serpapi import GoogleSearch

# -----------------------------------------------------------------------------
# 🔑 SERPAPI KEY SETTING
# -----------------------------------------------------------------------------
SERPAPI_KEY = "abc91768813961c26801b458c141039dbe48d6cf7d1c77262c45234081c795b4"

# -----------------------------------------------------------------------------
# 🎨 EXACT ORIGINAL INTERFACE THEME & CSS (PRESERVED)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="CatalogAI Enterprise Suite", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Full Application Base Layout */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #0e1117 !important;
    }
    
    .stMarkdown, p, span, h1, h2, h3, h4, h5, h6 {
        color: #f3f4f6 !important;
    }

    /* Uploader Layout */
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
    div[data-testid="stFileUploader"] label p {
        color: #00dfd8 !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    
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
    div[data-testid="stFileUploader"] button:hover {
        background-color: #00ff00 !important;
        color: #000000 !important;
        box-shadow: 0px 4px 15px rgba(0, 255, 0, 0.6) !important;
    }

    /* Action Buttons UI */
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

    /* Sidebar Custom Inputs */
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
    
    /* Title Bar Styling */
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
    
    /* Metrics Cards */
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
# 🛡️ UTILITIES & IMAGE FETCHING
# -----------------------------------------------------------------------------
GOOGLE_API_KEY = "AQ.Ab8RN6LJiaXdHWlgF3iOMvL0CbQ25-d0QhBUO5G0klffby4X2Q"
try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception:
    client = None

product_images = {
    "egg": "images/egg.jpg",
    "curd": "images/curd.jpg",
    "paneer": "images/paneer.jpg",
    "milk": "images/milk.jpg",
    "water": "images/water.jpg",
    "snacks": "images/snacks.jpg",
    "cigarette": "images/cigarette.jpg",
    "default": "images/default.jpg"
}

def create_placeholder_image(label_text="Product Asset Ready"):
    img = Image.new('RGB', (400, 400), color='#161b22')
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 390, 390], outline="#00dfd8", width=3)
    d.text((80, 185), "✨ CATALOG VISUAL READY", fill='#ffffff')
    return img

@st.cache_data(show_spinner="Parsing catalog PDF database...")
def parse_pdf_report(uploaded_file_bytes):
    all_data = []
    with pdfplumber.open(io.BytesIO(uploaded_file_bytes)) as pdf:
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
        return df
    return None

@st.cache_data(show_spinner=False)
def fetch_dynamic_product_image(product_name):
    p_lower = str(product_name).lower().strip()
    
    for key, path in product_images.items():
        if key in p_lower and os.path.exists(path):
            try:
                return Image.open(path)
            except Exception:
                pass

    if SERPAPI_KEY and SERPAPI_KEY != "YOUR_SERPAPI_KEY_HERE":
        try:
            search_params = {
                "q": product_name,
                "engine": "google_images",
                "api_key": SERPAPI_KEY,
                "num": "1"
            }
            search = GoogleSearch(search_params)
            results = search.get_dict()
            images_results = results.get("images_results", [])
            
            if images_results:
                image_url = images_results[0].get("original") or images_results[0].get("thumbnail")
                if image_url:
                    res = requests.get(image_url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                    if res.status_code == 200:
                        return Image.open(io.BytesIO(res.content))
        except Exception:
            pass

    return create_placeholder_image(product_name)

# 🎨 FIX 1: HIGH-CONTRAST PROMOTION CARD GENERATOR (HIGH VISIBILITY)
def create_marketing_poster(product_name, category, price, uom="PC"):
    canvas = Image.new('RGB', (800, 800), color='#111827')
    draw = ImageDraw.Draw(canvas)
    
    # Outer Border Glow
    draw.rectangle([15, 15, 785, 785], outline="#00dfd8", width=6)
    draw.rectangle([25, 25, 775, 775], outline="#ff007f", width=3)
    
    # Top Header
    draw.rectangle([40, 40, 760, 110], fill="#ff007f")
    draw.text((80, 55), "⚡ EXCLUSIVE WHOLESALE DEAL ⚡", fill="#ffffff")
    
    # Product Title (Wrapped)
    words = str(product_name).upper().split()
    lines, current_line = [], []
    for word in words:
        if len(" ".join(current_line + [word])) <= 20:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))
    
    y_offset = 160
    for line in lines[:3]: 
        draw.text((60, y_offset), line, fill="#ffffff")
        y_offset += 55
        
    draw.text((60, y_offset + 20), f"Category: {category}", fill="#00dfd8")
    draw.text((60, y_offset + 65), f"Unit: {uom}", fill="#f59e0b")
    
    # Bright Price Banner (High Contrast)
    price_box_y = y_offset + 130
    draw.rectangle([40, price_box_y, 760, price_box_y + 120], fill="#ff007f")
    draw.text((70, price_box_y + 35), f"SPECIAL PRICE: INR {price}/-", fill="#ffffff")
    
    draw.text((60, 720), "🌐 ORDER DIRECTLY VIA CATALOGAI ENTERPRISE", fill="#9ca3af")
    return canvas

def generate_ai_description(product_name, category):
    prompt = f"Write a premium 2-line commercial description for '{product_name}' under '{category}'."
    if client:
        try:
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            return response.text.strip()
        except Exception:
            pass
    return f"Premium industry-standard inventory listing for {product_name} in {category} segment."

# -----------------------------------------------------------------------------
# 📑 FRONTEND LAYOUT
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader("📂 Drag & Drop Inventory or Sales PDF Report Here", type=["pdf"], key="catalog_pdf_uploader_master")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    df = parse_pdf_report(file_bytes)

    if df is not None and not df.empty:
        st.success("✅ Document uploaded and parsed successfully!")

        st.markdown("### 📊 Live Operations Metrics")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="kpi-card-pink"><div>📋 Active SKU Inventory</div><div style="color: #fff; font-size: 24px; font-weight: bold;">{len(df):,} Items</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card-yellow"><div>💰 Gross Document Revenue</div><div style="color: #fff; font-size: 24px; font-weight: bold;">₹ {df["Sales Amount"].sum():,.2f}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card-cyan"><div>📈 Net Realized Yield</div><div style="color: #fff; font-size: 24px; font-weight: bold;">₹ {df["Profit"].sum():,.2f}</div></div>', unsafe_allow_html=True)

        st.sidebar.markdown("### 🎯 Analytics Panel")
        search = st.sidebar.text_input("🔍 Search SKU Name", key="global_search_sku")
        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[filtered_df["Product Name"].str.contains(search, case=False, na=False)]

        category_list = sorted(filtered_df["Category"].dropna().unique())
        category = st.sidebar.selectbox("📂 Department Filters", ["All"] + list(category_list), key="category_selectbox")
        if category != "All":
            filtered_df = filtered_df[filtered_df["Category"] == category]

        st.write("---")
        st.markdown('<div class="table-header-title">📋 Catalog Database Master Index</div>', unsafe_allow_html=True)
        st.dataframe(filtered_df, use_container_width=True)

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
                display_image = fetch_dynamic_product_image(clean_name)
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
                
                # 💬 FIX 2: ENHANCED & COMPREHENSIVE WHATSAPP BROADCAST SCRIPT
                with tab2:
                    if st.button("💬 Generate WhatsApp Broadcast Script", key=f"btn_wa_{clean_name}"):
                        desc_text = st.session_state["current_desc"] if st.session_state["current_desc"] else "Premium quality inventory ready for immediate B2B dispatch."
                        
                        code_val = selected_row.get('Product Code', 'N/A')
                        batch_val = selected_row.get('Batch ID', 'N/A')
                        uom_val = selected_row.get('UOM', 'PC')
                        qty_val = selected_row.get('Quantity', 0)
                        price_val = selected_row.get('Sales Amount', 0)
                        
                        whatsapp_msg = f"""🔥 *EXCLUSIVE B2B STOCK OFFER: {clean_name.upper()}* 🔥

📌 *PRODUCT SPECIFICATIONS:*
• *Item Name:* {clean_name}
• *Product Code SKU:* `{code_val}`
• *Batch ID:* `{batch_val}`
• *Category:* {clean_category}

💰 *COMMERCIAL & PRICING TERMS:*
• *Offer Price:* ₹ {price_val:,.2f} per {uom_val}
• *Available Quantity:* {qty_val} {uom_val}(s) in stock
• *Minimum Order Quantity:* 1 Pack / Box

📝 *KEY HIGHLIGHTS & SUMMARY:*
{desc_text}

⚡ *WHY PARTNER WITH US?*
✅ Guaranteed Fresh Batch & Quality Assurance
✅ Fast Dispatch & B2B Logistics Support
✅ Unbeatable Wholesale Profit Margins

📞 *ORDER NOW:*
Reply *'BOOK NOW'* or call our sales desk directly to secure your stock!
🌐 *CatalogAI Enterprise Suite*"""
                        st.text_area("📋 Copyable WhatsApp Broadcast Message:", value=whatsapp_msg, height=290)
                
                with tab3:
                    if st.button("🖼️ Render Automated Promotion Layout Card", key=f"btn_post_{clean_name}"):
                        uom_val = selected_row.get('UOM', 'PC')
                        poster_img = create_marketing_poster(clean_name, clean_category, selected_row['Sales Amount'], uom_val)
                        buf = io.BytesIO()
                        poster_img.save(buf, format="PNG")
                        st.image(buf.getvalue(), width=450)
            st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------------------------------------------------------
        # 📊 FIX 3: BUSINESS INTELLIGENCE DASHBOARD (NO OVERLAP & NO CUT-OFFS)
        # -----------------------------------------------------------------------------
        st.write("---")
        st.markdown("### 📊 Advanced Business Intelligence System")
        
        c_an1, c_an2 = st.columns(2)
        
        with c_an1:
            if st.button("📈 Initialize Product Revenue Distribution Breakdown", key="revenue_dist_btn"):
                # Filter Top 6 items so bars are neat
                top_products = filtered_df.groupby("Product Name")["Sales Amount"].sum().sort_values(ascending=False).head(6)
                
                fig, ax = plt.subplots(figsize=(7, 4.5))
                fig.patch.set_facecolor('#0e1117')
                ax.set_facecolor('#161b22')
                
                # Bar spacing & width adjust
                bars = ax.bar(range(len(top_products)), top_products.values, color="#ff007f", width=0.45)
                
                # Data labels on top of bars
                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2.0, yval + (max(top_products.values)*0.02), f'₹{yval:,.0f}', ha='center', va='bottom', color='white', fontsize=8, fontweight='bold')

                ax.tick_params(colors='white', labelsize=8)
                ax.set_title("Top Operational Grossing Revenue Pipelines", color="white", weight="bold", fontsize=11, pad=12)
                ax.set_xticks(range(len(top_products)))
                
                # Multi-line wrapped labels to prevent overlap
                labels = ["\n".join(str(name).split()[:3]) for name in top_products.index]
                ax.set_xticklabels(labels, rotation=0, color="white")
                
                plt.tight_layout()
                st.pyplot(fig)
        
        with c_an2:
            if st.button("💰 Initialize Operational Net Margin Audit Layout", key="margin_audit_btn"):
                profit_data = filtered_df.groupby("Product Name")["Profit"].sum().sort_values(ascending=False).head(6)
                
                fig3, ax3 = plt.subplots(figsize=(7, 4.5))
                fig3.patch.set_facecolor('#0e1117')
                ax3.set_facecolor('#161b22')
                
                bars3 = ax3.bar(range(len(profit_data)), profit_data.values, color="#00dfd8", width=0.45)
                
                for bar in bars3:
                    yval = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2.0, yval + (max(profit_data.values)*0.02), f'₹{yval:,.0f}', ha='center', va='bottom', color='white', fontsize=8, fontweight='bold')

                ax3.tick_params(colors='white', labelsize=8)
                ax3.set_title("Top Operational Net Margin Audit Layout", color="white", weight="bold", fontsize=11, pad=12)
                ax3.set_xticks(range(len(profit_data)))
                
                labels3 = ["\n".join(str(name).split()[:3]) for name in profit_data.index]
                ax3.set_xticklabels(labels3, rotation=0, color="white")
                
                plt.tight_layout()
                st.pyplot(fig3)