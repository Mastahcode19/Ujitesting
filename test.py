import pickle
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from sklearn.feature_extraction.text import TfidfVectorizer
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

# Load saved model
model_fraud = pickle.load(open('Model/model_fraud.sav', 'rb'))
loaded_vec = TfidfVectorizer(decode_error="replace", vocabulary=set(pickle.load(open("Model/new_selected_feature_tf-idf.sav", "rb"))))

# Function to load detection results from file
def load_detection_results(filename):
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        return pd.DataFrame(columns=['SMS', 'Keterangan'])

# Function to save detection results to file
def save_detection_results(df, filename):
    df.to_csv(filename, index=False)

# Load detection results
detection_results_promo = load_detection_results("Data/hasil_deteksi_promo.csv")
detection_results_penipuan = load_detection_results("Data/hasil_deteksi_penipuan.csv")
detection_results_normal = load_detection_results("Data/hasil_deteksi_normal.csv")

# Sidebar dengan option menu
with st.sidebar:
    page = option_menu(
        "Menu Navigasi",  # Judul menu
        ["Informasi SMS Spam", "Panduan Aplikasi", "Aplikasi Deteksi SMS", "List Hasil Deteksi", "Tentang Saya"],  # Opsi menu
        icons=["info-circle", "book", "search", "table", "person"],  # Ikon untuk opsi menu
        menu_icon="cast",  # Ikon untuk menu secara keseluruhan
        default_index=0,  # Indeks default
        styles={
            "nav-link-selected": {"background-color": "#68ADFF", "color": "white"},
        },
    )
    st.markdown(
        """
        <div style="margin-top: 190px;">  <!-- Sesuaikan margin sesuai kebutuhan -->
            <strong>Versi Aplikasi:</strong> 1.0.0
        <br>
        <small>&copy; 2024 by Kevin</small>
        </div>
        """,
        unsafe_allow_html=True
    )

# Halaman Tentang SMS Spam
if page == "Informasi SMS Spam":
    # ARTIKEL KE-1
    st.title('Apasih SMS Spam itu?')
    st.image("Assets/spamsms.png", caption="Gambar SMS spam", use_column_width=True)
    st.write("<br><br>", unsafe_allow_html=True)

# Halaman Panduan Aplikasi
elif page == "Panduan Aplikasi":
    st.title('Langkah-langkah Penggunaan Aplikasi')

# Halaman Aplikasi Deteksi
elif page == "Aplikasi Deteksi SMS":
    st.title('Sistem Deteksi SMS Spam')
    fraud_detection = ''

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
            fraud_detection = "Mohon Masukkan Pesan Teks SMS"
            st.markdown(
                f"""
                <div style="border: 2px ; border-radius: 15px; padding: 2px; display: flex; align-items: center;background-color: #1F211D ;" >
                <div style="color: #F1C40F; font-size: 25px; margin-left: 10px;"><strong>{fraud_detection}</strong></div>
                <iframe src="https://lottie.host/embed/c006c08e-3a86-47e6-aaae-3e11674c204b/cQiwVs5lkD.json" style="width: 100px; height: 100px;"></iframe>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            predict_fraud = model_fraud.predict(loaded_vec.fit_transform([clean_teks]))

            if predict_fraud == 0:
                fraud_detection = "SMS NORMAL"
                st.markdown(
                    f"""
                    <div style="border: 2px solid #177233; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #D6F9B7;">
                        <div style="flex: 1;">
                            <div style="color: #177233; font-size: 25px; margin-left: 10px;">
                                <strong>{fraud_detection}</strong>
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
                detection_results_normal = pd.concat([detection_results_normal, pd.DataFrame({'SMS': [clean_teks], 'Keterangan': [fraud_detection]})], ignore_index=True)
                save_detection_results(detection_results_normal, "Data/hasil_deteksi_normal.csv")

            elif predict_fraud == 1:
                fraud_detection = "SMS PENIPUAN"
                st.markdown(
                    f"""
                    <div style="border: 2px solid #D90000; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #FF9590;">
                        <div style="flex: 1;">
                            <div style="color: #D90000; font-size: 25px; margin-left: 10px;">
                                <strong>{fraud_detection}</strong>
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
                detection_results_penipuan = pd.concat([detection_results_penipuan, pd.DataFrame({'SMS': [clean_teks], 'Keterangan': [fraud_detection]})], ignore_index=True)
                save_detection_results(detection_results_penipuan, "Data/hasil_deteksi_penipuan.csv")

            elif predict_fraud == 2:
                fraud_detection = "SMS PROMO"
                st.markdown(
                    f"""
                    <div style="border: 2px solid #3773D6; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #C3E6FF;">
                        <div style="flex: 1;">
                            <div style="color: #3773D6; font-size: 25px; margin-left: 10px;">
                                <strong>{fraud_detection}</strong>
                            </div>
                            <div style="background-color: white; border-radius: 5px; padding: 5px; margin-top: 10px;">
                                <ul style="color: #3773D6; font-size: 18px; list-style-type: none; padding: 0; margin: 0;">
                                    <li>Pesan SMS ini adalah spam promo yang menawarkan penawaran khusus</li>
                                    <li>untuk membeli/menggunakan promo yang diberikan</li>
                                </ul>
                            </div>
                        </div>
                        <iframe src="https://lottie.host/embed/62ea7f76-6873-4024-9081-cd6cdf8a7246/amgyWxn0IT.json" style="width: 120px; height: 120px;"></iframe>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                detection_results_promo = pd.concat([detection_results_promo, pd.DataFrame({'SMS': [clean_teks], 'Keterangan': [fraud_detection]})], ignore_index=True)
                save_detection_results(detection_results_promo, "Data/hasil_deteksi_promo.csv")

# Halaman Tabel Dataset
elif page == "List Hasil Deteksi":
    st.title('Tabel Hasil Deteksi SMS')

    # Submenu untuk memilih jenis dataset
    dataset_type = st.selectbox(
        "Pilih Jenis Hasil Deteksi Dataset",
        ["Dataset Promo", "Dataset Penipuan", "Dataset Normal"]
    )

    # Filter dataset berdasarkan jenis yang dipilih
    if dataset_type == "Dataset Promo":
        filtered_data = detection_results_promo
    elif dataset_type == "Dataset Penipuan":
        filtered_data = detection_results_penipuan
    elif dataset_type == "Dataset Normal":
        filtered_data = detection_results_normal

    # Atur ulang indeks DataFrame dan mulai dari 1
    filtered_data.reset_index(drop=True, inplace=True)
    filtered_data.index = filtered_data.index + 1

    # Konfigurasi untuk AgGrid
    gb = GridOptionsBuilder.from_dataframe(filtered_data)
    gridOptions = gb.build()

    # Tampilkan tabel menggunakan AgGrid
    AgGrid(filtered_data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED)

    # Tombol untuk mengunduh data dalam format CSV
    csv = filtered_data.to_csv().encode('utf-8')
    st.download_button(
        label="Unduh data sebagai CSV",
        data=csv,
        file_name=f'{dataset_type.lower().replace(" ", "_")}_data.csv',
        mime='text/csv',
    )

# Halaman Tentang Saya
elif page == "Tentang Saya":
    st.image("Assets/profile2.png", caption="Profile Pembuat Program", use_column_width=True)
