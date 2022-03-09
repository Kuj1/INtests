import os
# import random
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

from test_dataset import main_company, type_app

from applicant import download_doc, pagination_test, filter_for_units, filter_number_docs, filter_for_units_app, \
    filter_for_deletion, input_elem


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


def filter_for_curator(grand_contract=None, date_app=None, type_application=None):
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

    # Filter date


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
        print('\tTest-Bot was logged in, like "Куратор"')

        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'swal2-confirm'))).click()

        # Enter to curator's folder
        try:
            enter_curator = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#curatorWrap"]')))
            enter_curator.click()
        except BaseException as ex:
            logging.error(f'Curator dropdown working incorrect. {ex}')
        else:
            logging.info('Curator dropdown working correct')

        # Applications
        logging.info('Testing "Заявки" - has begun...')
        print('[INFO]: Testing "Заявки" - has begun...')
        try:
            enter_app = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#curatorApplications"]')))
            enter_app.click()

            # Applications (list item)
            try:
                click_app_li = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/Curator/Applications"]')))
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

                filter_for_curator(grand_contract=main_company)

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
            dict_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#curatorDictWrap"]')))
            dict_tab.click()

            try:
                sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/Curator/SubCompanies"]')))
                sub_company.click()
            except BaseException as ex:
                logging.error(f'List item "Субподрядчики" working incorrect. {ex}')
            else:
                logging.info('List item "Субподрядчики" working correctly')

            # Pagination test
            page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="?page=2&MainCompanyId=1&IsActual=True"]')))
            if page_number:
                pagination_test(page_number)

            try:
                not_actual = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//div[@isactual="false"]')))
                not_actual.click()
            except BaseException as ex:
                logging.error(f'Tab "Не действующие" in list item "Субподрядчики"- working incorrect. {ex}')
            else:
                logging.info('Tab "Не действующие" in list item "Субподрядчики"- working correctly')

            try:
                actual = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//div[@isactual="true"]')))
                actual.click()
            except BaseException as ex:
                logging.error(f'Tab "Действующие" in list item "Субподрядчики"- working incorrect. {ex}')
            else:
                logging.info('Tab "Действующие" in list item "Субподрядчики"- working correctly')
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
                (By.XPATH, '//a[@href="#curatorReportsWrap"]')))
            reports_tab.click()

            # Expired docs
            try:
                reports_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/Curator/ExpiredDocs"]')))
                reports_tab.click()
            except BaseException as ex:
                logging.error(f'List item "Истекающие документы" working incorrect. {ex}')
            else:
                logging.info('List item "Истекающие документы" working correctly')

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            try:
                page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH,
                     '//a[@href="?page=2&SortingColumn=DaysLeft&SortingDirection=desc&IsActual=True"]')))
                page_number.click()
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

            try:
                download_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.ID, 'btnDownloadCsvFile')))
                download_sub_company.click()
            except BaseException as ex:
                logging.error(f'Button "Excel" in list item "Истекающие документы" - working incorrect. {ex}')
            else:
                logging.info('Button "Excel" in list item "Истекающие документы" - working correctly')

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
