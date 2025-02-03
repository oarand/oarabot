import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import os
from dotenv import load_dotenv
import subprocess
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def execute_command(command):
    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    return res

def spawn_command(command):
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
        #stdout, stderr = process.communicate()
        #logging.debug(f"Salida estándar: {stdout.decode()}")
        #logging.debug(f"Salida de error: {stderr.decode()}")

        logging.debug(f"Proceso iniciado con PID: {process.pid}")
        return process
    except Exception as e:
        logging.error(f"Error al crear el proceso: {str(e)}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Status", callback_data='status'),
         InlineKeyboardButton("Start VPN", callback_data='startVPN')],
        [InlineKeyboardButton("Stop VPN", callback_data='stopVPN')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Por favor, elige una opción:', reply_markup=reply_markup)
    #await context.bot.send_message(chat_id=update.effective_chat.id,  reply_markup=reply_markup)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    getIpCommand = "curl -4 icanhazip.com"
    ip = execute_command(getIpCommand).stdout

    openvpnAliveOutput = execute_command("ps -ef | grep openvpn | grep -v grep").stdout
    isOpenvpnAlive = bool(openvpnAliveOutput)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"IP: {ip}. VPN Alive: {isOpenvpnAlive}")

async def startVPN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = "sudo openvpn --config /etc/openvpn/pt-lis.prod.surfshark.com_tcp.ovpn --auth-user-pass /etc/openvpn/login-ss.file"
    process = spawn_command(command)
    if process not in [None, False]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Proceso iniciado con PID: {process.pid}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al iniciar el proceso: {process.stderr}")
    

async def stopVPN(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = "sudo killall openvpn"
    res = execute_command(command)
    if res.returncode == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="VPN detenida exitosamente")
        await status(update, context)
    else:
        logging.error(f"Error al detener la VPN: {res.stderr}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al detener la VPN: {res.stderr}")


async def button(update, context):
    query = update.callback_query
    query.answer()
    await query.edit_message_text(text=f"Seleccionaste la opción: {query.data}")

async def post_init(application):
    await application.bot.set_my_commands([
        ('status', 'Muestra el estado de la VPN'),
        ('start', 'Inicia la VPN'),
        ('stop', 'Detiene la VPN')])

def main():
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    # Reemplaza 'TU_TOKEN_AQUÍ' con el token que te proporcionó BotFather
    logging.info(f"Token: {TOKEN}")

    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    
    #application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('start', startVPN))
    application.add_handler(CommandHandler('stop', stopVPN))
    
    application.run_polling()


if __name__ == '__main__':
    main()
