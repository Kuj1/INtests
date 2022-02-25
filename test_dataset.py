import time
import random

# Worker data
first_name = [
    'Арнольд', 'Ермак', 'Леонард',
    'Роберт', 'Рудольф', 'Феликс',
    'Александр', 'Максим', 'Денис',
    'Константин', 'Владислав'
]

surname = [
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
    'Корвинов', 'Доходев', 'Тачков',
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
    'ВАЗ', 'Geely', 'Hummer',
    'Волга', 'УАЗ', 'Chevrolet'
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
owners_company_vehicle = '7804016807'
owners_company_name = 'ОАО "АБЗ-1"'

# Workers filter dataset
filter_organization = 'АО "ПРЕМЬЕРСТРОЙ"'
filter_name = 'new'
filter_position = 'Тунеядец'
filter_birth = '01.01.1961'

# Vehicles filter dataset
filter_datepick = '03.03.2020'
