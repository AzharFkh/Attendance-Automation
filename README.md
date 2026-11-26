# Automasi Presensi MagangHub Kemnaker

Layanan automasi presensi harian untuk portal [Monev MagangHub](https://monev.maganghub.kemnaker.go.id) menggunakan Python dan `undetected-chromedriver` (stealth Selenium).

## Fitur Utama
- **Stealth Browser**: Menggunakan `undetected-chromedriver` dengan deteksi versi Chrome otomatis, persistent Chrome profile (`chrome_profile/`), dan jeda/ketikan acak agar tidak terdeteksi sebagai bot.
- **Sumber Data JSON**: Mengambil isian `Uraian aktivitas`, `Pembelajaran yang diperoleh`, dan `Kendala yang dialami` dari `data_presensi_maganghub.json` berdasarkan tanggal hari ini (format Indonesia).
- **Form Lengkap (Vuetify 3)**: Otomatis memilih **Kehadiran = Hadir**, mengisi 3 textarea, mencentang checkbox pernyataan, dan menekan tombol **Simpan dan Kirim**.
- **Mode Development Pelan**: Mendukung `--headed` dan `--step-delay` (jeda antar tahap) untuk memantau alur di layar secara langsung.
- **Jadwal Homelab**: Berjalan otomatis di latar belakang setiap **Senin–Jumat pukul 15:00 WIB** melalui `scheduler.py` (`APScheduler`).
- **Screenshot & Retensi Log 4 Hari**: Menyimpan log (`logs/`) dan screenshot (`logs/screenshots/`) serta otomatis menghapus file yang lebih tua dari `LOG_RETENTION_DAYS` (default `4` hari).

## Setup Lokal

1. Siapkan `.venv`, dependensi, dan `.env`:
   ```bash
   make setup
   ```
   Lalu isi `KEMNAKER_EMAIL` dan `KEMNAKER_PASSWORD` pada `.env`.

2. Uji coba aman (browser tampil, jeda pelan per tahap, **tidak** klik Submit):
   ```bash
   make dev DATE=2026-11-27 DELAY=4
   ```
   Periksa tampilan browser dan screenshot di `logs/screenshots/`.

3. Jalankan unit test:
   ```bash
   make test
   ```

4. Setelah terverifikasi, ubah `DRY_RUN=false` pada `.env` untuk eksekusi nyata:
   ```bash
   make run                 # Presensi hari ini
   make run DATE=2026-11-27 # Presensi tanggal tertentu
   ```

## Deployment di Homelab

### Opsi 1: Docker Compose (Direkomendasikan)
Menggunakan `xvfb` agar Chrome berjalan non-headless di server tanpa GUI dan otomatis menyala di latar belakang:
```bash
make docker-up
make docker-logs
```

### Opsi 2: Systemd Service
Sesuaikan path pada `deploy/presensi.service`, lalu aktifkan:
```bash
sudo cp deploy/presensi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now presensi.service
sudo systemctl status presensi.service
```

Lihat semua perintah `Makefile` yang tersedia dengan `make help`.
