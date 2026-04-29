from playwright.sync_api import sync_playwright
from seleniumbase import SB

query = "site:sanfranciscobriefing.com"

with SB(uc=True) as sb:
    sb.activate_cdp_mode()
    endpoint_url = sb.cdp.get_endpoint_url()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(endpoint_url)
        context = browser.contexts[0]
        page = context.pages[0]

        # 1) Open Google
        page.goto("https://www.bing.com", wait_until="domcontentloaded", timeout=20000)

        # 2) Accept cookies
        try:
            page.locator(
                "button:has-text('I agree'), button:has-text('Accept all')"
            ).first.click(timeout=5000)
        except:
            pass

        # 3) Search
        page.fill("textarea[name='q'], input[name='q']", query)
        page.keyboard.press("Enter")

        # 4) Wait for results
        page.wait_for_selector("a h3", timeout=20000)

        # 5) Collect ALL matching links first
        link_locator = page.locator("a:has(h3)")
        matching_links = []

        for i in range(link_locator.count()):
            href = link_locator.nth(i).get_attribute("href")
            if href and "sanfranciscobriefing.com" in href:
                matching_links.append(href)

        if not matching_links:
            raise RuntimeError("No Google results found for sanfranciscobriefing.com")

        print(f"Found {len(matching_links)} matching links")

        # 6) Open each link in a NEW TAB
        for idx, link in enumerate(matching_links):
            print(f"Opening {idx+1}: {link}")

            new_page = context.new_page()
            new_page.goto(link, wait_until="domcontentloaded")

            print(f"Final URL {idx+1}: {new_page.url}")

            # optional: wait or interact
            new_page.wait_for_timeout(3000)

            new_page.close()