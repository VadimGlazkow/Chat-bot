from telebot import TeleBot, types
from random import shuffle

TOKEN = ''
bot = TeleBot(TOKEN)
users = {}
right_ans = {}

hard_words = [106, 108, 110, 113, 115, 117, 119, 120, 107, 109, 112, 114, 116, 118, 121, 122, 123, 124, 125, 126, 127,
              129, 131, 133, 139, 128, 130, 132, 138, 140, 141, 142, 144, 146, 148, 207, 145, 147, 149, 151, 208, 209,
              154, 156, 150, 152, 153, 155, 157, 158, 1, 2, 4, 7, 8, 9, 159, 5, 6, 10, 11, 160, 16, 13, 18, 21, 23, 20,
              21, 64]
shuffle(hard_words)


hard_words = [index - 1 for index in hard_words]


with open('words.txt', encoding='utf-8', mode='r') as file:
    words = [st.split() for st in file.read().split('\n')]
    count_words = len(words)
    for word_1, word_2 in words:
        right_ans[word_1.lower()] = word_1
    words = [list(set(pair)) for pair in words]


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    users[user_id] = {'name': message.from_user.first_name,
                      'surname': message.from_user.last_name,
                      'result': [],
                      'right': 0,
                      'wrong_ans': [],
                      'words_for_user': [],
                      'type': None,
                      'count': 0}
    start_work(message)


@bot.message_handler(commands=['rating'])
def rating(message):
    res = []
    for key in users:
        if users[key]['result']:
            res.append([users[key]['result'][-1], users[key]['name'], users[key]['surname']])
    if res:
        res.sort(key=lambda x: x[0][1], reverse=True)
        text = ''
        for i, inf in enumerate(res):
            text += f'{i + 1}. {inf[1]} {inf[2]} {inf[0][1]}% Вид - {inf[0][0]}\n'
        text = text[:-1]
        bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardHide())
    else:
        bot.send_message(message.chat.id, 'Тут пока никого нет...', reply_markup=types.ReplyKeyboardHide())


@bot.message_handler(commands=['list'])
def list_words(message):
    st = '\n'.join(list(right_ans.values()))
    bot.send_message(message.chat.id, st, reply_markup=types.ReplyKeyboardHide())


@bot.message_handler(commands=['help'])
def help_for_user(message):
    text = '''RescupBot - бот-помощник для изучания правильной постановки ударений в словах для ЕГЭ по русскому языку.\n
/start_work - ✏ Начать изучение слов
/help - ⚠ Помощь
/list - 📝 Список всех слова
/rating - 🏆Рейтинг
           '''
    bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardHide())


@bot.message_handler(commands=['start_work'])
def start_work(message):
    user_id = message.from_user.id
    if user_id not in users:
        start_message(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    but1 = types.KeyboardButton(f'Все ({count_words} слов)')
    but2 = types.KeyboardButton(f'Трудные ({len(hard_words)} слов)')
    markup.add(but1, but2)
    bot.send_message(message.chat.id, 'Какие слова хотите повторить?', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_user_text(message):
    try:
        flag_next_word = True
        flag_around = True
        text = message.text
        user_id = message.from_user.id
        if user_id not in users:
            start_message(message)
            return
        if text in (f'Все ({count_words} слов)', f'Трудные ({len(hard_words)} слов)'):
            diff_words(message)
            flag_next_word = False
        elif text.lower() in right_ans:
            all_cnt = users[user_id]['count']
            now_cnt = all_cnt - len(users[user_id]['words_for_user']) + 1
            if right_ans[text.lower()] == text:
                bot.send_message(message.chat.id, f'✅ Верно! {now_cnt}/{all_cnt}')
                users[user_id]['right'] += 1
            else:
                bot.send_message(message.chat.id, f'❌ Неверно! {now_cnt}/{all_cnt}')
                users[user_id]['wrong_ans'].append(right_ans[text.lower()])
            bot.send_message(message.chat.id, f'⚠ {right_ans[text.lower()]}')
        else:
            bot.send_message(message.chat.id, '⚠ Вы ввели некорректный вариант')
            flag_next_word = False
            flag_around = False
        if len(users[message.from_user.id]['words_for_user']) > 1:
            if flag_next_word:
                users[message.from_user.id]['words_for_user'].pop(0)
            pair = words[users[message.from_user.id]['words_for_user'][0]]
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            word1 = types.KeyboardButton(pair[0])
            word2 = types.KeyboardButton(pair[1])
            markup.add(word1, word2)
            if flag_around:
                bot.send_message(message.chat.id, 'Какой вариант правильный?', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Попробуйте еще раз. Какой вариант правильный?', reply_markup=markup)
        elif users[user_id]['count'] != 0:
            words_with_mistake = '\n'.join([f'⚠ {word}' for word in users[user_id]['wrong_ans']])
            pr = round(users[user_id]['right'] / users[user_id]['count'] * 100)
            text = f'Результат:\nПроцент выволнения {pr}%\n\nОшибки в словах:\n{words_with_mistake}'
            users[user_id]['result'].append([users[user_id]['type'], pr])
            users[user_id]['right'] = 0
            users[user_id]['wrong_ans'] = []
            bot.send_message(message.chat.id, text)
            start_work(message)
        else:
            print('Даааа')
            start_work(message)
    except:
        pass


def diff_words(message):
    user_id = message.from_user.id
    if user_id not in users:
        start_message(message)
        print('Это тупо 144 строка')
        return
    if 'Все' in message.text:
        users[user_id]['words_for_user'] = list(range(0, count_words))
        users[user_id]['count'] = count_words
        users[user_id]['type'] = 'Все'
        # 'right': 0,
        users[user_id]['right'] = 0
    else:
        users[user_id]['words_for_user'] = hard_words[:]
        users[user_id]['count'] = len(hard_words)
        users[user_id]['type'] = 'Трудные'
        users[user_id]['right'] = 0

    shuffle(users[user_id]['words_for_user'])


bot.polling(none_stop=True)


