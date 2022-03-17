import os
import time
import logging
import re
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

from data_test import filter_organization, filter_name_inv, filter_position, filter_datepick, \
    filter_number_invites_worker, filter_number_application_worker, \
    filter_number_invites_vehicle, filter_number_application_vehicle, filter_birth
from data_test import filter_name_pass, filter_number_pass_worker, filter_end_date_pass, filter_type_vehicle, \
    filter_number_application_vehicle_pass, filter_number_pass_vehicle, \
    vehicle_id, filter_type_vehicle_app, filter_name_vehicle_app, main_company, date_from_app, date_to_app


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
            logging.error('"Организация" filter working incorrect')
        elif len(units) == 10:
            logging.info('"Организация" filter working correct')

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
            logging.info('"ФИО" filter working correct')
        else:
            logging.error('"ФИО" filter working incorrect')

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
            logging.info('"Должность" filter working correct')
        elif error > 0:
            logging.error('"Должность" filter working incorrect')

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
            logging.info('"Дата рождения" filter working correct')
        else:
            logging.error('"Дата рождения" filter working correct')

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
            assert False

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
            assert False

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
            assert False

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
            assert False

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
        assert False

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
            assert False

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
            assert False

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
            assert False

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


class TestApplicant:
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

    def test_applicant_folder(self):
        enter_applicant = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#applicantWrap"]')))
        # enter_applicant.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#applicantApplications"]')))

        if check_title:
            assert True
        else:
            assert False

    def test_applicant_inv_folder(self):
        enter_inv = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#applicantInviteWrap"]')))
        enter_inv.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Applicant/WorkerInvites"]')))

        if check_title:
            assert True
        else:
            assert False

    def test_applicant_units_page(self):
        click_inv_li = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/Applicant/WorkerInvites']")))
        click_inv_li.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Приглашения сотрудников':
            assert True
        else:
            assert False

        not_actual_inv_workers = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, "//div[@isactual='false']")))
        not_actual_inv_workers.click()
        download_doc()

        actual_inv_workers = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, "//div[@isactual='true']")))
        actual_inv_workers.click()
        download_doc()

        for check_file in os.listdir(DriverInitialize.stuff_path):
            if check_file == 'Приглашения сотрудников.csv':
                assert True
            else:
                assert False

        os.remove(os.path.join(DriverInitialize.stuff_path, 'Приглашения сотрудников.csv'))

    def test_applicant_pagination_unit_page(self):
        not_actual_inv_workers = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, "//div[@isactual='false']")))
        not_actual_inv_workers.click()

        page_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable(
                (By.XPATH, '//a[@href="?page=2&SortingColumn=Id&SortingDirection=desc&IsActual=False"]')))
        if page_number:
            pagination_test(page_number)

    def test_applicant_filter_unit_page(self):
        open_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.ID, 'btnFilterDesktop')))
        open_filter.click()

        filter_number_docs(number_app=filter_number_application_worker,
                           count_column=4, number_inv=filter_number_invites_worker)
        filter_for_units(org=filter_organization, name=filter_name_inv,
                         position=filter_position, date_birth=filter_birth, tab=True)

    def test_applicant_vehicle_page(self):
        inv_vehicles = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Applicant/VehicleInvites"]')))
        inv_vehicles.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Приглашения транспорта':
            assert True
        else:
            assert False

        not_actual_vehicles = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//div[@isactual="false"]')))
        not_actual_vehicles.click()
        download_doc()

        actual_vehicles = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//div[@isactual="true"]')))
        actual_vehicles.click()
        download_doc()

        for check_file in os.listdir(DriverInitialize.stuff_path):
            if check_file == 'Приглашения транспорта.csv':
                assert True
            else:
                assert False

        os.remove(os.path.join(DriverInitialize.stuff_path, 'Приглашения транспорта.csv'))

    def test_applicant_pagination_vehicle_page(self):
        not_actual_vehicles = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//div[@isactual="false"]')))
        not_actual_vehicles.click()

        page_number = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="?page=2&IsActual=False"]')))
        if page_number:
            pagination_test(page_number)

    def test_applicant_filter_vehicle_page(self):
        open_filter = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'btnFilterDesktop')))
        open_filter.click()

        filter_for_units(org=filter_organization, tab=True)
        filter_number_docs(number_app=filter_number_application_vehicle,
                           count_column=4, number_inv=filter_number_invites_vehicle)

    def test_applicant_value_page(self):
        inv_values = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="/Applicant/ValueInvites"]')))
        inv_values.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Приглашения ТМЦ':
            assert True
        else:
            assert False

        # Less than one page. Testing pagination impossible
        # Filter only manual testing

        not_actual_value = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//div[@isactual="false"]')))
        not_actual_value.click()
        download_doc()

        actual_value = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//div[@isactual="true"]')))
        actual_value.click()
        download_doc()

        for check_file in os.listdir(DriverInitialize.stuff_path):
            if check_file == 'Приглашения ТМЦ.csv':
                assert True
            else:
                assert False

        os.remove(os.path.join(DriverInitialize.stuff_path, 'Приглашения ТМЦ.csv'))

    def test_quit(self):
        DriverInitialize.driver.close()
        DriverInitialize.driver.quit()
        os.rmdir(DriverInitialize.stuff_path)

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
#         download_doc()
#
#         # Pagination test
#         page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.XPATH, '//a[@href="?page=2&SortingColumn=Id&SortingDirection=desc&IsActual=False"]')))
#         if page_number:
#             pagination_test(page_number)
#
#         # Filter test
#         open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.ID, 'btnFilterDesktop')))
#         open_filter.click()
#         try:
#             filter_for_units(org=filter_organization, name=filter_name_pass,
#                              position=filter_position, date_birth=filter_birth, tab=True)
#             filter_number_docs(number_app=filter_number_application_worker, count_column=6,
#                                number_pass=filter_number_pass_worker, end_date=filter_end_date_pass)
#
#             # Filter antibodies
#             logging.warning('Input "Антитела" - manual testing only')
#
#         except BaseException as ex:
#             logging.error(f'Filter working incorrect. {ex}')
#         else:
#             logging.info('Filter working correctly')
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
#         download_doc()
#
#         for check_file in os.listdir(stuff_path):
#             if check_file in 'WorkerPasses.csv':
#                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
#     except BaseException as ex:
#         logging.error(f'List item "Сотрудники" in dropdown "Пропуска" - working incorrect. {ex}')
#     else:
#         logging.info('List item "Сотрудники" in dropdown "Пропуска" - working correctly')
#     finally:
#         os.remove(os.path.join(stuff_path, 'WorkerPasses.csv'))
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
#         download_doc()
#
#         # Pagination test
#         page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.XPATH, '//a[@href="?page=2&IsActual=False"]')))
#         if page_number:
#             pagination_test(page_number)
#
#         # Filter test
#         open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.ID, 'btnFilterDesktop')))
#         open_filter.click()
#
#         filter_for_units(type_vehicle=filter_type_vehicle)
#         filter_number_docs(number_app=filter_number_application_vehicle_pass, count_column=6,
#                            number_pass=filter_number_pass_vehicle, end_date=filter_end_date_pass)
#
#         try:
#             actual_pass_vehicles = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#                 (By.XPATH, "//div[@isactual='true']")))
#             actual_pass_vehicles.click()
#         except BaseException as ex:
#             logging.error(f'Tab "Действующие" in list item "Транспорт"- working incorrect. {ex}')
#         else:
#             logging.info('Tab "Действующие" in list item "Транспорт" - working correctly')
#
#         download_doc()
#
#         for check_file in os.listdir(stuff_path):
#             if check_file in 'VehiclePasses.csv':
#                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
#     except BaseException as ex:
#         logging.error(f'List item "Транспорт" in dropdown "Пропуска" - working incorrect. {ex}')
#     else:
#         logging.info('List item "Транспорт" in dropdown "Пропуска" - working correctly')
#     finally:
#         os.remove(os.path.join(stuff_path, 'VehiclePasses.csv'))
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
#         download_doc()
#
#         # # Pagination test
#         # page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#         #     (By.XPATH, '')))
#         # if page_number:
#         #     pagination_test(page_number)
#         # else:
#         #     logging.warning('Less than one page. Testing impossible')
#         logging.warning('Less than one page. Testing pagination impossible')
#
#         # Filter test
#         logging.warning('Filter only manual testing')
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
#         download_doc()
#
#         for check_file in os.listdir(stuff_path):
#             if check_file in 'ValuePasses.csv':
#                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
#     except BaseException as ex:
#         logging.error(f'List item "ТМЦ" in dropdown "Пропуска" - working incorrect. {ex}')
#     else:
#         logging.info('List item "ТМЦ" in dropdown "Пропуска" - working correctly')
#     finally:
#         os.remove(os.path.join(stuff_path, 'ValuePasses.csv'))
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
#
#     # Applications
#     try:
#         click_app_li = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.XPATH, '//a[@href="/Applicant/Applications"]')))
#         click_app_li.click()
#
#         download_doc()
#         for check_file in os.listdir(stuff_path):
#             if check_file in 'Applications.csv':
#                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
#
#         # Pagination test
#         page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.XPATH,
#              '//a[@href="?page=2&IsActual=True"]')))
#         if page_number:
#             pagination_test(page_number)
#
#         # Filter test
#         open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.ID, 'btnFilterMobile')))
#         open_filter.click()
#
#         logging.warning('Other filter input\'s should tested manually')
#
#         filter_for_apps(grand_contract=main_company, type_application='Сотрудники')
#         filter_for_apps(type_application='Транспорт', date_app=True)
#         filter_for_apps(type_application='ТМЦ')
#         logging.warning('"Субподрядчик" should tested manually')
#         logging.warning('"Статус" should tested manually')
#         logging.warning('"По роли" should tested manually')
#         logging.warning('"Согласующий" should tested manually')
#     except BaseException as ex:
#         logging.error(f'List item "Заявки" in dropdown "Заявки" - working incorrect. {ex}')
#     else:
#         logging.info('List item "Заявки" in dropdown "Заявки" - working correctly')
#     finally:
#         os.remove(os.path.join(stuff_path, 'Applications.csv'))
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
#         download_doc()
#
#         for check_file in os.listdir(stuff_path):
#             if check_file in 'Workers.csv':
#                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
#
#         # Pagination test
#         page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.XPATH, '//a[@href="?page=3&SortingColumn=FullName&SortingDirection=asc&IsActual=True"]')))
#         if page_number:
#             pagination_test(page_number)
#
#         # Filter test
#         open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.ID, 'btnFilterDesktop')))
#         open_filter.click()
#
#         filter_for_units(org=filter_organization, name=filter_name_pass,
#                          position=filter_position, link=True)
#         filter_for_units_app(birth_d=filter_birth)
#     except BaseException as ex:
#         logging.error(f'List item "Сотрудники" in dropdown "Заявки" - working incorrect. {ex}')
#     else:
#         logging.info('List item "Сотрудники" in dropdown "Заявки" - working correctly')
#     finally:
#         os.remove(os.path.join(stuff_path, 'Workers.csv'))
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
#         download_doc()
#
#         for check_file in os.listdir(stuff_path):
#             if check_file in 'Vehicles.csv':
#                 logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
#
#         # Pagination test
#         page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.XPATH, '//a[@href="?page=2&SortingColumn=Id&SortingDirection=asc&IsActual=True"]')))
#         if page_number:
#             pagination_test(page_number)
#
#         # Filter test
#         open_filter = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#             (By.ID, 'btnFilterDesktop')))
#         open_filter.click()
#         filter_for_units(org=filter_organization, link=True)
#         filter_for_units_app(birth_d=filter_datepick,
#                              type_vehicle=filter_type_vehicle_app,
#                              id_vehicle=vehicle_id, name_vehicle=filter_name_vehicle_app)
#     except BaseException as ex:
#         logging.error(f'List item "Транспорт" in dropdown "Заявки" - working incorrect. {ex}')
#     else:
#         logging.info('List item "Транспорт" in dropdown "Заявки" - working correctly')
#     finally:
#         os.remove(os.path.join(stuff_path, 'Vehicles.csv'))
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
#     except BaseException as ex:
#         logging.error(f'List item "На удаление" in dropdown "Заявки" - working incorrect. {ex}')
#     else:
#         logging.info('List item "На удаление" in dropdown "Заявки" - working correctly')
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
#             os.remove(os.path.join(stuff_path, 'Applications.csv'))
#         except BaseException as ex:
#             logging.error(f'Button "Выгрузка ТC" in list item "Заявки" -> '
#                           f'tab "Дубли данных" - working incorrect. {ex}')
#         else:
#             logging.info('Button "Выгрузка ТC" in list item "Заявки" -> '
#                          'tab "Дубли данных" - working correctly')
#     except BaseException as ex:
#         logging.error(f'List item "Дубли данных" in dropdown "Заявки" - working incorrect. {ex}')
#     else:
#         logging.info('List item "Дубли данных" in dropdown "Заявки" - working correctly')
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
#         # Pagination test
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
#         logging.error(f'List item "Должности" in dropdown "Заявки" - working incorrect. {ex}')
#     else:
#         logging.info('List item "Должности" in dropdown "Заявки" - working correctly')
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
#     # Pagination test
#     page_number = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#         (By.XPATH, '//a[@href="?page=2&MainCompanyId=1&IsActual=True"]')))
#     if page_number:
#         pagination_test(page_number)
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
#     download_doc()
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
#     download_doc()
#
#     for check_file in os.listdir(stuff_path):
#         if check_file in 'Субподрядчики.csv':
#             logging.warning(f'Must be updated button "Excel" or type of file: "{check_file}"')
#
#     logging.warning('"Создать Субподрядчика" should testing manually only')
#     # ?/
#     # try:
#     #     create_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#     #         (By.XPATH, '//a[@href="/Applicant/SubCompanies/Create"]')))
#     #     create_sub_company.click()
#     # except BaseException as ex:
#     #     logging.error(f'Button "Создать" working incorrect. {ex}')
#     # else:
#     #     logging.info('Button "Создать" working correctly')
#     # try:
#     #     enter_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#     #         (By.ID, 'party-input')))
#     #     enter_sub_company.send_keys(owners_company_name)
#     #     time.sleep(3)
#     #     enter_sub_company.send_keys(Keys.ENTER)
#
#     # WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#     #     (By.XPATH, """//span[text()='ООО "ЧОО "ИНТЕЛЛЕКТ"']"""))).click()
#
#     # except BaseException as ex:
#     #     logging.error(f'Input "Организация или ИП" working incorrect. {ex}')
#     # else:
#     #     logging.info('Input "Организация или ИП" working correctly')
#     # ?/
#
#     # try:
#     #     submit_create = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#     #         (By.XPATH, '//input[@type="submit"]')))
#     #     submit_create.click()
#     #     time.sleep(1)
#     #     error_valid = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#     #         (By.XPATH, '//span[@data-valmsg-for="INN"]')))
#     #     if error_valid:
#     #         back_sub_company = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(
#     #             (By.XPATH, '//a[@href="/Applicant/SubCompanies"]')))
#     #         back_sub_company.click()
#     # except BaseException as ex:
#     #     logging.error(f'Sub-company don\'t created. {ex}')
#     # else:
#     #     logging.info('Sub-company created successfully')
# except BaseException as ex:
#     logging.error('Something goes wrong during testing '
#                   '"Справочники". May be one or more element not found or been deprecated.')
#     print('[ERROR]: Something goes wrong during testing '
#           '"Справочники". May be one or more element not found or been deprecated.')
#     logging.error(ex)
# else:
#     logging.info('Testing "Справочники" - has finished!')
#     print('[SUCCESS]: Testing "Справочники" - has finished!\n')
# finally:
#     os.remove(os.path.join(stuff_path, 'Субподрядчики.csv'))
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
#             (By.XPATH, '//a[@href="/Applicant/WorkerDocuments/Delete/1254?appid=1"]')))
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
# finally:
#     os.remove(os.path.join(stuff_path, 'ExpiredDocs.csv'))
#
#
