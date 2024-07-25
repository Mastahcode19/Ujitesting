import pickle
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from sklearn.feature_extraction.text import TfidfVectorizer
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore with Firebase Admin SDK
cred = credentials.Certificate('generatekey.json')  # Replace with your Firebase key file path
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load saved model
model_spam = pickle.load(open('Model/model_spam.sav', 'rb'))
loaded_vec = TfidfVectorizer(decode_error="replace", vocabulary=set(pickle.load(open("Model/new_selected_feature_tf-idf.sav", "rb"))))

# Function to load detection results from Firestore
def load_detection_results(collection_name):
    try:
        docs = db.collection(collection_name).stream()
        data = [doc.to_dict() for doc in docs]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading data from Firestore: {e}")
        return pd.DataFrame(columns=['SMS', 'Keterangan'])

# Function to save detection results to Firestore
def save_detection_results(df, collection_name):
    try:
        collection_ref = db.collection(collection_name)
        # Clear existing documents
        docs = collection_ref.stream()
        for doc in docs:
            doc.reference.delete()
        # Add new documents
        for _, row in df.iterrows():
            collection_ref.add(row.to_dict())
    except Exception as e:
        print(f"Error saving data to Firestore: {e}")

# Load detection results
detection_results_promo = load_detection_results("hasil_deteksi_promo")
detection_results_penipuan = load_detection_results("hasil_deteksi_penipuan")
detection_results_normal = load_detection_results("hasil_deteksi_normal")

# Sidebar dengan option menu
with st.sidebar:
    page = option_menu(
        "Menu Navigasi",
        ["Informasi SMS Spam", "Panduan Aplikasi", "Aplikasi Deteksi SMS", "List Hasil Deteksi", "Tentang Saya"],
        icons=["info-circle", "book", "search", "table", "person"],
        menu_icon="cast",
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#68ADFF", "color": "white"}},
    )
    st.markdown(
        """
        <div style="margin-top: 190px;">
            <strong>Versi Aplikasi:</strong> 1.0.0
            <br>
            <small>&copy; 2024 by Kevin</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Halaman Tentang SMS Spam
if page == "Informasi SMS Spam":
    st.title('Apasih SMS Spam itu?')
    st.markdown(
        """
        <div style="text-align: justify;">
            Kalian pernah bertanya-tanya sebenernya SMS spam itu apasih?apakah berbahaya?. Weets, tenang dulu ya gess karena disini saya akan membahas lebih lanjut tentang topik ini, let's gooo.
            Secara umum SMS spam ialah sebuah pesan teks yang tidak diinginkan yang dikirim secara massal kepada banyak penerima.
            Pesan ini sering kali berisi penawaran promosi, penipuan, atau informasi yang tidak relevan. SMS spam dapat mengganggu dan menghabiskan sumber daya pada perangkat penerima.
            Maka dari itu dengan teknologi deteksi SMS spam, kita dapat memfilter dan mengelompokkan pesan-pesan ini untuk mengurangi dampak negatifnya.
        </div>
        <br><br><br>
        """,
        unsafe_allow_html=True,
    )
    st.image("Assets/spamsms.png", caption="Gambar SMS spam", use_column_width=True)
    st.write("<br><br>", unsafe_allow_html=True)

    st.title('Jenis Dan Tujuan SMS Spam')
    st.image("Assets/notification.gif", caption="Animasi notifikasi masuk", use_column_width=True)
    st.write("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: justify;">
            Berdasarkan penjelasan tentang arti spam yang telah disampaikan, berikut adalah beberapa tujuan spam yang perlu kita ketahui:
        <br>
        <h3>1. Skema Penipuan</h3>
        <p>Beberapa SMS spam dirancang untuk menipu penerima. Misalnya, pesan dapat mengklaim bahwa penerima telah memenangkan hadiah atau undian, meminta mereka untuk membayar biaya untuk mengklaim hadiah tersebut. Ini bisa berujung pada kerugian finansial bagi penerima.</p>
        <h3>2. Phishing</h3>
        <p>SMS phishing berusaha mendapatkan informasi sensitif, seperti nomor kartu kredit atau kata sandi. Pesan ini mungkin mengarahkan penerima ke situs web palsu yang terlihat mirip dengan situs resmi, di mana mereka diminta untuk memasukkan informasi pribadi.</p>
        <h3>3. Jenis Iklan Yang Menggangu</h3>
        <p>Banyak bisnis menggunakan SMS spam untuk mengirimkan iklan tanpa izin penerima. Ini sering kali dianggap sebagai gangguan dan dapat merusak reputasi pengirim.</p>
        <h3>4. Penawaran Jasa Keuangan</h3>
        <p>Beberapa pesan menawarkan layanan keuangan, seperti pinjaman atau investasi. Banyak dari layanan ini mungkin tidak sah atau memiliki syarat yang merugikan.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("<br><br>", unsafe_allow_html=True)

    st.title('Dampak Buruk SMS Spam')
    st.image("Assets/thinking.gif", caption="Animasi memikirkan jenis pesan", use_column_width=True)
    st.markdown(
        """
        <div style="text-align: justify;">
            Seperti yang kita ketahui bahwa pesan SMS yang kita terima memiliki berbagai jenis pesan-pesan yang masuk. Namun kalian tau ngga gess? Bahwasanya dari semua pesan yang masuk itu sudah tidak dipungkiri lagi terdapat jenis pesan spam. Terus emangnya kenapa min? Kan itu hanya sebuah teks pesan saja? Yup… kalian bener sekali itu hanya sebuah teks pesan biasa saja, tapi dibalik pesan spam yang masuk itu di antaranya memiliki dampak yang buruk jika kita selalu waspada akan isi pesan tersebut.
        <br><br>
        Belum lagi banyaknya modus penipuan yang hanya dikirim melalui SMS, oleh karena itu mimin hanya ingin menyampaikan beberapa dampak buruk SMS spam pada perorangan, di antaranya sebagai berikut ini:
        <br>
        <ol>
            <li>Spam sering digunakan untuk phishing, di mana penipu mencoba mendapatkan informasi pribadi seperti nomor kartu kredit, kata sandi, dan data sensitif lainnya.</li>
            <li>Beberapa spam berisi tautan atau lampiran yang mengandung malware, yang dapat menginfeksi perangkat penerima dan mencuri data pribadi.</li>
            <li>Individu yang tertipu oleh spam yang menjanjikan hadiah, lotere, atau tawaran keuangan palsu bisa mengalami kerugian finansial yang signifikan.</li>
            <li>Spam yang menggunakan identitas seseorang untuk mengirim pesan dapat merusak hubungan pribadi jika penerima merasa terganggu atau terancam.</li>
            <li>Menggunakan sumber daya perangkat elektronik secara berlebihan sehingga mengurangi efisiensi penggunaannya.</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Halaman Panduan Aplikasi
elif page == "Panduan Aplikasi":
    st.title('Langkah-langkah Penggunaan Aplikasi')
    st.write("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: justify;">
            Agar kalian tidak kebingungan cara menggunakan aplikasi deteksinya mimin akan kasih tau nih biar kalian ngga kebingungan. Sebenernya simple sih, tapi tidak apa-apa biar kalian paham dan sekalian baca-baca 😁. Nah kalau begitu berikut langkah-langkah penggunaan aplikasi:
        <br><br>
        <ol start="1">
            <li>Untuk memulai cara penggunaan aplikasi deteksi spam, langkah pertama kita pilih menu pada bagian “Aplikasi Deteksi SMS” pada halaman sidebar menu navigasi dan kita dapat melihat sebuah tampilan dari sistem deteksi SMS spam seperti gambar dibawah ini:</li>
        </ol>
        </div>
        <br>
        """,
        unsafe_allow_html=True,
    )
    st.image("Assets/LANGKAH1.PNG", caption="Panduan pertama", use_column_width=True)
    st.markdown(
        """
        <br><br>
        <div style="text-align: justify;">
        <ol start="2">
            <li>Kemudian sekarang kita akan memasukkan sebuah teks pesan SMS kita yang ada di HP kita masing-masing dengan cara copy and paste ke dalam form input text “Masukkan SMS”. Lalu kita tinggal klik button “Deteksi” untuk melakukan proses deteksi SMS spam.</li>
        </ol>
        </div>
        <br>
        """,
        unsafe_allow_html=True,
    )
    st.image("Assets/LANGKAH2.PNG", caption="Panduan kedua", use_column_width=True)
    st.markdown(
        """
        <br><br>
        <div style="text-align: justify;">
        <ol start="3">
            <li>Setelah kita klik button deteksi maka hasil dari pesan tersebut akan muncul seperti pada gambar di bawah ini. Hasil deteksi akan menampilkan sebuah keterangan dari teks SMS tersebut apakah merupakan pesan SMS normal, promosi, atau bahkan penipuan.</li>
        </ol>
        </div>
        <br>
        """,
        unsafe_allow_html=True,
    )
    st.image("Assets/LANGKAH3.PNG", caption="Panduan ketiga", use_column_width=True)
    st.markdown(
        """
        <br><br>
        <div style="text-align: justify;">
        <ol start="4">
            <li>Untuk melihat hasil dari deteksi sebelumnya maka kita bisa melihatnya dengan cara klik menu navigasi pada bagian “List Hasil Deteksi” maka hasil deteksi akan tampil dengan keterangan dari hasil deteksi sebelumnya seperti gambar dibawah ini.</li>
        </ol>
        </div>
        <br>
        """,
        unsafe_allow_html=True,
    )
    st.image("Assets/LANGKAH4.PNG", caption="Panduan keempat", use_column_width=True)

# Halaman Aplikasi Deteksi SMS
elif page == "Aplikasi Deteksi SMS":
    st.title('Aplikasi Deteksi SMS Spam')
    st.write("<br>", unsafe_allow_html=True)
    input_text = st.text_area("Masukkan SMS")

    if st.button("Deteksi"):
        if input_text:
            # Transform the input text
            input_text_transformed = loaded_vec.transform([input_text])
            # Predict the class (0 for normal, 1 for spam)
            prediction = model_spam.predict(input_text_transformed)
            if prediction[0] == 0:
                result = "Normal"
            elif prediction[0] == 1:
                result = "Penipuan"
            else:
                result = "Promosi"
            st.write(f"Hasil Deteksi: {result}")

            # Simpan hasil ke dalam Firestore
            result_data = {"SMS": input_text, "Keterangan": result}
            if result == "Promosi":
                db.collection("hasil_deteksi_promo").add(result_data)
            elif result == "Penipuan":
                db.collection("hasil_deteksi_penipuan").add(result_data)
            else:
                db.collection("hasil_deteksi_normal").add(result_data)
        else:
            st.write("Masukkan teks SMS untuk dideteksi.")

# Halaman List Hasil Deteksi
elif page == "List Hasil Deteksi":
    st.title('List Hasil Deteksi SMS')
    st.write("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Promosi", "Penipuan", "Normal"])

    with tab1:
        st.write("Hasil Deteksi Promosi")
        AgGrid(detection_results_promo)

    with tab2:
        st.write("Hasil Deteksi Penipuan")
        AgGrid(detection_results_penipuan)

    with tab3:
        st.write("Hasil Deteksi Normal")
        AgGrid(detection_results_normal)

# Halaman Tentang Saya
elif page == "Tentang Saya":
    st.title('Tentang Saya')
    st.image("Assets/kevin.jpg", caption="Foto Kevin", use_column_width=True)
    st.write("Nama saya Kevin, seorang mahasiswa Teknik Informatika. Saya memiliki minat dalam pengembangan aplikasi berbasis web dan machine learning. Aplikasi ini adalah proyek pribadi saya untuk membantu mendeteksi SMS spam dan memberikan informasi kepada pengguna tentang bahaya SMS spam.")
