import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os
from dotenv import load_dotenv
import subprocess

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
        return process.pid
    except Exception as e:
        logging.error(f"Error al crear el proceso: {str(e)}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    getIpCommand = "curl -4 icanhazip.com"
    ip = execute_command(getIpCommand).stdout

    openvpnAliveOutput = execute_command("ps -ef | grep openvpn | grep -v grep").stdout
    isOpenvpnAlive = bool(openvpnAliveOutput)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"IP: {ip}. VPN Alive: {isOpenvpnAlive}")

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv("TOKEN");
    # Reemplaza 'TU_TOKEN_AQUÍ' con el token que te proporcionó BotFather
    logging.info(f"Token: {TOKEN}")

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('status', status))
    
    application.run_polling()