import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Launch browser in visible mode
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # --- Step 1: Navigate to the URL ---
        print(">> Opening website...")
        page.goto("https://service2.diplo.de/rktermin/extern/choose_categoryList.do?locationCode=colo&realmId=1419&request_locale=en")
        page.wait_for_load_state("networkidle")

        # --- Step 2: Select Category (STUDENTS) ---
        print(">> Selecting 'Students' category...")
        try:
            # XPath Logic to find 'Students' and click 'Continue'
            page.locator("xpath=//*[contains(text(), 'Students') and not(contains(text(), 'except'))]//following::a[contains(text(), 'Continue')]").first.click()
        except Exception as e:
            print(f"Error clicking category: {e}")
            return

        # --- Step 3: Information Page ---
        print(">> Clicking Continue on Info page...")
        page.wait_for_load_state("domcontentloaded")
        try:
            page.get_by_role("link", name="Continue").first.click()
        except:
             page.locator("xpath=//a[contains(text(), 'Continue')]").click()

        # --- Step 4: CAPTCHA Page (Manual Input) ---
        captcha_success = False
        for attempt in range(2):
            print(">> ----------------------------------------------------")
            wait_time = 12 if attempt == 0 else 10
            print(f">> ATTEMPT {attempt + 1}: WAITING {wait_time} SECONDS FOR MANUAL CAPTCHA.")
            time.sleep(wait_time)
            
            print(">> PLEASE TYPE THE CODE MANUALLY...")
            print(">> Clicking Continue...")
            
            try:
                page.get_by_role("button", name="Continue").click()
                # Check for the calendar page
                page.wait_for_selector("text=Please select a date", timeout=5000)
                print(">> CAPTCHA Successful! Proceeding...")
                captcha_success = True
                break 
            except:
                print(">> Warning: Next page did not load. Retrying...")
        
        if not captcha_success:
            print(">> CRITICAL: CAPTCHA failed twice.")

        # --- Step 5: Find First Available Date ---
        print(">> Searching for available date slots...")
        found_date = False
        max_months = 12 
        
        for i in range(max_months):
            if page.locator("text=Appointments are available").count() > 0:
                print(f">> Date slot found in month {i+1}!")
                page.locator("text=Appointments are available").first.click()
                found_date = True
                break
            
            next_arrow = page.locator("a:has(img[src*='arrow'])").last
            if next_arrow.count() > 0:
                print(f">> No slots in month {i+1}. Checking next month...")
                next_arrow.click()
                page.wait_for_load_state("networkidle")
                time.sleep(1)
            else:
                break
        
        if not found_date:
            print(">> No appointments found. Ending script.")
            time.sleep(10)
            browser.close()
            return

        # --- Step 6: Select Time Slot ---
        print(">> Selecting first available time slot...")
        try:
            page.wait_for_selector("text=Book this appointment")
            page.locator("text=Book this appointment").first.click()
        except Exception as e:
            print(f"Error selecting time slot: {e}")
            return

        # --- Step 7: Fill Information (UPDATED DETAILS) ---
        print(">> Filling personal details for THUSHANTH SELVAKUMAR...")
        page.wait_for_load_state("domcontentloaded")

        try:
            # 1. Last Name
            page.fill("input[name='lastname']", "SELVAKUMAR")
            
            # 2. First Name
            page.fill("input[name='firstname']", "THUSHANTH")
            
            # 3. Email
            page.fill("input[name='email']", "selvakumarthushanth5@gmail.com")
            
            # 4. Repeat Email
            page.locator("xpath=//*[contains(text(), 'Repeat email')]//following::input[1]").fill("selvakumarthushanth5@gmail.com")

            # 5. Passport Number
            page.locator("xpath=//*[contains(text(), 'Passport Number')]//following::input[1]").fill("N10476291")

            # 6. Telephone Number
            phone = "0768688893" 
            if page.locator("input[name='telephonenumber']").count() > 0:
                 page.fill("input[name='telephonenumber']", phone)
            else:
                 page.locator("xpath=//*[contains(text(), 'Telephone')]//following::input[1]").first.fill(phone)

            # 7. Checkbox
            page.locator("input[type='checkbox']").first.check()

            print(">> Form filled successfully!")
            
        except Exception as e:
            print(f"Error filling form: {e}")

        # --- Keep Browser Open ---
        print(">> Done. Browser will remain open for 2 minutes for you to review.")
        time.sleep(120)
        browser.close()

if __name__ == "__main__":
    run()
