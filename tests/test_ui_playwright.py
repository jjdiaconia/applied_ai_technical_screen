from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest


def _wait_for_server(url: str, timeout_seconds: float = 25.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(url) as response:
                if response.status == 200:
                    return True
        except URLError:
            time.sleep(0.25)
    return False


@pytest.mark.integration
@pytest.mark.e2e_ui
def test_streamlit_ui_shows_fallback_notice_for_no_direct_match() -> None:
    playwright = pytest.importorskip("playwright.sync_api", reason="Install playwright to run UI E2E tests.")

    project_root = Path(__file__).resolve().parents[1]
    port = 8765
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env["OPENAI_API_KEY"] = ""

    process = subprocess.Popen(
        [
            "poetry",
            "run",
            "streamlit",
            "run",
            "app.py",
            "--server.headless",
            "true",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            str(port),
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=project_root,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        assert _wait_for_server(base_url), "Streamlit app did not become ready in time."

        with playwright.sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(base_url)

            chat_input = page.get_by_placeholder("Type your question...")
            chat_input.click()
            chat_input.fill("What is the weather in Boston today?")
            chat_input.press("Enter")

            page.get_by_text(
                "No direct match found in the predefined dataset. Using OpenAI fallback response."
            ).wait_for(timeout=8000)
            page.get_by_text("set OPENAI_API_KEY").wait_for(timeout=8000)

            browser.close()
    finally:
        process.terminate()
        process.wait(timeout=10)
