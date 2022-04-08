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
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from data_test import number_contract, date_app, type_application, type_app


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


# @pytest.mark.skip()
@allure.feature('Test approval of the application')
class TestApproveApp:
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

    @allure.title('Test create application')
    def test_create_app(self):
        WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#applicantWrap"]')))

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#applicantApplications"]')))

        if check_title:
            assert True
        else:
            assert False, 'Impossible enter in "Заявитель" folder'

        app_wrap = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#applicantApplications"]')))
        app_wrap.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Applicant/Applications"]')))

        if check_title:
            assert True
        else:
            assert False, 'Impossible enter in "Заявки" folder'

        click_app_li = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Applicant/Applications"]')))
        click_app_li.click()

        soup_app = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup_app.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False, 'Error with "Заявки" page. Not expected page, or something else'

        enter_create_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Applicant/Applications/Create"]')))
        enter_create_app.click()

        choose_contract = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//button[@data-id="ContractId"]')))
        choose_contract.click()

        change_contract = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, f'//span[text()="{number_contract}"]')))
        change_contract.click()

        change_date = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'EndDate')))
        change_date.send_keys(date_app, Keys.ENTER)

        app_type = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//button[@data-id="ApplicationType"]')))
        app_type.click()

        time.sleep(1)

        change_app_type = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, f'//span[text()="{type_application}"]')))
        change_app_type.click()

        time.sleep(1)

        choose_object = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//label[@title="ВМЛУ"]')))
        choose_object.click()

        create_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//input[@type="submit"]')))
        create_app.click()

        soup_new_app = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page_app = soup_new_app.find('span', {'id': 'lblActionName'}).text.strip()

        approval_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'sa-submit-to-approval')))

        if approval_app:
            assert True
        else:
            assert False, f'Error with "{name_page_app}" page. Not expected page, or something else'

        with open('applications.txt', 'w') as log:
            log.writelines(f'{name_page_app.replace("Заявка на транспортные средства # ", "")}\n')

    @allure.title('Test add unit to application')
    def test_add_unit_app(self):
        edit_app_items = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'edit-application-items')))
        edit_app_items.click()

        time.sleep(1)

        add_unit = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'tb-158')))
        add_unit.click()

        return_to_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-back')))
        coordinates = return_to_app.location_once_scrolled_into_view
        DriverInitialize.driver.execute_script(f"window.scrollTo({coordinates['x']}, {coordinates['y']})")
        return_to_app.click()

        new_unit = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'vehicle-158')))

        if new_unit:
            assert True
        else:
            assert False, 'Unit don\'t add to application'

    @allure.title('Test applicant send application to approval')
    def test_send_app(self):
        approval_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'sa-submit-to-approval')))
        approval_app.click()

        confirm_send = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_send.click()

        time.sleep(1)

        confirm_send = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_send.click()

        soup_app = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup_app.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False, 'Application don\'t send to approval'

    @allure.title('Test precurator approval application')
    def test_precurator_approval_app(self):
        enter_precurator = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#precuratorWrap"]')))
        enter_precurator.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#precuratorApplications"]')))

        if check_title:
            assert True
        else:
            assert False

        enter_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#precuratorApplications"]')))
        enter_app.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/precurator/Applications"]')))

        if check_title:
            assert True
        else:
            assert False

        click_app_li = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/precurator/Applications"]')))
        click_app_li.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False

        with open('applications.txt', 'r') as file:
            for check_num in file:
                link = f'href="/precurator/Applications/VehicleDetails/{check_num.strip()}"'

        enter_to_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, f'//a[@{link}]')))
        enter_to_app.click()

        approval_all_doc = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'sa-submit-all')))
        approval_all_doc.click()

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        time.sleep(1)

        send_to_the_next_role = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.ID, 'sa-finish-approval')))
        send_to_the_next_role.click()

        time.sleep(1)

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        time.sleep(1)

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False, 'Application don\'t send to approval to the next role'

    @allure.title('Test curator approval application')
    def test_curator_approval_app(self):
        enter_curator = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#curatorWrap"]')))
        enter_curator.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#curatorApplications"]')))

        if check_title:
            assert True
        else:
            assert False

        enter_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#curatorApplications"]')))
        enter_app.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/Applications"]')))

        if check_title:
            assert True
        else:
            assert False

        click_app_li = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/Curator/Applications"]')))
        click_app_li.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False

        with open('applications.txt', 'r') as file:
            for check_num in file:
                link = f'href="/Curator/Applications/VehicleDetails/{check_num.strip()}"'

        enter_to_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, f'//a[@{link}]')))
        enter_to_app.click()

        approval_all_doc = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'sa-submit-all')))
        approval_all_doc.click()

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        time.sleep(1)

        send_to_the_next_role = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'sa-finish-approval')))
        send_to_the_next_role.click()

        time.sleep(1)

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        time.sleep(1)

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False, 'Application don\'t send to approval to the next role'

    @allure.title('Test vehicle security approval application')
    def test_veh_sec_approval_app(self):
        enter_veh_sec = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#transportsecurityWrap"]')))
        enter_veh_sec.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).\
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#transportsecurityApplications"]')))

        if check_title:
            assert True
        else:
            assert False

        enter_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="#transportsecurityApplications"]')))
        enter_app.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/TransportSecurity/Applications"]')))

        if check_title:
            assert True
        else:
            assert False

        click_app_li = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/TransportSecurity/Applications"]')))
        click_app_li.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False

        with open('applications.txt', 'r') as file:
            for check_num in file:
                link = f'href="/TransportSecurity/Applications/VehicleDetails/{check_num.strip()}"'

        enter_to_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, f'//a[@{link}]')))
        enter_to_app.click()

        approval_all_doc = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'sa-submit-all')))
        approval_all_doc.click()

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        time.sleep(1)

        send_to_the_next_role = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'sa-finish-approval')))
        send_to_the_next_role.click()

        time.sleep(1)

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        time.sleep(1)

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False, 'Application don\'t send to approval to the next role'

    @allure.title('Test corporate security approval application')
    def test_corp_sec_approval_app(self):
        enter_corp_sec = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#corpsecurityWrap"]')))
        enter_corp_sec.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#corpsecurityApplications"]')))

        if check_title:
            assert True
        else:
            assert False

        enter_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#corpsecurityApplications"]')))
        enter_app.click()

        check_title = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/CorpSecurity/Applications"]')))

        if check_title:
            assert True
        else:
            assert False

        click_app_li = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, '//a[@href="/CorpSecurity/Applications"]')))
        click_app_li.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False

        with open('applications.txt', 'r') as file:
            for check_num in file:
                link = f'href="/CorpSecurity/Applications/VehicleDetails/{check_num.strip()}"'

        enter_to_app = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.XPATH, f'//a[@{link}]')))
        enter_to_app.click()

        approval_all_doc = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'sa-submit-all')))
        approval_all_doc.click()

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        time.sleep(1)

        send_to_the_next_role = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.ID, 'sa-finish-approval')))
        send_to_the_next_role.click()

        time.sleep(1)

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        time.sleep(1)

        confirm_approval = WebDriverWait(DriverInitialize.driver, DriverInitialize.timeout). \
            until(EC.element_to_be_clickable((By.CLASS_NAME, 'swal2-confirm')))
        confirm_approval.click()

        soup = BeautifulSoup(DriverInitialize.driver.page_source, 'html.parser')
        name_page = soup.find('span', {'id': 'lblActionName'}).text.strip()

        if name_page == 'Заявки':
            assert True
        else:
            assert False, 'Application don\'t send to approval to the next role'

    @allure.title('Close and Quit')
    def test_quit(self):
        DriverInitialize.driver.close()
        DriverInitialize.driver.quit()
        shutil.rmtree(DriverInitialize.stuff_path)