import os
import time
import re
import allure
import shutil
import random

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from data_test import first_name, second_name, middle_name, random_date, position, \
    name_vehicle, type_vehicle, numberplate, vin_vehicle, exp_year_vehicle, \
    owners_company_number, owners_company_name, contract_number, date_contract, filter_number_invites_worker, \
    filter_number_application_worker, filter_number_invites_vehicle, filter_number_application_vehicle


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


def find_created_worker(name, link=False):
    DriverInitialize.driver.execute_script('openFilterBlock(this);')

    filter_change_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
        until(EC.element_to_be_clickable((By.ID, 'Fio')))
    filter_change_name.send_keys(name, Keys.ENTER)

    soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
    if link:
        cell = soup.find('a', string=re.compile(f'{name}')).text.strip()
    else:
        cell = soup.find('strong', string=re.compile(f'{name}')).text.strip()

    if name in cell:
        assert True
    else:
        assert False, 'Worker not created'

    DriverInitialize.driver.execute_script('resetFilter();')


def find_created_vehicle(name, type):
    DriverInitialize.driver.execute_script('openFilterBlock(this);')

    filter_change_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
        until(EC.element_to_be_clickable((By.ID, 'Name')))
    filter_change_name.send_keys(name, Keys.ENTER)

    soup_name = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
    cell = soup_name.find(string=re.compile(f'{name}')).text.strip()

    WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//button[@data-id="TypeId"]'))).click()
    enter_type_vehicle = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
        until(EC.element_to_be_clickable((By.LINK_TEXT, type)))
    enter_type_vehicle.click()
    WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//input[@value="Применить"]'))).click()

    soup_type = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
    table_req = soup_type.find('table', class_="table-striped")
    rows = table_req.find_all('strong')
    cells = [row.find_all('span', {"title": re.compile(r'.*')}) for row in rows]
    types = list()
    for validate_cell in cells:
        for check_cell in validate_cell:
            res = check_cell.get('title').strip()
            types.append(res)
    error = 0
    for check_type in types:
        if type == check_type:
            continue
        else:
            error += 1
    if error == 0:
        assert True
    elif error > 0:
        assert False, 'Vehicle not created'

    if name in cell:
        assert True
    else:
        assert False, 'Vehicle not created'

    DriverInitialize.driver.execute_script('resetFilter();')


class DriverInitialize:
    # Load '.env' file
    load_dotenv()

    # make directory for stuff
    stuff_path = os.path.join(os.getcwd(), 'data')

    if not os.path.exists(stuff_path):
        os.mkdir(stuff_path)

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


@allure.feature('Test creating unit')
class TestCreatingUnit:
    @allure.title('Test authorization')
    def test_auth(self):
        DriverInitialize.driver.get(DriverInitialize.URL)

        # Authorization
        login = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.presence_of_element_located((By.ID, 'Email')))
        input_elem(login, DriverInitialize.LOGIN, Keys.ENTER)

        passwd = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'Password')))
        input_elem(passwd, DriverInitialize.PASSWD, Keys.ENTER)

        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'swal2-confirm'))).click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#applicantWrap"]')))

        if check_title:
            assert True
        else:
            assert False

    @allure.title('Test creating worker')
    def test_creating_worker(self):
        """
        Creating random worker
        :return:
        """
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until((EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Applicant/Workers"]')))).click()

        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Applicant/Workers/Create"]'))).click()

        s_name = random.choice(second_name)
        f_name = random.choice(first_name)
        m_name = middle_name()
        birthday = random_date('1.1.1970', '1.1.2003', random.random())
        work_position = 'Охранник - водитель ТРЭКОЛа'

        enter_second_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.ID, 'Worker_LastName')))
        enter_second_name.send_keys(s_name)

        enter_first_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.ID, 'Worker_FirstName')))
        enter_first_name.send_keys(f_name)

        enter_middle_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.ID, 'Worker_MiddleName')))
        enter_middle_name.send_keys(m_name)

        # For demo1 portal, where is this input
        #
        # birth_place = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
        #     EC.element_to_be_clickable((By.ID, 'Worker_Birthplace')))
        # birth_place.send_keys('г. Н-ск')

        birth_date = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.ID, 'Worker_Birthday')))
        birth_date.send_keys(birthday)

        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="worker-position"]'))).click()
        worker_position = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.LINK_TEXT, work_position)))
        worker_position.click()

        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'select2-worker-citizenship-container'))).click()
        worker_citizenship = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'select2-search__field')))
        worker_citizenship.send_keys('РФ', Keys.ENTER)

        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Сохранить"]'))).click()

        with open('workers.txt', 'a') as log:
            log.write('\t\t\t\t\t\t\t\t***')
            log.writelines(f'\n\t\t{s_name} {f_name} {m_name} - {work_position}\n')

        return_workers = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/Applicant/Workers"]')))
        return_workers.click()

        worker_name = f'{s_name} {f_name} {m_name}'

        find_created_worker(name=worker_name, link=True)

    @allure.title('Test creating vehicle')
    def test_creating_vehicle(self):
        """
        Creating random vehicle
        :return: vehicle name, vehicle type, vehicle numberplate / VIN
        """
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until((EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Applicant/Vehicles"]')))).click()
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Applicant/Vehicles/Create"]'))).click()

        v_type = random.choice(type_vehicle)
        v_name = random.choice(name_vehicle)
        v_numberplate = numberplate()
        v_vin = vin_vehicle()

        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="Vehicle_VehicleTypeId"]'))).click()
        enter_type = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.LINK_TEXT, v_type)))
        enter_type.click()

        enter_create_date = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.ID, 'Vehicle_ReleaseDate')))
        enter_create_date.send_keys(exp_year_vehicle, Keys.ENTER)

        enter_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.ID, 'Vehicle_Name')))
        enter_name.send_keys(v_name)

        vehicle_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.ID, 'Vehicle_Number')))
        vehicle_number.send_keys(v_numberplate)

        vehicle_vin = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.ID, 'Vehicle_VIN')))
        vehicle_vin.send_keys(v_vin)

        # For demo1 portal, where is this input
        #
        # owners_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
        #     EC.element_to_be_clickable((By.ID, 'party-input')))
        # owners_number.send_keys(owners_company_number)
        #
        # owners_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
        #     EC.element_to_be_clickable((By.ID, 'Vehicle_Owner')))
        # owners_name.send_keys(owners_company_name)
        #
        # owner_contract = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
        #     EC.element_to_be_clickable((By.ID, 'Vehicle_OwnerContract')))
        # owner_contract.send_keys(contract_number)
        #
        # contract_date = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
        #     EC.element_to_be_clickable((By.ID, 'Vehicle_OwnerDateFrom')))
        # contract_date.send_keys(date_contract, Keys.ENTER)

        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@value="Сохранить"]'))).send_keys(Keys.ENTER)

        with open('vehicles.txt', 'a') as log:
            log.write('\t\t\t\t\t\t\t\t***')
            log.writelines(f'\n\t\t{v_name} "{v_type}" - Гос. Номер: {v_numberplate} / VIN: {v_vin}\n')

        return_vehicles = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/Applicant/Vehicles"]')))
        return_vehicles.click()

        find_created_vehicle(name=v_name, type=v_type)

    @allure.title('Close and Quit')
    def test_quit(self):
        DriverInitialize.driver.close()
        DriverInitialize.driver.quit()
        shutil.rmtree(DriverInitialize.stuff_path)