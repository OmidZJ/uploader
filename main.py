import os
import subprocess
import requests
import telebot
from dotenv import load_dotenv
import time

# Load token from environment variables
load_dotenv()
TOKEN = os.getenv('7434733526:AAGsorRnGaWWzicG-yiWYdpACVIIR4aJwdI')
bot = telebot.TeleBot(TOKEN)

# Folder to store downloaded files
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Helper function to download and send file
def download_and_send_file(link, message):
    filename = os.path.join(DOWNLOAD_FOLDER, f'{int(time.time())}_{link.split("/")[-1]}')
    try:
        response = requests.get(link)
        response.raise_for_status()  # Check for request errors
        with open(filename, 'wb') as file:
            file.write(response.content)

        # Send file as document or video
        with open(filename, 'rb') as file:
            if filename.endswith(".mp4"):
                bot.send_video(message.chat.id, file)
            else:
                bot.send_document(message.chat.id, file)
        
        # Optionally delete file after upload
        os.remove(filename)
        bot.send_message(message.chat.id, "File uploaded successfully!")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred while downloading or sending the file: {e}")

# Handle the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me a link, and I'll upload the video (if it's .m3u or .mp4) or the file!")

# Handle incoming messages that contain links
@bot.message_handler(func=lambda message: message.text and message.text.startswith("http"))
def download_and_upload(message):
    link = message.text
    try:
        if link.endswith(".m3u") or link.endswith(".m3u8"):
            bot.send_message(message.chat.id, "This is an m3u/m3u8 link. Downloading and converting to mp4...")
            output_filename = os.path.join(DOWNLOAD_FOLDER, 'downloaded_video.mp4')
            ffmpeg_command = ['ffmpeg', '-i', link, '-c', 'copy', output_filename]
            
            try:
                subprocess.run(ffmpeg_command, check=True, timeout=600)  # 10 minutes timeout
            except subprocess.TimeoutExpired:
                bot.send_message(message.chat.id, "The process took too long and was timed out.")
                return
            except subprocess.CalledProcessError as e:
                bot.send_message(message.chat.id, f"Error during ffmpeg process: {e}")
                return

            if os.path.exists(output_filename):
                file_size = os.path.getsize(output_filename)
                bot.send_message(message.chat.id, f"File size: {file_size / (1024 * 1024):.2f} MB")
                
                try:
                    with open(output_filename, 'rb') as video_file:
                        bot.send_video(message.chat.id, video_file)
                    os.remove(output_filename)
                    bot.send_message(message.chat.id, "Video uploaded successfully!")
                except telebot.apihelper.ApiException as e:
                    bot.send_message(message.chat.id, f"Error during video upload: {e}")
            else:
                bot.send_message(message.chat.id, "Failed to download the video.")
        elif link.endswith(".mp4"):
            download_and_send_file(link, message)
        else:
            download_and_send_file(link, message)
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {e}")

# Start polling to keep the bot running
bot.polling()
