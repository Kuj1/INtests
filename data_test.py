import time
import random

# Worker data
first_name = [
    'Арнольд', 'Ермак', 'Леонард',
    'Роберт', 'Рудольф', 'Феликс',
    'Александр', 'Максим', 'Денис',
    'Константин', 'Владислав', 'Макар',
    'Артем', 'Иван', 'Гомер'
]

second_name = [
    'Макаров', 'Винокуров', 'Титов',
    'Гришин', 'Масленников', 'Винокуров',
    'Бочков', 'Кущин', 'Тараканов',
    'Друзь', 'Кумкватов', 'Коробов',
    'Дуров', 'Карманов', 'Кружков',
    'Тортов', 'Младшов', 'Гюгов',
    'Торцев', 'Грачев', 'Дубов',
    'Дорохов', 'Кластеров', 'Байтов',
    'Матриаршев', 'Гувер', 'Домкратов',
    'Коломойцев', 'Дурдомов', 'Подкидышевв',
    'Друзев', 'Баранов', 'Коблыкин',
    'Хомяков', 'Тостов', 'Толстых',
    'Корвинов', 'Доходеев', 'Тачков',
    'Курбанов', 'Кубов', 'Уравненьев'
]


def middle_name():
    new_middle_name = f'{random.choice(first_name)}ович'

    return new_middle_name


real_position = [
    'Сварщик', 'Водитель', 'Мессия',
    'Повар', 'Охранник', 'Сторож',
    'Моряк', 'Воздухобменник', 'Трубочист',
    'Мойщик', 'Официант', 'Рудокоп'
]

position = [
    'Тунеядец', 'Инженер по бурению', 'Археолог',
    'Взрывник', 'Автослесарь', 'Администратор'
]

doc_type_name = [
    '//a[@doctypename="Копия паспорта"]',
    '//a[@doctypename="Трудовой договор"]',
    '//a[@doctypename="Договор, на основании которого '
    'выполняются подрядчиком/субподрядчиком работы в интересах ООО «ГПН-Развитие» "]',
    '//a[@doctypename="Копия договора с ООО '
    '«СОГАЗ ПРОФМЕДИЦИНА» или гарантийное письмо об оплате услуг по тестированию."]',
    '//a[@doctypename="Медицинская книжка"]',
]


def time_prop(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    start_time = time.mktime(time.strptime(start, format))
    end_time = time.mktime(time.strptime(end, format))

    proportion_time = start_time + prop * (end_time - start_time)

    return time.strftime(format, time.localtime(proportion_time))


def random_date(start, end, prop):
    return time_prop(start, end, '%d.%m.%Y', prop)


# Vehicle data
name_vehicle = [
    'Toyota', 'BMW', 'Mercedes',
    'ВАЗ', 'Geely', 'Suzuki',
    'Волга', 'УАЗ', 'Chevrolet',
    'Hyundai', 'Mazda', 'Subaru',
    'Nissan', 'Fiat', 'SAAB',
    'Porsche', 'Renault', 'Ford',
    'Infiniti', 'KIA', 'Lexus'
]

type_vehicle = [
    'Категория D (автобусы)', 'Категория В (легковые автомобили)',
    'Жилой вагон', 'Категория Е (легковые и грузовые прицепы (полуприцепы))'
]


def numberplate():
    chars = 'АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ'
    nums = '1234567890'
    new_numberplate = f'{random.choice(chars)}{random.choice(nums)}{random.choice(nums)}{random.choice(nums)}' \
                      f'{random.choice(chars)}{random.choice(chars)}'

    return new_numberplate


def vin_vehicle():
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    length = 17
    new_vin = ''
    for i in range(length):
        new_vin += random.choice(chars)

    return new_vin


exp_year_vehicle = random_date('1.1.1970', '1.1.2003', random.random())
capacity_vehicle = random.randint(100, 300)
owners_company_number = '890501001'
owners_company_name = 'ООО "ЧОО "ИНТЕЛЛЕКТ"'
contract_number = '1000343123'
date_contract = '28.03.2022'
expired_doc = 'href="/Applicant/WorkerDocuments?workerId=835"'
delete_expired_doc = 'href="/Applicant/WorkerDocuments/Delete/1230?appid=0"'
edit_expired_doc = 'href="/Applicant/WorkerDocuments/Edit/1226?appid=0"'


# Workers filter dataset
filter_organization = 'АО "ПРЕМЬЕРСТРОЙ"'
filter_name_inv = 'New'
filter_name_pass = 'Monster'
filter_position = 'Тунеядец'
filter_number_invites_worker = '0100000336C'
filter_number_pass_worker = '2000336C'
filter_number_invites_value = '0100000001T'
filter_number_application_worker = '527'
filter_number_application_value = '35'
filter_birth = '03.02.2004'
filter_birth_for_apps = '23.03.2004'
filter_end_date_pass = '28.02.2022'
delete_unit = '/Applicant/ApplicationsForDeletion/WorkerDetails/201'

# Vehicles filter dataset
filter_datepick = '04.02.2020'
filter_number_invites_vehicle = '0100000035A'
filter_number_application_vehicle = '230'
filter_end_date_pass_v = '09.01.2022'
filter_type_vehicle = 'Категория С (грузовые автомобили)'
filter_number_application = '539'
filter_number_pass_vehicle = '1000031A'
vehicle_id = '1'
filter_type_vehicle_app = 'Категория D (автобусы)'
filter_name_vehicle_app = 'КПП-1'

# Curator
main_company = 'АО "ПРЕМЬЕРСТРОЙ"'
date_to_app = '25.02.2022'
date_to_app_v_s = '12.02.2022'
date_from_app = '24.02.2022'
date_from_app_v_s = '11.02.2022'
type_app = 'Сотрудники'
type_unit = 'Сотрудник'

# Approve app
number_contract = '№ 11111123 от 21.02.2022 [21.02.2022 — бессрочно]'
date_app = '16.04.2022'
type_application = 'Транспортные средства'
