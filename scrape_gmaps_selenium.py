"""
Scraper Google Maps Reviews - Destinasi Wisata Jawa Timur
Menggunakan Selenium + Chrome (Windows)
Output: wisata_jatim_reviews.csv

Requirements:
    pip install selenium webdriver-manager pandas

Cara pakai:
    1. pip install selenium webdriver-manager pandas
    2. python scrape_gmaps_selenium.py
"""

import time
import uuid
import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# KONFIGURASI
# ============================================================
MAX_REVIEWS_PER_TEMPAT = 1500
SCROLL_PAUSE            = 2.5
JEDA_ANTAR_TEMPAT       = 5

# ============================================================
# DATA DESTINASI — lengkap 13 tempat
# ============================================================
DESTINASI = [
    ("Jatim Park 1 Batu",                "Wisata Hiburan",         "Batu"),
    ("Jatim Park 2 Batu",                "Wisata Hiburan",         "Batu"),
    ("Jatim Park 3 Batu",                "Wisata Hiburan",         "Batu"),
    ("Batu Night Spectacular",           "Wisata Hiburan",         "Batu"),
    ("Museum Angkut Batu",               "Wisata Budaya/Edukasi",  "Batu"),
    ("Batu Secret Zoo",                  "Wisata Alam/Hiburan",    "Batu"),
    ("Kawah Ijen Banyuwangi",            "Wisata Alam",            "Banyuwangi"),
    ("De Djawatan Forest Banyuwangi",    "Wisata Alam",            "Banyuwangi"),
    ("Taman Nasional Baluran Situbondo", "Wisata Alam",            "Situbondo"),
    ("Gunung Bromo Probolinggo",         "Wisata Alam",            "Probolinggo"),
    ("Air Terjun Madakaripura",          "Wisata Alam",            "Probolinggo"),
    ("Tunjungan Plaza Surabaya",         "Wisata Belanja",         "Surabaya"),
    ("Taman Bungkul Surabaya",           "Taman Kota",             "Surabaya"),
    ("Monumen Kapal Selam Surabaya",     "Wisata Sejarah",         "Surabaya"),
    ("Masjid Al-Akbar Surabaya",         "Wisata Religi",          "Surabaya"),
    ("Taman Safari Prigen",              "Wisata Alam/Hiburan",    "Pasuruan"),
    ("Air Terjun Tumpak Sewu Lumajang",  "Wisata Alam",            "Lumajang"),
]

# ============================================================
# SETUP DRIVER
# ============================================================
def buat_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1280,900")
    options.add_argument("--lang=id-ID")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


# ============================================================
# HELPER
# ============================================================
def cek_captcha(driver):
    if "sorry" in driver.current_url or "captcha" in driver.page_source.lower():
        print("\n⚠️  CAPTCHA terdeteksi! Selesaikan di browser lalu tekan Enter...")
        input("    Tekan Enter > ")


def nama_bersih_dari(query: str) -> str:
    """Buang nama kota di akhir query untuk kolom destinasi."""
    for suffix in [" Batu", " Surabaya", " Probolinggo",
                   " Banyuwangi", " Pasuruan", " Lumajang"]:
        if query.endswith(suffix):
            return query[: -len(suffix)].strip()
    return query.strip()


# ============================================================
# BUKA HALAMAN + KLIK TAB ULASAN
# ============================================================
def buka_dan_klik_ulasan(driver, query: str) -> bool:
    """
    Strategi:
    1. Buka URL langsung ke halaman tempat via search
    2. Tunggu panel kiri muncul
    3. Klik hasil pertama jika masih di halaman daftar
    4. Scroll sedikit agar tab Ulasan muncul
    5. Klik tab Ulasan dengan beberapa selector fallback
    """
    url = "https://www.google.com/maps/search/" + query.replace(" ", "+")
    driver.get(url)
    time.sleep(4)
    cek_captcha(driver)

    # Jika masih di halaman daftar hasil pencarian, klik tempat pertama
    try:
        kartu = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.hfpxzc"))
        )
        kartu.click()
        time.sleep(4)
    except TimeoutException:
        pass  # sudah langsung ke halaman tempat

    cek_captcha(driver)

    # Scroll panel kiri sedikit agar semua tab (termasuk Ulasan) render
    try:
        panel = driver.find_element(By.CSS_SELECTOR, "div[role='main']")
        driver.execute_script("arguments[0].scrollTop = 300;", panel)
        time.sleep(1.5)
    except Exception:
        pass

    # Daftar selector tab Ulasan — dari yang paling spesifik ke umum
    SELECTORS = [
        (By.CSS_SELECTOR,  "button.hh2c6[aria-label*='Ulasan']"),
        (By.CSS_SELECTOR,  "button[role='tab'][aria-label*='Ulasan']"),
        (By.CSS_SELECTOR,  "button[role='tab'][aria-label*='Reviews']"),
        (By.XPATH,         "//button[@role='tab' and contains(@aria-label,'Ulasan')]"),
        (By.XPATH,         "//button[@role='tab' and contains(@aria-label,'Reviews')]"),
        # Fallback: cari semua tab dan pilih yang teksnya "Ulasan"
        (By.XPATH,         "//button[contains(@aria-label,'Ulasan')]"),
    ]

    for by, sel in SELECTORS:
        try:
            el = WebDriverWait(driver, 6).until(EC.presence_of_element_located((by, sel)))
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", el)
            time.sleep(2.5)
            print(f"  ✓ Tab Ulasan diklik via: {sel[:60]}")
            return True
        except (TimeoutException, NoSuchElementException):
            continue

    # Last resort: print semua button yang ada untuk debugging
    buttons = driver.find_elements(By.TAG_NAME, "button")
    tab_candidates = [
        f"aria='{b.get_attribute('aria-label')}' text='{b.text.strip()[:30]}'"
        for b in buttons
        if b.get_attribute("role") == "tab" or "lasan" in (b.get_attribute("aria-label") or "")
    ]
    print(f"  ✗ Tab Ulasan tidak ditemukan. Tab yang ada: {tab_candidates[:5]}")
    return False


# ============================================================
# SCROLL + EKSTRAK SEKALIGUS (fix virtual DOM)
# ============================================================
def scroll_dan_ekstrak(driver, nama: str, kategori: str, kota: str, max_reviews: int) -> list:
    PANEL_SELECTORS = [
        "div.m6QErb[aria-label*='Ulasan']",
        "div.m6QErb[aria-label*='Reviews']",
        "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",
        "div.m6QErb",
    ]
    scrollable = None
    for sel in PANEL_SELECTORS:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            scrollable = els[-1]
            break

    if not scrollable:
        print("  ⚠ Panel scroll tidak ditemukan")
        return []

    semua_rows = {}   # key: review_id atau teks[:80], value: dict — deduplikasi otomatis
    prev_count = 0
    stagnant = 0

    def ambil_kartu_visible():
        """Expand + ekstrak semua kartu yang ada di DOM sekarang."""
        # Expand "Selengkapnya" yang visible
        for sel in ["button.w8nwRe.kyuRq", "button[aria-label*='Selengkapnya']"]:
            for btn in driver.find_elements(By.CSS_SELECTOR, sel):
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.15)
                except Exception:
                    pass

        kartu_list = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
        if not kartu_list:
            kartu_list = driver.find_elements(By.CSS_SELECTOR, "div[data-review-id]")

        for kartu in kartu_list:
            try:
                # Ambil review_id sebagai key deduplikasi
                review_id = kartu.get_attribute("data-review-id") or ""

                teks = ""
                for s in ["span.wiI7pd", "span.HgLLd", "span.MyEned"]:
                    try:
                        teks = kartu.find_element(By.CSS_SELECTOR, s).text.strip()
                        if teks: break
                    except NoSuchElementException:
                        pass

                # Fallback key kalau data-review-id kosong
                key = review_id if review_id else teks[:80]
                if not key or key in semua_rows:
                    continue  # skip duplikat

                rating = ""
                for s in ["span.kvMYJc", "span[aria-label*='bintang']", "span[aria-label*='star']"]:
                    try:
                        aria = kartu.find_element(By.CSS_SELECTOR, s).get_attribute("aria-label") or ""
                        nums = re.findall(r"\d+(?:[.,]\d+)?", aria)
                        if nums:
                            rating = nums[0].replace(",", ".")
                            break
                    except NoSuchElementException:
                        pass

                tanggal = ""
                for s in ["span.rsqaWe", "span.dehysf", "span[class*='date']"]:
                    try:
                        tanggal = kartu.find_element(By.CSS_SELECTOR, s).text.strip()
                        if tanggal: break
                    except NoSuchElementException:
                        pass

                semua_rows[key] = {
                    "id":        str(uuid.uuid4()),
                    "destinasi": nama,
                    "kategori":  kategori,
                    "kota":      kota,
                    "review":    teks,
                    "rating":    rating,
                    "tanggal":   tanggal,
                    "platform":  "Google Maps",
                }

            except StaleElementReferenceException:
                continue

    # Loop scroll
    while len(semua_rows) < max_reviews:
        ambil_kartu_visible()
        now = len(semua_rows)

        if now == prev_count:
            stagnant += 1
            if stagnant >= 5:
                print(f"  → Tidak ada review baru, total: {now}")
                break
        else:
            stagnant = 0

        prev_count = now
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
        time.sleep(SCROLL_PAUSE)

    # Ambil sisa setelah scroll terakhir
    ambil_kartu_visible()
    print(f"  → {len(semua_rows)} review dikumpulkan")
    return list(semua_rows.values())

# ============================================================
# EKSTRAK REVIEW
# ============================================================
def ekstrak(driver, nama: str, kategori: str, kota: str) -> list:
    # Expand "Selengkapnya"
    for sel in ["button.w8nwRe.kyuRq", "button[aria-label*='Selengkapnya']"]:
        for btn in driver.find_elements(By.CSS_SELECTOR, sel):
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.2)
            except Exception:
                pass

    time.sleep(1)
    rows = []

    kartu_list = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
    if not kartu_list:
        kartu_list = driver.find_elements(By.CSS_SELECTOR, "div[data-review-id]")

    for kartu in kartu_list:
        try:
            # Teks
            teks = ""
            for s in ["span.wiI7pd", "span.HgLLd", "span.MyEned"]:
                try:
                    teks = kartu.find_element(By.CSS_SELECTOR, s).text.strip()
                    if teks: break
                except NoSuchElementException:
                    pass

            # Rating
            rating = ""
            for s in ["span.kvMYJc", "span[aria-label*='bintang']", "span[aria-label*='star']"]:
                try:
                    aria = kartu.find_element(By.CSS_SELECTOR, s).get_attribute("aria-label") or ""
                    nums = re.findall(r"\d+(?:[.,]\d+)?", aria)
                    if nums:
                        rating = nums[0].replace(",", ".")
                        break
                except NoSuchElementException:
                    pass

            # Tanggal
            tanggal = ""
            for s in ["span.rsqaWe", "span.dehysf", "span[class*='date']"]:
                try:
                    tanggal = kartu.find_element(By.CSS_SELECTOR, s).text.strip()
                    if tanggal: break
                except NoSuchElementException:
                    pass

            rows.append({
                "id":        str(uuid.uuid4()),
                "destinasi": nama,
                "kategori":  kategori,
                "kota":      kota,
                "review":    teks,
                "rating":    rating,
                "tanggal":   tanggal,
                "platform":  "Google Maps",
            })
        except StaleElementReferenceException:
            continue

    return rows


# ============================================================
# MAIN
# ============================================================
def scrape_semua() -> pd.DataFrame:
    driver = buat_driver()
    semua = []
    total = len(DESTINASI)

    try:
        for idx, (query, kategori, kota) in enumerate(DESTINASI, start=1):
            nama = nama_bersih_dari(query)
            print(f"\n[{idx}/{total}] {nama}")

            ok = buka_dan_klik_ulasan(driver, query)
            if not ok:
                continue

            print(f"  Scrolling... (target {MAX_REVIEWS_PER_TEMPAT})")
            rows = scroll_dan_ekstrak(driver, nama, kategori, kota, MAX_REVIEWS_PER_TEMPAT)
            semua.extend(rows)
            print(f"  ✓ {len(rows)} review diambil")

            if idx < total:
                time.sleep(JEDA_ANTAR_TEMPAT)

    except KeyboardInterrupt:
        print("\n\n⚠ Dihentikan. Menyimpan data yang sudah ada...")
    finally:
        driver.quit()

    return pd.DataFrame(semua, columns=[
        "id", "destinasi", "kategori", "kota",
        "review", "rating", "tanggal", "platform"
    ])


if __name__ == "__main__":
    print("=" * 60)
    print("  Scraper Google Maps Reviews (Selenium)")
    print("  13 Destinasi Wisata Jawa Timur")
    print(f"  Target: maks {MAX_REVIEWS_PER_TEMPAT} review/destinasi")
    print("=" * 60)
    print("\n⚠ PENTING:")
    print("  - Jangan klik/gerakkan window browser saat berjalan")
    print("  - Kalau muncul CAPTCHA, selesaikan manual di browser")
    print("  - Tekan Ctrl+C kapan saja untuk berhenti & simpan\n")

    df = scrape_semua()

    if df.empty:
        print("\n⚠ Tidak ada data terkumpul.")
    else:
        out = "wisata_jatim_reviews.csv"
        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"\n✅ Total: {len(df)} review → {out}")
        print("\nRingkasan per destinasi:")
        print(df.groupby(["destinasi", "kota"])["id"].count().rename("jumlah").to_string())