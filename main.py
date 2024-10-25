import requests
import telebot
import pandas
import datetime as dt
import time
# дополнительно два файла: calendar_plans.csv и users.csv
# users.csv - chat_id,saved_business_plans
# calendar_plans.csv - index(unnamed),chat_id,task,datetime
# инициализация бота
bot = telebot.TeleBot("<token>")

# Основное меню с кнопками
main_markup = telebot.util.quick_markup({
    'Обучение основам бизнеса': {'callback_data': '0'},
    'Генерация бизнес-планов': {'callback_data': '1'},
    'Планирование задач': {'callback_data': '2'},
    'Управление ресурсами': {'callback_data': '3'},
    'Успешные бизнес-кейсы': {'callback_data': '4'},
    'Часто задаваемые вопросы': {'callback_data': '5'},
    'Мини-викторина': {'callback_data': '6'},
    'Личный кабинет': {'callback_data': '7'}
})

# Меню для выбора ответов в мини-викторине
quiz_markup = telebot.util.quick_markup({
    'A': {'callback_data': 'qa:a'},
    'B': {'callback_data': 'qa:b'},
    'C': {'callback_data': 'qa:c'},
    'D': {'callback_data': 'qa:d'}
})

# Вопросы для мини-викторины
quiz_questions = {
    'qa1:c': '1. Что является первым шагом при запуске бизнеса?\n \
        A) Написание бизнес-плана\n \
        B) Выбор юридической формы\n \
        C) Выбор идеи для бизнеса\n \
        D) Нанимание сотрудников',
    'qa2:c': '2. Какой из следующих документов обычно НЕ требуется для регистрации бизнеса?\n \
        A) Устав компании\n \
        B) Договор аренды\n \
        C) Бизнес-план\n \
        D) Заявление о регистрации',
    'qa3:a': '3. Какой из следующих методов является эффективным для определения целевой аудитории?\n \
        A) Опросы и интервью\n \
        B) Случайный выбор людей на улице\n \
        C) Слушание мнений друзей\n \
        D) Игнорирование рынка',
    'qa4:c': '4. Какой из следующих показателей является ключевым для оценки финансового состояния бизнеса?\n \
        A) Уровень удовлетворенности сотрудников\n \
        B) Количество подписчиков в социальных сетях\n \
        C) Прибыль и убытки\n \
        D) Количество проведенных встреч',
    'qa5:c': '5. Какой из следующих методов является хорошей стратегией для продвижения бизнеса?\n \
        A) Игнорирование отзывов клиентов\n \
        B) Использование только платной рекламы\n \
        C) Создание качественного контента и SEO\n \
        D) Увеличение цен на все товары'
}

# Путь к изображениям успешных бизнес-кейсов
cases_paths = ['Bill.jpg', 'Elon.jpg', 'Jeff.jpg',
               'Steve.jpg', 'E:\\VSCODE\\Telegram-bot\\sources\\']
cases_index = 0
cases_list = list()

# Подсказки для GPT
prompts = ['', 'Расскажи, как мне распределить указанный мною капитал.',
           'Предложи поэтапный план реализации этой идеии.']

# Переменные для сообщений
img_message, txt_message = 0, 0

# Часто задаваемые вопросы
frequently_asked_questions = "Часто задаваемые вопросы\n\n \
    1.Как выбрать идею для бизнеса?\n\t\tОпределите свои интересы и навыки, исследуйте рынок на предмет потребностей и конкуренции. Идея должна быть уникальной и востребованной.\n\n \
    2.Как зарегистрировать бизнес?\n\t\tВыберите юридическую форму (ИП, ООО и т.д.), подготовьте необходимые документы, подайте заявление в налоговую службу и получите свидетельство о регистрации.\n\n \
    3.Как составить бизнес-план?\n\t\tБизнес-план должен включать описание бизнеса, анализ рынка, стратегию маркетинга, финансовый план и прогнозы доходов и расходов.\n\n \
    4.Как найти финансирование для бизнеса?\n\t\tРассмотрите различные источники: собственные сбережения, кредиты, инвестиции от бизнес-ангелов, краудфандинг или государственные гранты.\n\n \
    5.Как определить целевую аудиторию?\n\t\tИсследуйте рынок, проводите опросы и анализируйте данные о потребителях. Определите демографические, географические и психографические характеристики вашей аудитории.\n\n \
    6.Как продвигать свой бизнес?\n\t\tИспользуйте различные каналы: социальные сети, контент-маркетинг, SEO, рекламу (онлайн и офлайн), участие в выставках и мероприятиях.\n\n \
    7.Как управлять финансами бизнеса?\n\t\tВедите учет доходов и расходов, используйте бухгалтерские программы, анализируйте финансовые отчеты и планируйте бюджет.\n\n \
    8.Как нанимать сотрудников?\n\t\tОпределите потребности бизнеса, составьте описание вакансий, проводите собеседования и выбирайте кандидатов, соответствующих вашим требованиям.\n\n \
    9.Как справляться с конкуренцией?\n\t\tАнализируйте конкурентов, выявляйте их слабые стороны, улучшайте свои предложения и создавайте уникальное торговое предложение (УТП).\n\n \
    10.Как оценить успех бизнеса?\n\t\tИспользуйте ключевые показатели эффективности (KPI): прибыль, рост выручки, уровень удовлетворенности клиентов, количество новых клиентов и т.д.\n\n"

# Обработчик команд /start и /help


@bot.message_handler(commands=['start', 'help'])
def welcome_message(message):
    msg = tasks_reminder(message.chat.id)  # Напоминание о задачах
    bot.send_message(
        msg.chat.id, "Привет! Я бот, который поможет Вам распланировать задачи и оптимизировать распределение ресурсов, ответит на часто задаваемые вопросы по бизнесу, обучит основам бизнеса, предложит бизнес-план, предоставит примеры успешных бизнес-кейсов, а также проведет мини-викторину по основам бизнеса! Нажмите на кнопку с интересующей Вас темой, и я Вам помогу.",
        reply_markup=main_markup)  # Отправка приветственного сообщения

# Обработчик команды /task


@bot.message_handler(commands=['task'])
def closest_task(message):
    tasks_reminder(message.chat.id)

# Обработчик нажатий на кнопки основного меню


@bot.callback_query_handler(lambda call: ':' not in call.data)
def main_menu_actions(call):
    print('main menu action selected')  # Логирование выбора пользователя
    if call.data == '0':
        print('user has chosen "Обучение основам бизнеса"')
        msg = bot.send_message(call.message.chat.id,
                               'Что Вы хотите узнать?')  # Запрос информации
        bot.register_next_step_handler(msg, simple_gpt_prompt)
    elif call.data == '1':
        print('user has chosen "Генерация бизнес-планов"')
        # Запрос описания идеи
        msg = bot.send_message(call.message.chat.id, 'Опишите Вашу идею.')
        bot.register_next_step_handler(msg, plan_generator)
    elif call.data == '2':
        print('user has chosen "Планирование задач"')
        msg = bot.send_message(
            call.message.chat.id, 'Какую задачу Вы хотите запланировать?')  # Запрос задачи
        # Обработка планирования задачи
        bot.register_next_step_handler(msg, separate_task_planing)
    elif call.data == '3':
        print('user has chosen "Управление ресурсами"')
        msg = bot.send_message(call.message.chat.id,
                               'Опишите Ваш бизнес и капитал.')  # Запрос информации о бизнесе
        bot.register_next_step_handler(msg, resource_advisor)
    elif call.data == '4':
        print('user has chosen "Успешные бизнес-кейсы"')
        store_cases()
        msg1 = bot.send_media_group(call.message.chat.id, [
                                    cases_list[cases_index]])[0]  # Отправка первого кейса
        msg2 = bot.send_message(msg1.chat.id, 'Кейс №' + str(cases_index + 1), reply_markup=telebot.util.quick_markup(  # Отправка текста кейса
            {'Назад': {'callback_data': 'f:0'}, '->': {'callback_data': 'f:1'}}))
        cases(msg1, msg2)
    elif call.data == '5':
        print('user has chosen "Часто задаваемые вопросы"')
        bot.send_message(call.message.chat.id,
                         frequently_asked_questions)  # Отправка FAQ
        main_message(call.message.chat.id)
    elif call.data == '6':
        global question_number_gl
        question_number_gl = 1
        print('user has chosen "Мини-викторина"')
        quiz_handler(call.message)
    elif call.data == '7':
        print('user has chosen "Личный кабинет"')
        personal_data = telebot.util.quick_markup({
            'Сохраненные бизнес планы': {'callback_data': 'c:1'},
            'Невыполненные задачи': {'callback_data': 'c:2'},
            '🔙Назад': {'callback_data': 'c:0'}
        })
        msg = bot.send_message(
            call.message.chat.id, 'Какие данные Вы хотите просмотреть?', reply_markup=personal_data)  # Запрос выбора личных данных

        # Обработка выбора личных данных
        @ bot.callback_query_handler(lambda call1: call1.data.startswith('c:'))
        def personal_data_manager(call1):
            call_data = call1.data.split(':')[1]
            if call_data == '1':
                business_plans = pandas.read_csv(
                    'E:\\VSCODE\\Telegram-bot\\users.csv', index_col=['chat_id'])  # Чтение сохраненных бизнес-планов
                try:
                    for plan in business_plans.at[call1.message.chat.id, 'saved_business_plans'].split('//'):
                        bot.send_message(
                            call1.message.chat.id, plan)  # Отправка бизнес-планов
                except:
                    bot.send_message(
                        call1.message.chat.id, 'Нет сохраненных бизнес-планов')
            elif call_data == '2':
                pending_tasks = pandas.read_csv(
                    'E:\\VSCODE\\Telegram-bot\\calendar_plans.csv', index_col=0)  # Чтение невыполненных задач
                pending_tasks = pending_tasks.loc[lambda pending_tasks:
                                                  pending_tasks['chat_id'] == call1.message.chat.id]
                output = ''
                
                for i in range(len(pending_tasks)):
                    output += pending_tasks['task'].values.tolist(
                    )[i] + ' ' + pending_tasks['datetime'].values.tolist()[i] + '\n'  # Формирование вывода задач
                
                try:
                    bot.send_message(
                        call1.message.chat.id, output)  # Отправка невыполненных задач
                except:
                    bot.send_message(
                        call1.message.chat.id, 'Нет невыполненных задач')
                    
            main_message(call1.message.chat.id)  # Возврат в главное меню

# Функция генерации бизнес-планов


def plan_generator(message):
    result = gpt_prompt(
        message, 2)  # Запрос генерации бизнес-плана
    message_states = {}
    business_plan = telebot.util.quick_markup({'📅Перейти к планированию': {'callback_data': 'a:1'},
                                               'Сохранить бизнес-план': {'callback_data': 'a:2'},
                                               '🔙Назад': {'callback_data': 'a:0'}})
    add_plan_choices = bot.send_message(message.chat.id, result,
                                        reply_markup=business_plan)  # Отправка бизнес-плана
    message_states[add_plan_choices.chat.id] = add_plan_choices.message_id

    # Обработка выбора действий с бизнес-планом
    @ bot.callback_query_handler(lambda call: call.data.startswith('a:'))
    def business_planning(call):
        call_data = call.data.split(':')[1]
        if call_data == '1':  # Планирование задач: занесение задач в calendar_plans.csv
            planning_steps = telebot.types.InlineKeyboardMarkup()
            step_count = 1
            steps = steps_separator(result)  # Разделение шагов бизнес-плана
            for step in steps:
                planning_steps.add(telebot.types.InlineKeyboardButton(
                    text=step, callback_data=('b:' + str(step_count))))  # Добавление шагов в клавиатур
                step_count += 1
            bot.edit_message_text(chat_id=add_plan_choices.chat.id, message_id=message_states[add_plan_choices.chat.id],
                                  text='Выберите задачу', reply_markup=planning_steps)  # Выбор задачи

            # Обработка выбора задачи
            @bot.callback_query_handler(lambda call1: call1.data.startswith('b:'))
            def date_time_request(call1):
                call1_data = call1.data.split(':')[1]
                msg = bot.send_message(
                    call1.message.chat.id, 'Дата и время?(в формате дд.мм.гггг чч:ММ или дд.мм.гггг)')  # Запрос даты и времени, если время не предоставлено, то оно по-дефолту 00:00
                task = int(call1_data)
                # Обработка планирования задачи
                bot.register_next_step_handler(msg, task_planning_step, task)

            def task_planning_step(message, task):
                try:
                    if len(message.text) < 16:
                        dtime = message.text + ' 00:00'  # Установка времени по умолчанию
                    else:
                        dtime = message.text
                    dt.datetime.strptime(
                        dtime, '%d.%m.%Y %H:%M')  # Проверка формата даты и времени
                except:
                    bot.send_message(
                        message.chat.id, 'Неправильный формат даты и времени. Попробуйте ещё раз❌')  # Ошибка формата
                    date_time_request(task)  # Повторный запрос даты
                else:
                    task_planning(steps[task - 1], message,
                                  dtime)  # Планирование задачи
                    # Подтверждение добавления задачи
                    bot.send_message(message.chat.id, 'Задача добавлена✔️')
                    # Возврат в главное меню
                    main_message(call.message.chat.id)
        elif call_data == '2':  # Сохранение бизнес-плана
            csv = pandas.read_csv(
                '.\\users.csv', index_col=['chat_id'])  # Чтение CSV файла пользователей
            if call.message.chat.id in csv.index.values.tolist():
                csv.at[call.message.chat.id, 'saved_business_plans'] = csv.at[call.message.chat.id,
                                                                              'saved_business_plans'] + '//' + result  # Сохранение бизнес-плана
            else:
                csv.loc[call.message.chat.id] = {
                    'saved_business_plans': result}  # Добавление нового пользователя

            # Сохранение изменений в CSV
            csv.to_csv('.\\users.csv')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=add_plan_choices.message_id,
                                  text='Сохранено✔️')  # Подтверждение сохранения
            main_message(call.message.chat.id)  # Возврат в главное меню
        else:
            main_message(call.message.chat.id)

# Функция для управления ресурсами


def resource_advisor(message):
    result = gpt_prompt(
        message, 1)  # Запрос информации о ресурсах у YaGPT
    bot.send_message(message.chat.id, result)  # Отправка результата
    main_message(message.chat.id)  # Возврат в главное меню

# Функция для планирования задач отдельно от бизнес-плана


def separate_task_planing(message):
    msg = bot.send_message(
        message.chat.id, 'Дата и время?(в формате дд.мм.гггг чч:ММ или дд.мм.гггг)')  # Запрос даты и времени
    # Обработка планирования задачи
    bot.register_next_step_handler(msg, task_planning_step, message.text)

# Функция для обработки планирования задачи для функции выше


def task_planning_step(message, task):
    try:
        if len(message.text) < 16:
            dtime = message.text + ' 00:00'  # Установка времени по умолчанию
        else:
            dtime = message.text
        dt.datetime.strptime(dtime, '%d.%m.%Y %H:%M')  # Проверка формата даты
    except:
        bot.send_message(
            message.chat.id, 'Неправильный формат даты и времени. Попробуйте ещё раз❌')  # Ошибка формата
        separate_task_planing(task)  # Повторный запрос даты
    else:
        task_planning(task, message, dtime)
        bot.send_message(message.chat.id, 'Задача добавлена✔️')
        main_message(message.chat.id)

# Функция для простого запроса к GPT


def simple_gpt_prompt(message):
    bot.reply_to(message, gpt_prompt(message, 0))  # Ответ от GPT
    main_message(message.chat.id)

# Функция для обработки и вывода успешных бизнес-кейсов


def cases(img_message, txt_message):
    global cases_index, img_message_global, txt_message_global
    img_message_global = img_message
    txt_message_global = txt_message
    markup_switch = {0: 0, 1: 1, 2: 1, 3: 2}  # Переключение разметки
    markup_list = [
        telebot.util.quick_markup({
            'Назад': {'callback_data': 'f:0'},
            '->': {'callback_data': 'f:1'}
        }),
        telebot.util.quick_markup({
            '<-': {'callback_data': 'f:2'},
            '->': {'callback_data': 'f:1'},
            'Назад': {'callback_data': 'f:0'}
        }),
        telebot.util.quick_markup({
            '<-': {'callback_data': 'f:2'},
            'Назад': {'callback_data': 'f:0'}
        })]

    # Обработка навигации по кейсам
    @bot.callback_query_handler(lambda call: call.data.startswith('f:'))
    def case_control(call):
        global cases_index, cases_list, img_message_global, txt_message_global
        data = call.data.split(':')[1]
        if data == '0':  # При выходе удаляем сообщения с кейсами, чтобы не засорять чат с ботом
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=img_message_global.message_id)  # Удаление текущего изображения
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=txt_message_global.message_id)  # Удаление текущего текста
            main_message(call.message.chat.id)
            cases_index = 0
        elif data == '1':
            cases_index += 1  # Переход к индексу следующего кейсу
        elif data == '2':
            cases_index -= 1  # Переход к индексу предыдущего кейсу
        try:
            img_message = bot.edit_message_media(chat_id=call.message.chat.id, message_id=img_message_global.message_id,
                                                 media=cases_list[cases_index])  # Обновление изображения
            txt_message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=txt_message_global.message_id,
                                                text='Кейс №' + str(cases_index + 1), reply_markup=markup_list[markup_switch[cases_index]])  # Обновление текста
        except telebot.apihelper.ApiTelegramException:
            return
        cases(img_message, txt_message)

# Функция для планирования задач


def task_planning(task, message, dtime):
    try:
        tasks_file = pandas.read_csv(
            '.\\calendar_plans.csv', index_col=0)  # Чтение файла задач
        tasks_file.loc[len(tasks_file.index)] = {
            'chat_id': message.chat.id, 'task': task, 'datetime': dtime}  # Добавление новой задачи
        # Сохранение задач
        tasks_file.to_csv('.\\calendar_plans.csv')
    except Exception as e:
        print(e)  # Логирование ошибок
    else:
        print('Task added')  # Подтверждение добавления задачи

# Функция для отправки основного сообщения


def main_message(chat_id):
    msg = bot.send_message(
        chat_id, 'Чем могу Вам помочь?', reply_markup=main_markup)
    return msg

# Функция для разделения шагов бизнес-плана


def steps_separator(text):
    steps = list()
    for step in text.split('\n'):
        if step and step[0].isdigit():
            steps.append(step)  # Добавление шагов в список
    return steps

# Функция для запроса к GPT


def gpt_prompt(message, prompt):
    global prompts
    prompt = {
        # идентификатор каталога сюда
        "modelUri": "gpt://<Идентификатор каталога>/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты эксперт в ведении бизнеса, твоя роль помогать начинающим бизнесменам. Ответы даёшь короткие, но информативные."
            },
            {
                "role": "user",
                "text": message.text + prompts[prompt]
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key <api ключ>"  # сюда API-ключ
    }
    pend_msg = bot.send_message(
        message.chat.id, "Запрос обрабатывается, пожалуйста, подождите⏳")  # Сообщение о текущем процессе
    response = requests.post(url, headers=headers,  # Отправка запроса к API
                             json=prompt)  # возвращает тип str
    # Удаление сообщения о процессе
    bot.delete_message(pend_msg.chat.id, pend_msg.message_id)
    print('GPT response', response.text)
    try:
        result = response.text.replace('*', '')
        result = result.replace('\\n', '\n')
        start = result.index('"text":') + 8
        end = result.index('"}') + 1
    except Exception as e:
        print(e)  # Логирование ошибок
    else:
        # Обрезает лишнюю информацию в начале и в конце
        print('GPT request success')
        result = result[start:end]  # Извлечение текста из ответа
        return result

# Функция для напоминания о задачах


def tasks_reminder(chat_id):

    tasks_file = pandas.read_csv(
        '.\\calendar_plans.csv', index_col=0)  # Чтение файла задач
    tasks_file = tasks_file.loc[lambda tasks_file:
                                tasks_file['chat_id'] == chat_id]  # Фильтрация по chat_id
    if len(tasks_file) > 0:
        closest_task = sorted(list(filter(lambda x: x > dt.datetime.now(), [dt.datetime.strptime(i, '%d.%m.%Y %H:%M')
                                                                            for i in tasks_file['datetime'].values.tolist()])))[0].strftime('%d.%m.%Y %H:%M')  # Поиск ближайшей задачи
        print('closest task', closest_task)  # Логирование ближайшей задачи
        return bot.send_message(chat_id, 'Ближайшая задача - ' + str(tasks_file[tasks_file['chat_id'] == chat_id].iat[tasks_file[tasks_file['datetime'] == closest_task].index[0] - 2, 1]) + ' до ' + closest_task + f' (через {dt.datetime.strptime(closest_task, "%d.%m.%Y %H:%M") - dt.datetime.now()})')
    else:
        return bot.send_message(chat_id, 'Нет невыполненных задач')


def store_cases():
    # Обрабатывет файлы(.jpeg) с кейсами
    # и добавляет их в список cases_list,
    # как объекты InputMediaPhoto
    global cases_paths, cases_list
    cases_list = list()
    for i in range(4):
        with open(cases_paths[-1] + cases_paths[i], 'rb') as f:
            cases_list.append(telebot.types.InputMediaPhoto(f.read()))


# Переменные для викторины
question_number_gl = 1


def quiz_handler(message):
    msg = bot.send_message(message.chat.id, '⭐Мини-викторина по основам бизнеса⭐ \
                                            *На вопросы можно отвечать не по-порядку')
    for i in range(5):
        print(i)
        msg = quiz_question(msg, i)
        time.sleep(0.1)


def quiz_question(message, question_number):
    return bot.send_message(message.chat.id, list(quiz_questions.values())[question_number], reply_markup=quiz_markup)


@bot.callback_query_handler(lambda call: call.data.startswith('qa'))
def quiz_callback_query_handler(call):
    global quiz_questions, question_number_gl
    if call.data.split(':')[1] == list(quiz_questions.keys())[int(call.message.text[:1:]) - 1].split(':')[1]:
        bot.send_message(call.message.chat.id,
                         f'№{question_number_gl} Правильно!⭐')
    else:
        bot.send_message(call.message.chat.id,
                         f'№{question_number_gl} Неправильно!❌')
    bot.delete_message(call.message.chat.id, call.message.message_id)
    question_number_gl += 1


bot.infinity_polling()
