from __future__ import annotations

import logging
import os
import random
import re
import shutil
import subprocess
import time
from pathlib import Path

import undetected_chromedriver as uc
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.config import AppConfig

logger = logging.getLogger(__name__)


def human_delay(min_sec: float = 0.6, max_sec: float = 1.6) -> None:
    """Sleep for a randomized duration to mimic human pacing."""
    time.sleep(random.uniform(min_sec, max_sec))


def _detect_chrome_major_version() -> int | None:
    """Detect installed Chrome/Chromium major version to match ChromeDriver."""
    for binary in ("google-chrome", "chromium", "chromium-browser"):
        path = shutil.which(binary)
        if not path:
            continue
        try:
            output = subprocess.check_output([path, "--version"], text=True, timeout=5)
            match = re.search(r"(\d+)\.\d+\.\d+", output)
            if match:
                return int(match.group(1))
        except Exception:
            continue
    return None


def _cleanup_stale_profile_locks(profile_dir: Path) -> None:
    """Remove stale Chromium singleton lock files that can block startup in Docker."""
    for lock_name in ("SingletonLock", "SingletonSocket", "SingletonCookie"):
        lock_path = profile_dir / lock_name
        if lock_path.exists() or lock_path.is_symlink():
            try:
                lock_path.unlink()
            except OSError:
                pass


def create_stealth_driver(config: AppConfig) -> WebDriver:
    """Create an undetected-chromedriver instance with persistent profile and stealth options."""
    config.chrome_profile_dir.mkdir(parents=True, exist_ok=True)
    _cleanup_stale_profile_locks(config.chrome_profile_dir)

    headless = config.headless
    if not headless and os.name != "nt" and not os.environ.get("DISPLAY"):
        logger.warning(
            "DISPLAY tidak ditemukan pada environment; otomatis beralih ke mode headless=True."
        )
        headless = True

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={config.chrome_profile_dir}")
    options.add_argument("--lang=id-ID,id,en-US,en")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")

    if headless:
        options.add_argument("--headless=new")

    version_main = config.chrome_version_main or _detect_chrome_major_version()
    kwargs: dict = {
        "options": options,
        "use_subprocess": True,
    }
    if version_main is not None:
        kwargs["version_main"] = version_main

    logger.info(
        "Memulai stealth Chrome (headless=%s, version_main=%s, profile=%s)",
        headless,
        version_main,
        config.chrome_profile_dir,
    )
    driver = uc.Chrome(**kwargs)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(2)
    return driver


def scroll_into_view(driver: WebDriver, element: WebElement) -> None:
    """Smoothly scroll an element into the center of the viewport."""
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        element,
    )
    human_delay(0.25, 0.5)


def safe_click(driver: WebDriver, element: WebElement) -> None:
    """Click an element reliably with scroll and JS fallback."""
    scroll_into_view(driver, element)
    try:
        ActionChains(driver).move_to_element(element).pause(
            random.uniform(0.1, 0.3)
        ).click().perform()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", element)


def human_type(driver: WebDriver, element: WebElement, text: str, clear_first: bool = True) -> None:
    """Type text into an input/textarea in small randomized chunks."""
    safe_click(driver, element)
    if clear_first:
        element.send_keys(Keys.CONTROL, "a")
        human_delay(0.1, 0.25)
        element.send_keys(Keys.BACKSPACE)
        human_delay(0.15, 0.35)

    # Type in short chunks so long Indonesian paragraphs stay reliable yet natural.
    idx = 0
    while idx < len(text):
        chunk_size = random.randint(2, 6)
        chunk = text[idx : idx + chunk_size]
        element.send_keys(chunk)
        idx += chunk_size
        time.sleep(random.uniform(0.02, 0.08))


def find_first_visible(
    driver: WebDriver,
    locators: tuple[tuple[str, str], ...],
    timeout: float = 10.0,
) -> WebElement | None:
    """Return the first visible element matching any of the given locators."""
    end_time = time.monotonic() + timeout
    while time.monotonic() < end_time:
        for by, value in locators:
            elements = driver.find_elements(by, value)
            for el in elements:
                if el.is_displayed():
                    return el
        time.sleep(0.3)
    return None


def wait_for_clickable(
    driver: WebDriver,
    locator: tuple[str, str],
    timeout: float = 15.0,
) -> WebElement:
    """Wait until an element is clickable."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def save_screenshot(driver: WebDriver, screenshots_dir: Path, name: str) -> Path:
    """Save a PNG screenshot into screenshots_dir and return its path."""
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    path = screenshots_dir / f"{name}.png"
    driver.save_screenshot(str(path))
    logger.info("Screenshot disimpan: %s", path)
    return path
