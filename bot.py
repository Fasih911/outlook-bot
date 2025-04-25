import csv
import asyncio
import random
from pathlib import Path
from playwright.async_api import async_playwright
import httpx
import time

def load_accounts(filename):
    accounts = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            email, password, first_name, last_name = row
            accounts.append({
                "email": email.strip(),
                "password": password.strip(),
                "first_name": first_name.strip(),
                "last_name": last_name.strip()
            })
    return accounts

proxies = [
    "216.10.27.159:6837:qfoyebpk:x4mckvc6iokg",
    "154.36.110.199:6853:qfoyebpk:x4mckvc6iokg",
    "38.153.152.244:9594:qfoyebpk:x4mckvc6iokg",
    "86.38.234.176:6630:qfoyebpk:x4mckvc6iokg",
    "45.151.162.198:6600:qfoyebpk:x4mckvc6iokg",
    "185.199.229.156:7492:qfoyebpk:x4mckvc6iokg",
    "185.199.228.220:7300:qfoyebpk:x4mckvc6iokg",
    "173.211.0.148:6641:qfoyebpk:x4mckvc6iokg",
    "161.123.152.115:6360:qfoyebpk:x4mckvc6iokg",
    "185.199.231.45:8382:qfoyebpk:x4mckvc6iokg"
]

countries = [
    "United States", "Canada", "United Kingdom", "Australia", "India", "Germany", "France", "Italy"
]

def get_random_birthdate():
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    days = list(range(1, 32))
    years = list(range(1950, 2005))
    
    month = random.choice(months)
    day = random.choice(days)
    year = random.choice(years)
    
    return month, day, year

def random_delay(min_ms=1000, max_ms=3000):
    delay = random.randint(min_ms, max_ms)
    return delay

async def simulate_mouse_movements(page):
    width = random.randint(100, 1000)
    height = random.randint(100, 800)
    await page.mouse.move(width, height)
    await page.mouse.down()
    await page.mouse.up()

async def create_outlook_account(playwright, account):
    proxy = random.choice(proxies)
    proxy_host, proxy_port, proxy_user, proxy_password = proxy.split(":")
    
    browser = await playwright.firefox.launch(headless=False, slow_mo=150)
    context = await browser.new_context(
        proxy={
            "server": f"http://{proxy_host}:{proxy_port}",
            "username": proxy_user,
            "password": proxy_password
        }
    )
    page = await context.new_page()

    try:
        print(f"\n🌐 Opening signup for: {account['email']} with Proxy: {proxy}")
        await page.goto("https://signup.live.com/", wait_until="domcontentloaded")
        await page.wait_for_timeout(random_delay(2000, 4000))

        print("🔍 Searching for email input field...")
        possible_selectors = [
            'input[name="MemberName"]',
            'input[type="email"]',
            'input[aria-label*="Create a new email"]',
            'input[placeholder*="someone@example.com"]',
            'input.input'
        ]

        email_selector = None
        for sel in possible_selectors:
            el = await page.query_selector(sel)
            if el:
                is_visible = await el.is_visible()
                is_enabled = await el.is_enabled()
                if is_visible and is_enabled:
                    email_selector = sel
                    break

        if not email_selector:
            raise Exception("⚠️ Email field not found!")

        print(f"Filling email: {account['email']}")
        await page.fill(email_selector, account["email"])
        await page.mouse.wheel(0, random.randint(100, 300))
        await page.wait_for_timeout(random_delay())

        await simulate_mouse_movements(page)
        await page.wait_for_timeout(random_delay(1000, 2000))
        next_button_selector = 'input[type="submit"], button[type="submit"]'
        await page.click(next_button_selector)

        print("Waiting for password field...")
        await page.wait_for_selector('input[name="Password"]', timeout=15000)

        print(f"Filling password: {account['password']}")
        await page.fill('input[name="Password"]', account["password"])
        await page.mouse.wheel(0, random.randint(100, 300))
        await page.wait_for_timeout(random_delay())

        print("Clicking Next for password...")
        await page.click(next_button_selector)

        print("Waiting for first name and last name fields...")
        await page.wait_for_selector('input[name="firstNameInput"], input[name="lastNameInput"]', timeout=15000)

        print(f"Filling first name: {account['first_name']}")
        first_name_input = await page.query_selector('input[name="firstNameInput"]')
        if first_name_input:
            await first_name_input.fill(account["first_name"])
            await page.mouse.wheel(0, random.randint(100, 300))
            await page.wait_for_timeout(random_delay())

        print(f"Filling last name: {account['last_name']}")
        last_name_input = await page.query_selector('input[name="lastNameInput"]')
        if last_name_input:
            await last_name_input.fill(account["last_name"])
            await page.mouse.wheel(0, random.randint(100, 300))
            await page.wait_for_timeout(random_delay())

        print("Clicking Next after filling names...")
        await page.click(next_button_selector)

        country = random.choice(countries)
        print(f"Selecting country: {country}")
        await page.select_option('select#countryRegionDropdown', label=country)
        await page.mouse.wheel(0, random.randint(100, 300))
        await page.wait_for_timeout(random_delay())

        month, day, year = get_random_birthdate()
        print(f"Selecting birthdate: {month} {day}, {year}")
        await page.select_option('select[name="BirthMonth"]', label=month)
        await page.mouse.wheel(0, random.randint(100, 300))
        await page.wait_for_timeout(random_delay())

        await page.select_option('select[name="BirthDay"]', label=str(day))
        await page.mouse.wheel(0, random.randint(100, 300))
        await page.wait_for_timeout(random_delay())

        await page.fill('input[name="BirthYear"]', str(year))
        await page.mouse.wheel(0, random.randint(100, 300))
        await page.wait_for_timeout(random_delay())

        await page.click(next_button_selector)

        print("Waiting for CAPTCHA iframe to appear...")
        await page.wait_for_timeout(5000)

        iframe_element = await page.wait_for_selector('#game-core-frame', timeout=50000)
        frame = await iframe_element.content_frame()

        print("Searching for puzzle button inside iframe...")
        puzzle_button = await frame.wait_for_selector('.sc-nkuzb1-0.sc-d5trka-0.eZxMRy.button', timeout=10000)
        await puzzle_button.click()
        print("Clicked the 'Solve Puzzle' button.")

        print("Connecting to 2Captcha...")
        api_key = "a04bfefc95683664081449b0270c2418"
        sitekey = "i6209"
        page_url = page.url

        print("📡 Sending CAPTCHA to 2Captcha...")
        resp = httpx.post(
            "http://2captcha.com/in.php",
            data={
                "key": api_key,
                "method": "userrecaptcha",
                "googlekey": sitekey,
                "pageurl": page_url,
                "json": 1
            }
        )
        request_id = resp.json().get("request")
        print(f"CAPTCHA submitted to 2Captcha. Request ID: {request_id}")

        recaptcha_answer = None
        for _ in range(20):
            time.sleep(5)
            res = httpx.get(f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1")
            if res.json().get("status") == 1:
                recaptcha_answer = res.json().get("request")
                print("CAPTCHA solved successfully.")
                break
            else:
                print("Waiting for 2Captcha to solve...")

        if not recaptcha_answer:
            raise Exception("CAPTCHA was not solved in time.")

        print("Injecting CAPTCHA response token...")
        await frame.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{recaptcha_answer}";')
        await frame.evaluate('document.getElementById("g-recaptcha-response").dispatchEvent(new Event("change"));')
        print("CAPTCHA token injected, submitting form...")

        await frame.click('button[type="submit"]')
        print("CAPTCHA complete, continuing signup process...")

        print("Browser left open for debugging. Close manually after checking.")
        input("Press ENTER after reviewing the browser manually...")

    except Exception as e:
        print(f"Error for {account['email']}: {str(e)}")
        input("Press ENTER after reviewing the browser manually...")

    await browser.close()

async def main():
    accounts = load_accounts("accounts.csv")
    async with async_playwright() as playwright:
        for account in accounts:
            await create_outlook_account(playwright, account)

if __name__ == "__main__":
    asyncio.run(main())
