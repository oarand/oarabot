import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import os
from dotenv import load_dotenv
import subprocess
import requests
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

def execute_command(command):
    """
    Executes a given shell command and returns the result.

    Args:
        command (str): The shell command to be executed.

    Returns:
        subprocess.CompletedProcess: The result of the executed command, containing
                                     attributes such as stdout, stderr, and returncode.
    """
    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    return res

def spawn_command(command):
    """
    Spawns a new process to execute the given command in the background.
    Args:
        command (str): The command to be executed.
    Returns:
        subprocess.Popen: The process object if the process is created successfully.
        None: If there is an error while creating the process.
    Logs:
        Debug: Logs the command being executed, process creation success, and process PID.
        Error: Logs any error encountered during process creation.
    """
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

async def startMenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the start menu interaction with the user by displaying a set of inline keyboard buttons.

    Args:
        update (Update): Incoming update from Telegram, containing the message and other metadata.
        context (ContextTypes.DEFAULT_TYPE): Context object containing bot data and other information.

    Returns:
        None: This function sends a message with an inline keyboard to the user.

    The inline keyboard contains the following options:
        - PT-LIS
        - PT-OPO
        - DE-BER
        - DE-FRA
        - UK-LON
        - FR-PAR
        - FI-HEL
        - ES-BCN

    The user is prompted to choose one of these options.
    """
    keyboard = [
         [InlineKeyboardButton("PT-LIS", callback_data='pt-lis'),
         InlineKeyboardButton("PT-OPO", callback_data='pt-opo')],
         [InlineKeyboardButton("DE-BER", callback_data='de-ber'),
         InlineKeyboardButton("DE-FRA", callback_data='de-fra')],
         [InlineKeyboardButton("UK-LON", callback_data='uk-lon'),
         InlineKeyboardButton("UK-LON", callback_data='uk-lon')],
         [InlineKeyboardButton("FR-PAR", callback_data='fr-par'),
         InlineKeyboardButton("FI-HEL", callback_data='fi-hel')],
         [InlineKeyboardButton("ES-BCN", callback_data='es-bcn')]
]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Por favor, elige una opción:', reply_markup=reply_markup)
    #await context.bot.send_message(chat_id=update.effective_chat.id,  reply_markup=reply_markup)

async def handleStartButton(update, context):
    """
    Handles the start button callback query.

    This function is triggered when the start button is pressed. It retrieves the 
    location data from the callback query, sends an acknowledgment to the user, 
    updates the message text with the selected option, and starts the VPN connection 
    for the specified location.

    Args:
        update (telegram.Update): The update object that contains the callback query.
        context (telegram.ext.CallbackContext): The context object that contains 
            data related to the callback query.

    Returns:
        None
    """
    query = update.callback_query
    query.answer()
    location  = query.data
    await query.edit_message_text(text=f"Seleccionaste la opción: {location}")
    await startVPN(location, update, context)

async def getIpInfo():
    """
    Asynchronously fetches IP information from ipinfo.io and returns a formatted string.

    This function sends a GET request to ipinfo.io to retrieve information about the current IP address.
    The JSON response is then formatted into a readable string without braces and leading spaces.

    Returns:
        str: A formatted string containing the IP information.
    """
    # request ipinfo.io and get json response
    response = requests.get("https://ipinfo.io")
    data = response.json()
    # convert json response to string and print
    formatted_json = json.dumps(data, indent=4)
    formatted_json_without_braces =  formatted_json[1:-1].strip()

    # Eliminar espacios de inicio de cada línea
    lines = formatted_json_without_braces.split('\n')
    lines = [line.strip() for line in lines]
    return '\n'.join(lines)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /status command to check the status of the VPN and retrieve IP information.

    Args:
        update (Update): Incoming update.
        context (ContextTypes.DEFAULT_TYPE): Context for the callback.

    Returns:
        None

    Sends a message to the chat with the status of the VPN (whether it is alive or not) and the IP information.
    """
    openvpnAliveOutput = execute_command("ps -ef | grep openvpn | grep -v grep").stdout
    isOpenvpnAlive = bool(openvpnAliveOutput)

    ipinfo=await getIpInfo()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"VPN Alive: {isOpenvpnAlive}\n{ipinfo}")

async def startVPN(location, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts a VPN connection using the specified location configuration.

    This function stops any currently running VPN connection before starting a new one
    with the provided location configuration. It sends a message to the user indicating
    whether the VPN process was successfully started or if there was an error.

    Args:
        location (str): The location configuration to use for the VPN connection.
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.

    Returns:
        None
    """
    # Detener la VPN si ya está en ejecución
    stopVPN(update, context, silent=True)
    command = f"/usr/sbin/openvpn --config /etc/openvpn/surf-shark/{location}.prod.surfshark.com_tcp.ovpn --auth-user-pass /etc/openvpn/surf-shark/login-ss.file"
    process = spawn_command(command)
    if process not in [None, False]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Proceso iniciado con PID: {process.pid}")
    else:
        logging.error(f"Error al detener el proceso: {process.stderr}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al iniciar el proceso: {process.stderr}")

async def stopVPN(update: Update, context: ContextTypes.DEFAULT_TYPE, silent=False):
    """
    Stops the VPN by killing the OpenVPN process.

    Args:
        update (Update): The update object that contains information about the incoming update.
        context (ContextTypes.DEFAULT_TYPE): The context object that contains information about the current context.
        silent (bool, optional): If True, no messages will be sent to the user. Defaults to False.

    Returns:
        None

    Sends a message to the user indicating whether the VPN was stopped successfully or if there was an error.
    Logs an error message if the VPN could not be stopped.
    """
    command = "killall openvpn"
    res = execute_command(command)
    if res.returncode == 0:
        if not silent:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="VPN detenida exitosamente")
            await status(update, context)
    else:
        if not silent:
            logging.error(f"Error al detener la VPN: {res.stderr}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al detener la VPN: {res.stderr}")

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
    application.add_handler(CallbackQueryHandler(handleStartButton))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('start', startMenu))
    application.add_handler(CommandHandler('stop', stopVPN))
    
    application.run_polling()

if __name__ == '__main__':
    main()
