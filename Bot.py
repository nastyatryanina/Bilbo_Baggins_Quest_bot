import telebot, json, requests
from Quest import que, photos

TOKEN = "6326683097:AAGS-yCoobsetI2prdtJYYxeNX0W5K2aNgo"
URL = 'https://api.telegram.org/bot'
bot = telebot.TeleBot(TOKEN)
help_message = 'Я бот-квест, основанный на произведении Джона Рональда Руэла Толкина "Хоббит, или Туда и обратно". Тебе необходимо выбирать действие из предложенных на клавиатуре. От твоего выбора будет зависеть будущее вселенной. Проиграешь ты или выиграешь - решать тебе.'
buttons = {}
users = {}
for q in que.keys():
    if que[q][1]:
        child = que[q][1][0]
        if que[child][2]:
            but_for_ques = {que[i][0]: {'callback_data': f"{i}"} for i in que[q][1]}
            buttons[q] = telebot.util.quick_markup(but_for_ques, row_width=1)

@bot.message_handler(commands=['start'])
def start(message):
    id = str(message.chat.id)
    global users
    users = get_info()
    bot.send_message(int(id), text=f"Привет, {message.from_user.first_name}. " + help_message)
    users[id] = 1
    change_info(users)
    ask_que(id)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    id = str(call.from_user.id)
    ans = int(call.data)
    global users
    users[id] = ans
    ask_que(id)

def ask_que(id):
    global users
    cur_que = users[id]
    next_que = que[cur_que][1]
    if next_que: #проверяю, не конец ли квеста
        if cur_que in buttons.keys(): # если следующий этап кнопки, то вывожу клаву
            bot.send_message(int(id), text="Выбери, что предпримешь: ", reply_markup=buttons[cur_que])
        elif next_que[0] in photos.keys():
            send_photo(int(id), next_que[0])
            users[id] = next_que[0]
            ask_que(id)
        else: # иначе текст на ней
            bot.send_message(int(id), text=que[next_que[0]][0])
            users[id] = next_que[0]
            ask_que(id)
    else:
        bot.send_message(int(id), text="Спасибо, что поучаствовал в квесте. Чтобы попробовать еще раз нужно воспользоваться функцией /start")

def get_info():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}


def change_info(users):
    with open("users.json", "w") as f:
        json.dump(users, f, ensure_ascii=False)

def send_photo(chat_id, q):
    file = {'photo': open(photos[q], 'rb')}
    requests.post(f'https://api.telegram.org/bot{TOKEN}/sendPhoto', data={"chat_id": chat_id, "caption": que[q][0]}, files = file)
bot.polling()
