# Dokumentasi Dataset AI4I 2020 Predictive Maintenance

## 1. Informasi Dataset

| Informasi          | Keterangan                                                   |
| ------------------ | ------------------------------------------------------------ |
| Nama Dataset       | AI4I 2020 Predictive Maintenance Dataset                     |
| Nama File          | `ai4i2020.csv`                                               |
| Format             | CSV (Comma-Separated Values)                                 |
| Jumlah Data        | 10.000 baris                                                 |
| Jumlah Kolom       | 14 kolom                                                     |
| Jenis Data         | Data tabular                                                 |
| Domain             | Predictive Maintenance / Pemeliharaan Prediktif              |
| Jenis Permasalahan | Klasifikasi, clustering, dan simulasi reinforcement learning |

## 2. Deskripsi Dataset

AI4I 2020 Predictive Maintenance Dataset merupakan dataset yang berisi informasi karakteristik dan kondisi operasional mesin. Dataset ini dapat digunakan untuk mempelajari pemeliharaan prediktif, yaitu pendekatan untuk mengidentifikasi potensi kegagalan mesin berdasarkan data operasionalnya.

Dataset mencakup informasi mengenai suhu udara, suhu proses, kecepatan rotasi, torsi, dan keausan alat (*tool wear*). Dataset juga menyediakan label kegagalan mesin dan beberapa indikator jenis kegagalan.

Dalam proyek ini, dataset digunakan untuk eksplorasi data (*Exploratory Data Analysis* atau EDA) serta mempersiapkan data untuk pendekatan supervised learning, unsupervised learning, dan simulasi reinforcement learning.

## 3. Deskripsi Atribut

| No. | Nama Kolom                | Deskripsi                                                                          |
| --: | ------------------------- | ---------------------------------------------------------------------------------- |
|   1 | `UDI`                     | Identifikasi unik untuk setiap baris data.                                         |
|   2 | `Product ID`              | Identitas produk atau unit mesin.                                                  |
|   3 | `Type`                    | Kategori produk berdasarkan tipe L, M, atau H.                                     |
|   4 | `Air temperature [K]`     | Suhu udara dalam satuan Kelvin.                                                    |
|   5 | `Process temperature [K]` | Suhu proses dalam satuan Kelvin.                                                   |
|   6 | `Rotational speed [rpm]`  | Kecepatan rotasi dalam putaran per menit.                                          |
|   7 | `Torque [Nm]`             | Torsi mesin dalam Newton-meter.                                                    |
|   8 | `Tool wear [min]`         | Durasi keausan alat dalam menit.                                                   |
|   9 | `Machine failure`         | Label yang menunjukkan apakah terjadi kegagalan mesin: 0 = tidak gagal, 1 = gagal. |
|  10 | `TWF`                     | Indikator *Tool Wear Failure*.                                                     |
|  11 | `HDF`                     | Indikator *Heat Dissipation Failure*.                                              |
|  12 | `PWF`                     | Indikator *Power Failure*.                                                         |
|  13 | `OSF`                     | Indikator *Overstrain Failure*.                                                    |
|  14 | `RNF`                     | Indikator *Random Failure*.                                                        |

## 4. Struktur dan Karakteristik Data

Berdasarkan pemeriksaan awal terhadap dataset:

* Jumlah observasi: 10.000 baris.
* Jumlah atribut: 14 kolom.
* Nilai kosong (*missing values*): tidak ditemukan.
* Baris duplikat: tidak ditemukan.
* Target `Machine failure` memiliki distribusi kelas yang tidak seimbang (*class imbalance*).

Distribusi target `Machine failure`:

|     Kelas | Keterangan              |     Jumlah | Persentase |
| --------: | ----------------------- | ---------: | ---------: |
|         0 | Tidak terjadi kegagalan |      9.661 |     96,61% |
|         1 | Terjadi kegagalan       |        339 |      3,39% |
| **Total** |                         | **10.000** |   **100%** |

Ketidakseimbangan kelas perlu diperhatikan ketika membangun model klasifikasi. Evaluasi model sebaiknya tidak hanya menggunakan akurasi, tetapi juga precision, recall, F1-score, dan confusion matrix.

## 5. Tujuan Penggunaan Dataset

### 5.1 Supervised Learning

Supervised learning digunakan untuk memprediksi apakah mesin mengalami kegagalan berdasarkan fitur operasionalnya.

* **Target:** `Machine failure`
* **Fitur awal:** `Type`, `Air temperature [K]`, `Process temperature [K]`, `Rotational speed [rpm]`, `Torque [Nm]`, dan `Tool wear [min]`.
* **Pendekatan:** klasifikasi biner.

Kolom identitas seperti `UDI` dan `Product ID` tidak digunakan sebagai fitur prediksi utama. Indikator kegagalan seperti `TWF`, `HDF`, `PWF`, `OSF`, dan `RNF` juga perlu dipertimbangkan secara hati-hati karena dapat menyebabkan kebocoran target (*target leakage*), terutama jika tujuan model adalah memprediksi kegagalan sebelum terjadi.

### 5.2 Unsupervised Learning

Unsupervised learning digunakan untuk menemukan pola atau kelompok kondisi operasional mesin tanpa menggunakan label kegagalan sebagai masukan model.

Fitur yang dapat digunakan:

* `Air temperature [K]`
* `Process temperature [K]`
* `Rotational speed [rpm]`
* `Torque [Nm]`
* `Tool wear [min]`

Standardisasi fitur dapat dilakukan sebelum clustering karena masing-masing fitur memiliki rentang dan satuan yang berbeda. Metode yang dapat dieksplorasi antara lain K-Means, DBSCAN, dan PCA untuk visualisasi berdimensi lebih rendah.

Label `Machine failure` dapat digunakan setelah clustering untuk membantu menginterpretasikan kelompok yang terbentuk, bukan sebagai masukan clustering.

### 5.3 Reinforcement Learning

Dataset ini tidak secara langsung menyediakan struktur pengalaman berurutan yang lengkap untuk reinforcement learning. Oleh karena itu, penggunaannya memerlukan simulasi lingkungan pemeliharaan mesin.

Contoh rancangan simulasi:

* **State:** kondisi operasional mesin.
* **Action:** melanjutkan operasi atau melakukan pemeliharaan.
* **Reward:** nilai yang mempertimbangkan biaya pemeliharaan dan konsekuensi kegagalan.
* **Next state:** kondisi mesin setelah tindakan.
* **Done:** penanda berakhirnya episode simulasi.

Simulasi perlu mendefinisikan aturan transisi kondisi mesin dan fungsi reward secara eksplisit. Hasilnya tidak boleh langsung dianggap sebagai bukti kinerja pada mesin nyata.

## 6. Tahapan Preprocessing

Tahapan preprocessing yang dapat diterapkan meliputi:

1. Memuat dataset CSV ke dalam DataFrame.
2. Memeriksa dimensi, tipe data, dan nama kolom.
3. Memeriksa nilai kosong dan data duplikat.
4. Memeriksa distribusi kelas target.
5. Memisahkan fitur dan target sesuai tujuan analisis.
6. Mengubah fitur kategorikal `Type` menjadi representasi numerik, misalnya dengan one-hot encoding, untuk model yang memerlukannya.
7. Melakukan standardisasi fitur numerik jika diperlukan.
8. Membagi data menjadi data latih dan data uji untuk supervised learning dengan mempertahankan proporsi kelas target.
9. Menghindari penggunaan indikator kegagalan sebagai fitur apabila dapat membocorkan informasi target.

Parameter preprocessing, seperti scaler, harus dipelajari dari data latih saja dan kemudian diterapkan pada data uji untuk menghindari kebocoran data.

## 7. Catatan Analisis

Hasil EDA digunakan untuk memahami distribusi fitur, hubungan antarvariabel, kemungkinan pencilan (*outlier*), serta distribusi kegagalan mesin.

Temuan dari EDA tidak secara otomatis membuktikan hubungan sebab-akibat. Selain itu, hasil evaluasi model perlu mempertimbangkan ketidakseimbangan kelas dan kesesuaian fitur dengan tujuan prediksi.

## 8. File Terkait

* `ai4i2020.csv` — dataset yang dianalisis.
* `EDA_AI4I2020_Machine_Failure.ipynb` — notebook eksplorasi data dan analisis awal.
* `README.md` — dokumentasi dataset.

## 9. Sumber Dataset

AI4I 2020 Predictive Maintenance Dataset.

Referensi: [UCI Machine Learning Repository](https://archive.ics.uci.edu/).
