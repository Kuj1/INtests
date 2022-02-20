import os
import random
import time
import logging

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
import pyautogui

from test_dataset import filter_name, filter_position, filter_organization, filter_birth
from test_dataset import surname, first_name, middle_name, random_date, doc_type_name


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


def upload_document():
    """
    Upload document in modal window
    :return:
    """
    doc_path = os.path.join(resource_path, '1.pdf')

    try:
        # driver.execute_script('workerInstance.uploadFileDocument(this)')
        # time.sleep(1)
        # pyautogui.write(doc_path, interval=0.1)
        # pyautogui.press('return')
        # pyautogui.press('return')
        # time.sleep(1)
        # Good practice, but still not work
        up_doc = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            (By.XPATH, '//input[@type="file"]')))
        driver.execute_script("removeAttribute('hidden');", up_doc)
        up_doc.send_keys(doc_path)
        # WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #     (By.CLASS_NAME, 'swal2-cancel'))).click()
    except BaseException as ex:
        logging.error(f'Upload document failed. {ex}')
    else:
        logging.info('Document upload successfully')

    time.sleep(1)

    try:
        fill_name = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            (By.ID, 'worker-document-modal-number')))
        fill_name.send_keys(random.randint(1111, 9999))
        fill_name.send_keys(Keys.ENTER)
    except BaseException as ex:
        logging.error(f'Input "Номер" of the document filled incorrect. {ex}')
    else:
        logging.info('Input "Номер" of the document filled correctly')

    try:
        fill_date_start = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            (By.ID, 'worker-document-modal-start-date')))
        fill_date_start.send_keys(random_date('01.02.2022', '18.02.2022', random.random()))
        fill_date_start.send_keys(Keys.ENTER)
    except BaseException as ex:
        logging.error(f'Input "Дата выдачи" of the document filled incorrect. {ex}')
    else:
        logging.info('Input "Дата выдачи" of the document filled correctly')

    time.sleep(1)

    try:
        fill_date_end = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            (By.ID, 'worker-document-modal-end-date')))
        # fill_date_end_invisible = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
        #     (By.XPATH, '//div[@style="display: none;"]')))
        if fill_date_end:
            fill_date_end.send_keys(random_date('20.02.2022', '28.02.2022', random.random()))
            fill_date_end.send_keys(Keys.ENTER)
            time.sleep(1)
            driver.execute_script('workerInstance.uploadDocument()')
    except BaseException as ex:
        logging.error(f'Input "Дата окончания" of the document filled incorrect. {ex}')
    else:
        logging.info('Input "Дата окончания" of the document filled correctly')

    time.sleep(1)
    driver.execute_script('workerInstance.uploadDocument()')


def create_unit():
    """
    Create new unit
    :return: last name, first name, middle name, birth date and position
    """
    lst_nm = random.choice(surname)
    frst_nm = random.choice(first_name)
    mdl_nm = random.choice(middle_name)

    try:
        add_unit = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Applicant/Workers/Create"]')))
        try:
            add_unit.click()
        except BaseException as ex:
            logging.error(f'Something wrong happens. Don\'t clickable button "Создать". {ex}')
        else:
            logging.info('Button "Создать" - working correctly')

        try:
            enter_lastname = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.ID, 'Worker_LastName')))
            enter_lastname.send_keys(lst_nm)
        except BaseException as ex:
            logging.error(f'Input "Фамилия" - filled incorrect. {ex}')
        else:
            logging.info('Input "Фамилия" - filled correctly')

        try:
            enter_firstname = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.ID, 'Worker_FirstName')))
            enter_firstname.send_keys(frst_nm)
        except BaseException as ex:
            logging.error(f'Input "Имя" - filled incorrect. {ex}')
        else:
            logging.info('Input "Имя" - filled correctly')

        try:
            enter_middlename = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.ID, 'Worker_MiddleName')))
            enter_middlename.send_keys(mdl_nm)
        except BaseException as ex:
            logging.error(f'Input "Отчество" - filled incorrect. {ex}')
        else:
            logging.info('Input "Отчество" - filled correctly')

        try:
            enter_birthday = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.ID, 'Worker_Birthday')))
            enter_birthday.send_keys(random_date('1.1.1970', '1.1.2003', random.random()))
        except BaseException as ex:
            logging.error(f'Input "Дата рождения" - filled incorrect. {ex}')
        else:
            logging.info('Input "Дата рождения" - filled correctly')

        try:
            enter_position = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@data-id="worker-position"]')))
            enter_position.click()
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.LINK_TEXT, 'Тунеядец'))).click()
            time.sleep(1)
        except BaseException as ex:
            logging.error(f'Input "Должность" - filled incorrect. {ex}')
        else:
            logging.info('Input "Должность" - filled correctly')

        try:
            enter_citizenship = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.ID, 'select2-worker-citizenship-container')))
            enter_citizenship.click()
            change_citizenship = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.CLASS_NAME, 'select2-search__field')))
            change_citizenship.send_keys('РФ')
            time.sleep(1)
            change_citizenship.send_keys(Keys.ENTER)
        except BaseException as ex:
            logging.error(f'Input "Гражданство" - filled incorrect. {ex}')
        else:
            logging.info('Input "Гражданство" - filled correctly')

        try:
            for check_doc in doc_type_name:
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, check_doc))).click()
                upload_document()
        except BaseException as ex:
            logging.error(f'Documents upload failed. {ex}')
        else:
            logging.info('Documents upload successfully!')

        try:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//input[@type="submit"]'))).click()
            time.sleep(10)
        except BaseException as ex:
            logging.error(f'Something wrong happens. Unit don\'t saved. {ex}')

    except BaseException as ex:
        logging.error(f'Something wrong happens. Unit don\'t create. {ex}')
        print('[ERROR]: Something wrong happens. Unit don\'t create. {ex}')
    else:
        logging.info('Creating unit has been finished!')
        logging.info(f'Unit "{lst_nm} {frst_nm} {mdl_nm}" successfully created!')
        print('[INFO]: Creating unit has been finished!')


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

        # # Invites
        # logging.info('Testing "Приглашения" - has begun...')
        # print('[INFO]: Testing "Приглашения" - has begun...')
        # try:
        #     inv_wrap = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, "//a[@href='#applicantInviteWrap']")))
        #     inv_wrap.click()
        #
        #     # Worker invites
        #     try:
        #         inv_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, "//a[@href='/Applicant/WorkerInvites']")))
        #         try:
        #             inv_workers.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Сотрудники" - working correctly')
        #
        #         try:
        #             not_actual_inv_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, "//div[@isactual='false']")))
        #             not_actual_inv_workers.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Погашенные" in list item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Погашенные" in list item "Сотрудники" - working correctly')
        #
        #         try:
        #             not_actual_inv_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             not_actual_inv_download.click()
        #             time.sleep(1)
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Сотрудники" -> tab "Погашенные" - '
        #                           f'working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Сотрудники" -> tab "Погашенные" - working correctly')
        #
        #         try:
        #             actual_inv_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, "//div[@isactual='true']")))
        #             actual_inv_workers.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Действующие" in list item "Сотрудники" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Действующие" in list item "Сотрудники" - working correctly')
        #
        #         try:
        #             actual_inv_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             actual_inv_download.click()
        #             time.sleep(1)
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Сотрудники" -> tab "Действующие" - '
        #                           f'working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Сотрудники" -> tab "Действующие" - working correctly')
        #
        #         for check_file in os.listdir(stuff_path):
        #             if check_file in 'Приглашения сотрудников.csv':
        #                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #     except BaseException as ex:
        #         logging.error(f'List item "Сотрудники" in dropdown "Приглашения" - working incorrect. {ex}')
        #     else:
        #         logging.info('List item "Сотрудники" in dropdown "Приглашения" - working correctly')
        #
        #     # Transport invites
        #     try:
        #         inv_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/VehicleInvites"]')))
        #         try:
        #             inv_vehicles.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Транспорт" - working correctly')
        #
        #         try:
        #             not_actual_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//div[@isactual="false"]')))
        #             not_actual_vehicles.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Погашенные" in list item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Погашенные" in list item "Транспорт" - working correctly')
        #
        #         try:
        #             excel_not_actual_v_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             excel_not_actual_v_download.click()
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Транспорт" -> tab "Погашенные" - '
        #                           f'working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Транспорт" -> "Погашенные" - working correctly')
        #
        #         try:
        #             actual_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//div[@isactual="true"]')))
        #             actual_vehicles.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Действующие" in list item "Транспорт" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Действующие" in list item "Транспорт" - working correctly')
        #
        #         try:
        #             excel_actual_v_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             excel_actual_v_download.click()
        #             time.sleep(1)
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "Транспорт" -> tab "Действующие" - '
        #                           f'working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "Транспорт" -> tab "Действующие" - working correctly')
        #
        #         for check_file in os.listdir(stuff_path):
        #             if check_file in 'Приглашения транспорта.csv':
        #                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #     except BaseException as ex:
        #         logging.error(f'List item "Транспорт" in dropdown "Приглашения" - working incorrect. {ex}')
        #     else:
        #         logging.info('List item "Транспорт" in dropdown "Приглашения" - working correctly')
        #
        #     # Value Invites
        #     try:
        #         inv_values = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/ValueInvites"]')))
        #         try:
        #             inv_values.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "ТМЦ" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "ТМЦ" - working correctly')
        #
        #         try:
        #             not_actual_value = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//div[@isactual="false"]')))
        #             not_actual_value.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Погашенные" in list item "ТМЦ" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Погашенные" in list item "ТМЦ" - working correctly')
        #
        #         try:
        #             excel_not_actual_vl_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             excel_not_actual_vl_download.click()
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "ТМЦ" -> tab "Погашенные" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "ТМЦ" -> "Погашенные" - working correctly')
        #
        #         try:
        #             actual_value = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//div[@isactual="true"]')))
        #             actual_value.click()
        #         except BaseException as ex:
        #             logging.error(f'Tab "Действующие" in list item "ТМЦ" - working incorrect. {ex}')
        #         else:
        #             logging.info('Tab "Действующие" in list item "ТМЦ" - working correctly')
        #
        #         try:
        #             excel_actual_vl_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'btnDownloadCsvFile')))
        #             excel_actual_vl_download.click()
        #             time.sleep(2)
        #         except BaseException as ex:
        #             logging.error(f'Button "Excel" in list item "ТМЦ" -> tab "Действующие" - working incorrect. {ex}')
        #         else:
        #             logging.info('Button "Excel" in list item "ТМЦ" -> tab "Действующие" - working correctly')
        #
        #         for check_file in os.listdir(stuff_path):
        #             if check_file in 'Приглашения ТМЦ.csv':
        #                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
        #     except BaseException as ex:
        #         logging.error(f'List item "ТМЦ" in dropdown "Приглашения" - working incorrect. {ex}')
        #     else:
        #         logging.info('List item "ТМЦ" in dropdown "Приглашения" - working correctly')
        #
        #     # Print Invites
        #     try:
        #         inv_print = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #             (By.XPATH, '//a[@href="/Applicant/PrintInvite/GetPdf"]')))
        #         try:
        #             inv_print.click()
        #         except BaseException as ex:
        #             logging.error(f'List item "Печать приглашений" - working incorrect. {ex}')
        #         else:
        #             logging.info('List item "Печать приглашений" - working correctly')
        #
        #         try:
        #             download_inv_pdf = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Скачать"]')))
        #             download_inv_pdf.click()
        #
        #             WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.ID, 'ApplicationId-error')))
        #         except BaseException as ex:
        #             logging.error(f'Verification - failed (no alert for empty input). {ex}')
        #         else:
        #             logging.info('Verification for empty required input - working correctly')
        #
        #         try:
        #             download_inv_pdf = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.XPATH, '//input[@value="Скачать"]')))
        #             download_inv_pdf.send_keys('1000000 , d s addfdf', Keys.ENTER)
        #
        #             WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
        #                 (By.CLASS_NAME, 'validation-summary-errors')))
        #         except BaseException as ex:
        #             logging.error(f'Verification - failed. See log file. {ex}')
        #         else:
        #             logging.info('Verification for random input - working correctly')
        #     except BaseException as ex:
        #         logging.error(f'List item "Печать приглашений" in dropdown "Приглашения" - working incorrect. {ex}')
        #     else:
        #         logging.info('List item "Печать приглашений" in dropdown "Приглашения" - working correctly')
        # except BaseException as ex:
        #     logging.error('Something goes wrong during testing '
        #                   '"Приглашения". May be one or more element not found or been deprecated.')
        #     print('[ERROR]: Something goes wrong during testing '
        #           '"Приглашения". May be one or more element not found or been deprecated.')
        #     logging.error(ex)
        # else:
        #     logging.info('Dropdown "Приглашения" and all of elements in it - working correctly')
        #     logging.info('Testing "Приглашения" - is finished!')
        #     print('[SUCCESS]: Testing "Приглашения" - is finished!\n')
        #
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

        # Applications
        logging.info('Testing "Заявки" - has begun...')
        print('[INFO]: Testing "Заявки" - has begun...')
        try:
            app_wrap = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="#applicantApplications"]')))
            app_wrap.click()

            # Workers
            try:
                app_workers = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="/Applicant/Workers"]')))
            #     try:
            #         app_workers.click()
            #     except BaseException as ex:
            #         logging.error(f'List item "Сотрудники" - working incorrect. {ex}')
            #     else:
            #         logging.info('List item "Сотрудники" - working correctly')
            #
            #     try:
            #         workers_download = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.ID, 'btnDownloadCsvFile')))
            #         workers_download.click()
            #     except BaseException as ex:
            #         logging.error(f'Button "Excel" in list item "Сотрудники" - working incorrect. {ex}')
            #     else:
            #         logging.info('Button "Excel" in list item "Сотрудники" - working correctly')
            #
            #     for check_file in os.listdir(stuff_path):
            #         if check_file in 'Workers.csv':
            #             logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
            #
            #     try:
            #         pager_num = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.XPATH, '//a[@href="?page=5&SortingColumn=FullName&SortingDirection=asc&IsActual=True"]')))
            #         pager_num.click()
            #     except BaseException as ex:
            #         logging.error(f'Pagination numbers on list item "Сотрудники" - working incorrect. {ex}')
            #     else:
            #         logging.info('Pagination numbers on list item "Сотрудники" - working correctly')
            #
            #     try:
            #         pager_next = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.XPATH, '//a[text()="След."]')))
            #         pager_next.click()
            #     except BaseException as ex:
            #         logging.error(f'Pagination button "След." on list item "Сотрудники" - working incorrect. {ex}')
            #     else:
            #         logging.info('Pagination button "След." on list item "Сотрудники" - working correctly')
            #
            #     try:
            #         pager_prev = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.XPATH, '//a[text()="Пред."]')))
            #         pager_prev.click()
            #     except BaseException as ex:
            #         logging.error(f'Pagination button "Пред." on list item "Сотрудники" - working incorrect. {ex}')
            #     else:
            #         logging.info('Pagination button "Пред." on list item "Сотрудники" - working correctly')
            #
            #     # Filter test
            #     open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #         (By.ID, 'btnFilterDesktop')))
            #     open_filter.click()
            #
            #     # Test filter company
            #     try:
            #         filter_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.ID, 'select2-MainCompanyId-container')))
            #         filter_company.click()
            #
            #         filter_change_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.CLASS_NAME, 'select2-search__field')))
            #         filter_change_company.send_keys(filter_organization)
            #         time.sleep(1)
            #         filter_change_company.send_keys(Keys.ENTER)
            #
            #         filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.XPATH, '//input[@value="Применить"]')))
            #         filter_enter_button.click()
            #
            #         WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            #             (By.XPATH, """//span[@title='АО "ПРЕМЬЕРСТРОЙ"']""")))
            #     except BaseException as ex:
            #         logging.error(f'Input "Организация" - working incorrect. {ex}')
            #     else:
            #         logging.info('Input "Организация" - working correctly')
            #
            #     driver.execute_script('resetFilter()')
            #     driver.execute_script('openFilterBlock(this)')
            #
            #     # Test filter name
            #     try:
            #         filter_change_name = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.ID, 'Fio')))
            #         filter_change_name.send_keys(filter_name, Keys.ENTER)
            #
            #         WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            #             (By.XPATH, '//input[@value="new"]')))
            #     except BaseException as ex:
            #         logging.error(f'Input "ФИО" - working incorrect. {ex}')
            #     else:
            #         logging.info('Input "ФИО" - working correctly')
            #
            #     driver.execute_script('resetFilter()')
            #     driver.execute_script('openFilterBlock(this)')
            #
            #     # Change filter position
            #     try:
            #         filter_positions = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.XPATH, '//button[@data-id="WorkerPosition"]')))
            #         filter_positions.click()
            #         filter_positions.send_keys(filter_position)
            #         time.sleep(5)
            #         filter_positions.send_keys(Keys.ENTER)
            #
            #         filter_enter_button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.XPATH, '//input[@value="Применить"]')))
            #         filter_enter_button.click()
            #
            #         WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            #             (By.XPATH, '//span[@title="Тунеядец"]')))
            #     except BaseException as ex:
            #         logging.error(f'Input "Должность" - working incorrect. {ex}')
            #     else:
            #         logging.info('Input "Должность" - working correctly')
            #
            #     driver.execute_script('resetFilter()')
            #     driver.execute_script('openFilterBlock(this)')
            #
            #     # Test filter antibodies (?)
            #     # Test filter birth-date
            #     try:
            #         filter_date_from = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.ID, 'dateFrom')))
            #         filter_date_from.click()
            #         filter_date_from.send_keys(filter_birth)
            #         time.sleep(1)
            #
            #         filter_date_to = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.ID, 'dateTo')))
            #         filter_date_to.click()
            #         filter_date_to.send_keys(filter_birth)
            #         time.sleep(1)
            #         filter_date_to.send_keys(Keys.ENTER)
            #
            #         filter_enter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
            #             (By.XPATH, '//input[@value="Применить"]')))
            #         filter_enter.click()
            #
            #         WebDriverWait(driver, timeout).until(EC.presence_of_element_located(
            #             (By.XPATH, '//small[text()="01.01.1961"]')))
            #     except BaseException as ex:
            #         logging.error(f'Input "Дата рождения" - working incorrect. {ex}')
            #     else:
            #         logging.info('Input "Дата рождения" - working correctly')

                # Create unit
                create_unit()

            except BaseException as ex:
                logging.error(ex)
        except BaseException as ex:
            logging.error('Something goes wrong during testing '
                          '"Заявки". May be one or more element not found or been deprecated.')
            print('[ERROR]: Something goes wrong during testing '
                  '"Заявки". May be one or more element not found or been deprecated.')
            logging.error(ex)
        else:
            logging.info('Dropdown "Заявки" and all of elements in it - working correctly')
            logging.info('Testing "Заявки" - has finished!')
            print('[SUCCESS]: Testing "Заявки" - has finished!\n')

    except BaseException as ex:
        print(f'{ex} Something goes wrong. See the log file.')

    finally:
        driver.close()
        driver.quit()


def main():
    check_data(URL)


if __name__ == '__main__':
    main()
