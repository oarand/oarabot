import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import subprocess

# Reemplaza 'TU_TOKEN_AQUÍ' con el token que te proporcionó BotFather
bot = telebot.TeleBot('8148267154:AAEm7gtmJJNzFcdOZltGrVOpHWliR3q8gE8')


@bot.message_handler(commands=['ip'])
def show_ip(message):
    resultado = subprocess.run(['curl', '-4', 'icanhazip.com'], capture_output=True, text=True)
    bot.reply_to(message, resultado.stdout)

@bot.message_handler(commands=['menu'])
def comando_menu(message):
    bot.reply_to(message, "Selecciona una opción:", reply_markup=generar_menu())

@bot.message_handler(commands=['start'])
def ejecutar_start_vpn(message):
    comando = "sudo openvpn --config /etc/openvpn/pt-lis.prod.surfshark.com_tcp.ovpn --auth-user-pass /etc/openvpn/login-ss.fil"
    try:
        # Lanza el proceso en segundo plano
        proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        bot.reply_to(message, f"Proceso iniciado con PID: {proceso.pid}")
    except Exception as e:
        bot.reply_to(message, f"Error al iniciar el proceso: {str(e)}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message
                 , message.text)
def generar_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Opción 1", callback_data="opcion1"),
               InlineKeyboardButton("Opción 2", callback_data="opcion2"),
               InlineKeyboardButton("Opción 3", callback_data="opcion3"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "opcion1":
        bot.answer_callback_query(call.id, "Has seleccionado la Opción 1")
    elif call.data == "opcion2":
        bot.answer_callback_query(call.id, "Has seleccionado la Opción 2")
    elif call.data == "opcion3":
        bot.answer_callback_query(call.id, "Has seleccionado la Opción 3")

bot.polling()
