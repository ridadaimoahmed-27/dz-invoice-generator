import streamlit as st
from fpdf import FPDF
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منصة الفواتير الاحترافية", layout="centered")

# --- إضافة لمسة CSS لديكور احترافي ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .invoice-box {
        padding: 20px;
        border: 1px solid #eee;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- عنوان الصفحة ---
st.markdown("<h1> 📄 نظام الفواتير الذكي </h1>", unsafe_allow_html=True)
st.write("قم بتوليد فواتير احترافية لعملائك بسهولة.")

# --- قسم رفع الشعار (Logo) ---
st.sidebar.header("إعدادات الهوية")
uploaded_logo = st.sidebar.file_uploader("ارفع شعار المحل (Logo)", type=["png", "jpg", "jpeg"])

# --- واجهة إدخال البيانات ---
with st.container():
    st.markdown('<div class="invoice-box">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        seller_name = st.text_input("اسم المحل / البائع")
        seller_phone = st.text_input("رقم الهاتف")
    with col2:
        customer_name = st.text_input("اسم الزبون")
        invoice_date = st.date_input("تاريخ الفاتورة")

    st.divider()

    # إدخال السلع
    st.subheader("تفاصيل السلع")
    num_items = st.number_input("عدد السلع المختلفة", min_value=1, value=1, step=1)
    
    items = []
    total_price = 0.0

    for i in range(num_items):
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            name = st.text_input(f"اسم السلعة {i+1}")
        with c2:
            qty = st.number_input(f"الكمية", min_value=1, value=1, key=f"qty_{i}")
        with c3:
            price = st.number_input(f"السعر (دج)", min_value=0.0, value=0.0, key=f"pr_{i}")
        
        line_total = qty * price
        items.append({"name": name, "qty": qty, "price": price, "total": line_total})
        total_price += line_total

    st.divider()
    
    # حسابات إضافية للتأكد
    shipping = st.number_input("تكلفة التوصيل (دج)", min_value=0.0, value=0.0)
    final_total = total_price + shipping

    st.markdown(f"### المجموع الإجمالي: **{final_total:,.2f} دج**")
    st.markdown('</div>', unsafe_allow_html=True)

# --- وظيفة إنشاء PDF ---
def create_pdf(logo, seller, phone, customer, date, items, total, shipping):
    pdf = FPDF()
    pdf.add_page()
    
    # إضافة الشعار إذا وُجد
    if logo:
        with open("temp_logo.png", "wb") as f:
            f.write(logo.getbuffer())
        pdf.image("temp_logo.png", 10, 8, 33)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="INVOICE / فاتورة", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(100, 10, txt=f"Seller: {seller}")
    pdf.cell(100, 10, txt=f"Date: {date}", ln=True)
    pdf.cell(100, 10, txt=f"Phone: {phone}", ln=True)
    pdf.cell(100, 10, txt=f"Customer: {customer}", ln=True)
    
    pdf.ln(10)
    # جدول السلع
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(90, 10, "Item", 1, 0, 'C', True)
    pdf.cell(30, 10, "Qty", 1, 0, 'C', True)
    pdf.cell(30, 10, "Price", 1, 0, 'C', True)
    pdf.cell(40, 10, "Total", 1, 1, 'C', True)

    for item in items:
        pdf.cell(90, 10, item['name'], 1)
        pdf.cell(30, 10, str(item['qty']), 1, 0, 'C')
        pdf.cell(30, 10, f"{item['price']:.2f}", 1, 0, 'C')
        pdf.cell(40, 10, f"{item['total']:.2f}", 1, 1, 'C')

    pdf.ln(5)
    pdf.cell(150, 10, "Shipping:", 0, 0, 'R')
    pdf.cell(40, 10, f"{shipping:.2f} DZD", 1, 1, 'C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10, "Final Total:", 0, 0, 'R')
    pdf.cell(40, 10, f"{total+shipping:.2f} DZD", 1, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- زر استخراج الفاتورة ---
if st.button("تأكيد الحسابات واستخراج PDF"):
    if not seller_name or not customer_name:
        st.error("يرجى ملء بيانات البائع والزبون!")
    else:
        pdf_bytes = create_pdf(uploaded_logo, seller_name, seller_phone, customer_name, invoice_date, items, total_price, shipping)
        st.success("تم تأكيد الحسابات بنجاح!")
        st.download_button(label="📥 تحميل الفاتورة (PDF)",
                           data=pdf_bytes,
                           file_name=f"invoice_{customer_name}.pdf",
                           mime="application/pdf")
