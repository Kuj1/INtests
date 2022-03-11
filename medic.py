import os
import time
import logging

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from test_dataset import main_company, date_from_app, date_to_app


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
    """
    Test filter's input
    :param grand_contract: main contract
    :param date_app: date application
    :param type_application: type application
    :return:
    """
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
        filter_date_from.send_keys(date_from_app)

        filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.ID, 'dateTo')))
        filter_date_to.send_keys(date_to_app, Keys.ENTER)

        filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="application-table table table-hover table-striped")
        date = table_req.find_all('tr')[1].find_all('td')[-2].text.strip().split(' ')
        if date_from_app == date[0]:
            logging.info('"Дата подачи" filter working correct')
        else:
            logging.error('"Дата подачи" filter working correct')

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
        print('\tTest-Bot was logged in, like "Медик"')

        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'swal2-confirm'))).click()

        # Enter to medic's folder
        try:
            enter_medic = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#medicWrap"]')))
            enter_medic.click()
        except BaseException as ex:
            logging.error(f'"Медик" dropdown working incorrect. {ex}')
        else:
            logging.info('"Медик"  dropdown working correct')

        # Applications
        logging.info('Testing "Заявки" - has begun...')
        print('[INFO]: Testing "Заявки" - has begun...')
        try:
            enter_app = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#medicApplications"]')))
            enter_app.click()

            # Applications
            try:
                click_app_li = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/Medic/Applications"]')))
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
