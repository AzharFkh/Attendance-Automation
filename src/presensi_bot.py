from __future__ import annotations

import logging
import time
from datetime import date, datetime

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from src import selectors
from src.browser import (
    create_stealth_driver,
    find_first_visible,
    human_delay,
    human_type,
    safe_click,
    save_screenshot,
)
from src.config import AppConfig
from src.data_loader import AttendanceEntry, load_attendance_for_date, today_in_timezone

logger = logging.getLogger(__name__)


class AttendanceBotError(RuntimeError):
    """Raised when attendance automation encounters an unrecoverable state."""


def _is_login_page(driver: WebDriver) -> bool:
    url = driver.current_url.lower()
    if "login" in url or "account.kemnaker" in url or "auth" in url:
        return True
    password_el = find_first_visible(driver, selectors.LOGIN_PASSWORD_LOCATORS, timeout=1.5)
    return password_el is not None


def _perform_login(driver: WebDriver, config: AppConfig) -> None:
    config.validate_credentials()
    logger.info("Halaman login terdeteksi (%s). Mencoba login...", driver.current_url)

    email_el = find_first_visible(driver, selectors.LOGIN_EMAIL_LOCATORS, timeout=15)
    password_el = find_first_visible(driver, selectors.LOGIN_PASSWORD_LOCATORS, timeout=10)
    if not email_el or not password_el:
        raise AttendanceBotError("Field email/password pada halaman login tidak ditemukan.")

    human_type(driver, email_el, config.kemnaker_email)
    human_delay(0.4, 0.9)
    human_type(driver, password_el, config.kemnaker_password)
    human_delay(0.5, 1.1)

    submit_el = find_first_visible(driver, selectors.LOGIN_SUBMIT_LOCATORS, timeout=5)
    if not submit_el:
        raise AttendanceBotError("Tombol submit login tidak ditemukan.")

    safe_click(driver, submit_el)
    logger.info("Kredensial dikirim, menunggu redirect ke dashboard...")

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if "monev.maganghub.kemnaker.go.id" in driver.current_url and not _is_login_page(driver):
            logger.info("Login berhasil. URL saat ini: %s", driver.current_url)
            human_delay(1.5, 2.5)
            return
        time.sleep(0.5)

    save_screenshot(driver, config.screenshots_dir, "login_timeout")
    raise AttendanceBotError(
        "Login belum berhasil setelah 30 detik (kemungkinan kredensial salah atau ada CAPTCHA/OTP)."
    )


def _detect_existing_status(driver: WebDriver) -> str | None:
    body_text = driver.execute_script("return document.body ? document.body.innerText : '';") or ""
    for status in selectors.ALREADY_FILLED_TEXTS:
        if status in body_text:
            return status
    return None


def _select_kehadiran_hadir(driver: WebDriver) -> None:
    select_el = find_first_visible(driver, selectors.KEHADIRAN_SELECT_LOCATORS, timeout=4)
    if select_el is not None:
        select = Select(select_el)
        for option in select.options:
            if option.text.strip().lower() == "hadir":
                select.select_by_visible_text(option.text)
                logger.info("Dropdown <select> Kehadiran dipilih: %s", option.text.strip())
                return

    dropdown_btn = find_first_visible(driver, selectors.KEHADIRAN_CUSTOM_DROPDOWN_LOCATORS, timeout=6)
    if dropdown_btn is None:
        raise AttendanceBotError("Dropdown 'Kehadiran' tidak ditemukan pada halaman.")

    safe_click(driver, dropdown_btn)
    human_delay(0.4, 0.8)

    hadir_opt = find_first_visible(driver, selectors.HADIR_OPTION_LOCATORS, timeout=5)
    if hadir_opt is None:
        raise AttendanceBotError("Opsi 'Hadir' pada dropdown Kehadiran tidak ditemukan.")

    safe_click(driver, hadir_opt)
    logger.info("Custom dropdown Kehadiran dipilih: Hadir")


def _fill_attendance_form(driver: WebDriver, entry: AttendanceEntry) -> None:
    _select_kehadiran_hadir(driver)
    human_delay(0.5, 1.0)

    fields = [
        ("Uraian Aktivitas", selectors.URAIAN_TEXTAREA_LOCATORS, entry.uraian_aktivitas),
        (
            "Pembelajaran yang Diperoleh",
            selectors.PEMBELAJARAN_TEXTAREA_LOCATORS,
            entry.pembelajaran_diperoleh,
        ),
        ("Kendala yang Dialami", selectors.KENDALA_TEXTAREA_LOCATORS, entry.kendala_dialami),
    ]

    for label, locators, value in fields:
        textarea = find_first_visible(driver, locators, timeout=8)
        if textarea is None:
            raise AttendanceBotError(f"Textarea '{label}' tidak ditemukan.")
        human_type(driver, textarea, value)
        logger.info("Field '%s' berhasil diisi (%d karakter).", label, len(value))
        human_delay(0.5, 1.2)


def run_attendance(config: AppConfig, target_date: date | None = None) -> bool:
    """Run the attendance workflow for target_date. Returns True if handled cleanly."""
    resolved_date = target_date or today_in_timezone(config.timezone)
    entry = load_attendance_for_date(config.data_file, resolved_date)
    if entry is None:
        logger.warning(
            "Tidak ada data presensi untuk tanggal %s (%s). Proses dilewati.",
            resolved_date.isoformat(),
            resolved_date.strftime("%A"),
        )
        return True

    target_url = f"{config.base_url}?date={entry.date_iso}&view=detail"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    driver: WebDriver | None = None

    try:
        driver = create_stealth_driver(config)
        logger.info("Membuka halaman presensi: %s", target_url)
        driver.get(target_url)
        human_delay(2.5, 4.0)

        if _is_login_page(driver):
            _perform_login(driver, config)
            driver.get(target_url)
            human_delay(2.5, 4.0)

        # Pastikan form atau status sudah ter-render
        find_first_visible(
            driver,
            selectors.URAIAN_TEXTAREA_LOCATORS + selectors.KEHADIRAN_CUSTOM_DROPDOWN_LOCATORS,
            timeout=10,
        )

        existing_status = _detect_existing_status(driver)
        if existing_status:
            logger.info(
                "Presensi %s sudah berstatus '%s'. Tidak perlu diisi ulang.",
                entry.date_label,
                existing_status,
            )
            save_screenshot(driver, config.screenshots_dir, f"already_{entry.date_iso}_{timestamp}")
            return True

        _fill_attendance_form(driver, entry)
        human_delay(0.8, 1.5)

        if config.dry_run:
            logger.info("DRY_RUN aktif: form sudah diisi untuk %s, submit dilewati.", entry.date_label)
            save_screenshot(driver, config.screenshots_dir, f"dryrun_{entry.date_iso}_{timestamp}")
            return True

        submit_btn = find_first_visible(driver, selectors.SUBMIT_FORM_LOCATORS, timeout=8)
        if submit_btn is None:
            raise AttendanceBotError("Tombol submit form presensi tidak ditemukan.")

        safe_click(driver, submit_btn)
        human_delay(0.8, 1.5)

        confirm_btn = find_first_visible(driver, selectors.CONFIRM_MODAL_LOCATORS, timeout=3)
        if confirm_btn is not None:
            safe_click(driver, confirm_btn)

        human_delay(2.5, 4.0)
        final_status = _detect_existing_status(driver)
        save_screenshot(driver, config.screenshots_dir, f"submitted_{entry.date_iso}_{timestamp}")
        logger.info(
            "Presensi %s selesai dikirim. Status halaman: %s",
            entry.date_label,
            final_status or "Periksa screenshot",
        )
        return True
    except Exception:
        logger.exception("Gagal menjalankan automasi presensi untuk %s", entry.date_label)
        if driver is not None:
            try:
                save_screenshot(driver, config.screenshots_dir, f"error_{entry.date_iso}_{timestamp}")
            except Exception:
                logger.warning("Gagal menyimpan screenshot error.")
        return False
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
