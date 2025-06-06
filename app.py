import streamlit as st
import pandas as pd
import numpy as np
from persiantools.jdatetime import JalaliDate

st.set_page_config(page_title="ارزیابی موفقیت کمپین تبلیغاتی", layout="centered")

# استایل کامل
st.markdown("""
    <style>
    * {
        font-family: Tahoma, sans-serif !important;
    }
    html, body, [class*="css"] {
        background-color: #3a3a3a;
        color: #ffffff;
    }
    .block-container {
        padding: 2rem;
    }
    .stButton > button {
        color: white !important;
        background-color: #2563eb !important;
    }
    a {
        color: #93c5fd !important;
        text-decoration: none;
    }
    .centered {
        text-align: center;
    }
    h1 {
        font-size: 1.5rem !important;
    }
    section[data-testid="stExpander"] div[role="button"] {
        background-color: #4a4a4a !important;
        color: white !important;
    }
    section[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
        background-color: #4a4a4a !important;
        padding: 1rem;
        border-radius: 0 0 8px 8px;
    }
    </style>
""", unsafe_allow_html=True)

# لوگو بالا
st.image("logo.png", width=100)

# تاریخ شمسی + روز هفته
today = JalaliDate.today()
weekday_map = {
    'Saturday': 'شنبه', 'Sunday': 'یکشنبه', 'Monday': 'دوشنبه', 'Tuesday': 'سه‌شنبه',
    'Wednesday': 'چهارشنبه', 'Thursday': 'پنج‌شنبه', 'Friday': 'جمعه'
}
weekday_fa = weekday_map[today.to_gregorian().strftime('%A')]
st.markdown(f"تاریخ امروز: {weekday_fa}، {today.strftime('%Y/%m/%d')}")

st.title("تحلیل موفقیت کمپین تبلیغاتی")

mode = st.radio("نوع تحلیل را انتخاب کنید:", ["تحلیل یک کمپین", "مقایسه چند کمپین"])

criteria = {
    "میزان دیده‌شدن": "تعداد افرادی که کمپین را مشاهده کرده‌اند",
    "نرخ درگیری مخاطب": "درصد تعامل کاربران با کمپین (لایک، کلیک، کامنت و...)",
    "نرخ تبدیل": "درصد تبدیل مخاطب به اقدام هدف (خرید، ثبت‌نام و...)",
    "کیفیت پیام": "وضوح و اثرگذاری پیام کمپین",
    "هماهنگی با برند": "همراستایی پیام و ظاهر کمپین با هویت برند",
    "واکنش رسانه‌ای": "بازتاب کمپین در رسانه‌ها و منابع خبری",
    "بازخورد مخاطبان": "نظرات، برداشت‌ها و احساسات کاربران",
    "بازده هزینه‌ای": "نسبت نتیجه‌گیری کمپین به هزینه انجام‌شده"
}

st.sidebar.header("وزن شاخص‌ها")
weights = []
for crit, desc in criteria.items():
    w = st.sidebar.slider(f"{crit}", 0.0, 1.0, 0.125, 0.01, help=desc)
    weights.append(w)
weights = np.array(weights)
weights = weights / np.sum(weights)

num = 1 if mode == "تحلیل یک کمپین" else st.number_input("تعداد کمپین‌ها برای مقایسه", min_value=2, max_value=10, value=2)
campaigns = []

st.subheader("امتیازدهی به کمپین‌ها (۰ تا ۱۰)")
for i in range(num):
    with st.expander(f"کمپین {i+1}"):
        name = st.text_input(f"نام کمپین {i+1}", key=f"name_{i}")
        scores = []
        for crit in criteria:
            score = st.slider(f"{crit}", 0, 10, 5, key=f"{crit}_{i}")
            scores.append(score)
        campaigns.append({"name": name, "scores": scores})

if st.button("تحلیل نهایی"):
    results = []
    for c in campaigns:
        weighted_score = np.dot(c["scores"], weights)
        final_score = round((weighted_score / 10) * 100, 2)
        results.append({"نام": c["name"], "امتیاز نهایی (از ۱۰۰)": final_score, "raw_scores": c["scores"]})

    df = pd.DataFrame(results).sort_values("امتیاز نهایی (از ۱۰۰)", ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    df.insert(0, "رتبه", df.index)

    st.success("نتایج تحلیل:")
    st.dataframe(df[["رتبه", "نام", "امتیاز نهایی (از ۱۰۰)"]])
    st.bar_chart(df.set_index("نام")["امتیاز نهایی (از ۱۰۰)"])

    top = df.iloc[0]
    top_name = top["نام"]
    top_scores = df.iloc[0]["raw_scores"]

    st.markdown("### تحلیل شاخص‌های قوی")
    strong = []
    for crit, val in zip(criteria.keys(), top_scores):
        if val >= 7:
            if val == 10:
                strong.append(f"در شاخص {crit} امتیاز عالی و کامل کسب شده است.")
            else:
                strong.append(f"در شاخص {crit} عملکرد بسیار خوبی دیده می‌شود.")

    if strong:
        st.markdown("شاخص‌های برجسته این کمپین:")
        for s in strong:
            st.markdown(f"- {s}")

    st.markdown(f"امتیاز نهایی: {top['امتیاز نهایی (از ۱۰۰)']} از ۱۰۰")
    st.markdown("---")
    st.markdown("تمام حقوق این نرم‌افزار متعلق به شرکت <a href='https://inohub.ir' target='_blank'>اینوهاب</a> است.", unsafe_allow_html=True)
    st.image("logo.png", width=100)
