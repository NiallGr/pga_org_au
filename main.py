from datetime import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

columnslist = ["Source", "Firm", "URL", "Email_Address"]
list_of_data = []
numbers_printed = 0
empty = pd.DataFrame(list_of_data, columns=columnslist)
empty.to_csv('pga_org_au.csv', encoding='utf-8-sig', index=False)


def click_button():
    options = webdriver.ChromeOptions()
    # Open window to large size
    WINDOW_SIZE = "1920,1080"
    # options.add_argument("--headless")
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    # options.add_argument('--headless')
    # Download google chrome driver (Needed for Selenuim)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://pga.org.au/find-a-pga-pro/')

    time.sleep(2)

    postcode_input = driver.find_element(By.XPATH, '//*[@id="members_value"]')

    # list of page sources
    sourcelist = []
    # Loop through increments of 5 for the postcodes.
    for postcode in range(5, 65, 5):
        # print(postcode)
        parent_div = driver.find_element(By.XPATH, '//*[@id="members_dropdown"]')
        # 2 seconds or will not catch
        time.sleep(2)
        postcode_input.send_keys(postcode)
        # 2 seconds or will not catch
        time.sleep(2)
        count_of_divs = len(parent_div.find_elements(By.CLASS_NAME, "angucomplete-row"))
        # print(count_of_divs)

        # Loop through all the elements in a dropdown
        for dropdowns in range(1, count_of_divs + 1):
        # Testing
        # for dropdowns in range(2, 5, 1):

            postcode_input.send_keys(postcode)

            time.sleep(2)
            print(dropdowns, 'out of', count_of_divs, 'results in postcode search: ', postcode)

            try:
                dropdown_increments = driver.find_element(By.XPATH, f'//*[@id="members_dropdown"]/div[{dropdowns}]')
                names_of_postcodes = driver.find_element(By.XPATH,
                                                         f'//*[@id="members_dropdown"]/div[{dropdowns}]/div[1]').text

                # print(dropdown_increments)
                print('Postcode: ', names_of_postcodes)

                driver.execute_script(
                    "arguments[0].setAttribute('class', 'angucomplete-row ng-scope angucomplete-selected-row')",
                    dropdown_increments)


            except:
                print('no dropdown or element found')
            time.sleep(3)
            try:
                dropdown_increments.click()
            except:
                print('There is no button')
            time.sleep(3)
            postcode_input.clear()
            # Get page source
            page_source = driver.page_source
            # Add to list of sources
            sourcelist.append(page_source)
    # list of soups
    souplist = []
    # Loop through list of soups
    for x in range(len(sourcelist)):
        # Create soup object
        soup = BeautifulSoup(sourcelist[x], 'lxml')
        # Add soup to souplist and return the souplist
        souplist.append(soup)
        # print(souplist)
    return souplist


def scrape(soup):
    scraped_data_list = []
    Source = 'https://www.aiff.net.au/2022-exhibitor-list/'
    try:
        info_section = soup.find_all('div', 'col-md-4 cards-stacked below-row ng-scope')
        # print(info_section)

        for info in info_section:

            try:
                Firm = info.find('h3', 'name-of-pro ng-binding').text
            except:
                Firm = 'null'
            try:
                URL = info.find(lambda tag: tag.name == "a" and "WEBSITE" in tag.text)['href']
            except:
                URL = 'null'
            try:
                Email_Address = info.find('a', class_='btn btn-primary find-pro-info')['href']

            except:
                Email_Address = 'null'

            scraped_data = (Source, Firm, URL, Email_Address)
            scraped_data_list.append(scraped_data)

    except:
        pass

    return scraped_data_list


souplist = click_button()

for soup in souplist:
    try:
        # calls scrape function
        for data_tuple in scrape(soup):
            print('t', data_tuple)
            numbers_printed += 1

            list_of_data.append(data_tuple)
            df = pd.DataFrame([data_tuple], columns=columnslist)
            df.to_csv('pga_org_au.csv', encoding='utf-8-sig', index=False, mode='a', header=False)
            print('Number of results printed: ', numbers_printed)
    except Exception as e:
        print('Scrape ended early, refer to error message, saving scraped data to file')
        print(e)
        df = pd.DataFrame(list_of_data, columns=columnslist)
        df.to_csv('pga_org_au_crashed.csv', encoding='utf-8-sig', index=False)
        print("Saved with a total volume of: ", len(df))
