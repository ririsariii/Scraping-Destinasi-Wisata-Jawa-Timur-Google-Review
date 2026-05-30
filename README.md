# 🗺️ Google Maps Reviews Scraper - Destinasi Wisata Jawa Timur

Sistem web scraping untuk mengumpulkan ulasan (reviews) dari Google Maps pada berbagai destinasi wisata populer di Jawa Timur menggunakan **Python**, **Selenium**, dan **ChromeDriver**.

Data yang berhasil dikumpulkan akan disimpan dalam format CSV dan dapat digunakan untuk kebutuhan:

* Sentiment Analysis
* Aspect-Based Sentiment Analysis (ABSA)
* Text Mining
* Opinion Mining
* Analisis Kepuasan Wisatawan
* Penelitian Pariwisata

---

## 📌 Fitur

* Scraping review Google Maps secara otomatis
* Mendukung hingga **1500 review per destinasi**
* Auto scroll hingga review habis dimuat
* Auto expand tombol **"Selengkapnya"**
* Mengambil informasi:

  * ID Review
  * Nama Destinasi
  * Kategori Wisata
  * Kota
  * Isi Review
  * Rating
  * Tanggal Review
  * Platform
* Deduplikasi review otomatis
* Penanganan CAPTCHA secara manual
* Menyimpan hasil ke file CSV

---

## 🏞️ Destinasi Wisata yang Dikumpulkan

### Batu

* Jatim Park 1
* Jatim Park 2
* Jatim Park 3
* Batu Night Spectacular
* Museum Angkut
* Batu Secret Zoo

### Banyuwangi

* Kawah Ijen
* De Djawatan Forest

### Situbondo

* Taman Nasional Baluran

### Probolinggo

* Gunung Bromo
* Air Terjun Madakaripura

### Surabaya

* Tunjungan Plaza
* Taman Bungkul
* Monumen Kapal Selam
* Masjid Al-Akbar

### Pasuruan

* Taman Safari Prigen

### Lumajang

* Air Terjun Tumpak Sewu

---

## 📂 Struktur Output

File hasil scraping:

```text
wisata_jatim_reviews.csv
```

Kolom yang dihasilkan:

| Kolom     | Keterangan                |
| --------- | ------------------------- |
| id        | UUID unik review          |
| destinasi | Nama destinasi wisata     |
| kategori  | Kategori wisata           |
| kota      | Lokasi kota               |
| review    | Isi ulasan pengguna       |
| rating    | Rating bintang            |
| tanggal   | Tanggal review            |
| platform  | Sumber data (Google Maps) |

Contoh data:

| destinasi     | rating | review                                         |
| ------------- | ------ | ---------------------------------------------- |
| Jatim Park 1  | 5      | Tempat wisata yang sangat menarik dan edukatif |
| Gunung Bromo  | 5      | Pemandangan sunrise sangat indah               |
| Taman Bungkul | 4      | Taman kota yang nyaman untuk keluarga          |

---

## ⚙️ Requirements

Python 3.9+

Install library yang dibutuhkan:

```bash
pip install selenium webdriver-manager pandas
```

---

## 🚀 Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/username/google-maps-review-scraper-jatim.git
```

### 2. Masuk ke Folder Project

```bash
cd google-maps-review-scraper-jatim
```

### 3. Install Dependencies

```bash
pip install selenium webdriver-manager pandas
```

### 4. Jalankan Program

```bash
python scrape_gmaps_selenium.py
```

---

## 📊 Konfigurasi

Parameter utama dapat diubah pada bagian konfigurasi:

```python
MAX_REVIEWS_PER_TEMPAT = 1500
SCROLL_PAUSE = 2.5
JEDA_ANTAR_TEMPAT = 5
```

| Parameter              | Fungsi                               |
| ---------------------- | ------------------------------------ |
| MAX_REVIEWS_PER_TEMPAT | Jumlah maksimum review per destinasi |
| SCROLL_PAUSE           | Jeda saat scrolling                  |
| JEDA_ANTAR_TEMPAT      | Jeda perpindahan antar destinasi     |

---

## ⚠️ Catatan Penting

* Jangan menggerakkan atau mengklik browser saat scraping berjalan.
* Jika muncul CAPTCHA Google, selesaikan secara manual pada browser yang terbuka.
* Program akan menunggu hingga CAPTCHA selesai.
* Tekan `Ctrl + C` kapan saja untuk menghentikan scraping dan menyimpan data yang sudah berhasil dikumpulkan.

---

## 📈 Contoh Ringkasan Output

```text
Jatim Park 1            1500
Jatim Park 2            1500
Museum Angkut           1500
Gunung Bromo            1500
Taman Bungkul           1200
```

---

## 🛠️ Teknologi yang Digunakan

* Python
* Selenium
* ChromeDriver
* WebDriver Manager
* Pandas
* Google Maps

---

## 📚 Penggunaan Data

Dataset yang dihasilkan dapat digunakan untuk:

* Sentiment Analysis
* Aspect-Based Sentiment Analysis (ABSA)
* Machine Learning
* Natural Language Processing (NLP)
* Analisis Kepuasan Wisatawan
* Penelitian Pariwisata Jawa Timur

---

## 👩‍💻 Author

**Yuliani Purwitasari**

GitHub: https://github.com/ririsariii

---

## 📄 License

Project ini dibuat untuk kebutuhan penelitian dan pembelajaran akademik.

Pastikan penggunaan data hasil scraping tetap mematuhi Terms of Service Google Maps dan kebijakan penggunaan data yang berlaku.
