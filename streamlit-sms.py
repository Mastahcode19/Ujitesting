import pickle
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from streamlit_option_menu import option_menu
from sklearn.feature_extraction.text import TfidfVectorizer
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

# Cek apakah Firebase sudah diinisialisasi
if not firebase_admin._apps:
    cred = credentials.Certificate('generatekey.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Fungsi untuk menyimpan hasil deteksi ke Firestore
def save_detection_to_firestore(sms_text, label):
    doc_ref = db.collection('sms_detections').document()
    doc_ref.set({
        'SMS': sms_text,
        'Keterangan': label
    })

# Fungsi untuk mengambil    i Firestore
def load_detection_results_from_firestore():
    docs = db.collection('sms_detections').stream()
    data = []
    for doc in docs:
        data.append(doc.to_dict())
    return pd.DataFrame(data)

# Load saved model
model_spam = pickle.load(open('Model/model_spam.sav', 'rb'))
loaded_vec = TfidfVectorizer(decode_error="replace", vocabulary=set(pickle.load(open("Model/new_selected_feature_tf-idf.sav", "rb"))))

# Sidebar dengan option menu
with st.sidebar:
    page = option_menu(
        "Menu Navigasi",
        ["Informasi SMS Spam","Panduan Aplikasi", "Aplikasi Deteksi SMS", "List Hasil Deteksi","Tentang Saya"],
        icons=["info-circle","book","search", "table","person"],
        menu_icon="cast",
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": "#68ADFF", "color": "white"},
        },
    )
    st.markdown(
        """
        <div style="margin-top: 190px;">
            <strong>Versi Aplikasi:</strong> 1.0.0
        <br>
        <small>&copy; 2024 by Kevin</small>
        </div>
        """,
        unsafe_allow_html=True
    )

# Halaman Tentang SMS Spam
if page == "Informasi SMS Spam":
    st.title('Apasih SMS Spam itu?')
    st.markdown(
        """
        <div style="text-align: justify;">
            Kalian pernah bertanya-tanya sebenernya SMS spam itu apasih?apakah berbahaya?.Weets,tenang dulu ya gess karena disini saya akan membahas lebih lanjut tentang topik ini,let's gooo.
            Secara umum SMS spam ialah sebuah pesan teks yang tidak diinginkan yang dikirim secara massal kepada banyak penerima.
            Pesan ini sering kali berisi penawaran promosi, penipuan, atau informasi yang tidak relevan. SMS spam dapat mengganggu dan menghabiskan sumber daya pada perangkat penerima.
            Maka dari itu dengan teknologi deteksi SMS spam, kita dapat memfilter dan mengelompokkan pesan-pesan ini untuk mengurangi dampak negatifnya.
        </div>
        <br><br><br>
        """,
        unsafe_allow_html=True
    )
    st.image("Assets/spamsms.png", caption="Gambar SMS spam", use_column_width=True)
    st.write("<br><br>", unsafe_allow_html=True)

# Halaman Aplikasi Deteksi
elif page == "Aplikasi Deteksi SMS":
    st.title('Sistem Deteksi SMS Spam')
    spam_detection = ''

    # Mengatur styling text_area
    st.markdown(
        """
        <style>
        textarea {
            font-size: 20px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    sms_text = st.text_area("Masukkan Teks SMS Dibawah Ini")
    if st.button('Cek Deteksi'):
        clean_teks = sms_text.strip()

        if clean_teks == "":
            spam_detection = "Mohon Masukkan Pesan Teks SMS"
            st.markdown(
            f"""
            <div style="border: 2px ; border-radius: 15px; padding: 2px; display: flex; align-items: center;background-color: #1F211D ;" >
            <div style="color: #F1C40F; font-size: 25px; margin-left: 10px;"><strong>{spam_detection}</strong></div>
            <iframe src="https://lottie.host/embed/c006c08e-3a86-47e6-aaae-3e11674c204b/cQiwVs5lkD.json" style="width: 100px; height: 100px;"></iframe>
            </div>
            """,
            unsafe_allow_html=True
            )
        else:
            predict_spam = model_spam.predict(loaded_vec.fit_transform([clean_teks]))

            if predict_spam == 0:
                spam_detection = "SMS NORMAL"
                st.markdown(
                f"""
                <div style="border: 2px solid #177233; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #D6F9B7;">
                    <div style="flex: 1;">
                        <div style="color: #177233; font-size: 25px; margin-left: 10px;">
                            <strong>{spam_detection}</strong>
                        </div>
                        <div style="background-color: white; border-radius: 5px; padding: 5px; margin-top: 10px;">
                            <ul style="color: #177233; font-size: 18px; list-style-type: none; padding: 0; margin: 0;">
                                <li>Pesan SMS ini bukan termasuk pesan spam promo/penipuan</li>
                                <li>melainkan pesan normal pada umumnya dan aman untuk ditanggapi</li>
                            </ul>
                        </div>
                    </div>
                    <iframe src="https://lottie.host/embed/94ef5ba2-ff8e-4b1a-868b-6a6a926cfca0/D3oNNvId2Y.json" style="width: 120px; height: 120px;"></iframe>
                </div>
                """,
                unsafe_allow_html=True
                )
                save_detection_to_firestore(clean_teks, spam_detection)

            elif predict_spam == 1:
                spam_detection = "SMS PENIPUAN"
                st.markdown(
                f"""
                <div style="border: 2px solid #D90000; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #FF9590;">
                    <div style="flex: 1;">
                        <div style="color: #D90000; font-size: 25px; margin-left: 10px;">
                            <strong>{spam_detection}</strong>
                        </div>
                        <div style="background-color: white; border-radius: 5px; padding: 5px; margin-top: 10px;">
                            <ul style="color: #F00B00; font-size: 18px; list-style-type: none; padding: 0; margin: 0;">
                                <li>Pesan SMS ini terindikasi pesan spam penipuan</li>
                                <li>dikarenakan terdapat informasi yang mencurigakan</li>
                            </ul>
                        </div>
                    </div>
                    <iframe src="https://lottie.host/embed/66044930-6b4e-4546-9765-4fcf4a98ca37/U6WsPr1BHE.json" style="width: 120px; height: 120px;"></iframe>
                </div>
                """,
                unsafe_allow_html=True
                )
                save_detection_to_firestore(clean_teks, spam_detection)

            elif predict_spam == 2:
                spam_detection = "SMS PROMO"
                st.markdown(
                f"""
                <div style="border: 2px solid #3773D6; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #C3E6FF;">
                    <div style="flex: 1;">
                        <div style="color: #3773D6; font-size: 25px; margin-left: 10px;">
                            <strong>{spam_detection}</strong>
                        </div>
                        <div style="background-color: white; border-radius: 5px; padding: 5px; margin-top: 10px;">
                            <ul style="color: #3773D6; font-size: 18px; list-style-type: none; padding: 0; margin: 0;">
                                <li>Pesan SMS ini merupakan pesan spam promo</li>
                                <li>dikarenakan terdapat unsur promosi</li>
                            </ul>
                        </div>
                    </div>
                    <iframe src="https://lottie.host/embed/4d0dffb0-b61f-4869-bb7e-d474d930d1e6/jFdCdWlZ9i.json" style="width: 120px; height: 120px;"></iframe>
                </div>
                """,
                unsafe_allow_html=True
                )
                save_detection_to_firestore(clean_teks, spam_detection)

# Halaman List Hasil Deteksi
elif page == "List Hasil Deteksi":
    st.title('List Hasil Deteksi SMS Spam')

    results_df = load_detection_results_from_firestore()
    
if not results_df.empty:
    gb = GridOptionsBuilder.from_dataframe(results_df)
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_selection('single')
    grid_options = gb.build()
    grid_response = AgGrid(
        results_df,
        gridOptions=grid_options,
        data_return_mode='FILTERED',
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=True,
        height=400,
        reload_data=True
    )
    
else:
    st.write("Belum ada hasil deteksi yang tersimpan.")

# Halaman Panduan Aplikasi
elif page == "Panduan Aplikasi":
    st.title('Panduan Aplikasi')
    st.markdown(
        """
        <div style="text-align: justify;">
            1. Pada halaman "Aplikasi Deteksi SMS", masukkan teks SMS yang ingin Anda deteksi pada kotak yang telah disediakan.
            <br><br>
            2. Tekan tombol "Cek Deteksi" untuk mengetahui hasil deteksi apakah SMS tersebut termasuk dalam kategori spam atau tidak.
            <br><br>
            3. Hasil deteksi akan ditampilkan dengan informasi tambahan terkait.
            <br><br>
            4. Anda bisa melihat riwayat hasil deteksi pada halaman "List Hasil Deteksi".
            <br><br>
            5. Informasi mengenai SMS spam dapat Anda temukan pada halaman "Informasi SMS Spam".
        </div>
        <br><br>
        """,
        unsafe_allow_html=True
    )

# Halaman Tentang Saya
elif page == "Tentang Saya":
    st.title('Tentang Saya')
    st.markdown(
        """
        <div style="text-align: justify;">
            Halo! Saya Kevin, seorang developer aplikasi yang berfokus pada pengembangan sistem deteksi SMS spam. 
            Saya memiliki minat yang tinggi dalam pengembangan perangkat lunak dan keamanan siber. 
            Aplikasi ini dibuat untuk membantu masyarakat dalam mengidentifikasi pesan-pesan SMS yang tidak diinginkan dan berpotensi merugikan.
            Terima kasih telah menggunakan aplikasi ini!
        </div>
        <br><br>
        """,
        unsafe_allow_html=True
    )
    st.image("Assets/profile.png", caption="Kevin", use_column_width=True)
    st.write("<br><br>", unsafe_allow_html=True)
