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
    filter_number_pass_vehicle

from applicant import download_doc, pagination_test, input_elem


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
        print('\tTest-Bot was logged in, like "Трансп. безопасность"')

        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'swal2-confirm'))).click()

        close_app_wrap = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='#applicantWrap']")))
        close_app_wrap.click()

        # Enter to vehicle security folder
        try:
            enter_v_c = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#transportsecurityWrap"]')))
            enter_v_c.click()
        except BaseException as ex:
            logging.error(f'"Трансп. безопасность" dropdown working incorrect. {ex}')
        else:
            logging.info('"Трансп. безопасность"  dropdown working correct')

        # Passes
        logging.info('Testing "Пропуска" - has begun...')
        print('[INFO]: Testing "Пропуска" - has begun...')
        try:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#transportsecurityPassesWrap"]'))).click()

            # Vehicles passes
            try:
                pass_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/TransportSecurity/VehiclePasses"]')))
                try:
                    pass_vehicles.click()
                except BaseException as ex:
                    logging.error(f'List item "Транспорт" - working incorrect. {ex}')
                else:
                    logging.info('List item "Транспорт" - working correctly')

                try:
                    not_actual_pass_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[@isactual='false']")))
                    not_actual_pass_vehicles.click()
                except BaseException as ex:
                    logging.error(f'Tab "Не действующие" in list item "Транспорт" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Не действующие" in list item "Транспорт" - working correctly')

                download_doc()

                # Pagination test
                page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="?page=2&IsActual=False"]')))
                if page_number:
                    pagination_test(page_number)

                # Filter test
                open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.ID, 'btnFilterDesktop')))
                open_filter.click()

                filter_for_units(type_vehicle=filter_type_vehicle)
                filter_number_docs(number_app=filter_number_application_vehicle_pass, count_column=6,
                                   number_pass=filter_number_pass_vehicle, end_date=filter_end_date_pass)

                try:
                    actual_pass_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[@isactual='true']")))
                    actual_pass_vehicles.click()
                except BaseException as ex:
                    logging.error(f'Tab "Действующие" in list item "Транспорт"- working incorrect. {ex}')
                else:
                    logging.info('Tab "Действующие" in list item "Транспорт" - working correctly')

                download_doc()

                for check_file in os.listdir(stuff_path):
                    if check_file in 'VehiclePasses.csv':
                        logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
            except BaseException as ex:
                logging.error(f'List item "Транспорт" in dropdown "Пропуска" - working incorrect. {ex}')
            else:
                logging.info('List item "Транспорт" in dropdown "Пропуска" - working correctly')
            finally:
                os.remove(os.path.join(stuff_path, 'VehiclePasses.csv'))

        except BaseException as ex:
            logging.error('Something goes wrong during testing '
                          '"Пропуска". May be one or more element not found or been deprecated.')
            print('[ERROR]: Something goes wrong during testing '
                  '"Пропуска". May be one or more element not found or been deprecated.')
            logging.error(ex)
        else:
            logging.info('Dropdown "Пропуска" and all of elements in it - working correctly')
            logging.info('Testing "Пропуска" - is finished!')
            print('[SUCCESS]: Testing "Пропуска" - is finished!\n')
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