import asyncio
import nodriver as uc
import os
import anticaptchaofficial.recaptchav2proxyless as rcv2
import anticaptchaofficial.recaptchav2proxyon as rcv2p
import re
import random

## todo: bypass Google Captcha

async def click_recaptcha_checkbox(tab):
    await tab.wait_for('iframe[title="reCAPTCHA"]', timeout=30)
    reCAPTCHA_iframe = await tab.select('iframe[title="reCAPTCHA"]')
    await tab.sleep(2)
    iframe_tab = next(filter(lambda x: str(x.target_id) == str(reCAPTCHA_iframe.frame_id), tab.browser.targets))
    iframe_tab.websocket_url = iframe_tab.websocket_url.replace("iframe", "page")
    await iframe_tab.wait_for('div.recaptcha-checkbox-border', timeout=30)
    checkbox = await iframe_tab.select('div.recaptcha-checkbox-border')
    await checkbox.click()

async def get_site_key(tab):
    # Wait for the reCAPTCHA iframe to be present
    await tab.wait_for('iframe[title="reCAPTCHA"]', timeout=30)
    
    # Select the reCAPTCHA iframe
    reCAPTCHA_iframe = await tab.select('iframe[title="reCAPTCHA"]')
    if reCAPTCHA_iframe is None:
        print("reCAPTCHA iframe not found")
        return None

    print("reCAPTCHA iframe found")
    
    # Get the HTML content of the iframe
    iframe_html = await reCAPTCHA_iframe.get_html()
    
    # Find the src attribute from the HTML content using regex
    match = re.search(r'src="([^"]+)"', iframe_html)
    if match:
        iframe_src = match.group(1)
        print(f"iframe src found: {iframe_src}")
        
        # Extract the site key from the src URL
        site_key_match = re.search(r'k=([^&]+)', iframe_src)
        if site_key_match:
            site_key = site_key_match.group(1)
            print(f"Site key found: {site_key}")
            return site_key
        else:
            print("Site key not found")
            return None
    else:
        print("iframe src attribute not found")
        return None

async def solve_captcha(site_key, api_key):
    solver = rcv2.recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key(api_key)
    solver.set_website_url("https://accounts.google.com/signin/v2/identifier")
    solver.set_website_key(site_key)

    token = solver.solve_and_return_solution()
    if token == 0:
        print("CAPTCHA solving failed")
        print(solver.error_code)
        return None
    else:
        print("CAPTCHA solved successfully")
        return token

async def inject_script(tab):
    await tab.sleep(3)
    # Function to inject script to set up window.zt and handleCaptcha
    script = '''
    (function() {
        console.log("Injecting script...");

        window.zt = undefined;

        window.handleCaptcha = async function(token) {
            await console.log("Handling captcha with token:", token);
            window.zt = token;
            await console.log("handleCaptcha called with token:", token);
            await sleep(15000);
            await document.querySelector("form").submit();
        };

        // Sleep function
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    })();
    '''
    try:
        # Injecting script into the page
        await tab.evaluate(script)
        print("Script injected successfully")
    except Exception as e:
        print(f"Script injection failed: {e}")

async def wait_for_zt_and_solve_captcha(tab):
        site_key = await get_site_key(tab)
        if site_key:
            token = await solve_captcha(site_key)
            if token:
                await tab.evaluate(f'''
                (function() {{
                    var responseElement = document.getElementById("g-recaptcha-response");
                    if (responseElement) {{
                        responseElement.style.display = "block";
                        responseElement.textContent = "{token}";
                        return "Token injected";
                    }} else {{
                        return "g-recaptcha-response element not found";
                    }}
                }})();
                ''')
                await tab.evaluate(f'window.handleCaptcha("{token}");')
   

async def main():
    email = "synthesxs.xs@gmail.com"
    email_password = "Fdsvsvdvasdgdj"
    account_birth_month = "03"
    account_birth_day = "14"
    account_birth_year = "2000"
    account_password = "password123"

    api_key = os.getenv('ANTICAPTCHA_API_KEY') # Set your API key here
    

    # Define path to the WEBRTC BLOCKER extension
    WEBRTC_BLOCKER_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/WEBRTC-BLOCKER")
    CSP_DISABLE_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/CSP-DISABLE")
    ANTICAPTCHA_PLUGIN_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/ANTICAPTCHA-PLUGIN")
    BUSTER_CAPTCHA_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/BUSTER-CAPTCHA")
    
    # Pass the extension path as an argument to the browser
    browser_args = [
        f'--load-extension={WEBRTC_BLOCKER_path},{BUSTER_CAPTCHA_path}',
        "--start-maximized",
    ]

    browser = await uc.start(browser_args=browser_args)
    
    ####################################################################################################################################################
    ####################################################################################################################################################
    ####################################################################################################################################################
    # 01: Go to the osrs homepage
    tab = await browser.get("https://browserscan.net/")
    
    # # Check if it asks to save cookies
    # try:
    #     allow_all_cookies_button = await tab.find("Allow all cookies", best_match=True, timeout=30)
    #     await allow_all_cookies_button.click()
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    # # 02: Click sign up button
    # new_user_sign_up_button = await tab.find("New User?", best_match=True, timeout=30)
    # await new_user_sign_up_button.click()    

    # # 03: Click new account button
    # new_account_button = await tab.find("New account", best_match=True, timeout=30)
    # await new_account_button.click()

    # # Check if it asks to save cookies
    # try:
    #     allow_all_cookies_button = await tab.find("Allow all cookies", best_match=True, timeout=30)
    #     await allow_all_cookies_button.click()
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    # # 04: Click email field and input email
    # account_email_field = await tab.select('input[type="email"][name="email"]', timeout=30)
    # await account_email_field.click()
    # await account_email_field.send_keys(email)

    # # 05: Click birth day field and input birth day
    # birth_day_field = await tab.select('input[type="number"][name="day"]', timeout=30)
    # await birth_day_field.click()
    # await birth_day_field.send_keys(account_birth_day)

    # # 06: Click birth month field and input birth month
    # birth_month_field = await tab.select('input[type="number"][name="month"]', timeout=30)
    # await birth_month_field.click()
    # await birth_month_field.send_keys(account_birth_month)

    # # 07: Click birth year field and input birth year
    # birth_year_field = await tab.select('input[type="number"][name="year"]', timeout=30)
    # await birth_year_field.click()
    # await birth_year_field.send_keys(account_birth_year)

    # # 08 Check terms and conditions box
    # terms_and_conditions_checkbox = await tab.select('input[type="checkbox"][id="registration-start-accept-agreements"]', timeout=30)
    # await terms_and_conditions_checkbox.click()

    # await tab.sleep(20)

    # # 09 Click continue
    # continue_button = await tab.find("Continue", timeout=30)
    # await continue_button.click()
    ####################################################################################################################################################
    ####################################################################################################################################################
    ####################################################################################################################################################


    ####################################################################################################################################################
    ############################################### Google Activation ##################################################################################
    ####################################################################################################################################################
    await tab.sleep(3)
    tab2 = await browser.get("https://www.google.com/", new_tab=True)
    await tab.bring_to_front()
    await tab2.sleep(3)
    await tab2.bring_to_front()

    gmail_button = await tab2.find("Gmail")
    await gmail_button.click()

    await tab2.wait_for('a.button[data-action="sign in"][data-category="cta"][data-label="header"]', timeout=30)
    gmail_sign_in_button = await tab2.select('a.button[data-action="sign in"][data-category="cta"][data-label="header"]', timeout=30)
    await gmail_sign_in_button.click()

    await tab2.wait_for('input[type="email"][name="identifier"]', timeout=30)
    gmail_email_field = await tab2.select('input[type="email"][name="identifier"]', timeout=30)
    await gmail_email_field.click()
    await gmail_email_field.send_keys(email)

    gmail_to_password_next_button = await tab2.find("Next")
    await gmail_to_password_next_button.click()

 

    # Inject the script to set window.zt and handleCaptcha
    #await inject_script(tab2)

    # Wait for the zt variable and solve the captcha
    #await wait_for_zt_and_solve_captcha(tab2)
    await click_recaptcha_checkbox(tab2)
    

    await tab2.wait_for('input[type="password"][name="Passwd"]', timeout=300)
    gmail_password_field = await tab2.select('input[type="password"][name="Passwd"]', timeout=30)
    await gmail_email_field.click()
    ####################################################################################################################################################
    ####################################################################################################################################################
    ####################################################################################################################################################

    await asyncio.sleep(10000)

if __name__ == '__main__':
    uc.loop().run_until_complete(main())
