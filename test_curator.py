import os
import time
import logging
import allure
import pytest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from data_test import main_company, date_from_app, date_to_app


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
        enter_grand_contract = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'select2-MainCompany-container')))
        enter_grand_contract.click()
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-search__field'))).\
            send_keys(grand_contract)
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, f"""//li[text()='{grand_contract}']"""))).\
            click()

        filter_enter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup_req = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        table_req = soup_req.find('table', class_="table-striped")
        rows = table_req.find_all('tr')
        cells = [row.find_all('td') for row in rows]
        name_comp = list()
        for cell in cells:
            count = 0
            for check_cell in cell:
                if count == 1:
                    res = check_cell.text.strip().split('</tr>')
                    for check_res in res:
                        name_comp.append(check_res)
                count += 1
        if main_company in name_comp:
            assert True
        else:
            assert False

        DriverInitialize.driver.execute_script('resetFilter();')
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter type app
    if type_application:
        type_request = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//button[@data-id="appType"]')))
        type_request.click()

        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, './/div/input[@type="text"]'))).send_keys(type_application, Keys.ENTER)

        filter_enter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup_req = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            if error == 0:
                assert True
            else:
                assert False

        elif type_application == 'Транспорт':
            error = 0
            for check_workers in unit:
                if check_workers != 'fa-car':
                    error += 1
                    break
            if error == 0:
                assert True
            else:
                assert False

        elif type_application == 'ТМЦ':
            error = 0
            for check_workers in unit:
                if check_workers != 'fa-camera':
                    error += 1
                    break
            if error == 0:
                assert True
            else:
                assert False

        DriverInitialize.driver.execute_script('resetFilter();')
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter date
    if date_app:
        filter_date_from = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'dateFrom')))
        filter_date_from.send_keys(date_from_app)

        filter_date_to = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'dateTo')))
        filter_date_to.send_keys(date_to_app, Keys.ENTER)

        filter_enter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        table_req = soup.find('table', class_="application-table table table-hover table-striped")
        date = table_req.find_all('tr')[1].find_all('td')[-2].text.strip().split(' ')
        if date_from_app == date[0]:
            assert True
        else:
            assert False

        DriverInitialize.driver.execute_script('resetFilter();')
        DriverInitialize.driver.execute_script('openFilterBlock(this);')


def pagination_test(path_to_number):
    """
    Pagination test
    :param path_to_number: Xpath to button-number
    :return:
    """
    if path_to_number:
        assert True
    else:
        assert False
    path_to_number.click()

    prev_btn = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//a[text()="Пред."]')))
    if prev_btn:
        assert True
    else:
        assert False
    prev_btn.click()

    next_btn = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//a[text()="След."]')))
    if next_btn:
        assert True
    else:
        assert False
    next_btn.click()


def download_doc():
    """
    Click to "Excel" button and download document
    :return:
    """
    not_actual_inv_download = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
        until(EC.element_to_be_clickable((By.ID, 'btnDownloadCsvFile')))
    not_actual_inv_download.click()
    time.sleep(1)


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


class DriverInitialize:
    # Load '.env' file
    load_dotenv()

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


class TestCurator:
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
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#curatorWrap"]')))

        if check_title:
            assert True
        else:
            assert False

    def test_curator_folder(self):
        enter_curator = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#curatorWrap"]')))
        enter_curator.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#curatorApplications"]')))

        if check_title:
            assert True
        else:
            assert False

    def test_curator_app_folder(self):
        enter_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#curatorApplications"]')))
        enter_app.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/Applications"]')))

        if check_title:
            assert True
        else:
            assert False

    def test_curator_app_page(self):
        click_app_li = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/Applications"]')))
        click_app_li.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False

        download_doc()
        for check_file in os.listdir(DriverInitialize.stuff_path):
            if check_file == 'Applications.csv':
                assert True
            else:
                assert False

        os.remove(os.path.join(DriverInitialize.stuff_path, 'Applications.csv'))

    def test_curator_pagination_app_page(self):
        page_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH,
             '//a[@href="?page=2&IsActual=True"]')))
        if page_number:
            pagination_test(page_number)

    def test_curator_filter_app_page(self):
        open_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'btnFilterMobile')))
        open_filter.click()

        filter_for_apps(grand_contract=main_company, type_application='Сотрудники')
        filter_for_apps(type_application='Транспорт', date_app=True)
        filter_for_apps(type_application='ТМЦ')

    def test_curator_dict_folder(self):
        dict_tab = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#curatorDictWrap"]')))
        dict_tab.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/SubCompanies"]')))

        if check_title:
            assert True
        else:
            assert False

    def test_curator_sub_comp_page(self):
        sub_company = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Curator/SubCompanies"]')))
        sub_company.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Субподрядчики':
            assert True
        else:
            assert False

        not_actual = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@isactual="false"]')))
        not_actual.click()

        actual = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@isactual="true"]')))
        actual.click()

    def test_curator_pagination_sub_comp_page(self):
        page_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="?page=2&MainCompanyId=1&IsActual=True"]')))
        if page_number:
            pagination_test(page_number)

    def test_curator_report_folder(self):
        reports_tab = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#curatorReportsWrap"]')))
        reports_tab.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/ExpiredDocs"]')))

        if check_title:
            assert True
        else:
            assert False

    def test_curator_expired_docs_page(self):
        reports_tab = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Curator/ExpiredDocs"]')))
        reports_tab.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Истекающие документы':
            assert True
        else:
            assert False

        download_doc()
        for check_file in os.listdir(DriverInitialize.stuff_path):
            if check_file == 'ExpiredDocs.csv':
                assert True
            else:
                assert False

        os.remove(os.path.join(DriverInitialize.stuff_path, 'ExpiredDocs.csv'))

    def test_curator_pagination_expired_docs_page(self):
        page_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="?page=2&SortingColumn=DaysLeft&SortingDirection=desc&IsActual=True"]')))
        if page_number:
            pagination_test(page_number)

    def test_curator_filter_expired_docs_page(self):
        open_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'btnFilterDesktop')))
        open_filter.click()

        # Filter type
        enter_selector = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//button[@data-id="Type"]')))
        enter_selector.click()
        change_type = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@type="text"]')))
        change_type.send_keys('Сотрудник', Keys.ENTER)

        submit_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))

        submit_filter.click()
        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
        if error == 0:
            assert True
        else:
            assert False

        reset_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'a-clear')))
        reset_filter.click()

        DriverInitialize.driver.execute_script('openFilterBlock(this);')

        # Filter name
        enter_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'Name')))
        enter_name.send_keys('Карманов Марсель Феликсович', Keys.ENTER)
        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
        if error == 0:
            assert True
        else:
            assert False

        reset_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'a-clear')))
        reset_filter.click()

        DriverInitialize.driver.execute_script('openFilterBlock(this);')

        # Filter doc
        enter_doc = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'DocName')))
        enter_doc.send_keys('Трудовой договор', Keys.ENTER)
        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
        if error == 0:
            assert True
        else:
            assert False

        reset_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'a-clear')))
        reset_filter.click()

        DriverInitialize.driver.execute_script('openFilterBlock(this);')

        # Filter date
        date_from = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'dateFrom')))
        date_from.send_keys('28.02.2022')

        time.sleep(1)

        date_to = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'dateTo')))
        date_to.send_keys('28.02.2022')
        submit_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
        submit_filter.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
        if error == 0:
            assert True
        else:
            assert False

        reset_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'a-clear')))
        reset_filter.click()

    def test_quit(self):
        DriverInitialize.driver.close()
        DriverInitialize.driver.quit()
