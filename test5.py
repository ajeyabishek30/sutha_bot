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
            # XPath Logic:
            # 1. Find element containing "Students"
            # 2. Exclude "except" (to avoid the wrong category)
            # 3. Click the 'Continue' link immediately following it.
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

        # --- Step 4: CAPTCHA Page (With Retry Logic) ---
        captcha_success = False
        
        for attempt in range(2):
            print(">> ----------------------------------------------------")
            if attempt == 0:
                print(f">> CAPTCHA ATTEMPT 1: WAITING 12 SECONDS.")
                time.sleep(12)
            else:
                print(f">> CAPTCHA FAILED OR RELOADED.")
                print(f">> CAPTCHA ATTEMPT 2: WAITING ANOTHER 10 SECONDS.")
                time.sleep(10)
            
            print(">> PLEASE TYPE THE CODE MANUALLY...")
            print(">> Clicking Continue...")
            
            try:
                page.get_by_role("button", name="Continue").click()
                
                # Check if it worked by looking for the Next Page element
                page.wait_for_selector("text=Please select a date", timeout=5000)
                
                print(">> CAPTCHA Successful! Proceeding...")
                captcha_success = True
                break 
            except:
                print(">> Warning: Next page did not load. Retrying...")
        
        if not captcha_success:
            print(">> CRITICAL: CAPTCHA failed twice. The script will try to proceed anyway, but may fail.")

        # --- Step 5: Find First Available Date ---
        print(">> Searching for available date slots...")
        
        found_date = False
        max_months_to_check = 12 
        
        for i in range(max_months_to_check):
            if page.locator("text=Appointments are available").count() > 0:
                print(f">> Date slot found in month {i+1}! Clicking...")
                page.locator("text=Appointments are available").first.click()
                found_date = True
                break
            
            next_arrow = page.locator("a:has(img[src*='arrow'])").last
            
            if next_arrow.count() > 0:
                print(f">> No slots in month {i+1}. Clicking Next Month arrow...")
                next_arrow.click()
                page.wait_for_load_state("networkidle")
                time.sleep(1)
            else:
                print(">> No 'Next Month' arrow found. End of calendar reached.")
                break
        
        if not found_date:
            print(">> No appointments found. Script ending.")
            time.sleep(60)
            browser.close()
            return

        # --- Step 6: Select First Time Slot ---
        print(">> Selecting first available time slot...")
        try:
            page.wait_for_selector("text=Book this appointment")
            page.locator("text=Book this appointment").first.click()
        except Exception as e:
            print(f"Error selecting time slot: {e}")
            return

        # --- Step 7: Fill Information (KIRUSHAN MANIVANNAN) ---
        print(">> Filling personal details...")
        page.wait_for_load_state("domcontentloaded")

        try:
            # 1. Last Name
            page.fill("input[name='lastname']", "MANIVANNAN")
            
            # 2. First Name
            page.fill("input[name='firstname']", "KIRUSHAN")
            
            # 3. Email
            page.fill("input[name='email']", "haranjanoffer9@gmail.com")
            
            # 4. Repeat Email
            print(">> Filling Repeat Email...")
            page.locator("xpath=//*[contains(text(), 'Repeat email')]//following::input[1]").fill("haranjanoffer9@gmail.com")

            # 5. Passport Number
            print(">> Filling Passport Number...")
            page.locator("xpath=//*[contains(text(), 'Passport Number')]//following::input[1]").fill("N9464205")

            # 6. Telephone Number
            print(">> Filling Telephone...")
            if page.locator("input[name='telephonenumber']").count() > 0:
                 page.fill("input[name='telephonenumber']", "0763235467")
            else:
                 page.locator("xpath=//*[contains(text(), 'Telephone')]//following::input[1]").first.fill("0763235467")

            # 7. Checkbox
            print(">> Ticking Confirmation Checkbox...")
            page.locator("input[type='checkbox']").first.check()

            print(">> Form filled successfully!")
            
        except Exception as e:
            print(f"Error filling form: {e}")

        # --- Keep Browser Open ---
        print(">> Done. Browser will remain open for 2 minutes.")
        time.sleep(120)
        browser.close()

if __name__ == "__main__":
    run()
