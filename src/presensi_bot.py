from __future__ import annotations

import logging
import re
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


def _step_pause(stage: str, delay_sec: float) -> None:
    """Log the current stage clearly and pause so the user can inspect it manually."""
    logger.info("[TAHAP] %s", stage)
    if delay_sec > 0:
        logger.info("Menunggu %.1f detik sebelum tahap berikutnya...", delay_sec)
        time.sleep(delay_sec)


def _is_login_page(driver: WebDriver) -> bool:
    url = driver.current_url.lower()
    if "login" in url or "account.kemnaker" in url or "auth" in url:
        return True
    password_el = find_first_visible(driver, selectors.LOGIN_PASSWORD_LOCATORS, timeout=1.5)
    return password_el is not None


def _perform_login(driver: WebDriver, config: AppConfig) -> None:
    config.validate_credentials()
    _step_pause(f"Login ke akun Kemnaker ({driver.current_url})", config.step_delay_sec)

    email_el = find_first_visible(driver, selectors.LOGIN_EMAIL_LOCATORS, timeout=15)
    password_el = find_first_visible(driver, selectors.LOGIN_PASSWORD_LOCATORS, timeout=10)
    if not email_el or not password_el:
        raise AttendanceBotError("Field email/password pada halaman login tidak ditemukan.")

    human_type(driver, email_el, config.kemnaker_email)
    _step_pause("Email/Username login sudah diisi", config.step_delay_sec)
    human_type(driver, password_el, config.kemnaker_password)
    _step_pause("Password login sudah diisi", config.step_delay_sec)

    submit_el = find_first_visible(driver, selectors.LOGIN_SUBMIT_LOCATORS, timeout=5)
    if not submit_el:
        raise AttendanceBotError("Tombol submit login tidak ditemukan.")

    safe_click(driver, submit_el)
    logger.info("Kredensial dikirim, menunggu redirect ke dashboard...")

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if "monev.maganghub.kemnaker.go.id" in driver.current_url and not _is_login_page(driver):
            _step_pause(f"Login berhasil ({driver.current_url})", config.step_delay_sec)
            return
        time.sleep(0.5)

    save_screenshot(driver, config.screenshots_dir, "login_timeout")
    raise AttendanceBotError(
        "Login belum berhasil setelah 30 detik (kemungkinan kredensial salah atau ada CAPTCHA/OTP)."
    )


def _strip_calendar_legend(body_text: str) -> str:
    """Remove the top calendar legend text so it never causes false-positive status matches."""
    cleaned = re.sub(
        r"Hadir disetujui\s+Izin disetujui\s+Tidak Hadir\s+Kehadiran Ditolak\s+Perlu Tindakan Anda",
        "",
        body_text,
    )
    cleaned = re.sub(
        r"Menunggu Tindakan Mentor\s+Belum Diisi\s+Hari Libur",
        "",
        cleaned,
    )
    return cleaned


def _detect_existing_status(driver: WebDriver) -> str | None:
    # Jika form input (textarea) tampil, berarti presensi hari ini BELUM diisi.
    if find_first_visible(driver, selectors.URAIAN_TEXTAREA_LOCATORS, timeout=1.0) is not None:
        return None

    body_text = driver.execute_script("return document.body ? document.body.innerText : '';") or ""
    if "Tambah laporan" in body_text:
        return None

    detail_text = _strip_calendar_legend(body_text)
    for holiday in selectors.HOLIDAY_TEXTS:
        if holiday in detail_text:
            return "Hari Libur"

    for status in selectors.ALREADY_FILLED_TEXTS:
        if status in detail_text:
            return status
    return None


def _select_kehadiran_hadir(driver: WebDriver) -> None:
    select_el = find_first_visible(driver, selectors.KEHADIRAN_SELECT_LOCATORS, timeout=2)
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

    if "hadir" in (dropdown_btn.text or "").strip().lower():
        logger.info("Dropdown Kehadiran sudah terpilih: Hadir")
        return

    safe_click(driver, dropdown_btn)
    human_delay(0.4, 0.8)

    hadir_opt = find_first_visible(driver, selectors.HADIR_OPTION_LOCATORS, timeout=5)
    if hadir_opt is None:
        raise AttendanceBotError("Opsi 'Hadir' pada dropdown Kehadiran tidak ditemukan.")

    safe_click(driver, hadir_opt)
    logger.info("Custom dropdown Kehadiran dipilih: Hadir")


def _check_declaration_checkbox(driver: WebDriver, step_delay_sec: float) -> None:
    checkbox_inputs = driver.find_elements(
        *selectors.DECLARATION_CHECKBOX_LOCATORS[2]
    ) or driver.find_elements(*selectors.DECLARATION_CHECKBOX_LOCATORS[4])
    if checkbox_inputs and checkbox_inputs[0].is_selected():
        _step_pause("Checkbox pernyataan sudah dicentang", step_delay_sec)
        return

    clickable_target = find_first_visible(driver, selectors.DECLARATION_CHECKBOX_LOCATORS, timeout=6)
    if clickable_target is None:
        raise AttendanceBotError("Checkbox pernyataan 'Saya menyatakan telah meninjau...' tidak ditemukan.")

    safe_click(driver, clickable_target)
    _step_pause("Checkbox pernyataan sudah dicentang", step_delay_sec)


def _fill_attendance_form(driver: WebDriver, entry: AttendanceEntry, step_delay_sec: float) -> None:
    _select_kehadiran_hadir(driver)
    _step_pause("Dropdown Kehadiran 'Hadir' sudah dipilih", step_delay_sec)

    fields = [
        ("Uraian aktivitas", selectors.URAIAN_TEXTAREA_LOCATORS, entry.uraian_aktivitas),
        (
            "Pembelajaran yang diperoleh",
            selectors.PEMBELAJARAN_TEXTAREA_LOCATORS,
            entry.pembelajaran_diperoleh,
        ),
        ("Kendala yang dialami", selectors.KENDALA_TEXTAREA_LOCATORS, entry.kendala_dialami),
    ]

    for label, locators, value in fields:
        textarea = find_first_visible(driver, locators, timeout=8)
        if textarea is None:
            raise AttendanceBotError(f"Textarea '{label}' tidak ditemukan.")
        human_type(driver, textarea, value)
        _step_pause(f"Field '{label}' sudah diisi ({len(value)} karakter)", step_delay_sec)

    _check_declaration_checkbox(driver, step_delay_sec)


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
        _step_pause(f"Browser siap, membuka halaman: {target_url}", config.step_delay_sec)
        driver.get(target_url)
        human_delay(2.0, 3.0)

        if _is_login_page(driver):
            _perform_login(driver, config)
            _step_pause(f"Kembali ke halaman target: {target_url}", config.step_delay_sec)
            driver.get(target_url)
            human_delay(2.0, 3.0)

        # Pastikan form atau status sudah ter-render
        find_first_visible(
            driver,
            selectors.URAIAN_TEXTAREA_LOCATORS + selectors.KEHADIRAN_CUSTOM_DROPDOWN_LOCATORS,
            timeout=10,
        )

        existing_status = _detect_existing_status(driver)
        if existing_status == "Hari Libur":
            _step_pause(
                f"Tanggal {entry.date_label} adalah Hari Libur di MagangHub. Presensi dilewati.",
                config.step_delay_sec,
            )
            save_screenshot(driver, config.screenshots_dir, f"holiday_{entry.date_iso}_{timestamp}")
            return True

        if existing_status:
            _step_pause(
                f"Presensi {entry.date_label} sudah berstatus '{existing_status}'. Tidak perlu diisi ulang.",
                config.step_delay_sec,
            )
            save_screenshot(driver, config.screenshots_dir, f"already_{entry.date_iso}_{timestamp}")
            return True

        _fill_attendance_form(driver, entry, config.step_delay_sec)

        if config.dry_run:
            _step_pause(
                f"DRY_RUN aktif: seluruh form untuk {entry.date_label} sudah diisi (tanpa submit)",
                config.step_delay_sec,
            )
            save_screenshot(driver, config.screenshots_dir, f"dryrun_{entry.date_iso}_{timestamp}")
            return True

        submit_btn = find_first_visible(driver, selectors.SUBMIT_FORM_LOCATORS, timeout=8)
        if submit_btn is None:
            raise AttendanceBotError("Tombol submit form presensi tidak ditemukan.")

        safe_click(driver, submit_btn)
        _step_pause("Tombol Submit diklik, mengecek dialog konfirmasi...", config.step_delay_sec)

        confirm_btn = find_first_visible(driver, selectors.CONFIRM_MODAL_LOCATORS, timeout=3)
        if confirm_btn is not None:
            safe_click(driver, confirm_btn)
            _step_pause("Dialog konfirmasi diklik", config.step_delay_sec)

        human_delay(2.0, 3.0)
        final_status = _detect_existing_status(driver)
        save_screenshot(driver, config.screenshots_dir, f"submitted_{entry.date_iso}_{timestamp}")
        _step_pause(
            f"Presensi {entry.date_label} selesai dikirim. Status halaman: {final_status or 'Periksa screenshot'}",
            config.step_delay_sec,
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
