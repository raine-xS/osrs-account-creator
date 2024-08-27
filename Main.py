import asyncio
import nodriver as uc
import os
import anticaptchaofficial.recaptchav2proxyless as rcv2
import anticaptchaofficial.recaptchav2proxyon as rcv2p
import re
import random
import urllib.request
from datetime import datetime
import http.client
import json
import traceback

async def do_google_phone_verification_with_smspva(tab, buget_per_order=2.5, api_key="pwVbSdhTubxeLbhyak74qSlWphlK3I"):
    try:
        country = "NL"
        service_code = "opt1"  # Opt1 for Google (YT/Gmail) Service / opt19 other
        order_id = None
        phone_number = None
        country_code = None
        qualified_phone_number = None

        # Get price
        conn = http.client.HTTPSConnection("api.smspva.com")
        headers = {'apikey': api_key}
        conn.request("GET", f"/activation/serviceprice/{country}/{service_code}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        res_json = json.loads(data.decode("utf-8"))
        order_price = float(res_json["data"]["price"])
        print(f"Order will cost: {order_price}")

        # Check if price is within budget
        if float(order_price) > float(buget_per_order):
            print("Order costs more than your specified budget: aborting phone verification...")
            return False
        else:
            print("Continuing in 5s...\n\n")
            await tab.sleep(5)

        # Create new order
        conn = http.client.HTTPSConnection("api.smspva.com")
        conn.request("GET", f"/activation/number/{country}/{service_code}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        print(data, "\n")
        res_json = json.loads(data.decode("utf-8"))
        status_code = str(res_json["statusCode"])
        if status_code != str(200):
            print ("Failed to create a new order...\n", data.decode("utf-8"), "\n")
            return False
        order_id = str(res_json["data"]["orderId"])
        phone_number = str(res_json["data"]["phoneNumber"])
        country_code = str(res_json["data"]["countryCode"])
        qualified_phone_number = country_code + phone_number 
        print("Creating new order... \n", data.decode("utf-8"), "\n", "Order ID: ", order_id, "\n", "Phone Number: ", phone_number, "\n\n")
        await tab.sleep(3)
        
        # Enter phone number onto phone field
        await tab.wait_for('input[type="tel"][id="phoneNumberId"]')
        google_creation_phone_number_field = await tab.select('input[type="tel"][id="phoneNumberId"]')
        await google_creation_phone_number_field.click()
        await tab.sleep(1)
        await tab.evaluate('''document.querySelector('input[type="tel"][id="phoneNumberId"]').value = '';''') # Clear input
        await google_creation_phone_number_field.send_keys(country_code)
        await tab.sleep(1)
        await tab.evaluate('''document.querySelector('input[type="tel"][id="phoneNumberId"]').value = '';''') # Clear input
        await tab.sleep(1)
        await google_creation_phone_number_field.send_keys(phone_number)
        await tab.sleep(1)
        google_phone_page_next_button = await tab.select('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf')
        await google_phone_page_next_button.click()

        # Refuse SMS and abort if we haven't went to the next page - bad phone number
        try:
            await tab.wait_for('input[type="tel"][name="code"][id="code"]', timeout=15)
        except Exception as e:
            # Ban number
            conn = http.client.HTTPSConnection("smspva.com")
            conn.request("GET", f"/priemnik.php?apikey={api_key}&service={service_code}&id={order_id}&method=ban", headers=headers)
            res = conn.getresponse()
            data = res.read()
            print("Refusing number... \n", data.decode("utf-8"), "\n\n")
            return False

        # Get SMS of order
        sms = None
        tries = 1
        maxTries = 15
        while (tries <= maxTries):
            conn = http.client.HTTPSConnection("api.smspva.com")
            conn.request("GET", f"/activation/sms/{order_id}", headers=headers)
            res = conn.getresponse()
            data = res.read()
            print(f"({tries})- Attempting to get SMS...\n", data.decode("utf-8"), "\n\n")
            res_json = json.loads(data.decode("utf-8"))
            try:
                sms = res_json["data"]["sms"]["code"]
                print("Received SMS: ", res_json["data"]["sms"])
                print("Code: ", sms)
                break
            except Exception as e:
                pass
            tries = tries + 1
            await tab.sleep(10)
        # Refuse the phone number if it exceeded max attempts without getting SMS
        if tries > maxTries:
            # Ban number
            conn = http.client.HTTPSConnection("smspva.com")
            conn.request("GET", f"/priemnik.php?apikey={api_key}&service={service_code}&id={order_id}&method=ban", headers=headers)
            res = conn.getresponse()
            data = res.read()
            print("Refusing number... \n", data.decode("utf-8"), "\n\n")
            print("Verification failed...\n")
            return False
        
        # Else input the code on the next page
        if sms != None:
            await tab.wait_for('input[type="tel"][name="code"][id="code"]', timeout=15)
            enter_code_field = await tab.select('input[type="tel"][name="code"][id="code"]')
            await enter_code_field.click()
            await tab.sleep(2)
            await enter_code_field.send_keys(str(sms))
            await tab.sleep(2)
            google_enter_code_page_next_button = await tab.select('button.VfPpkd-LgbsSe[jsname="LgbsSe"][type="button"]')
            await google_enter_code_page_next_button.click()
        else:
            conn = http.client.HTTPSConnection("smspva.com")
            conn.request("GET", f"/priemnik.php?apikey={api_key}&service={service_code}&id={order_id}&method=ban", headers=headers)
            res = conn.getresponse()
            data = res.read()
            print("Refusing number... \n", data.decode("utf-8"), "\n\n")
            print("Verification failed...\n")
            return False
        
        # Order Success - Clear SMS to receive a new one
        conn = http.client.HTTPSConnection("api.smspva.com")
        conn.request("PUT", "/activation/clearsms/123456", headers=headers)
        res = conn.getresponse()
        data = res.read()
        print("Clearing SMS...\n", data.decode("utf-8"))
        return True
    
    except Exception as e:
        conn = http.client.HTTPSConnection("smspva.com")
        conn.request("GET", f"/priemnik.php?apikey={api_key}&service={service_code}&id={order_id}&method=ban", headers=headers)
        res = conn.getresponse()
        data = res.read()
        print("Refusing number... \n", data.decode("utf-8"), "\n\n")

        print("An error occurred:", e)
        print("Traceback:\n", traceback.format_exc())

        await tab.sleep(5)
        return False
        




async def extract_verification_code_from_email_page(tab):
    # Wait for the specific email rows to load
    await tab.wait_for('tr[role="row"]', timeout=30)
       
    # Get all the rows
    email_rows = await tab.select_all('tr[role="row"]')

    #Define the verification code pattern
    pattern = re.compile(r'\b([A-Z0-9]{5})\s+is your Jagex verification code\b')
    
    # Use regex to find the 5-digit verification code
    for row in email_rows:
        if "is your Jagex verification code" in str(row):
            match = pattern.search(str(row))
            if match:
                verification_code = match.group(1)
                print("Found the verification code:", verification_code)
                return verification_code
    
    # Return None if no code is found
    print("No verification code found.")
    return None

async def click_google_recaptcha_checkbox(tab):
    await tab.wait_for('iframe[title="reCAPTCHA"]', timeout=30)
    reCAPTCHA_iframe = await tab.select('iframe[title="reCAPTCHA"]')
    await tab.sleep(2)
    iframe_tab = next(filter(lambda x: str(x.target_id) == str(reCAPTCHA_iframe.frame_id), tab.browser.targets))
    iframe_tab.websocket_url = iframe_tab.websocket_url.replace("iframe", "page")
    await iframe_tab.wait_for('div.recaptcha-checkbox-border', timeout=30)
    checkbox = await iframe_tab.select('div.recaptcha-checkbox-border')
    await checkbox.click()

async def click_buster_solve_button(tab):
    await tab.wait_for('iframe[title="recaptcha challenge expires in two minutes"]', timeout=30)
    reCAPTCHA_popup_iframe = await tab.select('iframe[title="recaptcha challenge expires in two minutes"]')
    await tab.sleep(2)
    iframe_tab = next(filter(lambda x: str(x.target_id) == str(reCAPTCHA_popup_iframe.frame_id), tab.browser.targets))
    iframe_tab.websocket_url = iframe_tab.websocket_url.replace("iframe", "page")
    await iframe_tab.wait_for('div.help-button-holder', timeout=30)
    button = await iframe_tab.select('div.help-button-holder')
    await button.send_keys("\t")
    await iframe_tab.sleep(2)
    await button.send_keys("\r\n")

async def random_digits(num_of_digits):
    if num_of_digits < 1:
        num_digits = 1
    lower_bound = 10**(num_of_digits - 1)
    upper_bound = 10**num_of_digits - 1
    return str(random.randint(lower_bound, upper_bound))

async def random_word(dictionary_file_name):
    with open(dictionary_file_name, 'r') as file:
        words = []
        for line in file:
            stripped_line = line.strip()  # Remove leading/trailing whitespace
            if stripped_line:  # Check if the line is not empty
                words.append(stripped_line)  # Add the line to the list
    return random.choice(words)

async def generate_random_gmail(dictionary_file_name, min_prefix_characters=5, max_prefix_characters=15):
    word1 = await random_word(dictionary_file_name)
    word2 = await random_word(dictionary_file_name)
    four_digits = await random_digits(4)
    email_prefix = f"{word1}.{word2}{four_digits}"
    
    # Ensure the email prefix is at least 5 characters long
    while len(email_prefix) < min_prefix_characters:
        email_prefix += await random_digits(1)
    
    # Trim the email prefix to ensure the total length with domain is at most 15 characters
    if len(email_prefix) > max_prefix_characters:
        email_prefix = email_prefix[:max_prefix_characters]

    # Ensure the first character is a letter or digit
    if not email_prefix[0].isalnum():
        email_prefix = f"{await random_digits(1)}{email_prefix[1:]}"
    
    # Ensure the last character is a letter or digit
    if not email_prefix[-1].isalnum():
        email_prefix = f"{email_prefix[:-1]}{await random_digits(1)}"
    
    email = f"{email_prefix}@gmail.com"
    return email

async def generate_random_password(dictionary_file_name, min_length=6):
    # Get two random words from the dictionary
    word1 = await random_word(dictionary_file_name)
    word2 = await random_word(dictionary_file_name)
    
    # Get two random digits
    two_digits = await random_digits(2)
    
    # Capitalize the first letter of the first word
    word1_capitalized = word1.capitalize()
    
    # Construct the initial password
    password = f"{word1_capitalized}{word2}{two_digits}"
    
    while len(password) < min_length:
        # Append additional random digits if password is too short
        password += await random_digits(1)
    
    return password

async def generate_random_account_name(dictionary_file_name, min_length=5, max_length=12):
    # Get two random words from the dictionary
    word1 = await random_word(dictionary_file_name)
    word2 = await random_word(dictionary_file_name)
    
    # Determine the number of random digits to append (between 2 and 5)
    num_digits = random.randint(2, 5)
    digits = await random_digits(num_digits)
    
    # Construct the account name by combining the words and digits
    account_name = f"{word1}{word2}{digits}"
    
    # If the account name is too short, append additional random digits
    while len(account_name) < min_length:
        account_name += await random_digits(1)
    
    # If the account name is too long, truncate it
    if len(account_name) > max_length:
        account_name = account_name[:max_length]
    
    return account_name

async def generate_random_date(start_year=1975, end_year=datetime.now().year-18):
  
    # Generate a random year within the specified range
    year = random.randint(start_year, end_year)
    
    # Generate a random month
    month = random.randint(1, 12)
    
    # Determine the number of days in the month
    if month == 2:
        # Check if the year is a leap year
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_days = 29
        else:
            max_days = 28
    elif month in [4, 6, 9, 11]:
        max_days = 30
    else:
        max_days = 31

    # Generate a random day within the valid range for the month
    day = random.randint(1, max_days)
    
    # Format day, month, and year with leading zeros
    formatted_day = f"{day:02}"
    formatted_month = f"{month:02}"
    formatted_year = f"{year}"
    
    return [formatted_month, formatted_day, formatted_year]

async def generate_name(list_of_names_file):
    # Read the file and get the list of words
    with open(list_of_names_file, 'r') as file:
        names = [line.strip() for line in file if line.strip()]
    
    # Select a random word from the list
    selected_name = random.choice(names)
    
    # Convert the word to lowercase, then capitalize the first letter
    formatted_name = selected_name.lower().capitalize()
    
    return formatted_name

async def month_twodigit_to_string(month_code: str) -> str:
    MONTHS = {
    '01': 'Jan',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Apr',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'Aug',
    '09': 'Sept',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dec'
    }
    return MONTHS.get(month_code, None)

async def get_email_prefix(email: str) -> str:
    """
    Extracts the prefix from an email address.

    Args:
    email (str): The email address from which to extract the prefix.

    Returns:
    str: The prefix of the email address, i.e., the part before the '@' symbol.
    """
    if '@' not in email:
        raise ValueError("Invalid email address: '@' symbol not found.")
    
    return email.split('@')[0]
    
async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    first_name_file = os.path.join(current_dir, 'first-names.txt')
    last_name_file = os.path.join(current_dir, 'last-names.txt')
    words_file = os.path.join(current_dir, 'words.txt')

    first_name = await generate_name(first_name_file)
    last_name = await generate_name(last_name_file)
    email = await generate_random_gmail(words_file)
    email_prefix = await get_email_prefix(email)
    email_password = await generate_random_password(words_file)
    birthdate = await generate_random_date()
    account_birth_month = str(birthdate[0])
    account_birth_day = str(birthdate[1])
    account_birth_year = str(birthdate[2])
    account_password = email_password
    account_name = await generate_random_account_name(words_file)
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

    print(f"\n\nCreating a new account...")
    print(f"First Name: {first_name}")
    print(f"Last Name: {last_name}")
    print(f"Email: {email}")
    print(f"Email Password: {email_password}")
    print(f"Birthdate: {account_birth_month}/{account_birth_day}/{account_birth_year}")
    print(f"Account Password: {account_password}")
    print(f"Account Name: {account_name}")
    print(f"IP: {external_ip}")
    print('\n\n')

    
    api_key = os.getenv('ANTICAPTCHA_API_KEY') # Set your API key here
    

    # Define path to the WEBRTC BLOCKER extension
    WEBRTC_BLOCKER_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/WEBRTC-BLOCKER")
    CSP_DISABLE_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/CSP-DISABLE")
    ANTICAPTCHA_PLUGIN_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/ANTICAPTCHA-PLUGIN")
    BUSTER_CAPTCHA_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extensions/BUSTER-CAPTCHA")
    
    user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"

    # Pass the extension path as an argument to the browser
    browser_args = [
        f'--load-extension={WEBRTC_BLOCKER_path},{BUSTER_CAPTCHA_path}',
        '--start-maximized',
    ]

    browser = await uc.start(browser_args=browser_args)

    ####################################################################################################################################################
    ########################################################## Gmail Creation###########################################################################
    ####################################################################################################################################################
    tab = await browser.get("https://www.youtube.com/")

    await tab.wait_for('a.yt-spec-button-shape-next', timeout=15)
    youtube_signin_button = await tab.select('a.yt-spec-button-shape-next')
    await youtube_signin_button.click()

    await tab.wait_for('button.ksBjEc.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.lKxP2d.LQeN7.BqKGqe.eR0mzb.TrZEUc.J7pUA[aria-expanded="false"][aria-haspopup="menu"]', timeout=15)
    google_create_account_button = await tab.select('button.ksBjEc.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.lKxP2d.LQeN7.BqKGqe.eR0mzb.TrZEUc.J7pUA[aria-expanded="false"][aria-haspopup="menu"]')
    await google_create_account_button.click()
    await tab.wait_for('li.gNVsKb.G3hhxb.VfPpkd-StrnGf-rymPhb-ibnC6b[role="menuitem"][tabindex="-1"] span.VfPpkd-StrnGf-rymPhb-b9t22c[jsname="K4r5Ff"]', timeout=15)
    for_my_personal_use = await tab.select('li.gNVsKb.G3hhxb.VfPpkd-StrnGf-rymPhb-ibnC6b[role="menuitem"][tabindex="-1"] span.VfPpkd-StrnGf-rymPhb-b9t22c[jsname="K4r5Ff"]')
    await for_my_personal_use.click()

    await tab.wait_for('input[name="firstName"]', timeout=15)
    google_first_name_field = await tab.select('input[id="firstName"]')
    await tab.sleep(1)
    await google_first_name_field.click()
    await tab.sleep(1)
    await google_first_name_field.send_keys(first_name)
    await tab.sleep(1)

    await tab.wait_for('input[name="lastName"]', timeout=15)
    google_last_name_field = await tab.select('input[id="lastName"]')
    await tab.sleep(1)
    await google_last_name_field.click()
    await tab.sleep(1)
    await google_last_name_field.send_keys(last_name)
    await tab.sleep(1)

    google_name_page_next_button = await tab.select('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.BqKGqe.Jskylb.TrZEUc.lw1w4b[jsname="LgbsSe"] span.VfPpkd-vQzf8d[jsname="V67aGc"]')
    await google_name_page_next_button.click()

    # Select the container div around the Month dropdown
    await tab.wait_for('div.QmtZbb', timeout=15)
    month_container = await tab.select_all('div.QmtZbb')
    month_container = await month_container[0]
    await tab.sleep(1)
    # Click the container div to focus the dropdown
    await month_container.click()
    await tab.sleep(1)
    # Select the month by sending keys or by interacting with the dropdown options
    month_dropdown = await tab.select('select[id="month"]')
    month_string = await month_twodigit_to_string(account_birth_month)
    await tab.sleep(1)
    await month_dropdown.send_keys(month_string)
    await tab.sleep(1)

    # Select the container div around the Day input field
    await tab.wait_for('div.Xb9hP', timeout=15)
    day_container = await tab.select_all('div.Xb9hP')
    day_container = await day_container[0]
    await tab.sleep(1)
    # Click the container div, which should focus the input field
    await day_container.click()
    await tab.sleep(1)
    # Send keys to the input field after clicking the container
    day_field = await tab.select('input[id="day"]')
    await day_field.send_keys(account_birth_day)
    await tab.sleep(1)

    # Select the container div around the Year input field
    await tab.wait_for('div.Xb9hP', timeout=15)
    year_container = await tab.select_all('div.Xb9hP')
    year_container = await year_container[1]
    await tab.sleep(1)
    # Click the container div to focus the input field
    await year_container.click()
    await tab.sleep(1)
    # Send keys to the year input field
    year_field = await tab.select('input[id="year"]')
    await year_field.send_keys(account_birth_year)
    await tab.sleep(1)

    # Select the container div around the Month dropdown
    await tab.wait_for('div.QmtZbb', timeout=15)
    gender_container = await tab.select_all('div.QmtZbb')
    gender_container = await gender_container[1]
    await tab.sleep(1)
    # Click the container div to focus the dropdown
    await gender_container.click()
    await tab.sleep(1)
    # Select the month by sending keys or by interacting with the dropdown options
    gender_dropdown = await tab.select('select[id="gender"]')
    await gender_dropdown.send_keys("Rather not say")
    await tab.sleep(1)

    google_birthdate_and_gender_page_next_button = await tab.select('button[jsname="LgbsSe"]')
    await google_birthdate_and_gender_page_next_button.click()

    await tab.wait_for('button[jsname="Pb0oFb"][jsaction="click:ueE5Uc"]', timeout=15)
    get_gmail_address_instead = await tab.select('button[jsname="Pb0oFb"][jsaction="click:ueE5Uc"]')
    await get_gmail_address_instead.click()

    await tab.wait_for('div.t5nRo.Id5V1')
    create_your_own_email_address = await tab.select_all('div.t5nRo.Id5V1')
    create_your_own_email_address = await create_your_own_email_address[2]
    await create_your_own_email_address.click()
    await tab.sleep(3)

    await tab.wait_for('input.whsOnd.zHQkBf[name="Username"]')
    google_email_creation_field = await tab.select('input.whsOnd.zHQkBf[name="Username"]')
    await google_email_creation_field.click()
    await tab.sleep(2)
    await google_email_creation_field.send_keys(email_prefix)
    await tab.sleep(2)

    ## todo: check if username is taken or if allowed and redo it if it failed
    google_email_creation_page_next_button = await tab.select('button.VfPpkd-LgbsSe[jsname="LgbsSe"][type="button"]')
    await google_email_creation_page_next_button.click()
    await tab.sleep(1)

    await tab.wait_for('input[type="password"][aria-label="Password"][name="Passwd"]')
    google_password_creation_field = await tab.select('input[type="password"][aria-label="Password"][name="Passwd"]')
    await google_password_creation_field.click()
    await tab.sleep(1)
    await google_password_creation_field.send_keys(email_password)
    await tab.sleep(1)

    await tab.wait_for('input[type="password"][aria-label="Confirm"][name="PasswdAgain"]')
    google_repassword_creation_field = await tab.select('input[type="password"][aria-label="Confirm"][name="PasswdAgain"]')
    await google_repassword_creation_field.click()
    await tab.sleep(1)
    await google_repassword_creation_field.send_keys(email_password)
    await tab.sleep(1)

    await tab.wait_for('button.VfPpkd-LgbsSe[jsname="LgbsSe"][type="button"]')
    google_password_creation_page_next_button = await tab.select('button.VfPpkd-LgbsSe[jsname="LgbsSe"][type="button"]')
    await tab.sleep(1)
    await google_password_creation_page_next_button.click()
    await tab.sleep(1)

    #todo: if phone number page (confirm you're not a robot). sometimes it shows, sometimes it doesnt
    attempts = 1
    maxAttempts = 5
    while (attempts <= maxAttempts):
        success = await do_google_phone_verification_with_smspva(tab)
        print("do_google_phone_verification_with_smspva(): ", success)
        if success == True:
            break
        else:
            # If we are on the enter code page, then press "get new code" to return back to the number entry page
            try:
                await tab.wait_for('input[type="tel"][name="code"][id="code"]', timeout=35)
                print("Returning to phone entry page...\n")
                get_new_code_link = await tab.select('input[type="tel"][name="code"][id="code"]')
                await get_new_code_link.click()
            except:
                pass
        attempts = attempts + 1

    if attempts > maxAttempts:
        print("Phone verification failed. Exiting in 3s...")
        await tab.sleep(3)
        browser.stop()

    # Skip add recovery email
    await tab.wait_for('button[jsname="LgbsSe"][type="button"]', timeout=15)
    skip_recover_email_button = await tab.select('button[jsname="LgbsSe"][type="button"]', timeout=15)
    await skip_recover_email_button.click()

    # Press next on review account information
    await tab.wait_for('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ[type="button"][jsname="LgbsSe"]', timeout=15)
    google_review_account_information_next_button = await tab.select('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ[type="button"][jsname="LgbsSe"]', timeout=15)
    await google_review_account_information_next_button.click()

    # Accept Terms and Conditions
    await tab.wait_for('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ[type="button"][jsname="LgbsSe"]', timeout=15)
    google_accept_terms_button = await tab.select('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ[type="button"][jsname="LgbsSe"]', timeout=15)
    await google_accept_terms_button.click()

    # Confirm Personalization
    await tab.wait_for('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.ksBjEc.lKxP2d.LQeN7.TrZEUc', timeout=15)
    google_confirm_personalization_button = await tab.select('button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.ksBjEc.lKxP2d.LQeN7.TrZEUc', timeout=15)
    await google_confirm_personalization_button.click()
    
    # Finish Gmail creation
    browser.stop()


    ####################################################################################################################################################
    ####################################################################################################################################################
    ####################################################################################################################################################

    ####################################################################################################################################################
    ####################################################################################################################################################
    ####################################################################################################################################################
    browser = await uc.start(browser_args=browser_args)

    # 01: Go to the osrs homepage
    tab = await browser.get("https://oldschool.runescape.com/")
    
    # Check if it asks to save cookies
    try:
        allow_all_cookies_button = await tab.find("Allow all cookies", best_match=True, timeout=30)
        await allow_all_cookies_button.click()
    except Exception as e:
        print(f"An error occurred: {e}")

    # 02: Click sign up button
    new_user_sign_up_button = await tab.find("New User?", best_match=True, timeout=30)
    await new_user_sign_up_button.click()    

    # 03: Click new account button
    new_account_button = await tab.find("New account", best_match=True, timeout=30)
    await new_account_button.click()

    # Check if it asks to save cookies
    try:
        allow_all_cookies_button = await tab.find("Allow all cookies", best_match=True, timeout=30)
        await allow_all_cookies_button.click()
    except Exception as e:
        print(f"An error occurred: {e}")

    # 04: Click email field and input email
    account_email_field = await tab.select('input[type="email"][name="email"]', timeout=30)
    await account_email_field.click()
    await account_email_field.send_keys(email)

    # 05: Click birth day field and input birth day
    birth_day_field = await tab.select('input[type="number"][name="day"]', timeout=30)
    await birth_day_field.click()
    await birth_day_field.send_keys(account_birth_day)

    # 06: Click birth month field and input birth month
    birth_month_field = await tab.select('input[type="number"][name="month"]', timeout=30)
    await birth_month_field.click()
    await birth_month_field.send_keys(account_birth_month)

    # 07: Click birth year field and input birth year
    birth_year_field = await tab.select('input[type="number"][name="year"]', timeout=30)
    await birth_year_field.click()
    await birth_year_field.send_keys(account_birth_year)

    # 08 Check terms and conditions box
    terms_and_conditions_checkbox = await tab.select('input[type="checkbox"][id="registration-start-accept-agreements"]', timeout=30)
    await terms_and_conditions_checkbox.click()

    await tab.sleep(20)

    # 09 Click continue
    continue_button = await tab.find("Continue", timeout=30)
    await continue_button.click()
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

    gmail_user_page_next_button = await tab2.find("Next")
    await gmail_user_page_next_button.click()

 

    # Inject the script to set window.zt and handleCaptcha
    #await inject_script(tab2)

    # Wait for the zt variable and solve the captcha
    #await wait_for_zt_and_solve_captcha(tab2)
    await click_recaptcha_checkbox(tab2)
    await click_randomly_within_iframe(tab, "api2/bframe", num_clicks=10)
    

    await tab2.wait_for('input[type="password"][name="Passwd"]', timeout=300)
    gmail_password_field = await tab2.select('input[type="password"][name="Passwd"]', timeout=30)
    await gmail_password_field.click()
    await gmail_password_field.send_keys(email_password)

    gmail_password_to_signin_next_button = await tab2.find("Next")
    await gmail_password_to_signin_next_button.click()

    # Click "not now" on the "complete a few suggestions" page for new accounts. Sometimes it shows, sometimes it doesn't.
    try:
        await tab2.wait_for('Not now', timeout=15)
        gmail_suggestions_not_now_button = await tab2.find('Not now', timeout=15)
        gmail_suggestions_not_now_button.click()
    except Exception as e:
        pass


    verification_code = await extract_verification_code_from_email_page(tab2)

    ####################################################################################################################################################
    ####################################################################################################################################################
    ####################################################################################################################################################

    #
    await tab.bring_to_front()
    await tab.wait_for('input[id="registration-verify-form-code-input"]', timeout=30)
    verification_field = await tab.select('input[id="registration-verify-form-code-input"]', timeout=30)
    await verification_field.click()
    await verification_field.send_keys(verification_code)
    
    verification_page_continue_button = await tab.find("Continue", timeout=30)
    await verification_page_continue_button.click()

    #
    await tab.wait_for('input[id="displayName"]', timeout=30)
    account_name_field = await tab.select('input[id="displayName"]', timeout=30)
    await account_name_field.click()
    await tab.sleep(1)
    await account_name_field.send_keys(account_name)
    await tab.sleep(2)

    account_name_page_continue_button = await tab.find("Continue", timeout=30)
    await account_name_page_continue_button.click() #check if name already exists

    #
    await tab.wait_for('input[id="password"]')
    account_password_field = await tab.select('input[id="password"]')
    await account_password_field.click()
    await tab.sleep(1)
    await account_password_field.send_keys(account_password)
    await tab.sleep(2)

    account_repassword_field = await tab.select('input[id="repassword"]')
    await account_repassword_field.click()
    await tab.sleep(1)
    await account_repassword_field.send_keys(account_password)
    await tab.sleep(2)

    account_password_page_continue_button = await tab.find("Create account", timeout=30)
    await account_password_page_continue_button.click()

    # Write details to a file
    file_path = 'created_accounts.csv'
    write_header = not os.path.exists(file_path) or os.path.getsize(file_path) == 0

    with open(file_path, 'a') as file:
        if write_header:
            file.write('account_name,account_password,MM,DD,YYYY,email,email_password,ip\n')
        
        file.write(f'{account_name},{account_password},{account_birth_month},{account_birth_day},{account_birth_year},{email},{email_password},{external_ip}\n')

    await asyncio.sleep(10000)


if __name__ == '__main__':
    uc.loop().run_until_complete(main())
