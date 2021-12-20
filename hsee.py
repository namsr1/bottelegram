import telebot
from hselab import get_map_cell


bot = telebot.TeleBot('5068128024:AAEbGs52vMoxGt2nRfk7gTregPBRUQaK5dc')

cols, rows = 8, 8
"""
столбцы и строки представляем  как 8
"""
#создаем стрелки (кнопки)

keyboard = telebot.types.InlineKeyboardMarkup()
"""Keyboa помогает создавать встроенные клавиатуры любой сложности для ботов, разработанных на базе pyTelegramBotAPI
inline_keyboard определен как массив, состоящий из массивов кнопок
основной массив - это клавиатура в целом, а его элементы - это ряды кнопок
при нажатии ← кружок будет двигаться влево, ↑ - навверх , ↓ - вниз, → - вправо
"""
keyboard.row( telebot.types.InlineKeyboardButton('←', callback_data='left'),
			  telebot.types.InlineKeyboardButton('↑', callback_data='up'),
			  telebot.types.InlineKeyboardButton('↓', callback_data='down'),
			  telebot.types.InlineKeyboardButton('→', callback_data='right') )

maps = {}
#получает карту и координаты игрока, а возвращать строку сообщением

def get_map_str(map_cell, player):
	"""
создаем функцию которая будет получать  карту и координаты игрока а возвращать строку сообщением 
также функция map применяет функцию к каждому элементу последовательности и возвращает итератор с результатами 
"""
	map_str = ""
	for y in range(rows * 2 - 1):
		for x in range(cols * 2 - 1):
			if map_cell[x + y * (cols * 2 - 1)]:
				map_str += "⬛"
			elif (x, y) == player:
				map_str += "🔴"
			else:
				map_str += "⬜"
		map_str += "\n"

	return map_str
#бот будет выдавать карту накоманду 'play'
@bot.message_handler(commands=['play'])
def play_message(message):
	map_cell = get_map_cell(cols, rows)
#для каждого пользователя будем хранить лабиринт , а также координаты игрока 
	user_data = {
		'map': map_cell,
		'x': 0,
		'y': 0
	}

	maps[message.chat.id] = user_data

	bot.send_message(message.from_user.id, get_map_str(map_cell, (0, 0)), reply_markup=keyboard)
#вызывает нажатием на кнопку,получим лабиринт и старые координаты , определим новые координаты 

@bot.callback_query_handler(func=lambda call: True)
def callback_func(query):
	
	"""
	создаем функцию которая будет вызываться по нажатию на кнопку 
	lambda-оператор или лямбда-функция используются для создания небольших, одноразовых и анонимных объектов функции в Python.
	функция получает лабиринт и старые координаты , определяет новые координаты(x,y) и проверяем возможен ли такой ход  
    """
	user_data = maps[query.message.chat.id]
	new_x, new_y = user_data['x'], user_data['y']

	if query.data == 'left':
		new_x -= 1
	if query.data == 'right':
		new_x += 1
	if query.data == 'up':
		new_y -= 1
	if query.data == 'down':
		new_y += 1
	
	if new_x < 0 or new_x > 2 * cols - 2 or new_y < 0 or new_y > rows * 2 - 2:
		return None
	if user_data['map'][new_x + new_y * (cols * 2 - 1)]:
		return None
	"""
	сохраняем данные и изменим сообщение 
	"""
	user_data['x'], user_data['y'] = new_x, new_y
	"""
	добавляем сообщение , после прохождения игры 'Вы выиграли' 
	для этого проверяем находится ли пользовтель на самой нижней правой клетки 
	"""
	if new_x == cols * 2 - 2 and new_y == rows * 2 - 2:
		bot.edit_message_text( chat_id=query.message.chat.id,
							   message_id=query.message.id,
							   text="Вы выиграли" )
		return None

	bot.edit_message_text( chat_id=query.message.chat.id, 
						
							
						   message_id=query.message.id,
						   text=get_map_str(user_data['map'], (new_x, new_y)),
						   reply_markup=keyboard )

bot.polling(none_stop=False, interval=0)