# Automasi Presensi MagangHub Kemnaker

Layanan automasi presensi harian untuk portal [Monev MagangHub](https://monev.maganghub.kemnaker.go.id) menggunakan Python dan `undetected-chromedriver` (stealth Selenium).

## Fitur Utama
- **Stealth Browser**: Menggunakan `undetected-chromedriver`, persistent Chrome profile (`chrome_profile/`), dan jeda/ketikan acak agar tidak terdeteksi sebagai bot.
- **Sumber Data JSON**: Mengambil isian `Uraian Aktivitas`, `Pembelajaran yang Diperoleh`, dan `Kendala yang Dialami` dari `data_presensi_maganghub.json` berdasarkan tanggal hari ini (format Indonesia).
- **Dropdown Kehadiran**: Otomatis memilih opsi **Hadir**.
- **Jadwal Homelab**: Berjalan otomatis setiap **Senin–Jumat pukul 15:00 WIB** melalui `scheduler.py` (`APScheduler`).
- **Screenshot & Logging**: Menyimpan log dan screenshot hasil/error di `logs/screenshots/` untuk pemantauan.

## Setup Lokal

1. Buat virtual environment dan install dependensi:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Salin `.env.example` menjadi `.env` lalu isi kredensial Anda:
   ```bash
   cp .env.example .env
   ```

3. Uji coba aman (`--dry-run`, tidak menekan Submit):
   ```bash
   python main.py --run-now --date 2026-11-27 --dry-run
   ```
   Periksa hasil screenshot di `logs/screenshots/` untuk memastikan login, dropdown `Hadir`, dan 3 textarea terisi dengan benar.

4. Setelah terverifikasi, ubah `DRY_RUN=false` pada `.env`.

## Deployment di Homelab

### Opsi 1: Docker Compose (Direkomendasikan)
Menggunakan `xvfb` agar Chrome berjalan non-headless di server tanpa GUI:
```bash
docker compose up -d --build
docker compose logs -f
```

### Opsi 2: Systemd Service
Sesuaikan path pada `deploy/presensi.service`, lalu aktifkan:
```bash
sudo cp deploy/presensi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now presensi.service
sudo systemctl status presensi.service
```
