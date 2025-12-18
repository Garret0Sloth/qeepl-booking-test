import re
from playwright.sync_api import sync_playwright, expect


def test_booking_payment_button_is_active():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500
        )
        page = browser.new_page()

        try:
            page.goto("https://qeepl.com/ru/map", timeout=30000)

            # Поиск Москва
            search_input = page.locator("input[type='search'], input[placeholder*='город']")
            search_input.fill("Моск")
            page.wait_for_timeout(2000)
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")

            # Первая локацияЙ
            first_location = page.locator("[data-testid='company-card'], .company-card").first
            expect(first_location).to_be_visible(timeout=15000)
            first_location.click()

            # Забронировать
            book_button = page.locator("div.company-card-full >> button:has-text('Забронировать')").first
            book_button.wait_for(state="visible", timeout=20000)
            book_button.click()

            # Ждём форму бронирования
            page.wait_for_selector("text=Оставлю", state="visible", timeout=30000)

            # Открываем общий календарь
            dropoff_container = page.locator("div.col-6.q-pr-sm").first
            dropoff_button = dropoff_container.locator("button.location-select__icon-btn").first
            dropoff_button.click()

            # Ждём открытия календаря
            page.wait_for_selector(".q-date", state="visible", timeout=10000)

            # Закрываем cookie banner, если появился
            cookie_close_candidates = [
                page.get_by_role("button", name="Принять"),
                page.get_by_role("button", name="Согласен"),
                page.get_by_role("button", name="Закрыть"),
                page.get_by_role("button", name="close", exact=True),
                page.locator("button[aria-label='close']"),
                page.locator("button[aria-label='Close']"),
                page.get_by_text("Принять все"),
                page.get_by_text("Согласиться"),
                page.locator(".q-notification >> button"),
            ]

            for candidate in cookie_close_candidates:
                if candidate.is_visible(timeout=3000):
                    candidate.click()
                    page.wait_for_timeout(500)
                    break

            # Переходим на январь
            page.get_by_role("button", name="Следующий месяц").click()
            page.wait_for_timeout(800)

            # Выбираем 1 января
            page.get_by_role("button", name="1", exact=True).click()

            # Выбираем 2 января
            page.get_by_role("button", name="2", exact=True).click()

            # Подтверждаем выбор дат
            confirm_button = page.get_by_role("button", name=re.compile("Подтвердить", re.IGNORECASE))
            confirm_button.wait_for(state="visible", timeout=15000)
            confirm_button.click()

            # Ждём закрытия календаря
            page.wait_for_selector(".q-date", state="hidden", timeout=10000)
            page.wait_for_timeout(1000)

            # Финальная кнопка оплаты
            payment_button = page.locator("button.pay-btn").first
            payment_button.wait_for(state="visible", timeout=15000)
            expect(payment_button).to_be_enabled(timeout=10000)

            # Кликаем на кнопку оплаты
            payment_button.click()

            # === КРИТЕРИЙ УСПЕХА: появление модалки регистрации ===
            page.wait_for_selector("text=Введите ваши данные", state="visible", timeout=20000)
            expect(page.get_by_text("Введите ваши данные")).to_be_visible()

            print("Тест успешно пройден: модалка регистрации открыта!")
            page.screenshot(path="success_registration_modal_opened.png")

        except Exception as e:
            page.screenshot(path="error_debug.png")
            raise e
        finally:
            browser.close()


if __name__ == "__main__":
    test_booking_payment_button_is_active()