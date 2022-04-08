### Доступ, через env. файл
- Перед запуском скрипта нужно создатьь в корне env. файл вида:
```python
    LOGIN = your_login
    PASSWD = your_password 
```
### Охват тестов и прочее
- В пакете ```test_classes``` лежат модули, которые содержат в себе код тестов UI/UX тестирования (проверка кнопок, проверка фильтров и проверка доступности страниц). Они одноименны ролям и имеют нейминг: ```test_ui_{имя_роли}.py```;
- Так же, в пакете представлен модуль ```test_create_unit.py```, который содержит в себе код теста на создание юнитов (сотрудника и ТС). Как в случае сотрудника, так и в случае ТС - создаются юниты с рандомными параметрами (ФИО у сотрудника, ВИН номер у ТС итд.). Для удобства проверки, после окончания теста будет сгенерирован файл .txt (```workers.txt``` / ```vehicles.txt```);
- Так же, в пакете представлен модуль ```test_approve_app.py```, который содержит в себе код теста на создание, согласование и выдачу пропуска юниту (в данный момент из юнитов, реализован только ТС из-за особенности тестируемого сервиса, которые я не в силах преодолеть). ВАЖНО!!! Маршруты заданы стандартные и изменение оных приведет к ожидаемой поломке кода;
- В код интегрирован ```allure```, при помощи ```allure-pytest```;
- Команда для запуска скриптов из пакета ```test_classes```: 
  ```bash
     pytest test_classes --alluredir /Путь/к/папке/с/reports -v
  ``` 
- Во время работы скрипта будет сгенерирована папка ```reports``` в которую поместятся все отчеты по тестам;
- Для генерации отчета в allure-style: 
  ```bash
     allure serve /Путь/к/папке/reports
  ```
