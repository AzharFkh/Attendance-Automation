from __future__ import annotations

from selenium.webdriver.common.by import By

Locator = tuple[str, str]

# --- Login / SSO Kemnaker ---
LOGIN_EMAIL_LOCATORS: tuple[Locator, ...] = (
    (By.CSS_SELECTOR, "input[type='email']"),
    (By.CSS_SELECTOR, "input[name='username']"),
    (By.CSS_SELECTOR, "input[name='email']"),
    (By.CSS_SELECTOR, "input[id='username']"),
    (By.CSS_SELECTOR, "input[id='email']"),
    (By.XPATH, "//input[contains(@placeholder, 'Email') or contains(@placeholder, 'NIK') or contains(@placeholder, 'Username')]"),
)

LOGIN_PASSWORD_LOCATORS: tuple[Locator, ...] = (
    (By.CSS_SELECTOR, "input[type='password']"),
    (By.CSS_SELECTOR, "input[name='password']"),
    (By.CSS_SELECTOR, "input[id='password']"),
)

LOGIN_SUBMIT_LOCATORS: tuple[Locator, ...] = (
    (By.CSS_SELECTOR, "button[type='submit']"),
    (By.CSS_SELECTOR, "input[type='submit']"),
    (By.XPATH, "//button[contains(., 'Masuk') or contains(., 'Login') or contains(., 'Sign In')]"),
)

# --- Status Badges / Indicators ---
ALREADY_FILLED_TEXTS: tuple[str, ...] = (
    "Menunggu Persetujuan",
    "Menunggu Tindakan Mentor",
    "Hadir disetujui",
    "Izin disetujui",
    "Hari Libur",
)

# --- Form Kehadiran (Dropdown + 3 Textarea) ---
KEHADIRAN_SELECT_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[contains(normalize-space(text()), 'Kehadiran')]/following::select[1]"),
    (By.CSS_SELECTOR, "select[name*='kehadiran' i]"),
    (By.CSS_SELECTOR, "select[name*='status' i]"),
    (By.CSS_SELECTOR, "select"),
)

KEHADIRAN_CUSTOM_DROPDOWN_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[contains(normalize-space(text()), 'Kehadiran')]/following::button[@role='combobox' or @aria-haspopup='listbox' or self::button][1]"),
    (By.XPATH, "//*[@role='combobox'][contains(., 'Pilih') or contains(., 'Kehadiran') or contains(., 'Hadir')]"),
    (By.XPATH, "//button[contains(., 'Pilih Kehadiran') or contains(., 'Pilih Status')]"),
)

HADIR_OPTION_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[@role='option' and normalize-space(.)='Hadir']"),
    (By.XPATH, "//li[normalize-space(.)='Hadir']"),
    (By.XPATH, "//div[@role='listbox']//*[normalize-space(.)='Hadir']"),
    (By.XPATH, "//button[normalize-space(.)='Hadir']"),
)

URAIAN_TEXTAREA_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[contains(normalize-space(text()), 'Uraian Aktivitas')]/following::textarea[1]"),
    (By.CSS_SELECTOR, "textarea[name*='uraian' i]"),
    (By.CSS_SELECTOR, "textarea[name*='aktivitas' i]"),
    (By.XPATH, "(//textarea)[1]"),
)

PEMBELAJARAN_TEXTAREA_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[contains(normalize-space(text()), 'Pembelajaran yang Diperoleh')]/following::textarea[1]"),
    (By.CSS_SELECTOR, "textarea[name*='pembelajaran' i]"),
    (By.XPATH, "(//textarea)[2]"),
)

KENDALA_TEXTAREA_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[contains(normalize-space(text()), 'Kendala yang Dialami')]/following::textarea[1]"),
    (By.CSS_SELECTOR, "textarea[name*='kendala' i]"),
    (By.XPATH, "(//textarea)[3]"),
)

SUBMIT_FORM_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//button[@type='submit' and (contains(., 'Simpan') or contains(., 'Kirim') or contains(., 'Submit'))]"),
    (By.XPATH, "//button[contains(., 'Simpan Presensi') or contains(., 'Kirim Presensi') or contains(., 'Simpan') or contains(., 'Kirim')]"),
    (By.CSS_SELECTOR, "form button[type='submit']"),
)

CONFIRM_MODAL_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[@role='dialog']//button[contains(., 'Ya') or contains(., 'Konfirmasi') or contains(., 'Kirim') or contains(., 'Simpan')]"),
)
