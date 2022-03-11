import os
import time
import logging
import re

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from test_dataset import filter_end_date_pass, filter_number_application_vehicle_pass, filter_type_vehicle, \
    filter_number_pass_vehicle, main_company, date_from_app_v_s, date_to_app_v_s, filter_organization, filter_datepick, \
    filter_type_vehicle_app, vehicle_id, filter_name_vehicle_app, filter_position, filter_name_pass, \
    filter_number_application_worker, filter_birth, filter_number_pass_worker


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

# Logging config
logging.basicConfig(
    filename='test.log',
    filemode='w',
    format='[%(levelname)s]: %(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)

# make directory for stuff
stuff_path = os.path.join(os.getcwd(), 'data')
resource_path = os.path.join(os.getcwd(), 'resource')
doc_path = os.path.join(resource_path, '1.pdf')

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
# options.add_argument('--headless')
options.add_argument('--enable-javascript')
download_pref = {'download.default_directory': stuff_path, "download.prompt_for_download": False}
options.add_experimental_option("prefs", download_pref)

# Driver initial
s = Service(f'{os.getcwd()}/chromedriver')
driver = webdriver.Chrome(service=s, options=options)
driver = enable_download_in_headless_chrome(driver, stuff_path)

# Other var
timeout = 10


def filter_for_apps(grand_contract=None, date_app=None, type_application=None):
    # Filter grand contact
    if grand_contract:
        enter_grand_contract = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'select2-MainCompany-container')))
        enter_grand_contract.click()
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'select2-search__field'))).send_keys(grand_contract)

        filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup_req = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup_req.find('table', class_="table-striped")
        rows = table_req.find_all('tr')
        cells = [row.find_all('td') for row in rows]
        name_comp = list()
        for cell in cells:
            count = 0
            for check_cell in cell:
                if count == 0:
                    res = check_cell.text.strip().split('</tr>')
                    for check_res in res:
                        name_comp.append(check_res)
        if main_company in name_comp:
            logging.info('"Генподрядчик" filter working correct')
        else:
            logging.error('"Генподрядчик" filter working incorrect')

        driver.execute_script('resetFilter();')
        driver.execute_script('openFilterBlock(this);')

    # Filter sub companies
    # Filter type app
    if type_application:
        type_request = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="appType"]')))
        type_request.click()

        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, './/div/input[@type="text"]'))).send_keys(type_application, Keys.ENTER)

        filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup_req = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup_req.find('table', class_="application-table table table-hover table-striped")
        info_delete = [i['class'] for i in table_req.find_all('i', class_='fa')]
        unit = list()
        for check_class in info_delete:
            for check_right_icon in check_class:
                if check_right_icon != 'fa' and check_right_icon != 'fa-lock' and check_right_icon != 'fa-check'\
                        and check_right_icon != 'float-right' \
                        and check_right_icon != 'm-r-15' \
                        and check_right_icon != 'p-t-5' \
                        and check_right_icon != 'fa-times':
                    unit.append(check_right_icon)

        if type_application == 'Сотрудники':
            error = 0
            for check_workers in unit:
                if check_workers != 'fa-users':
                    error += 1
                    break
            if error >= 1:
                logging.error('Method "Сотрудники" of filter "Вид заявки" working incorrect')
            else:
                logging.info('Method "Сотрудники" of filter "Вид заявки" working correctly')

        elif type_application == 'Транспорт':
            error = 0
            for check_workers in unit:
                if check_workers != 'fa-car':
                    error += 1
                    break
            if error >= 1:
                logging.error('Method "Транспорт" of filter "Вид заявки" working incorrect')
            else:
                logging.info('Method "Транспорт" of filter "Вид заявки" working correctly')

        elif type_application == 'ТМЦ':
            error = 0
            for check_workers in unit:
                if check_workers != 'fa-camera':
                    error += 1
                    break
            if error >= 1:
                logging.error('Method "ТМЦ" of filter "Вид заявки" working incorrect')
            else:
                logging.info('Method "ТМЦ" of filter "Вид заявки" working correctly')

        driver.execute_script('resetFilter();')
        driver.execute_script('openFilterBlock(this);')

    # Filter date
    if date_app:
        filter_date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'dateFrom')))
        filter_date_from.send_keys(date_from_app_v_s)

        filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'dateTo')))
        filter_date_to.send_keys(date_to_app_v_s, Keys.ENTER)

        filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="application-table table table-hover table-striped")
        date = table_req.find_all('tr')[1].find_all('td')[-2].text.strip().split(' ')
        if date_from_app_v_s == date[0]:
            logging.info('"Дата подачи" filter working correct')
        else:
            logging.error('"Дата подачи" filter working correct')

        driver.execute_script('resetFilter();')
        driver.execute_script('openFilterBlock(this);')


def filter_for_units(org=None, name=None, position=None, date_birth=None, type_vehicle=None, tab=False, link=False):
    """
    Test common filter input of units
    :param org: company / organisation
    :param name: name worker
    :param position: position
    :param date_birth: birth day
    :param type_vehicle: type of vehicle
    :param tab: if need change tab before test
    :param link: if unit name is a link
    :return:
    """
    # Filter company
    if org:
        filter_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'select2-MainCompanyId-container')))
        filter_company.click()
        change_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'select2-search__field')))
        change_company.send_keys(org)
        change_company.send_keys(Keys.ENTER)
        filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]')))
        filter_enter_button.click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="table-striped")
        rows = table_req.find_all('tr')
        cells = [row.find_all('span', {"title": re.compile(r'АО "ПРЕМЬЕРСТРОЙ"')}) for row in rows]
        units = list()
        for cell in cells:
            for check_cell in cell:
                res = check_cell.text.strip().split('</td>')
                for check_res in res:
                    units.append(check_res)
        if len(units) != 10:
            logging.error('"Организация" filter working incorrect')
        elif len(units) == 10:
            logging.info('"Организация" filter working correct')

        driver.execute_script('resetFilter();')
        if tab:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@isactual='false']"))).click()
        driver.execute_script('openFilterBlock(this);')

    # Filter name
    if name:
        filter_change_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'Fio')))
        filter_change_name.send_keys(name, Keys.ENTER)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if link:
            cell = soup.find('a', string=re.compile(f'{name}')).text.strip()
        else:
            cell = soup.find('strong', string=re.compile(f'{name}')).text.strip()

        if name in cell:
            logging.info('"ФИО" filter working correct')
        else:
            logging.error('"ФИО" filter working incorrect')

        driver.execute_script('resetFilter();')
        if tab:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@isactual='false']"))).click()
        driver.execute_script('openFilterBlock(this);')

        # Filter position
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="WorkerPosition"]'))).click()
        worker_position = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.LINK_TEXT, position)))
        worker_position.click()
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="table-striped")
        rows = table_req.find_all('div', 'table-info')
        cells = [row.find_all('span', {"title": re.compile(r'.*')}) for row in rows]
        positions = list()
        for cell in cells:
            for check_cell in cell:
                res = check_cell.text.strip().split('</td>')
                for check_res in res:
                    positions.append(check_res)
        error = 0
        for check_position in positions:
            if position in check_position:
                continue
            else:
                error += 1

        if error == 0:
            logging.info('"Должность" filter working correct')
        elif error > 0:
            logging.error('"Должность" filter working incorrect')

        driver.execute_script('resetFilter();')
        if tab:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@isactual='false']"))).click()
        driver.execute_script('openFilterBlock(this);')

    # Filter date birth
    if date_birth:
        filter_date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'birthdayFrom')))
        filter_date_from.send_keys(date_birth)

        filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'birthdayTo')))
        filter_date_to.send_keys(date_birth, Keys.ENTER)

        filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup_req = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup_req.find('table', class_="table-striped")
        date_birthday = table_req.find('small', text=re.compile('03.02.2004')).text.strip()

        if date_birth == date_birthday:
            logging.info('"Дата рождения" filter working correct')
        else:
            logging.error('"Дата рождения" filter working correct')

        driver.execute_script('resetFilter();')
        if tab:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@isactual='false']"))).click()
        driver.execute_script('openFilterBlock(this);')

    # Filter type of vehicle
    if type_vehicle:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="VehicleTypeId"]'))).click()
        enter_type_vehicle = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.LINK_TEXT, type_vehicle)))
        enter_type_vehicle.click()
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="table-striped")
        rows = table_req.find_all('strong')
        cells = [row.find_all('span', {"title": re.compile(r'.*')}) for row in rows]
        types = list()
        for cell in cells:
            for check_cell in cell:
                res = check_cell.get('title').strip()
                types.append(res)
        error = 0
        for check_type in types:
            if type_vehicle == check_type:
                continue
            else:
                error += 1
        if error == 0:
            logging.info('"Тип ТС" filter working correct')
        elif error > 0:
            logging.error('"Тип ТС" filter working incorrect')


def filter_number_docs(number_app=None, count_column=None, number_inv=None, number_pass=None, end_date=None):
    """
    Test common filter input of docs
    :param number_app: number of application
    :param count_column: number of column where placed needful data
    :param number_inv: number of invites
    :param number_pass: number of pass
    :param end_date: date of the end of pass
    :return:
    """
    # Filter number invites
    if number_inv:
        enter_number_inv = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'Number')))
        enter_number_inv.send_keys(number_inv, Keys.ENTER)
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="table-striped")
        rows = table_req.find_all('tr')
        cells = [row.find_all('td') for row in rows]
        num_inv = ''
        for cell in cells:
            count = 0
            for check_cell in cell:
                count += 1
                if count == 3:
                    res = check_cell.text.strip().split(' ')
                    for check_res in res:
                        num_inv = ''.join(check_res)
        if num_inv == number_inv:
            logging.info('"Номер приглашения" filter working correct')
        else:
            logging.error('"Номер приглашения" filter working incorrect')

        driver.execute_script('resetFilter();')
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@isactual='false']"))).click()
        driver.execute_script('openFilterBlock(this);')

    # Filter number application
    if number_app:
        enter_number_app = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'ApplicationId')))
        enter_number_app.send_keys(number_app, Keys.ENTER)
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="table-striped")
        rows = table_req.find_all('tr')
        cells = [row.find_all('td') for row in rows]
        num_app = ''
        for cell in cells:
            count = 0
            for check_cell in cell:
                count += 1
                if count == count_column:
                    res = check_cell.text.strip().split(' ')
                    for check_res in res:
                        num_app = ''.join(check_res)
        if num_app == number_app:
            logging.info('"Номер заявки" filter working correct')
        else:
            logging.error('"Номер заявки" filter working incorrect')

        driver.execute_script('resetFilter();')
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@isactual='false']"))).click()
        driver.execute_script('openFilterBlock(this);')

    # Filter number pass
    if number_pass:
        enter_number_inv = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'BarCode')))
        enter_number_inv.send_keys(number_pass, Keys.ENTER)
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="table-striped")
        rows = table_req.find_all('tr')
        cells = [row.find_all('td') for row in rows]
        num_pass = ''
        for cell in cells:
            count = 0
            for check_cell in cell:
                count += 1
                if count == 3:
                    res = check_cell.text.strip().split(' ')
                    for check_res in res:
                        num_pass = ''.join(check_res)
        if num_pass == number_pass:
            logging.info('"Номер пропуска" filter working correct')
        else:
            logging.error('"Номер пропуска" filter working incorrect')

        driver.execute_script('resetFilter();')
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@isactual='false']"))).click()
        driver.execute_script('openFilterBlock(this);')

    # Filter end date of pass
    if end_date:
        filter_date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'dateFrom')))
        filter_date_from.send_keys(end_date)

        filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'dateTo')))
        filter_date_to.send_keys(filter_end_date_pass, Keys.ENTER)

        filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="table-striped")
        rows = table_req.find_all('tr')
        cells = [row.find_all('td') for row in rows]
        end_dates = list()
        for cell in cells:
            count = 0
            for check_cell in cell:
                count += 1
                if count == 5:
                    res = check_cell.text.strip().split(' ')
                    for check_res in res:
                        end_dates.append(check_res)
        error = 0
        for check_date in end_dates:
            if end_date == check_date:
                continue
            else:
                error += 1

        if error == 0:
            logging.info('"Дата окончания" filter working correct')
        elif error >= 1:
            logging.error('"Дата окончания" filter working incorrect')

        driver.execute_script('resetFilter();')
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@isactual='false']"))).click()
        driver.execute_script('openFilterBlock(this);')


def filter_for_units_app(birth_d=None, type_vehicle=None, id_vehicle=None, name_vehicle=None):
    """
    SPECIAL for units from tab application
    :param birth_d: birth day date from app
    :param type_vehicle: type of vehicle from app
    :param id_vehicle: id of vehicle from app
    :param name_vehicle: name of vehicle from app
    :return:
    """
    # Filter date
    filter_date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'dateFrom')))
    filter_date_from.send_keys(birth_d)

    filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'dateTo')))
    filter_date_to.send_keys(filter_end_date_pass, Keys.ENTER)

    filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//input[@value="Применить"]')))
    filter_enter.click()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table_req = soup.find('table', class_="table-striped")
    date_birthday = table_req.find(text=re.compile(f'{birth_d}')).text.strip()

    if birth_d == date_birthday:
        logging.info('"Дата выпуска" filter working correct')
    else:
        logging.error('"Дата выпуска" filter working correct')

    driver.execute_script('resetFilter();')
    driver.execute_script('openFilterBlock(this);')

    # Filter type of vehicle
    if type_vehicle:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="TypeId"]'))).click()
        enter_type_vehicle = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.LINK_TEXT, type_vehicle)))
        enter_type_vehicle.click()
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="table-striped")
        rows = table_req.find_all('strong')
        cells = [row.find_all('span', {"title": re.compile(r'.*')}) for row in rows]
        types = list()
        for cell in cells:
            for check_cell in cell:
                res = check_cell.get('title').strip()
                types.append(res)
        error = 0
        for check_type in types:
            if type_vehicle == check_type:
                continue
            else:
                error += 1
        if error == 0:
            logging.info('"Тип ТС" filter working correct')
        elif error > 0:
            logging.error('"Тип ТС" filter working incorrect')

        driver.execute_script('resetFilter();')
        driver.execute_script('openFilterBlock(this);')

    # Filter id vehicle
    if id_vehicle:
        enter_id_vehicle = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'VehicleId')))
        enter_id_vehicle.send_keys(id_vehicle)

        filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup_req = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup_req.find('table', class_="table-striped")
        rows = table_req.find_all('tr')
        cells = [row.find_all('td') for row in rows]
        id_v = ''
        for cell in cells:
            count = 0
            for check_cell in cell:
                count += 1
                if count == 1:
                    res = check_cell.text.strip().split(' ')
                    for check_res in res:
                        id_v = ''.join(check_res)
        if id_v == id_vehicle:
            logging.info('"Код ТС" filter working correct')
        else:
            logging.error('"Код ТС" filter working incorrect')

        driver.execute_script('resetFilter();')
        driver.execute_script('openFilterBlock(this);')

    # Filter name vehicle
    if name_vehicle:
        filter_change_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'Name')))
        filter_change_name.send_keys(name_vehicle, Keys.ENTER)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cell = soup.find(string=re.compile(f'{name_vehicle}')).text.strip()

        if name_vehicle in cell:
            logging.info('"Марка" filter working correct')
        else:
            logging.error('"Марка" filter working incorrect')

        driver.execute_script('resetFilter();')
        driver.execute_script('openFilterBlock(this);')


def pagination_test(path_to_number):
    """
    Pagination test
    :param path_to_number: Xpath to button-number
    :return:
    """
    try:
        path_to_number.click()
    except BaseException as ex:
        logging.error(f'Pagination\'s number working incorrect.{ex}')
    else:
        logging.info('Pagination\'s number working correctly')

    try:
        prev_btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[text()="Пред."]')))
        prev_btn.click()
    except BaseException as ex:
        logging.error(f'Pagination\'s button "Пред." working incorrect.{ex}')
    else:
        logging.info('Pagination\'s button "Пред." working correctly')

    try:
        prev_btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[text()="След."]')))
        prev_btn.click()
    except BaseException as ex:
        logging.error(f'Pagination\'s button "След." working incorrect.{ex}')
    else:
        logging.info('Pagination\'s button "След." working correctly')


def download_doc():
    """
    Click to "Excel" button and download document
    :return:
    """
    try:
        not_actual_inv_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'btnDownloadCsvFile')))
        not_actual_inv_download.click()
        time.sleep(1)
    except BaseException as ex:
        logging.error(f'Button "Excel" '
                      f'working incorrect. {ex}')
    else:
        logging.info('Button "Excel" working correctly')


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


def check_data(url):
    """
    Check main functional of role
    :param url: url
    :return:
    """
    try:
        driver.get(url)

        # Authorization
        login = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, 'Email')))
        input_elem(login, LOGIN, Keys.ENTER)

        passwd = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'Password')))
        input_elem(passwd, PASSWD, Keys.ENTER)
        logging.info('Test-Bot was logged in')
        print('\tTest-Bot was logged in, like "Пром. безопасность"')

        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'swal2-confirm'))).click()

        # Enter to vehicle security folder
        try:
            enter_v_c = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#industrialsecurityWrap"]')))
            enter_v_c.click()
        except BaseException as ex:
            logging.error(f'"Пром. безопасность" dropdown working incorrect. {ex}')
        else:
            logging.info('"Пром. безопасность"  dropdown working correct')

        # Passes
        logging.info('Testing "Пропуска" - has begun...')
        print('[INFO]: Testing "Пропуска" - has begun...')
        try:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#industrialsecurityPassesWrap"]'))).click()

            # Workers passes
            try:
                pass_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/IndustrialSecurity/WorkerPasses"]')))
                try:
                    pass_workers.click()
                except BaseException as ex:
                    logging.error(f'List item "Сотрудники" - working incorrect. {ex}')
                else:
                    logging.info('List item "Сотрудники" - working correctly')

                try:
                    not_actual_pass_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[@isactual='false']")))
                    not_actual_pass_workers.click()
                except BaseException as ex:
                    logging.error(f'Tab "Не действующие" in list item "Сотрудники" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Не действующие" in list item "Сотрудники" - working correctly')

                download_doc()

                # Pagination test
                page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="?page=2&SortingColumn=Id&SortingDirection=desc&IsActual=False"]')))
                if page_number:
                    pagination_test(page_number)

                # Filter test
                open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.ID, 'btnFilterDesktop')))
                open_filter.click()
                try:
                    filter_for_units(org=filter_organization, name=filter_name_pass,
                                     position=filter_position, date_birth=filter_birth, tab=True)
                    filter_number_docs(number_app=filter_number_application_worker, count_column=6,
                                       number_pass=filter_number_pass_worker, end_date=filter_end_date_pass)

                    # Filter antibodies
                    logging.warning('Input "Антитела" - manual testing only')

                except BaseException as ex:
                    logging.error(f'Filter working incorrect. {ex}')
                else:
                    logging.info('Filter working correctly')

                try:
                    actual_pass_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[@isactual='true']")))
                    actual_pass_workers.click()
                except BaseException as ex:
                    logging.error(f'Tab "Действующие" in list item "Сотрудники"- working incorrect. {ex}')
                else:
                    logging.info('Tab "Действующие" in list item "Сотрудники" - working correctly')

                download_doc()

                for check_file in os.listdir(stuff_path):
                    if check_file in 'WorkerPasses.csv':
                        logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
            except BaseException as ex:
                logging.error(f'List item "Сотрудники" in dropdown "Пропуска" - working incorrect. {ex}')
            else:
                logging.info('List item "Сотрудники" in dropdown "Пропуска" - working correctly')
            finally:
                os.remove(os.path.join(stuff_path, 'WorkerPasses.csv'))

            # Value passes
            try:
                pass_values = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/IndustrialSecurity/ValuePasses"]')))
                try:
                    pass_values.click()
                except BaseException as ex:
                    logging.error(f'List item "ТМЦ" - working incorrect. {ex}')
                else:
                    logging.info('List item "ТМЦ" - working correctly')

                try:
                    not_actual_pass_value = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, '//div[@isactual="false"]')))
                    not_actual_pass_value.click()
                except BaseException as ex:
                    logging.error(f'Tab "Не действующие" in list item "ТМЦ" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Не действующие" in list item "ТМЦ" - working correctly')

                download_doc()

                # # Pagination test
                # page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                #     (By.XPATH, '')))
                # if page_number:
                #     pagination_test(page_number)
                # else:
                #     logging.warning('Less than one page. Testing impossible')
                logging.warning('Less than one page. Testing pagination impossible')

                # Filter test
                logging.warning('Filter only manual testing')

                try:
                    actual_pass_value = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, '//div[@isactual="true"]')))
                    actual_pass_value.click()
                except BaseException as ex:
                    logging.error(f'Tab "Действующие" in list item "ТМЦ" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Действующие" in list item "ТМЦ" - working correctly')

                download_doc()

                for check_file in os.listdir(stuff_path):
                    if check_file in 'ValuePasses.csv':
                        logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
            except BaseException as ex:
                logging.error(f'List item "ТМЦ" in dropdown "Пропуска" - working incorrect. {ex}')
            else:
                logging.info('List item "ТМЦ" in dropdown "Пропуска" - working correctly')
            finally:
                os.remove(os.path.join(stuff_path, 'ValuePasses.csv'))

            # Print Invites
            try:
                inv_print = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/IndustrialSecurity/PrintPass/GetPdf"]')))
                try:
                    inv_print.click()
                except BaseException as ex:
                    logging.error(f'List item "Печать пропусков" - working incorrect. {ex}')
                else:
                    logging.info('List item "Печать пропусков" - working correctly')

                try:
                    download_inv_pdf = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, '//input[@value="Скачать"]')))
                    download_inv_pdf.click()

                    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.ID, 'ApplicationId-error')))
                except BaseException as ex:
                    logging.error(f'Verification - failed (no alert for empty input). {ex}')
                else:
                    logging.info('Verification for empty required input - working correctly')

                try:
                    download_inv_pdf = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, '//input[@value="Скачать"]')))
                    download_inv_pdf.send_keys('1000000 , d s addfdf', Keys.ENTER)

                    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.CLASS_NAME, 'validation-summary-errors')))
                except BaseException as ex:
                    logging.error(f'Verification - failed. See log file. {ex}')
                else:
                    logging.info('Verification for random input - working correctly')
            except BaseException as ex:
                logging.error(f'List item "Печать пропусков" in dropdown "Пропуска" - working incorrect. {ex}')
            else:
                logging.info('List item "Печать пропусков" in dropdown "Пропуска" - working correctly')
        except BaseException as ex:
            logging.error('Something goes wrong during testing '
                          '"Пропуска". May be one or more element not found or been deprecated.')
            print('[ERROR]: Something goes wrong during testing '
                  '"Пропуска". May be one or more element not found or been deprecated.')
            logging.error(ex)
        else:
            logging.info('Testing "Пропуска" - is finished!')
            print('[SUCCESS]: Testing "Пропуска" - is finished!\n')

        # Applications
        logging.info('Testing "Заявки" - has begun...')
        print('[INFO]: Testing "Заявки" - has begun...')
        try:
            enter_app = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#industrialsecurityApplications"]')))
            enter_app.click()

            # Applications
            try:
                click_app_li = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/IndustrialSecurity/Applications"]')))
                click_app_li.click()

                download_doc()
                for check_file in os.listdir(stuff_path):
                    if check_file in 'Applications.csv':
                        logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')

                # Pagination test
                page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '//a[@href="?page=2&IsActual=True"]')))
                if page_number:
                    pagination_test(page_number)

                # Filter test
                open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.ID, 'btnFilterMobile')))
                open_filter.click()

                logging.warning('Other filter input\'s should tested manually')

                filter_for_apps(grand_contract=main_company, type_application='Сотрудники')
                filter_for_apps(type_application='Транспорт', date_app=True)
                filter_for_apps(type_application='ТМЦ')
                logging.warning('"Субподрядчик" should tested manually')
                logging.warning('"Статус" should tested manually')
                logging.warning('"По роли" should tested manually')
                logging.warning('"Согласующий" should tested manually')
            except BaseException as ex:
                logging.error(f'List item "Заявки" in dropdown "Заявки" - working incorrect. {ex}')
            else:
                logging.info('List item "Заявки" in dropdown "Заявки" - working correctly')
            finally:
                os.remove(os.path.join(stuff_path, 'Applications.csv'))
        except BaseException as ex:
            logging.error('Something goes wrong during testing '
                          '"Заявки". May be one or more element not found or been deprecated.')
            print('[ERROR]: Something goes wrong during testing '
                  '"Заявки". May be one or more element not found or been deprecated.')
            logging.error(ex)
        else:
            logging.info('Testing "Заявки" - has finished!')
            print('[SUCCESS]: Testing "Заявки" - has finished!\n')

        # Dict
        logging.info('Testing "Справочники" - has begun...')
        print('[INFO]: Testing "Справочники" - has begun...')
        try:
            enter_dict = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#industrialsecurityDictWrap"]')))
            enter_dict.click()

            # Position requirement
            try:
                click_req_li = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/IndustrialSecurity/WorkerDocumentTypes"]')))
                click_req_li.click()

                logging.warning('List item "Треб. должностей" should tested manually')
            except BaseException as ex:
                logging.error(f'List item "Треб. должностей" in dropdown "Справочники" - working incorrect. {ex}')
            else:
                logging.info('List item "Треб. должностей" in dropdown "Справочники" - working correctly')

            # Object
            try:
                click_obj_li = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/IndustrialSecurity/Locations"]')))
                click_obj_li.click()

                download_doc()

                for check_file in os.listdir(stuff_path):
                    if check_file in 'Locations.csv':
                        logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')

                # Pagination test
                page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="?page=2&IsActual=True"]')))
                if page_number:
                    pagination_test(page_number)
            except BaseException as ex:
                logging.error(f'List item "Объекты" in dropdown "Справочники" - working incorrect. {ex}')
            else:
                logging.info('List item "Объекты" in dropdown "Справочники" - working correctly')
            finally:
                os.remove(os.path.join(stuff_path, 'Locations.csv'))
        except BaseException as ex:
            logging.error('Something goes wrong during testing '
                          '"Справочники". May be one or more element not found or been deprecated.')
            print('[ERROR]: Something goes wrong during testing '
                  '"Справочники". May be one or more element not found or been deprecated.')
            logging.error(ex)
        else:
            logging.info('Testing "Справочники" - has finished!')
            print('[SUCCESS]: Testing "Справочники" - has finished!\n')

        # Reports
        logging.info('Testing "Отчёты" - has begun...')
        print('[INFO]: Testing "Отчёты" - has begun...')
        try:
            reports_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#industrialsecurityReportsWrap"]')))
            reports_tab.click()

            # Expired docs
            try:
                reports_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/IndustrialSecurity/ExpiredDocs"]')))
                reports_tab.click()
            except BaseException as ex:
                logging.error(f'List item "Истекающие документы" working incorrect. {ex}')
            else:
                logging.info('List item "Истекающие документы" working correctly')

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Pagination test
            page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="?page=2&SortingColumn=DaysLeft&SortingDirection=desc&IsActual=True"]')))
            if page_number:
                pagination_test(page_number)

            download_doc()

            for check_file in os.listdir(stuff_path):
                if check_file in 'ExpiredDocs.csv':
                    logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')

            # Filter test
            open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.ID, 'btnFilterDesktop')))
            open_filter.click()

            try:
                # Filter type
                enter_selector = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//button[@data-id="Type"]')))
                enter_selector.click()
                change_type = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//input[@type="text"]')))
                change_type.send_keys('Сотрудник', Keys.ENTER)

                submit_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//input[@value="Применить"]')))
                submit_filter.click()
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table_req = soup.find('table', class_="table table-hover table-striped")
                rows = table_req.find_all('tr')
                cells = [row.find_all('td') for row in rows]
                units = list()
                for cell in cells:
                    count = 0
                    for check_cell in cell:
                        count += 1
                        if count == 5:
                            res = check_cell.text.strip().split(' ')
                            for check_res in res:
                                units.append(check_res)
                            count = 0
                error = 0
                for check_unit in units:
                    if check_unit != 'Сотрудник':
                        error += 1
                if error >= 1:
                    logging.error('"Тип" filter working incorrect')
                else:
                    logging.info('"Тип" filter working correct')

                reset_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'a-clear')))
                reset_filter.click()

                driver.execute_script('openFilterBlock(this);')

                # Filter name
                enter_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.ID, 'Name')))
                enter_name.send_keys('Карманов Марсель Феликсович', Keys.ENTER)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table_req = soup.find('table', class_="table table-hover table-striped")
                rows = table_req.find_all('tr')
                cells = [row.find_all('td') for row in rows]
                units = list()
                for cell in cells:
                    count = 0
                    for check_cell in cell:
                        count += 1
                        if count == 4:
                            res = check_cell.text.strip().split('</td>')
                            for check_res in res:
                                units.append(check_res)
                            count = 0
                clear_units = [j for j in units if j != 'Не действителен']
                error = 0
                for check_unit in clear_units:
                    if 'Карманов Марсель Феликсович' not in check_unit:
                        error += 1
                if error >= 1:
                    logging.error('"Наименование" filter working incorrect')
                else:
                    logging.info('"Наименование" filter working correct')

                reset_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'a-clear')))
                reset_filter.click()

                driver.execute_script('openFilterBlock(this);')

                # Filter doc
                enter_doc = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.ID, 'DocName')))
                enter_doc.send_keys('Трудовой договор', Keys.ENTER)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table_req = soup.find('table', class_="table table-hover table-striped")
                rows = table_req.find_all('tr')
                cells = [row.find_all('td') for row in rows]
                units = list()
                for cell in cells:
                    count = 0
                    for check_cell in cell:
                        count += 1
                        if count == 6:
                            res = check_cell.text.strip().split('</td>')
                            for check_res in res:
                                units.append(check_res)
                            count = 0
                error = 0
                for check_unit in units:
                    if 'Трудовой договор' not in check_unit:
                        error += 1
                if error >= 1:
                    logging.error('"Документ" filter working incorrect')
                else:
                    logging.info('"Документ" filter working correct')

                reset_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'a-clear')))
                reset_filter.click()

                driver.execute_script('openFilterBlock(this);')

                # Filter date
                date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.ID, 'dateFrom')))
                date_from.send_keys('28.02.2022')

                time.sleep(1)

                date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.ID, 'dateTo')))
                date_to.send_keys('28.02.2022')
                submit_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//input[@value="Применить"]')))
                submit_filter.click()

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table_req = soup.find('table', class_="table table-hover table-striped")
                rows = table_req.find_all('tr')
                cells = [row.find_all('td') for row in rows]
                units = list()
                for cell in cells:
                    count = 0
                    for check_cell in cell:
                        count += 1
                        if count == 7:
                            res = check_cell.text.strip().split('</td>')
                            for check_res in res:
                                units.append(check_res)
                            count = 0
                error = 0
                for check_unit in units:
                    if '28.02.2022' not in check_unit:
                        error += 1
                if error >= 1:
                    logging.error('"Дата окончания" filter working incorrect')
                else:
                    logging.info('"Дата окончания" filter working correct')

                reset_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.CLASS_NAME, 'a-clear')))
                reset_filter.click()
            except BaseException as ex:
                logging.error(f'Filter working incorrect. {ex}')
            else:
                logging.info('Filter working correctly')

        except BaseException as ex:
            logging.error('Something goes wrong during testing '
                          '"Отчёты". May be one or more element not found or been deprecated.')
            print('[ERROR]: Something goes wrong during testing '
                  '"Отчёты". May be one or more element not found or been deprecated.')
            logging.error(ex)
        else:
            logging.info('Testing "Отчёты" - has finished!')
            print('[SUCCESS]: Testing "Отчёты" - has finished!\n')
        finally:
            os.remove(os.path.join(stuff_path, 'ExpiredDocs.csv'))
    except BaseException as ex:
        print(f'{ex} Something goes wrong. See the log file.')

    finally:
        driver.close()
        driver.quit()
        os.rmdir(stuff_path)


def main():
    check_data(URL)


if __name__ == '__main__':
    main()