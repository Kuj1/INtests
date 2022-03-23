import os
import time
import re
import allure
import shutil
import pytest

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from data_test import filter_end_date_pass, main_company, date_from_app, date_to_app


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
            assert False, 'Filter input "Генподрядчик" work incorrect'

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
                assert False, 'Filter input "Вид заявки" work incorrect with type "Сотрудники"'

        elif type_application == 'Транспорт':
            error = 0
            for check_workers in unit:
                if check_workers != 'fa-car':
                    error += 1
                    break
            if error == 0:
                assert True
            else:
                assert False, 'Filter input "Вид заявки" work incorrect with type "Транспорт"'

        elif type_application == 'ТМЦ':
            error = 0
            for check_workers in unit:
                if check_workers != 'fa-camera':
                    error += 1
                    break
            if error == 0:
                assert True
            else:
                assert False, 'Filter input "Вид заявки" work incorrect with type "ТМЦ"'

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
            assert False, 'Filter input "Дата подачи" work incorrect'

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
        assert 'Pagination work incorrect. Maybe there is only one page'
    path_to_number.click()

    prev_btn = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//a[text()="Пред."]')))
    if prev_btn:
        assert True
    else:
        assert False, 'Pagination work incorrect. Button "Пред." is missing'
    prev_btn.click()

    next_btn = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//a[text()="След."]')))
    if next_btn:
        assert True
    else:
        assert False, 'Pagination work incorrect. Button "След." is missing'
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
        filter_company = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'select2-MainCompanyId-container')))
        filter_company.click()
        change_company = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'select2-search__field')))
        change_company.send_keys(org)
        change_company.send_keys(Keys.ENTER)
        filter_enter_button = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
        filter_enter_button.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert False, 'Filter input "Организация" work incorrect'
        elif len(units) == 10:
            assert True

        DriverInitialize.driver.execute_script('resetFilter();')
        if tab:
            WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@isactual='false']"))).click()
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter name
    if name:
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
            assert False, 'Filter input "ФИО" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        if tab:
            WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@isactual='false']"))).click()
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

        # Filter position
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="WorkerPosition"]'))).click()
        worker_position = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.LINK_TEXT, position)))
        worker_position.click()
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert True
        elif error > 0:
            assert False, 'Filter input "Должность" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        if tab:
            WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@isactual='false']"))).click()
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter date birth
    if date_birth:
        filter_date_from = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'birthdayFrom')))
        filter_date_from.send_keys(date_birth)

        filter_date_to = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'birthdayTo')))
        filter_date_to.send_keys(date_birth, Keys.ENTER)

        filter_enter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup_req = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        table_req = soup_req.find('table', class_="table-striped")
        date_birthday = table_req.find('small', text=re.compile('03.02.2004')).text.strip()

        if date_birth == date_birthday:
            assert True
        else:
            assert False, 'Filter input "Дата рождения" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        if tab:
            WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@isactual='false']"))).click()
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter type of vehicle
    if type_vehicle:
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="VehicleTypeId"]'))).click()
        enter_type_vehicle = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.LINK_TEXT, type_vehicle)))
        enter_type_vehicle.click()
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert True
        elif error > 0:
            assert False, 'Filter input "Тип ТС" work incorrect'


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
        enter_number_inv = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'Number')))
        enter_number_inv.send_keys(number_inv, Keys.ENTER)
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert True
        else:
            assert False, 'Filter input "Номер приглашения" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@isactual='false']"))).click()
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter number application
    if number_app:
        enter_number_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'ApplicationId')))
        enter_number_app.send_keys(number_app, Keys.ENTER)
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert True
        else:
            assert False, 'Filter input "Номер пропуска" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@isactual='false']"))).click()
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter number pass
    if number_pass:
        enter_number_inv = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'BarCode')))
        enter_number_inv.send_keys(number_pass, Keys.ENTER)
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert True
        else:
            assert False, 'Filter input "Номер заявки" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@isactual='false']"))).click()
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter end date of pass
    if end_date:
        filter_date_from = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'dateFrom')))
        filter_date_from.send_keys(end_date)

        filter_date_to = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'dateTo')))
        filter_date_to.send_keys(filter_end_date_pass, Keys.ENTER)

        filter_enter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert True
        else:
            assert False, 'Filter input "Дата окончания" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@isactual='false']"))).click()
        DriverInitialize.driver.execute_script('openFilterBlock(this);')


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
    filter_date_from = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
        until(EC.element_to_be_clickable((By.ID, 'dateFrom')))
    filter_date_from.send_keys(birth_d)

    filter_date_to = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
        until(EC.element_to_be_clickable((By.ID, 'dateTo')))
    filter_date_to.send_keys(filter_end_date_pass, Keys.ENTER)

    filter_enter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
        until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
    filter_enter.click()

    soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
    table_req = soup.find('table', class_="table-striped")
    date_birthday = table_req.find(text=re.compile(f'{birth_d}')).text.strip()

    if birth_d == date_birthday:
        assert True
    else:
        assert False, 'Filter input "Дата рождения" work incorrect'

    DriverInitialize.driver.execute_script('resetFilter();')
    DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter type of vehicle
    if type_vehicle:
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-id="TypeId"]'))).click()
        enter_type_vehicle = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.LINK_TEXT, type_vehicle)))
        enter_type_vehicle.click()
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@value="Применить"]'))).click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert True
        elif error > 0:
            assert False, 'Filter input "Тип ТС" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter id vehicle
    if id_vehicle:
        enter_id_vehicle = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'VehicleId')))
        enter_id_vehicle.send_keys(id_vehicle)

        filter_enter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Применить"]')))
        filter_enter.click()

        soup_req = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
            assert True
        else:
            assert False, 'Filter input "Код ТС" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        DriverInitialize.driver.execute_script('openFilterBlock(this);')

    # Filter name vehicle
    if name_vehicle:
        filter_change_name = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'Name')))
        filter_change_name.send_keys(name_vehicle, Keys.ENTER)

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        cell = soup.find(string=re.compile(f'{name_vehicle}')).text.strip()

        if name_vehicle in cell:
            assert True
        else:
            assert False, 'Filter input "Марка" work incorrect'

        DriverInitialize.driver.execute_script('resetFilter();')
        DriverInitialize.driver.execute_script('openFilterBlock(this);')


def filter_for_deletion(request):
    """
    Testing filter from the list item "Заявки на удаление"
    :param request: the value to be filtered by
    :return:
    """
    open_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.ID, 'btnFilterDesktop')))
    open_filter.click()

    type_request = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//button[@data-id="AppType"]')))
    type_request.click()

    change_type_request = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
        until(EC.element_to_be_clickable((By.XPATH, './/div/input[@type="text"]')))
    change_type_request.send_keys(request, Keys.ENTER)

    filter_enter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
        (By.XPATH, '//input[@value="Применить"]')))
    filter_enter.click()

    soup_req = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
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
        if error == 0:
            assert True
        else:
            assert False, 'Filter input "Тип запроса" work incorrect'

    elif request == 'Транспортное средство на удаление':
        error = 0
        for check_workers in workers_delete:
            if check_workers != 'fa-car':
                error += 1
                break
        if error == 1:
            assert True
        else:
            assert False, 'Filter input "Тип запроса" work incorrect'


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


@pytest.mark.skip()
@allure.feature('Test for role "Куратор"')
class TestCurator:
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
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#curatorWrap"]')))

        if check_title:
            assert True
        else:
            assert False

    @allure.title('Test "Куратор" folder')
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

    @allure.title('Test "Заявки" folder')
    def test_app_folder(self):
        enter_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#curatorApplications"]')))
        enter_app.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/Applications"]')))

        if check_title:
            assert True
        else:
            assert False

    @allure.title('Test page "Заявки" from "Заявки"')
    def test_app_application_page(self):
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

    @allure.title('Test pagination on page "Заявки" from "Заявки"')
    def test_app_pagination_application_page(self):
        page_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH,
             '//a[@href="?page=2&IsActual=True"]')))
        if page_number:
            pagination_test(page_number)

    @allure.title('Test filter on page "Заявки" from "Заявки"')
    def test_app_filter_application_page(self):
        open_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'btnFilterMobile')))
        open_filter.click()

        filter_for_apps(grand_contract=main_company, type_application='Сотрудники')
        filter_for_apps(type_application='Транспорт', date_app=True)
        filter_for_apps(type_application='ТМЦ')

    @allure.title('Test "Справочники" folder')
    def test_dict_folder(self):
        dict_tab = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#curatorDictWrap"]')))
        dict_tab.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/SubCompanies"]')))

        if check_title:
            assert True
        else:
            assert False

    @allure.title('Test page "Субподрядчики" from "Справочники"')
    def test_dict_sub_comp_page(self):
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

    @allure.title('Test pagination on page "Субподрядчики" from "Справочники"')
    def test_dict_pagination_comp_page(self):
        page_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="?page=2&MainCompanyId=1&IsActual=True"]')))
        if page_number:
            pagination_test(page_number)

    @allure.title('Test "Отчеты" folder')
    def test_reports_folder(self):
        reports_tab = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#curatorReportsWrap"]')))
        reports_tab.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/ExpiredDocs"]')))

        if check_title:
            assert True
        else:
            assert False

    @allure.title('Test page "Истекающие документы" from "Отчеты"')
    def test_reports_expired_page(self):
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

    @allure.title('Test pagination on page "Истекающие документы" from "Отчеты"')
    def test_reports_pagination_expired_page(self):
        page_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="?page=2&SortingColumn=DaysLeft&SortingDirection=desc&IsActual=True"]')))
        if page_number:
            pagination_test(page_number)

    @allure.title('Test filter on page "Истекающие документы" from "Отчеты"')
    def test_reports_filter_expired_page(self):
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

    @allure.title('Close and Quit')
    def test_quit(self):
        DriverInitialize.driver.close()
        DriverInitialize.driver.quit()
        shutil.rmtree(DriverInitialize.stuff_path)
