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

from test_dataset import filter_organization, filter_name, filter_birth, filter_position, filter_datepick, \
    owners_company_vehicle


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


def filter_for_deletion(request):
    """
    Testing filter from the list item "Заявки на удаление"
    :param request: the value to be filtered by
    :return:
    """
    open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.ID, 'btnFilterDesktop')))
    open_filter.click()

    type_request = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//button[@data-id="AppType"]')))
    type_request.click()

    change_type_request = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.XPATH, './/div/input[@type="text"]')))
    change_type_request.send_keys(request, Keys.ENTER)

    filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//input[@value="Применить"]')))
    filter_enter.click()

    soup_req = BeautifulSoup(driver.page_source, 'html.parser')
    table_req = soup_req.find('table', class_="table table-hover")
    info_delete = [i['class'] for i in table_req.find_all('i', class_='fa')]
    info_delete_smallest = [j for j in info_delete if j[1] != 'fa-lock']
    workers_delete = list()
    for check_class in info_delete_smallest:
        for check_right_icon in check_class:
            if check_right_icon != 'fa':
                workers_delete.append(check_right_icon)

    if request == 'Сотрудник на удаление':
        error = 0
        for check_workers in workers_delete:
            if check_workers != 'fa-users':
                error += 1
                break
        if error >= 1:
            logging.error('Method "Сотрудник на удаление" of filter "Тип запроса" working incorrect')
        else:
            logging.info('Method "Сотрудник на удаление" of filter "Тип запроса" working correctly')

    elif request == 'Транспортное средство на удаление':
        error = 0
        for check_workers in workers_delete:
            if check_workers != 'fa-car':
                error += 1
                break
        if error >= 1:
            logging.error('Method "Транспортное средство на удаление" of filter "Тип запроса" working incorrect')
        else:
            logging.info('Method "Транспортное средство на удаление" of filter "Тип запроса" working correctly')


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
        print('\tTest-Bot was logged in, like "Заявитель"')

        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, 'swal2-confirm'))).click()

        # Invites
        logging.info('Testing "Приглашения" - has begun...')
        print('[INFO]: Testing "Приглашения" - has begun...')
        try:
            inv_wrap = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, "//a[@href='#applicantInviteWrap']")))
            inv_wrap.click()

            # Worker invites
            try:
                inv_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[@href='/Applicant/WorkerInvites']")))
                try:
                    inv_workers.click()
                except BaseException as ex:
                    logging.error(f'List item "Сотрудники" - working incorrect. {ex}')
                else:
                    logging.info('List item "Сотрудники" - working correctly')

                try:
                    not_actual_inv_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[@isactual='false']")))
                    not_actual_inv_workers.click()
                except BaseException as ex:
                    logging.error(f'Tab "Погашенные" in list item "Сотрудники" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Погашенные" in list item "Сотрудники" - working correctly')

                # Pagination test
                try:
                    page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                            (By.XPATH, '//a[@href="?page=2&SortingColumn=Id&SortingDirection=desc&IsActual=False"]')))
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

                # # Filter test
                # open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                #     (By.ID, 'btnFilterDesktop')))
                # open_filter.click()
                #
                # try:
                #     filter_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                #         (By.ID, 'select2-MainCompanyId-container')))
                #     filter_company.click()
                #
                #     filter_change_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                #         (By.CLASS_NAME, 'select2-search__field')))
                #     filter_change_company.send_keys(filter_organization)
                #     time.sleep(1)
                #     filter_change_company.send_keys(Keys.ENTER)
                #
                #     filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                #         (By.XPATH, '//input[@value="Применить"]')))
                #     filter_enter_button.click()
                #
                #     soup = BeautifulSoup(driver.page_source, 'html.parser')
                #     table_req = soup.find('table', class_="table table-striped")
                #     rows = table_req.find_all('tr')
                #     cells = [row.find_all('span', {"title": re.compile(r".*")}) for row in rows]
                #     units = list()
                #     for cell in cells:
                #         for check_cell in cell:
                #             res = check_cell.text.strip().split('</td>')
                #             for check_res in res:
                #                 units.append(check_res)
                #     print(units)
                #
                #     error = 0
                #     for check_unit in units:
                #         if check_unit != 'Сотрудник':
                #             error += 1
                #     if error >= 1:
                #         logging.error('"Тип" filter working incorrect')
                #     else:
                #         logging.info('"Тип" filter working correct')
                # except BaseException as ex:
                #     logging.error(f' {ex}')
                # else:
                #     logging.info('')
                #
                # driver.execute_script('resetFilter()')
                # driver.execute_script('openFilterBlock(this)')

                # # Test filter name
                # try:
                #     filter_change_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                #         (By.ID, 'Fio')))
                #     filter_change_name.send_keys(filter_name, Keys.ENTER)
                #
                #     WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
                #         (By.XPATH, '//input[@value="new"]')))
                # except BaseException as ex:
                #     logging.error(f'Input "ФИО" - working incorrect. {ex}')
                # else:
                #     logging.info('Input "ФИО" - working correctly')
                #
                # driver.execute_script('resetFilter()')
                # driver.execute_script('openFilterBlock(this)')
                #
                # # Change filter position
                # try:
                #     filter_positions = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                #         (By.XPATH, '//button[@data-id="WorkerPosition"]')))
                #     filter_positions.click()
                #     filter_positions.send_keys(filter_position)
                #     time.sleep(5)
                #     filter_positions.send_keys(Keys.ENTER)
                #
                #     filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                #         (By.XPATH, '//input[@value="Применить"]')))
                #     filter_enter_button.click()
                #
                #     WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
                #         (By.XPATH, '//span[@title="Тунеядец"]')))
                # except BaseException as ex:
                #     logging.error(f'Input "Должность" - working incorrect. {ex}')
                # else:
                #     logging.info('Input "Должность" - working correctly')

                try:
                    not_actual_inv_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.ID, 'btnDownloadCsvFile')))
                    not_actual_inv_download.click()
                    time.sleep(1)
                except BaseException as ex:
                    logging.error(f'Button "Excel" in list item "Сотрудники" -> tab "Погашенные" - '
                                  f'working incorrect. {ex}')
                else:
                    logging.info('Button "Excel" in list item "Сотрудники" -> tab "Погашенные" - working correctly')

                try:
                    actual_inv_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[@isactual='true']")))
                    actual_inv_workers.click()
                except BaseException as ex:
                    logging.error(f'Tab "Действующие" in list item "Сотрудники" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Действующие" in list item "Сотрудники" - working correctly')

                try:
                    actual_inv_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.ID, 'btnDownloadCsvFile')))
                    actual_inv_download.click()
                    time.sleep(1)
                except BaseException as ex:
                    logging.error(f'Button "Excel" in list item "Сотрудники" -> tab "Действующие" - '
                                  f'working incorrect. {ex}')
                else:
                    logging.info('Button "Excel" in list item "Сотрудники" -> tab "Действующие" - working correctly')

                for check_file in os.listdir(stuff_path):
                    if check_file in 'Приглашения сотрудников.csv':
                        logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
            except BaseException as ex:
                logging.error(f'List item "Сотрудники" in dropdown "Приглашения" - working incorrect. {ex}')
            else:
                logging.info('List item "Сотрудники" in dropdown "Приглашения" - working correctly')

            # Transport invites
            try:
                inv_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/Applicant/VehicleInvites"]')))
                try:
                    inv_vehicles.click()
                except BaseException as ex:
                    logging.error(f'List item "Транспорт" - working incorrect. {ex}')
                else:
                    logging.info('List item "Транспорт" - working correctly')

                try:
                    not_actual_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, '//div[@isactual="false"]')))
                    not_actual_vehicles.click()
                except BaseException as ex:
                    logging.error(f'Tab "Погашенные" in list item "Транспорт" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Погашенные" in list item "Транспорт" - working correctly')

                try:
                    excel_not_actual_v_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.ID, 'btnDownloadCsvFile')))
                    excel_not_actual_v_download.click()
                except BaseException as ex:
                    logging.error(f'Button "Excel" in list item "Транспорт" -> tab "Погашенные" - '
                                  f'working incorrect. {ex}')
                else:
                    logging.info('Button "Excel" in list item "Транспорт" -> "Погашенные" - working correctly')

                try:
                    actual_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, '//div[@isactual="true"]')))
                    actual_vehicles.click()
                except BaseException as ex:
                    logging.error(f'Tab "Действующие" in list item "Транспорт" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Действующие" in list item "Транспорт" - working correctly')

                try:
                    excel_actual_v_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.ID, 'btnDownloadCsvFile')))
                    excel_actual_v_download.click()
                    time.sleep(1)
                except BaseException as ex:
                    logging.error(f'Button "Excel" in list item "Транспорт" -> tab "Действующие" - '
                                  f'working incorrect. {ex}')
                else:
                    logging.info('Button "Excel" in list item "Транспорт" -> tab "Действующие" - working correctly')

                for check_file in os.listdir(stuff_path):
                    if check_file in 'Приглашения транспорта.csv':
                        logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
            except BaseException as ex:
                logging.error(f'List item "Транспорт" in dropdown "Приглашения" - working incorrect. {ex}')
            else:
                logging.info('List item "Транспорт" in dropdown "Приглашения" - working correctly')

            # Value Invites
            try:
                inv_values = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/Applicant/ValueInvites"]')))
                try:
                    inv_values.click()
                except BaseException as ex:
                    logging.error(f'List item "ТМЦ" - working incorrect. {ex}')
                else:
                    logging.info('List item "ТМЦ" - working correctly')

                try:
                    not_actual_value = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, '//div[@isactual="false"]')))
                    not_actual_value.click()
                except BaseException as ex:
                    logging.error(f'Tab "Погашенные" in list item "ТМЦ" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Погашенные" in list item "ТМЦ" - working correctly')

                try:
                    excel_not_actual_vl_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.ID, 'btnDownloadCsvFile')))
                    excel_not_actual_vl_download.click()
                except BaseException as ex:
                    logging.error(f'Button "Excel" in list item "ТМЦ" -> tab "Погашенные" - working incorrect. {ex}')
                else:
                    logging.info('Button "Excel" in list item "ТМЦ" -> "Погашенные" - working correctly')

                try:
                    actual_value = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.XPATH, '//div[@isactual="true"]')))
                    actual_value.click()
                except BaseException as ex:
                    logging.error(f'Tab "Действующие" in list item "ТМЦ" - working incorrect. {ex}')
                else:
                    logging.info('Tab "Действующие" in list item "ТМЦ" - working correctly')

                try:
                    excel_actual_vl_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                        (By.ID, 'btnDownloadCsvFile')))
                    excel_actual_vl_download.click()
                    time.sleep(2)
                except BaseException as ex:
                    logging.error(f'Button "Excel" in list item "ТМЦ" -> tab "Действующие" - working incorrect. {ex}')
                else:
                    logging.info('Button "Excel" in list item "ТМЦ" -> tab "Действующие" - working correctly')

                for check_file in os.listdir(stuff_path):
                    if check_file in 'Приглашения ТМЦ.csv':
                        logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
            except BaseException as ex:
                logging.error(f'List item "ТМЦ" in dropdown "Приглашения" - working incorrect. {ex}')
            else:
                logging.info('List item "ТМЦ" in dropdown "Приглашения" - working correctly')

            # Print Invites
            try:
                inv_print = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/Applicant/PrintInvite/GetPdf"]')))
                try:
                    inv_print.click()
                except BaseException as ex:
                    logging.error(f'List item "Печать приглашений" - working incorrect. {ex}')
                else:
                    logging.info('List item "Печать приглашений" - working correctly')

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
                logging.error(f'List item "Печать приглашений" in dropdown "Приглашения" - working incorrect. {ex}')
            else:
                logging.info('List item "Печать приглашений" in dropdown "Приглашения" - working correctly')
        except BaseException as ex:
            logging.error('Something goes wrong during testing '
                          '"Приглашения". May be one or more element not found or been deprecated.')
            print('[ERROR]: Something goes wrong during testing '
                  '"Приглашения". May be one or more element not found or been deprecated.')
            logging.error(ex)
        else:
            logging.info('Dropdown "Приглашения" and all of elements in it - working correctly')
            logging.info('Testing "Приглашения" - is finished!')
            print('[SUCCESS]: Testing "Приглашения" - is finished!\n')

        # # Passes
        # logging.info('Testing "Пропуска" - has begun...')
        # print('[INFO]: Testing "Пропуска" - has begun...')
        # try:
        #     passes_wrap = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, "//a[@href='#applicantPassesWrap']")))
        #     passes_wrap.click()
        #
        #     # Workers passes
        #     try:
        #         pass_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, "//a[@href='/Applicant/WorkerPasses']")))
        #         try:
        #             pass_workers.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Сотрудники" - working correctly')
        #
        #         try:
        #             not_actual_pass_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, "//div[@isactual='false']")))
        #             not_actual_pass_workers.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Не действующие" in list item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Не действующие" in list item "Сотрудники" - working correctly')
        #
        #         try:
        #             not_actual_pass_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             not_actual_pass_download.click()
        #             time.sleep(2)
        #         except BaseException as ex:
        #             logging.error('Button "Excel" in list item "Сотрудники" -> '
        #                           f'tab "Не действующие" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Сотрудники" -> '
        #                          'tab "Не действующие" - working correctly')
        #
        #         try:
        #             actual_pass_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, "//div[@isactual='true']")))
        #             actual_pass_workers.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Действующие" in list item "Сотрудники"- working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Действующие" in list item "Сотрудники" - working correctly')
        #
        #         try:
        #             actual_pass_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             actual_pass_download.click()
        #             time.sleep(2)
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Сотрудники" -> '
        #                           f'tab "Действующие" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Сотрудники" -> '
        #                          'tab "Действующие" - working correctly')
        #
        #         for check_file in os.listdir(stuff_path):
        #             if check_file in 'WorkerPasses.csv':
        #                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #     except BaseException as ex:
        #         logging.error(f'List item "Сотрудники" in dropdown "Пропуска" - working incorrect. {ex}')
        #     else:
        #         logging.info('List item "Сотрудники" in dropdown "Пропуска" - working correctly')
        #
        #     # Vehicles passes
        #     try:
        #         pass_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, "//a[@href='/Applicant/VehiclePasses']")))
        #         try:
        #             pass_vehicles.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Транспорт" - working correctly')
        #
        #         try:
        #             not_actual_pass_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, "//div[@isactual='false']")))
        #             not_actual_pass_vehicles.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Не действующие" in list item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Не действующие" in list item "Транспорт" - working correctly')
        #
        #         try:
        #             not_actual_pass_v_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             not_actual_pass_v_download.click()
        #             time.sleep(1)
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Транспорт" -> '
        #                           f'tab "Не действующие" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Транспорт" -> '
        #                          'tab "Не действующие" - working correctly')
        #         try:
        #             actual_pass_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, "//div[@isactual='true']")))
        #             actual_pass_vehicles.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Действующие" in list item "Транспорт"- working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Действующие" in list item "Транспорт" - working correctly')
        #
        #         try:
        #             actual_pass_v_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             actual_pass_v_download.click()
        #             time.sleep(1)
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Транспорт" -> '
        #                           f'tab "Действующие" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Транспорт" -> tab "Действующие" - working correctly')
        #
        #         for check_file in os.listdir(stuff_path):
        #             if check_file in 'VehiclePasses.csv':
        #                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #     except BaseException as ex:
        #         logging.error(f'List item "Транспорт" in dropdown "Пропуска" - working incorrect. {ex}')
        #     else:
        #         logging.info('List item "Транспорт" in dropdown "Пропуска" - working correctly')
        #
        #     # Value passes
        #     try:
        #         pass_values = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/ValuePasses"]')))
        #         try:
        #             pass_values.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "ТМЦ" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "ТМЦ" - working correctly')
        #
        #         try:
        #             not_actual_pass_value = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//div[@isactual="false"]')))
        #             not_actual_pass_value.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Не действующие" in list item "ТМЦ" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Не действующие" in list item "ТМЦ" - working correctly')
        #
        #         try:
        #             not_actual_vl_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             not_actual_vl_download.click()
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "ТМЦ" -> '
        #                           f'tab "Не действующие" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "ТМЦ" -> "Не действующие" - working correctly')
        #
        #         try:
        #             actual_pass_value = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//div[@isactual="true"]')))
        #             actual_pass_value.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Действующие" in list item "ТМЦ" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Действующие" in list item "ТМЦ" - working correctly')
        #
        #         try:
        #             actual_vl_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             actual_vl_download.click()
        #             time.sleep(2)
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "ТМЦ" -> tab "Действующие" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "ТМЦ" -> tab "Действующие" - working correctly')
        #
        #         for check_file in os.listdir(stuff_path):
        #             if check_file in 'ValuePasses.csv':
        #                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #     except BaseException as ex:
        #         logging.error(f'List item "ТМЦ" in dropdown "Пропуска" - working incorrect. {ex}')
        #     else:
        #         logging.info('List item "ТМЦ" in dropdown "Пропуска" - working correctly')
        # except BaseException as ex:
        #     logging.error('Something goes wrong during testing '
        #                   '"Пропуска". May be one or more element not found or been deprecated.')
        #     print('[ERROR]: Something goes wrong during testing '
        #           '"Пропуска". May be one or more element not found or been deprecated.')
        #     logging.error(ex)
        # else:
        #     logging.info('Dropdown "Пропуска" and all of elements in it - working correctly')
        #     logging.info('Testing "Пропуска" - is finished!')
        #     print('[SUCCESS]: Testing "Пропуска" - is finished!\n')
        #
        # # Applications
        # logging.info('Testing "Заявки" - has begun...')
        # print('[INFO]: Testing "Заявки" - has begun...')
        # try:
        #     app_wrap = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #         (By.XPATH, '//a[@href="#applicantApplications"]')))
        #     app_wrap.click()
        #     # time.sleep(1)
        #     # app_wrap.click()
        #
        #     # Workers
        #     try:
        #         app_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/Workers"]')))
        #         try:
        #             app_workers.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Сотрудники" - working correctly')
        #
        #         try:
        #             workers_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             workers_download.click()
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Сотрудники" - working correctly')
        #
        #         for check_file in os.listdir(stuff_path):
        #             if check_file in 'Workers.csv':
        #                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #
        #         try:
        #             pager_num = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[@href="?page=5&SortingColumn=FullName&SortingDirection=asc&IsActual=True"]')))
        #             pager_num.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination numbers on list item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('Pagination numbers on list item "Сотрудники" - working correctly')
        #
        #         try:
        #             pager_next = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[text()="След."]')))
        #             pager_next.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination button "След." on list item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('Pagination button "След." on list item "Сотрудники" - working correctly')
        #
        #         try:
        #             pager_prev = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[text()="Пред."]')))
        #             pager_prev.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination button "Пред." on list item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('Pagination button "Пред." on list item "Сотрудники" - working correctly')
        #
        #         # Filter test
        #         open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'btnFilterDesktop')))
        #         open_filter.click()
        #
        #         # Test filter company
        #         try:
        #             filter_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'select2-MainCompanyId-container')))
        #             filter_company.click()
        #
        #             filter_change_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.CLASS_NAME, 'select2-search__field')))
        #             filter_change_company.send_keys(filter_organization)
        #             time.sleep(1)
        #             filter_change_company.send_keys(Keys.ENTER)
        #
        #             filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Применить"]')))
        #             filter_enter_button.click()
        #
        #             WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #                 (By.XPATH, """//span[@title='АО "ПРЕМЬЕРСТРОЙ"']""")))
        #         except BaseException as ex:
        #             logging.error(f'Input "Организация" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "Организация" - working correctly')
        #
        #         driver.execute_script('resetFilter()')
        #         driver.execute_script('openFilterBlock(this)')
        #
        #         # Test filter name
        #         try:
        #             filter_change_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'Fio')))
        #             filter_change_name.send_keys(filter_name, Keys.ENTER)
        #
        #             WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #                 (By.XPATH, '//input[@value="new"]')))
        #         except BaseException as ex:
        #             logging.error(f'Input "ФИО" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "ФИО" - working correctly')
        #
        #         driver.execute_script('resetFilter()')
        #         driver.execute_script('openFilterBlock(this)')
        #
        #         # Change filter position
        #         try:
        #             filter_positions = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//button[@data-id="WorkerPosition"]')))
        #             filter_positions.click()
        #             filter_positions.send_keys(filter_position)
        #             time.sleep(5)
        #             filter_positions.send_keys(Keys.ENTER)
        #
        #             filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Применить"]')))
        #             filter_enter_button.click()
        #
        #             WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #                 (By.XPATH, '//span[@title="Тунеядец"]')))
        #         except BaseException as ex:
        #             logging.error(f'Input "Должность" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "Должность" - working correctly')
        #
        #         driver.execute_script('resetFilter()')
        #         driver.execute_script('openFilterBlock(this)')
        #
        #         # Test filter antibodies (?)
        #         # Test filter birth-date
        #         try:
        #             filter_date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'dateFrom')))
        #             filter_date_from.click()
        #             filter_date_from.send_keys(filter_birth)
        #             time.sleep(1)
        #
        #             filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'dateTo')))
        #             filter_date_to.click()
        #             filter_date_to.send_keys(filter_birth)
        #             time.sleep(1)
        #             filter_date_to.send_keys(Keys.ENTER)
        #
        #             filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Применить"]')))
        #             filter_enter.click()
        #
        #             WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #                 (By.XPATH, '//small[text()="01.01.1961"]')))
        #         except BaseException as ex:
        #             logging.error(f'Input "Дата рождения" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "Дата рождения" - working correctly')
        #     except BaseException as ex:
        #         logging.error(ex)
        #
        #     # Vehicles
        #     try:
        #         app_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/Vehicles"]')))
        #         try:
        #             app_vehicles.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Транспорт" - working correctly')
        #
        #         try:
        #             vehicles_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             vehicles_download.click()
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Транспорт" - working correctly')
        #
        #             for check_file in os.listdir(stuff_path):
        #                 if check_file in 'Vehicles.csv':
        #                     logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #
        #         try:
        #             pager_num = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[@href="?page=2&SortingColumn=Id&SortingDirection=asc&IsActual=True"]')))
        #             pager_num.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination by numbers on list item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('Pagination by numbers on list item "Транспорт" - working correctly')
        #
        #         try:
        #             pager_next = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[text()="След."]')))
        #             pager_next.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination by button "След." on list item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('Pagination by button "След." on list item "Сотрудники" - working correctly')
        #
        #         try:
        #             pager_prev = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[text()="Пред."]')))
        #             pager_prev.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination by button "Пред." on list item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('Pagination by button "Пред." on list item "Транспорт" - working correctly')
        #
        #         # Filter test
        #         open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'btnFilterDesktop')))
        #         open_filter.click()
        #
        #         # Test filter company
        #         try:
        #             filter_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'select2-MainCompanyId-container')))
        #             filter_company.click()
        #
        #             filter_change_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.CLASS_NAME, 'select2-search__field')))
        #             filter_change_company.send_keys(filter_organization)
        #             time.sleep(1)
        #             filter_change_company.send_keys(Keys.ENTER)
        #
        #             filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Применить"]')))
        #             filter_enter_button.click()
        #
        #             WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #                 (By.XPATH, """//span[@title='АО "ПРЕМЬЕРСТРОЙ"']""")))
        #         except BaseException as ex:
        #             logging.error(f'Input "Организация" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "Организация" - working correctly')
        #
        #         driver.execute_script('resetFilter()')
        #         driver.execute_script('openFilterBlock(this)')
        #
        #         # Test filter type
        #         try:
        #             filter_type = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//button[@data-id="TypeId"]')))
        #             filter_type.click()
        #
        #             filter_change_type = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//span[text()="Категория С (грузовые автомобили)"]')))
        #             filter_change_type.click()
        #
        #             filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Применить"]')))
        #             filter_enter_button.click()
        #
        #             WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                             (By.XPATH, '//span[@title="Категория С (грузовые автомобили)"]')))
        #         except BaseException as ex:
        #             logging.error(f'Input "Тип ТС" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "Тип ТС" - working correctly')
        #
        #         driver.execute_script('resetFilter()')
        #         driver.execute_script('openFilterBlock(this)')
        #
        #         # Test filter id
        #         try:
        #             filter_id = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'VehicleId')))
        #             filter_id.send_keys('79', Keys.ENTER)
        #
        #             WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #                 (By.XPATH, '//td[contains(text(),"79")]')))
        #         except BaseException as ex:
        #             logging.error(f'Input "Код ТС" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "Код ТС" - working correctly')
        #
        #         driver.execute_script('resetFilter()')
        #         driver.execute_script('openFilterBlock(this)')
        #
        #         # Test filter name
        #         try:
        #             filter_name_v = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'Name')))
        #             filter_name_v.send_keys('VOLVO', Keys.ENTER)
        #
        #             WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #                 (By.XPATH, '//a[contains(text(),"VOLVO")]')))
        #         except BaseException as ex:
        #             logging.error(f'Input "Марка" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "Марка" - working correctly')
        #
        #         driver.execute_script('resetFilter()')
        #         driver.execute_script('openFilterBlock(this)')
        #
        #         # Test filter date exp
        #         try:
        #             filter_date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'dateFrom')))
        #             filter_date_from.click()
        #             filter_date_from.send_keys(filter_datepick)
        #             time.sleep(1)
        #
        #             filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'dateTo')))
        #             filter_date_to.click()
        #             filter_date_to.send_keys(filter_datepick)
        #             time.sleep(1)
        #             filter_date_to.send_keys(Keys.ENTER)
        #
        #             filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Применить"]')))
        #             filter_enter.click()
        #
        #             WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #                 (By.XPATH, '//tr[contains(.,"03.03.2020")]')))
        #         except BaseException as ex:
        #             logging.error(f'Input "Дата выпуска" - working incorrect. {ex}')
        #         else:
        #             logging.info('Input "Дата выпуска" - working correctly')
        #     except BaseException as ex:
        #         logging.error(ex)
        #
        #     # For deletion
        #     try:
        #         for_delete = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/ApplicationsForDeletion"]')))
        #         try:
        #             for_delete.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "На удаление" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "На удаление" - working correctly')
        #         first_request = 'Транспортное средство на удаление'
        #         second_request = 'Сотрудник на удаление'
        #
        #         filter_for_deletion(first_request)
        #         driver.execute_script('resetFilter()')
        #         time.sleep(1)
        #
        #         filter_for_deletion(second_request)
        #         driver.execute_script('resetFilter()')
        #         time.sleep(1)
        #
        #         driver.execute_script('openFilterBlock(this)')
        #         try:
        #             filter_date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'dateFrom')))
        #             filter_date_from.send_keys('09.08.2021')
        #
        #             filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'dateTo')))
        #             filter_date_to.send_keys('09.08.2021', Keys.ENTER)
        #
        #             filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Применить"]')))
        #             filter_enter.click()
        #
        #             soup_req = BeautifulSoup(driver.page_source, 'html.parser')
        #             table_req = soup_req.find('table', class_="table table-hover")
        #             rows = table_req.find_all('tr')
        #             cells = [row.find_all('td') for row in rows]
        #             date_create = list()
        #             for cell in cells:
        #                 count = 0
        #                 for check_cell in cell:
        #                     count += 1
        #                     if count == 4:
        #                         res = check_cell.text.strip().split(' ')[:1]
        #                         for check_res in res:
        #                             date_create.append(check_res)
        #                         count = 0
        #             error = 0
        #             for check_date in date_create:
        #                 if check_date != '09.08.2021':
        #                     error += 1
        #             if error >= 1:
        #                 logging.error('"Дата" filter working incorrect')
        #             else:
        #                 logging.info('"Дата" filter working correct')
        #
        #         except BaseException as ex:
        #             logging.error(f'Input "Дата" from filter "Заявки на удаление" - working incorrect. {ex}')
        #         else:
        #             logging.info(f'Input "Дата" from filter "Заявки на удаление" - working correct')
        #
        #         detailed_view = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/ApplicationsForDeletion/WorkerDetails/201"]')))
        #         try:
        #             detailed_view.click()
        #         except BaseException as ex:
        #             logging.error(f'Detailed view of the application for deletion is working incorrect. {ex}')
        #         else:
        #             logging.info('Detailed view of the application for deletion is working correct')
        #
        #     except BaseException as ex:
        #         logging.error(ex)
        #
        #     # Duplicate unit
        #     try:
        #         duplicate_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/ApplicationsForDropDuplicate"]')))
        #         try:
        #             duplicate_tab.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Дубли данных" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Дубли данных" - working correctly')
        #
        #         try:
        #             choose_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[@href="/Applicant/ApplicationsForDropDuplicate/ViewDetails/1"]')))
        #             choose_company.click()
        #         except BaseException as ex:
        #             logging.error(f'Extended view of duplicate data for chosen company working incorrect. {ex}')
        #         else:
        #             logging.info(f'Extended view of duplicate data for chosen company working correctly')
        #
        #         try:
        #             driver.execute_script('javascript:submitWorkersCsvFileForm();')
        #             for check_file in os.listdir(stuff_path):
        #                 if check_file in 'Applications.csv':
        #                     logging.warning(
        #                         f'Must be updated button "Выгрузка сотрудников" or type of file: "{check_file}"')
        #         except BaseException as ex:
        #             logging.error(f'Button "Выгрузка сотрудников" in list item "Заявки" -> '
        #                           f'tab "Дубли данных" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Выгрузка сотрудников" in list item "Заявки" -> '
        #                          'tab "Дубли данных" - working correctly')
        #
        #         try:
        #             driver.execute_script('javascript:submitDownloadVehicleCsvFileForm();')
        #             for check_file in os.listdir(stuff_path):
        #                 if check_file in 'Applications.csv':
        #                     logging.warning(f'Must be updated button "Выгрузка ТC" or type of file: "{check_file}"')
        #         except BaseException as ex:
        #             logging.error(f'Button "Выгрузка ТC" in list item "Заявки" -> '
        #                           f'tab "Дубли данных" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Выгрузка ТC" in list item "Заявки" -> '
        #                          'tab "Дубли данных" - working correctly')
        #     except BaseException as ex:
        #         logging.error(ex)
        #
        #     # Worker positions
        #     try:
        #         worker_position_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/ApplicationWorkerPositions"]')))
        #         try:
        #             worker_position_tab.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Должности" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Должности" - working correct')
        #
        #         try:
        #             create_position = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[@href="/Applicant/ApplicationWorkerPositions/Create"]')))
        #             create_position.click()
        #         except BaseException as ex:
        #             logging.error(f'Button "Создать" from list item "Должности" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Создать" from list item "Должности" - working correct')
        #
        #         try:
        #             choose_position = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'position-values-button')))
        #             choose_position.click()
        #         except BaseException as ex:
        #             logging.error(f'Button "Выбрать должность" from list item "Должности" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Выбрать должность" from list item "Должности" - working correct')
        #
        #         try:
        #             page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[text()="5"]')))
        #             page_number.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination number work incorrect. {ex}')
        #         else:
        #             logging.info('Pagination number work correctly')
        #
        #         time.sleep(1)
        #
        #         try:
        #             prev_page = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[text()="Пред."]')))
        #             prev_page.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination word "Пред." working incorrect. {ex}')
        #         else:
        #             logging.info(f'Pagination word "Пред." working correct')
        #
        #         time.sleep(1)
        #
        #         try:
        #             prev_page = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[text()="След."]')))
        #             prev_page.click()
        #         except BaseException as ex:
        #             logging.error(f'Pagination word "След." working incorrect. {ex}')
        #         else:
        #             logging.info(f'Pagination word "След." working correct')
        #
        #         time.sleep(1)
        #
        #         WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[text()="1"]'))).click()
        #
        #         try:
        #             try_position = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//label[text()="Автоклавщик"]')))
        #             try_position.click()
        #
        #             submit_position = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'position-values-check')))
        #             submit_position.click()
        #         except BaseException as ex:
        #             logging.error(f'Position don\'t add. Something wrong, may be with position\'s list. {ex}')
        #         else:
        #             logging.info('Position add successful')
        #
        #         try:
        #             add_comment = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'Comment')))
        #             add_comment.send_keys('Hello, there!')
        #         except BaseException as ex:
        #             logging.error(f'Comment don\'t added. {ex}')
        #         else:
        #             logging.info('Comment added successful')
        #
        #         try:
        #             add_position = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Создать"]')))
        #             add_position.click()
        #         except BaseException as ex:
        #             logging.error(f'Position don\'t created. {ex}')
        #         else:
        #             logging.info('Position created successful')
        #     except BaseException as ex:
        #         logging.error(ex)
        # except BaseException as ex:
        #     logging.error('Something goes wrong during testing '
        #                   '"Заявки". May be one or more element not found or been deprecated.')
        #     print('[ERROR]: Something goes wrong during testing '
        #           '"Заявки". May be one or more element not found or been deprecated.')
        #     logging.error(ex)
        # else:
        #     logging.info('Testing "Заявки" - has finished!')
        #     print('[SUCCESS]: Testing "Заявки" - has finished!\n')
        #
        # # Dict
        # logging.info('Testing "Справочники" - has begun...')
        # print('[INFO]: Testing "Справочники" - has begun...')
        # try:
        #     dict_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #         (By.XPATH, '//a[@href="#applicantDictWrap"]')))
        #     dict_tab.click()
        #
        #     try:
        #         sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/SubCompanies"]')))
        #         sub_company.click()
        #     except BaseException as ex:
        #         logging.error(f'List item "Субподрядчики" working incorrect. {ex}')
        #     else:
        #         logging.info('List item "Субподрядчики" working correctly')
        #
        #     try:
        #         page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="?page=2&MainCompanyId=1&IsActual=True"]')))
        #         page_number.click()
        #     except BaseException as ex:
        #         logging.error(f'Pagination\'s number working incorrect.{ex}')
        #     else:
        #         logging.info('Pagination\'s number working correctly')
        #
        #     try:
        #         prev_btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[text()="Пред."]')))
        #         prev_btn.click()
        #     except BaseException as ex:
        #         logging.error(f'Pagination\'s button "Пред." working incorrect.{ex}')
        #     else:
        #         logging.info('Pagination\'s button "Пред." working correctly')
        #
        #     try:
        #         prev_btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[text()="След."]')))
        #         prev_btn.click()
        #     except BaseException as ex:
        #         logging.error(f'Pagination\'s button "След." working incorrect.{ex}')
        #     else:
        #         logging.info('Pagination\'s button "След." working correctly')
        #
        #     try:
        #         not_actual = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//div[@isactual="false"]')))
        #         not_actual.click()
        #     except BaseException as ex:
        #         logging.error(f'Tab "Не действующие" in list item "Субподрядчики"- working incorrect. {ex}')
        #     else:
        #         logging.info('Tab "Не действующие" in list item "Субподрядчики"- working correctly')
        #
        #     try:
        #         download_sub_company = WebDriverWait(driver, timeout).until(EC. element_to_be_clickable(
        #             (By.ID, 'btnDownloadCsvFile')))
        #         download_sub_company.click()
        #     except BaseException as ex:
        #         logging.error(f'Button "Excel" in list item "Субподрядчики" - working incorrect. {ex}')
        #     else:
        #         logging.info('Button "Excel" in list item "Субподрядчики" - working correctly')
        #
        #     for check_file in os.listdir(stuff_path):
        #         if check_file in 'Субподрядчики.csv':
        #             logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #
        #     try:
        #         actual = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//div[@isactual="true"]')))
        #         actual.click()
        #     except BaseException as ex:
        #         logging.error(f'Tab "Действующие" in list item "Субподрядчики"- working incorrect. {ex}')
        #     else:
        #         logging.info('Tab "Действующие" in list item "Субподрядчики"- working correctly')
        #
        #     try:
        #         download_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'btnDownloadCsvFile')))
        #         download_sub_company.click()
        #     except BaseException as ex:
        #         logging.error(f'Button "Excel" in list item "Субподрядчики" - working incorrect. {ex}')
        #     else:
        #         logging.info('Button "Excel" in list item "Субподрядчики" - working correctly')
        #
        #     for check_file in os.listdir(stuff_path):
        #         if check_file in 'Субподрядчики.csv':
        #             logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #
        #     try:
        #         create_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/SubCompanies/Create"]')))
        #         create_sub_company.click()
        #     except BaseException as ex:
        #         logging.error(f'Button "Создать" working incorrect. {ex}')
        #     else:
        #         logging.info('Button "Создать" working correctly')
        #
        #     try:
        #         enter_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'party-input')))
        #         enter_sub_company.send_keys(owners_company_vehicle)
        #         time.sleep(1)
        #         change_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, """//span[text()='ОАО "АБЗ-1"']""")))
        #         time.sleep(1)
        #         change_sub_company.click()
        #     except BaseException as ex:
        #         logging.error(f'Input "Организация или ИП" working incorrect. {ex}')
        #     else:
        #         logging.info('Input "Организация или ИП" working correctly')
        #
        #     try:
        #         submit_create = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//input[@type="submit"]')))
        #         submit_create.click()
        #         time.sleep(1)
        #         error_valid = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//span[@data-valmsg-for="INN"]')))
        #         if error_valid:
        #             back_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[@href="/Applicant/SubCompanies"]')))
        #             back_sub_company.click()
        #     except BaseException as ex:
        #         logging.error(f'Sub-company don\'t created. {ex}')
        #     else:
        #         logging.info('Sub-company created successfully')
        # except BaseException as ex:
        #     logging.error('Something goes wrong during testing '
        #                   '"Справочники". May be one or more element not found or been deprecated.')
        #     print('[ERROR]: Something goes wrong during testing '
        #           '"Справочники". May be one or more element not found or been deprecated.')
        #     logging.error(ex)
        # else:
        #     logging.info('Testing "Справочники" - has finished!')
        #     print('[SUCCESS]: Testing "Справочники" - has finished!\n')
        #
        # # Reports
        # logging.info('Testing "Отчёты" - has begun...')
        # print('[INFO]: Testing "Отчёты" - has begun...')
        # try:
        #     reports_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #         (By.XPATH, '//a[@href="#applicantReportsWrap"]')))
        #     reports_tab.click()
        #
        #     # Expired docs
        #     try:
        #         reports_tab = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/ExpiredDocs"]')))
        #         reports_tab.click()
        #     except BaseException as ex:
        #         logging.error(f'List item "Истекающие документы" working incorrect. {ex}')
        #     else:
        #         logging.info('List item "Истекающие документы" working correctly')
        #
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #
        #     try:
        #         page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//a[@href="?page=2&SortingColumn=DaysLeft&SortingDirection=desc&IsActual=True"]')))
        #         page_number.click()
        #     except BaseException as ex:
        #         logging.error(f'Pagination\'s number working incorrect.{ex}')
        #     else:
        #         logging.info('Pagination\'s number working correctly')
        #
        #     try:
        #         prev_btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[text()="Пред."]')))
        #         prev_btn.click()
        #     except BaseException as ex:
        #         logging.error(f'Pagination\'s button "Пред." working incorrect.{ex}')
        #     else:
        #         logging.info('Pagination\'s button "Пред." working correctly')
        #
        #     try:
        #         prev_btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[text()="След."]')))
        #         prev_btn.click()
        #     except BaseException as ex:
        #         logging.error(f'Pagination\'s button "След." working incorrect.{ex}')
        #     else:
        #         logging.info('Pagination\'s button "След." working correctly')
        #
        #     try:
        #         download_sub_company = WebDriverWait(driver, timeout).until(EC. element_to_be_clickable(
        #             (By.ID, 'btnDownloadCsvFile')))
        #         download_sub_company.click()
        #     except BaseException as ex:
        #         logging.error(f'Button "Excel" in list item "Истекающие документы" - working incorrect. {ex}')
        #     else:
        #         logging.info('Button "Excel" in list item "Истекающие документы" - working correctly')
        #
        #     for check_file in os.listdir(stuff_path):
        #         if check_file in 'ExpiredDocs.csv':
        #             logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #
        #     # Filter test
        #     open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #         (By.ID, 'btnFilterDesktop')))
        #     open_filter.click()
        #
        #     try:
        #         # Filter type
        #         enter_selector = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//button[@data-id="Type"]')))
        #         enter_selector.click()
        #         change_type = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//input[@type="text"]')))
        #         change_type.send_keys('Сотрудник', Keys.ENTER)
        #
        #         submit_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//input[@value="Применить"]')))
        #         submit_filter.click()
        #         soup = BeautifulSoup(driver.page_source, 'html.parser')
        #         table_req = soup.find('table', class_="table table-hover table-striped")
        #         rows = table_req.find_all('tr')
        #         cells = [row.find_all('td') for row in rows]
        #         units = list()
        #         for cell in cells:
        #             count = 0
        #             for check_cell in cell:
        #                 count += 1
        #                 if count == 5:
        #                     res = check_cell.text.strip().split(' ')
        #                     for check_res in res:
        #                         units.append(check_res)
        #                     count = 0
        #         error = 0
        #         for check_unit in units:
        #             if check_unit != 'Сотрудник':
        #                 error += 1
        #         if error >= 1:
        #             logging.error('"Тип" filter working incorrect')
        #         else:
        #             logging.info('"Тип" filter working correct')
        #
        #         reset_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.CLASS_NAME, 'a-clear')))
        #         reset_filter.click()
        #
        #         driver.execute_script('openFilterBlock(this);')
        #
        #         # Filter name
        #         enter_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'Name')))
        #         enter_name.send_keys('Карманов Марсель Феликсович', Keys.ENTER)
        #         soup = BeautifulSoup(driver.page_source, 'html.parser')
        #         table_req = soup.find('table', class_="table table-hover table-striped")
        #         rows = table_req.find_all('tr')
        #         cells = [row.find_all('td') for row in rows]
        #         units = list()
        #         for cell in cells:
        #             count = 0
        #             for check_cell in cell:
        #                 count += 1
        #                 if count == 4:
        #                     res = check_cell.text.strip().split('</td>')
        #                     for check_res in res:
        #                         units.append(check_res)
        #                     count = 0
        #         clear_units = [j for j in units if j != 'Не действителен']
        #         error = 0
        #         for check_unit in clear_units:
        #             if 'Карманов Марсель Феликсович' not in check_unit:
        #                 error += 1
        #         if error >= 1:
        #             logging.error('"Наименование" filter working incorrect')
        #         else:
        #             logging.info('"Наименование" filter working correct')
        #
        #         reset_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.CLASS_NAME, 'a-clear')))
        #         reset_filter.click()
        #
        #         driver.execute_script('openFilterBlock(this);')
        #
        #         # Filter doc
        #         enter_doc = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'DocName')))
        #         enter_doc.send_keys('Трудовой договор', Keys.ENTER)
        #         soup = BeautifulSoup(driver.page_source, 'html.parser')
        #         table_req = soup.find('table', class_="table table-hover table-striped")
        #         rows = table_req.find_all('tr')
        #         cells = [row.find_all('td') for row in rows]
        #         units = list()
        #         for cell in cells:
        #             count = 0
        #             for check_cell in cell:
        #                 count += 1
        #                 if count == 6:
        #                     res = check_cell.text.strip().split('</td>')
        #                     for check_res in res:
        #                         units.append(check_res)
        #                     count = 0
        #         error = 0
        #         for check_unit in units:
        #             if 'Трудовой договор' not in check_unit:
        #                 error += 1
        #         if error >= 1:
        #             logging.error('"Документ" filter working incorrect')
        #         else:
        #             logging.info('"Документ" filter working correct')
        #
        #         reset_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.CLASS_NAME, 'a-clear')))
        #         reset_filter.click()
        #
        #         driver.execute_script('openFilterBlock(this);')
        #
        #         # Filter date
        #         date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'dateFrom')))
        #         date_from.send_keys('28.02.2022')
        #
        #         time.sleep(1)
        #
        #         date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'dateTo')))
        #         date_to.send_keys('28.02.2022')
        #         submit_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//input[@value="Применить"]')))
        #         submit_filter.click()
        #
        #         soup = BeautifulSoup(driver.page_source, 'html.parser')
        #         table_req = soup.find('table', class_="table table-hover table-striped")
        #         rows = table_req.find_all('tr')
        #         cells = [row.find_all('td') for row in rows]
        #         units = list()
        #         for cell in cells:
        #             count = 0
        #             for check_cell in cell:
        #                 count += 1
        #                 if count == 7:
        #                     res = check_cell.text.strip().split('</td>')
        #                     for check_res in res:
        #                         units.append(check_res)
        #                     count = 0
        #         error = 0
        #         for check_unit in units:
        #             if '28.02.2022' not in check_unit:
        #                 error += 1
        #         if error >= 1:
        #             logging.error('"Дата окончания" filter working incorrect')
        #         else:
        #             logging.info('"Дата окончания" filter working correct')
        #
        #         reset_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.CLASS_NAME, 'a-clear')))
        #         reset_filter.click()
        #     except BaseException as ex:
        #         logging.error(f'Filter working incorrect. {ex}')
        #     else:
        #         logging.info('Filter working correctly')
        #
        #     try:
        #         link_doc = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/WorkerDocuments?workerId=887"]')))
        #         link_doc.click()
        #         time.sleep(5)
        #     except BaseException as ex:
        #         logging.error(f'Link to document working incorrect. {ex}')
        #     else:
        #         logging.info('Link to document working correctly')
        #
        #     try:
        #         archive = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="#notActualDocs"]')))
        #         archive.click()
        #     except BaseException as ex:
        #         logging.error(f'Tab "Архив" working incorrect. {ex}')
        #     else:
        #         logging.info('Tab "Архив" working correctly')
        #
        #     try:
        #         delete_archive_doc = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/WorkerDocuments/Delete/1254?appid=0"]')))
        #         delete_archive_doc.click()
        #
        #         confirm_delete = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//input[@value="Удалить"]')))
        #         confirm_delete.click()
        #     except BaseException as ex:
        #         logging.error(f'Delete archive document working incorrect. '
        #                       f'Not found document, or document has been delete earlier {ex}')
        #     else:
        #         logging.info('Delete archive document working correctly')
        #
        #     try:
        #         actual_doc = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="#actualDocs"]')))
        #         actual_doc.click()
        #     except BaseException as ex:
        #         logging.error(f'Tab "Актуальные документы" working incorrect. {ex}')
        #     else:
        #         logging.info('Tab "Актуальные документы" working correctly')
        #
        #     try:
        #         edit_doc = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/WorkerDocuments/Edit/1258?appid=0"]')))
        #         edit_doc.click()
        #
        #         edit_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.ID, 'Document_Number')))
        #         edit_number.send_keys('123456')
        #
        #         submit_btn = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//input[@value="Сохранить"]')))
        #         submit_btn.click()
        #     except BaseException as ex:
        #         logging.error(f'Edit actual document working incorrect. '
        #                       f'Not found document, or document has been delete. {ex}')
        #     else:
        #         logging.info('Edit actual document working correctly')
        #
        #     try:
        #         delete_actual_doc = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/WorkerDocuments/Delete/1258?appid=0"]')))
        #         delete_actual_doc.click()
        #
        #         confirm_delete = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//input[@value="Удалить"]')))
        #         confirm_delete.click()
        #     except BaseException as ex:
        #         logging.error(f'Delete actual document working incorrect. '
        #                       f'Not found document, or document has been delete. {ex}')
        #     else:
        #         logging.info('Delete actual document working correctly')
        # except BaseException as ex:
        #     logging.error('Something goes wrong during testing '
        #                   '"Отчёты". May be one or more element not found or been deprecated.')
        #     print('[ERROR]: Something goes wrong during testing '
        #           '"Отчёты". May be one or more element not found or been deprecated.')
        #     logging.error(ex)
        # else:
        #     logging.info('Testing "Отчёты" - has finished!')
        #     print('[SUCCESS]: Testing "Отчёты" - has finished!\n')

    except BaseException as ex:
        print(f'{ex} Something goes wrong. See the log file.')

    finally:
        driver.close()
        driver.quit()


def main():
    check_data(URL)


if __name__ == '__main__':
    main()
