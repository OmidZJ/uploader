import telebot
import requests
import os
import subprocess

# Your bot's token from BotFather
TOKEN = '7434733526:AAGsorRnGaWWzicG-yiWYdpACVIIR4aJwdI'
bot = telebot.TeleBot(TOKEN)

# Folder to store downloaded files
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Handle the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Send me a link, and I'll upload the video (if it's .m3u or .mp4) or the file!")

# Handle incoming messages that contain links
@bot.message_handler(func=lambda message: message.text and message.text.startswith("http"))
def download_and_upload(message):
    link = message.text
    try:
        # Handle m3u/m3u8 links (stream to mp4 conversion)
        if link.endswith(".m3u") or link.endswith(".m3u8"):
            bot.send_message(message.chat.id, "This is an m3u/m3u8 link. Downloading and converting to mp4...")

            # Set the output video file name
            output_filename = os.path.join(DOWNLOAD_FOLDER, 'downloaded_video.mp4')

            # Use ffmpeg to download and convert the stream
            ffmpeg_command = ['ffmpeg', '-i', link, '-c', 'copy', output_filename]
            subprocess.run(ffmpeg_command)

            # Check if the file was successfully created
            if os.path.exists(output_filename):
                # Upload the mp4 video to the chat as video
                with open(output_filename, 'rb') as video_file:
                    bot.send_video(message.chat.id, video_file)
                
                # Optionally delete the file after uploading (to save space)
                os.remove(output_filename)
                bot.send_message(message.chat.id, "Video uploaded successfully!")
            else:
                bot.send_message(message.chat.id, "Failed to download the video.")

        # Handle mp4 links (upload directly as video)
        elif link.endswith(".mp4"):
            bot.send_message(message.chat.id, "This is an mp4 link. Downloading and uploading as video...")

            # Download the mp4 file
            filename = os.path.join(DOWNLOAD_FOLDER, link.split('/')[-1])
            response = requests.get(link)
            with open(filename, 'wb') as file:
                file.write(response.content)

            # Upload the mp4 video to Telegram as video
            with open(filename, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)

            # Optionally delete the file after uploading (to save space)
            os.remove(filename)
            bot.send_message(message.chat.id, "Video uploaded successfully!")

        # Handle all other file types (upload as document)
        else:
            bot.send_message(message.chat.id, "Downloading the file...")

            # Download the file
            filename = os.path.join(DOWNLOAD_FOLDER, link.split('/')[-1])
            response = requests.get(link)
            with open(filename, 'wb') as file:
                file.write(response.content)

            # Upload the file as a document
            with open(filename, 'rb') as file:
                bot.send_document(message.chat.id, file)

            # Optionally delete the file after uploading (to save space)
            os.remove(filename)
            bot.send_message(message.chat.id, "File uploaded successfully!")

    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {e}")

# Start polling to keep the bot running
bot.polling()
