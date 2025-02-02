import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import subprocess
import os
import logging

# Reemplaza 'TU_TOKEN_AQUÍ' con el token que te proporcionó BotFather
bot = telebot.TeleBot('8148267154:AAEm7gtmJJNzFcdOZltGrVOpHWliR3q8gE8')

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@bot.message_handler(commands=['ip'])
def show_ip(message):
    resultado = subprocess.run(['curl', '-4', 'icanhazip.com'], capture_output=True, text=True)
    bot.reply_to(message, resultado.stdout)

@bot.message_handler(commands=['menu'])
def comando_menu(message):
    bot.reply_to(message, "Selecciona una opción:", reply_markup=generar_menu())

@bot.message_handler(commands=['start'])
def ejecutar_start_vpn(message):
    command = "sudo openvpn --config /etc/openvpn/pt-lis.prod.surfshark.com_tcp.ovpn --auth-user-pass /etc/openvpn/login-ss.file"
    
    pid = execute_command(command)

    if (pid not None):
        bot.reply_to(message, f"Proceso iniciado con PID: {pid}")
    else:
        bot.reply_to(message, f"Error al iniciar el proceso")

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



def execute_command(command):
    logging.debug(f"Intentando ejecutar el comando: {command}")
    try:
        # Lanza el proceso en segundo plano
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            close_fds=True,
            shell=True,
            preexec_fn=os.setsid
        )
        logging.debug("Proceso creado exitosamente")
        
        # Desconectar el proceso del proceso padre
        stdout, stderr = process.communicate()
        logging.debug(f"Salida estándar: {stdout.decode()}")
        logging.debug(f"Salida de error: {stderr.decode()}")

        logging.debug(f"Proceso iniciado con PID: {process.pid}")
        return process.pid
    except Exception as e:
        logging.error(f"Error al crear el proceso: {str(e)}")
        return None