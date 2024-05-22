from flask import Flask, request, jsonify, send_from_directory
import os
import time
import yt_dlp
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloads'


def delete_old_files():
    folder_path = 'downloads'
    file_extension = '.mp4'
    time_threshold = 120  # 2 minutes in seconds

    current_time = time.time()

    for filename in os.listdir(folder_path):
        if filename.endswith(file_extension):
            file_path = os.path.join(folder_path, filename)
            try:
                creation_time = os.path.getctime(file_path)
                if (current_time - creation_time) > time_threshold:
                    os.remove(file_path)
                    print(f"Arquivo '{filename}' removido.")
            except Exception as e:
                print(f"Erro ao excluir o arquivo '{filename}': {str(e)}")


def download_video(url, videoRandomID):

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'username': os.getenv("TWITTER_USERNAME"),
        'password': os.getenv("TWITTER_PASSWORD"),
        'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], videoRandomID+'.mp4')
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@app.route('/', methods=['GET'])
def index():
    return "running ✅"


@app.route('/baixar', methods=['POST'])
def baixar_video():
    delete_old_files()
    data = request.json
    video_url = data.get('url')
    
    if video_url and 'x.com' in video_url:
        video_url = video_url.replace('x.com', 'twitter.com')
    
    videoRandomID = str(uuid.uuid4()).rsplit('-', 1)[-1]
    if video_url:
        if 'twitter.com' in video_url:
            try:
                download_video(video_url, videoRandomID)
                file_url = f"{request.host_url}download/{videoRandomID}.mp4"
                return jsonify({'file': file_url})
            except:
                return jsonify({'error': 'erro ao baixar'}), 400
        else:
            return jsonify({'error': 'apenas videos do twitter/X'}), 401

    else:
        return jsonify({'error': 'URL inválida'}), 500


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    delete_old_files()
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)


if __name__ == '__main__':
    if not os.path.exists(app.config['DOWNLOAD_FOLDER']):
        os.makedirs(app.config['DOWNLOAD_FOLDER'])
    app.run(host="0.0.0.0", port=5000)
