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
    "Hadir disetujui",
    "Izin disetujui",
)

# --- Form Kehadiran (Vuetify 3 Dropdown + 3 Textarea + Checkbox) ---
KEHADIRAN_SELECT_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[contains(translate(normalize-space(text()), 'KEHADIRAN', 'kehadiran'), 'kehadiran')]/following::select[1]"),
    (By.CSS_SELECTOR, "select[name*='kehadiran' i]"),
    (By.CSS_SELECTOR, "select[name*='status' i]"),
    (By.CSS_SELECTOR, "select"),
)

KEHADIRAN_CUSTOM_DROPDOWN_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//div[contains(@class, 'v-select')]//div[contains(@class, 'v-field')]"),
    (By.XPATH, "//*[contains(normalize-space(.), 'Kehadiran')]/ancestor::*[contains(@class, 'v-input')][1]//div[contains(@class, 'v-field')]"),
    (By.XPATH, "//*[@role='combobox'][contains(., 'Pilih') or contains(., 'Kehadiran') or contains(., 'Hadir')]"),
)

HADIR_OPTION_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//div[contains(@class, 'v-overlay__content')]//div[contains(@class, 'v-list-item') and normalize-space(.)='Hadir']"),
    (By.XPATH, "//*[@role='option' and normalize-space(.)='Hadir']"),
    (By.XPATH, "//li[normalize-space(.)='Hadir']"),
    (By.XPATH, "//div[@role='listbox']//*[normalize-space(.)='Hadir']"),
)

URAIAN_TEXTAREA_LOCATORS: tuple[Locator, ...] = (
    (By.CSS_SELECTOR, "textarea.v-field__input[placeholder*='uraian aktivitas' i]"),
    (By.CSS_SELECTOR, "textarea[placeholder*='uraian' i]"),
    (By.XPATH, "(//textarea[contains(@class, 'v-field__input')])[1]"),
    (By.XPATH, "(//textarea)[1]"),
)

PEMBELAJARAN_TEXTAREA_LOCATORS: tuple[Locator, ...] = (
    (By.CSS_SELECTOR, "textarea.v-field__input[placeholder*='pembelajaran' i]"),
    (By.CSS_SELECTOR, "textarea[placeholder*='pembelajaran' i]"),
    (By.XPATH, "(//textarea[contains(@class, 'v-field__input')])[2]"),
    (By.XPATH, "(//textarea)[2]"),
)

KENDALA_TEXTAREA_LOCATORS: tuple[Locator, ...] = (
    (By.CSS_SELECTOR, "textarea.v-field__input[placeholder*='kendala' i]"),
    (By.CSS_SELECTOR, "textarea[placeholder*='kendala' i]"),
    (By.XPATH, "(//textarea[contains(@class, 'v-field__input')])[3]"),
    (By.XPATH, "(//textarea)[3]"),
)

DECLARATION_CHECKBOX_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//label[contains(., 'Saya menyatakan telah meninjau')]"),
    (By.XPATH, "//*[contains(@class, 'v-checkbox')]//div[contains(@class, 'v-selection-control__wrapper')]"),
    (By.CSS_SELECTOR, "input[type='checkbox'][aria-label*='Saya menyatakan telah meninjau']"),
    (By.XPATH, "//*[contains(@class, 'v-checkbox')]//input[@type='checkbox']"),
    (By.CSS_SELECTOR, "input[type='checkbox']"),
)

SUBMIT_FORM_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//button[contains(., 'Simpan dan Kirim') and not(@disabled)]"),
    (By.XPATH, "//button[contains(., 'Simpan dan Kirim')]"),
    (By.XPATH, "//button[contains(., 'Simpan Presensi') or contains(., 'Kirim Presensi')]"),
    (By.CSS_SELECTOR, "form button[type='submit']"),
)

CONFIRM_MODAL_LOCATORS: tuple[Locator, ...] = (
    (By.XPATH, "//*[@role='dialog']//button[contains(., 'Ya') or contains(., 'Konfirmasi') or contains(., 'Kirim') or contains(., 'Simpan')]"),
)
