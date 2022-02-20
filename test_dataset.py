# import datetime
# import random
import time


first_name = [
    'Арнольд', 'Евсей', 'Ермак',
    'Леонардо', 'Нобель', 'Марсель',
    'Роберт', 'Рафаэль', 'Рудольф',
    'Феликс', 'Андрей', 'Александр',
    'Максим', 'Григорий', 'Денис',
    'Павел', 'Константин', 'Владислав'
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

middle_name = [
    'Арнольдович', 'Евсеивич', 'Ермакович',
    'Леонардович', 'Нобельевич', 'Марсельевич',
    'Робертович', 'Рафаэльевич', 'Рудольфович',
    'Феликсович', 'Андреевич', 'Александрович',
    'Максимович', 'Григориевич', 'Денисович',
    'Павлович', 'Константинович', 'Владиславович'
]

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

# Workers filter dataset
filter_organization = 'АО "ПРЕМЬЕРСТРОЙ"'
filter_name = 'new'
filter_position = 'Тунеядец'
filter_birth = '01.01.1961'


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
