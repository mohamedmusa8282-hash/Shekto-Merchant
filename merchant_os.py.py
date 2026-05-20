import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import date
import sqlite3

# ==========================================
# 0. إعدادات الصفحة (هجومية وسريعة)
# ==========================================
st.set_page_config(page_title="Shekto Field OS", layout="centered", page_icon="⚖️")

st.markdown("""
    <style>
    .big-bank { font-size:22px !important; font-weight: bold; color: #0D47A1; background-color: #E3F2FD; padding: 10px; border-radius: 5px; text-align: center;}
    .big-cash { font-size:22px !important; font-weight: bold; color: #1B5E20; background-color: #E8F5E9; padding: 10px; border-radius: 5px; text-align: center;}
    .loss-font { font-size:16px !important; font-weight: bold; color: #B71C1C; background-color: #FFEBEE; padding: 10px; border-radius: 5px;}
    .broker-font { font-size:18px !important; font-weight: bold; color: #E65100; background-color: #FFF3E0; padding: 10px; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# تهيئة قاعدة البيانات
# ==========================================
DB_MERCHANT = "shekto_merchant.db"
def init_merchant_db():
    conn = sqlite3.connect(DB_MERCHANT)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS merchant_history 
                 (Date TEXT, Bar_ID TEXT, Gross_Weight REAL, 
                  Sheshena REAL, Equiv_21k REAL, Bank_Value REAL, Cash_Value REAL)''')
    conn.commit()
    conn.close()

init_merchant_db()

# ==========================================
# دالة توليد PDF (مصححة التشفير والمسافات)
# ==========================================
class AssayPDF(FPDF):
    def footer(self):
        self.set_y(-40)
        self.set_font("Arial", 'B', 10)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        self.cell(60, 10, "Shekto Field Assayer", align='C')
        self.cell(70, 10, "Merchant Signature", align='C')
        self.cell(60, 10, "Partner Signature", align='C')

def generate_pdf(bar_id, weight, sheshena, equiv_21, price_bank, price_cash):
    pdf = AssayPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SHEKTO FIELD VALUATION REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Date: {date.today()} | Bar ID: {bar_id}", ln=True)
    pdf.cell(0, 10, f"Gross Weight: {weight} g | Sheshena: {sheshena}/1000", ln=True)
    pdf.cell(0, 10, f"Equivalent Trading Weight (21K): {equiv_21:.2f} g", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Total Value (Bank Transfer): {price_bank:,.0f} SDG", ln=True)
    if price_cash < price_bank:
        pdf.cell(0, 10, f"Total Value (Cash Deal): {price_cash:,.0f} SDG", ln=True)
    
    # السطر الذي تم تصحيحه وضبط مسافته بدقة
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 1. إعدادات الصباح (القائمة الجانبية المخفية)
# ==========================================
with st.sidebar:
    st.header("⚙️ إعدادات السوق اليومية")
    st.caption("أدخلها في الصباح ثم أغلق القائمة.")
    global_oz_usd = st.number_input("سعر الأونصة العالمي ($)", value=2050.0, step=10.0)
    usd_to_sdg = st.number_input("سعر الدولار (موازي)", value=2500.0, step=50.0)
    
    st.divider()
    st.subheader("💵 معامل السيولة (الكاش)")
    cash_discount_pct = st.number_input("نسبة فرق الكاش من بنكك (%)", value=5.0, step=1.0, help="اجعلها 0 إذا كان الكاش مساوياً للتحويل")
    
    st.divider()
    st.subheader("📝 بيانات التوثيق (للطباعة)")
    bar_id = st.text_input("رقم السبيكة", "B-001")

# ==========================================
# المحرك الرياضي الأساسي لأسعار الجرام
# ==========================================
gram_24k_usd = global_oz_usd / 31.103
gram_21k_usd = gram_24k_usd * 0.875
gram_21k_sdg_bank = gram_21k_usd * usd_to_sdg
gram_21k_sdg_cash = gram_21k_sdg_bank * (1 - (cash_discount_pct / 100))

st.title("⚖️ Shekto Field OS")

# ==========================================
# 2. نظام التبويبات الميداني (Tabs)
# ==========================================
tab1, tab2, tab3 = st.tabs(["🧮 التقييم الميداني السريع", "💼 هندسة الصفقة والمحاصصة", "🗄️ الأرشيف والتقارير"])

# ------------------------------------------
# التبويب الأول: التقييم الميداني
# ------------------------------------------
with tab1:
    st.subheader("فحص السبيكة وتسعيرها")
    
    smrc_status = st.checkbox("⚠️ خاضعة لخصم الدولة (SMRC)؟")
    smrc_pct = st.number_input("نسبة خصم SMRC (%)", value=15.0, step=1.0) if smrc_status else 0.0

    col1, col2 = st.columns(2)
    with col1:
        gross_weight = st.number_input("الوزن الإجمالي (جرام)", value=100.0, step=1.0)
    with col2:
        my_sheshena = st.number_input("أسهم الششنة (من 1000)", value=890.0, step=1.0)

    net_gross_weight = gross_weight * (1 - (smrc_pct / 100))
    equiv_weight_21k = net_gross_weight * (my_sheshena / 875.0)
    
    total_bank_value = equiv_weight_21k * gram_21k_sdg_bank
    total_cash_value = equiv_weight_21k * gram_21k_sdg_cash

    st.markdown(f"**الوزن التجاري الصافي (عيار 21):** `{equiv_weight_21k:.2f} جرام`")

    if cash_discount_pct > 0:
        c_bank, c_cash = st.columns(2)
        with c_bank:
            st.markdown(f"<div class='big-bank'>السعر (بنكك)<br>{total_bank_value:,.0f} جنيه</div>", unsafe_allow_html=True)
        with c_cash:
            st.markdown(f"<div class='big-cash'>السعر (كاش)<br>{total_cash_value:,.0f} جنيه</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='big-bank'>السعر العادل الموحد<br>{total_bank_value:,.0f} جنيه</div>", unsafe_allow_html=True)

    st.divider()
    with st.expander("🕵️ رادار تلاعب معمل التاجر", expanded=False):
        merchant_sheshena = st.number_input("ششنة التاجر", value=my_sheshena, step=1.0)
        if merchant_sheshena < my_sheshena:
            lost_shares = my_sheshena - merchant_sheshena
            loss_sdg = (net_gross_weight * (lost_shares / 875.0)) * gram_21k_sdg_bank
            st.markdown(f"<div class='loss-font'>🚨 التاجر خفض {lost_shares} أسهم. الخسارة: {loss_sdg:,.0f} جنيه!</div>", unsafe_allow_html=True)
        elif merchant_sheshena > my_sheshena:
            st.success("✅ تقييم التاجر أعلى من تقييمك (لصالحك).")
        else:
            st.info("⚖️ لا يوجد تلاعب. الششنة متطابقة.")

# ------------------------------------------
# التبويب الثاني: هندسة الصفقة
# ------------------------------------------
with tab2:
    st.subheader("توزيع الكاش (المحاصصة)")
    
    deal_base_value = total_cash_value if cash_discount_pct > 0 else total_bank_value
    st.info(f"إجمالي قيمة الصفقة المعتمدة للتوزيع: **{deal_base_value:,.0f} جنيه**")
    
    st.markdown("#### 🕵️‍♂️ عمولة الوسيط (كاش فوري)")
    broker_pct = st.number_input("نسبة عمولتك كمهندس صفقة (%)", value=1.0, step=0.5)
    broker_cut = deal_base_value * (broker_pct / 100)
    st.markdown(f"<div class='broker-font'>💰 حصتك: {broker_cut:,.0f} جنيه</div>", unsafe_allow_html=True)
    
    distributable_cash = deal_base_value - broker_cut
    
    st.markdown("#### 🤝 قسمة الشركاء (بعد الخصميات والعمولة)")
    c_sp1, c_sp2, c_sp3 = st.columns(3)
    p1 = c_sp1.number_input("صاحب الكرتة (%)", value=50.0, step=5.0)
    p2 = c_sp2.number_input("الطاحونة (%)", value=30.0, step=5.0)
    p3 = c_sp3.number_input("الممول (%)", value=20.0, step=5.0)
    
    if (p1 + p2 + p3) == 100:
        c_res1, c_res2, c_res3 = st.columns(3)
        c_res1.metric("حصة الكرتة", f"{(distributable_cash * p1/100):,.0f}")
        c_res2.metric("حصة الطاحونة", f"{(distributable_cash * p2/100):,.0f}")
        c_res3.metric("حصة الممول", f"{(distributable_cash * p3/100):,.0f}")
    else:
        st.error("🚨 إجمالي النسب يجب أن يكون 100%")

# ------------------------------------------
# التبويب الثالث: الأرشيف والطباعة
# ------------------------------------------
with tab3:
    st.subheader("إدارة السجلات")
    
    c_save, c_print = st.columns(2)
    with c_save:
        if st.button("💾 حفظ العملية في الأرشيف", type="primary"):
            conn = sqlite3.connect(DB_MERCHANT)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO merchant_history VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (str(date.today()), bar_id, gross_weight, my_sheshena, round(equiv_weight_21k,2), round(total_bank_value,0), round(total_cash_value,0)))
            conn.commit()
            conn.close()
            st.success("✅ تم الحفظ بنجاح.")
            
    with c_print:
        pdf_bytes = generate_pdf(bar_id, gross_weight, my_sheshena, equiv_weight_21k, total_bank_value, total_cash_value)
        st.download_button(label="📄 استخراج PDF للطباعة", data=pdf_bytes, file_name=f"Report_{bar_id}.pdf", mime="application/pdf")
    
    st.divider()
    conn = sqlite3.connect(DB_MERCHANT)
    df = pd.read_sql("SELECT * FROM merchant_history", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)
