import os
import random
import time
import re

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from test_dataset import first_name, second_name, middle_name, random_date, position, \
    name_vehicle, type_vehicle, numberplate, vin_vehicle, exp_year_vehicle, \
    owners_company_number, owners_company_name, contract_number, date_contract


def enable_download_in_headless_chrome(web_dr, download_dir):
    """
    Add missing support for chrome "send_command"  to selenium web driver
    :param web_dr: web driver
    :param download_dir: directory where the file will be saved
    :return: renew web driver
    """
    web_dr.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    web_dr.execute("send_command", params)
    return web_dr


# Load '.env' file
load_dotenv()

# make directory for stuff
stuff_path = os.path.join(os.getcwd(), 'data')
resource_path = os.path.join(os.getcwd(), 'resource')
doc_path = os.path.join(resource_path, '1.pdf')

# Constants
URL = 'https://demo.i-propusk.ru'
LOGIN = os.getenv('LOGIN')
PASSWD = os.getenv('PASSWD')

# Options
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('start-maximized')
options.add_argument('--headless')
options.add_argument('--enable-javascript')
download_pref = {'download.default_directory': stuff_path, "download.prompt_for_download": False}
options.add_experimental_option("prefs", download_pref)

# Driver initial
s = Service(f'{os.getcwd()}/chromedriver')
driver = webdriver.Chrome(service=s, options=options)
driver = enable_download_in_headless_chrome(driver, stuff_path)

# Other var
timeout = 10
count_workers = 5
count_vehicle = 5


def create_vehicle():
    """
    Creating random vehicle
    :return: vehicle name, vehicle type, vehicle numberplate / VIN
    """
    v_type = random.choice(type_vehicle)
    v_name = random.choice(name_vehicle)
    v_numberplate = numberplate()
    v_vin = vin_vehicle()

    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//button[@data-id="Vehicle_VehicleTypeId"]'))).click()
    enter_type = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.LINK_TEXT, v_type)))
    enter_type.click()

    enter_create_date = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Vehicle_ReleaseDate')))
    enter_create_date.send_keys(exp_year_vehicle, Keys.ENTER)

    enter_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Vehicle_Name')))
    enter_name.send_keys(v_name)

    vehicle_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Vehicle_Number')))
    vehicle_number.send_keys(v_numberplate)

    vehicle_vin = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Vehicle_VIN')))
    vehicle_vin.send_keys(v_vin)

    owners_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'party-input')))
    owners_number.send_keys(owners_company_number)

    owners_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Vehicle_Owner')))
    owners_name.send_keys(owners_company_name)

    owner_contract = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Vehicle_OwnerContract')))
    owner_contract.send_keys(contract_number)

    contract_date = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Vehicle_OwnerDateFrom')))
    contract_date.send_keys(date_contract, Keys.ENTER)

    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//input[@value="Сохранить"]'))).send_keys(Keys.ENTER)

    print(f'\t\t{v_name} "{v_type}" - Гос. Номер: {v_numberplate} / VIN: {v_vin}')


def create_worker():
    """
    Creating random worker
    :return: second name, first name,  middle name, position
    """
    s_name = random.choice(second_name)
    f_name = random.choice(first_name)
    m_name = middle_name()
    birthday = random_date('1.1.1970', '1.1.2003', random.random())
    work_position = random.choice(position)

    enter_second_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Worker_LastName')))
    enter_second_name.send_keys(s_name)

    enter_first_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Worker_FirstName')))
    enter_first_name.send_keys(f_name)

    enter_middle_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Worker_MiddleName')))
    enter_middle_name.send_keys(m_name)

    birth_date = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'Worker_Birthday')))
    birth_date.send_keys(birthday)

    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//button[@data-id="worker-position"]'))).click()
    worker_position = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.LINK_TEXT, work_position)))
    worker_position.click()

    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'select2-worker-citizenship-container'))).click()
    worker_citizenship = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.CLASS_NAME, 'select2-search__field')))
    worker_citizenship.send_keys('РФ', Keys.ENTER)

    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//input[@value="Сохранить"]'))).click()

    print(f'\t\t{s_name} {f_name} {m_name} - {work_position}')


def input_elem(elem, key, key_bind):
    """
    Focus and enter value on login screen
    :param elem: input element, which must be in focus
    :param key: value, which must be enter
    :param key_bind: key bind
    :return:
    """
    elem.clear()
    elem.send_keys(key, key_bind)


def check_data(url, workers=None, vehicles=None):
    try:
        driver.get(url)

        # Authorization
        login = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, 'Email')))
        input_elem(login, LOGIN, Keys.ENTER)

        passwd = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'Password')))
        input_elem(passwd, PASSWD, Keys.ENTER)
        print('[INFO]: Test-Bot was logged in')

        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'swal2-confirm'))).click()

        WebDriverWait(driver, timeout).until((EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Applicant/Workers"]')))).click()

        print('[INFO]: Workers created:')
        while workers != 0:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="/Applicant/Workers/Create"]'))).click()
            create_worker()
            workers -= 1

        WebDriverWait(driver, timeout).until((EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Applicant/Vehicles"]')))).click()

        print('[INFO]: Vehicles created:')
        while vehicles != 0:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="/Applicant/Vehicles/Create"]'))).click()
            create_vehicle()
            vehicles -= 1

    except BaseException as ex:
        print(f'Something happens. {ex}')

    finally:
        print('[INFO]: Test-Bot was logged out')
        driver.close()
        driver.quit()


def main():
    check_data(URL, workers=count_workers, vehicles=count_vehicle)


if __name__ == '__main__':
    main()
