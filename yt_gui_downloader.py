import os
import threading
import subprocess
from pytubefix import YouTube, Playlist
from tkinter import *
from tkinter import ttk, filedialog, messagebox

def download_video():
    url = url_entry.get()
    quality = quality_var.get()
    download_type = type_var.get()
    download_folder = path_label.cget("text")

    if not url:
        messagebox.showerror("Error", "Please enter a URL.")
        return

    try:
        if 'playlist' in url:
            playlist = Playlist(url)
            for video_url in playlist.video_urls:
                yt = YouTube(video_url, on_progress_callback=on_progress)
                download_stream(yt, quality, download_type, download_folder)
        else:
            yt = YouTube(url, on_progress_callback=on_progress)
            download_stream(yt, quality, download_type, download_folder)

        status_label.config(text="Download completed!")
        progress_bar['value'] = 100
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

def download_stream(yt, quality, download_type, download_folder):
    global filesize
    title = yt.title.replace(" ", "_").replace("|", "_")

    if download_type == "Audio":
        stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
        if stream:
            filesize = stream.filesize
            out_file = stream.download(output_path=download_folder, filename=title + "_audio")
            base, ext = os.path.splitext(out_file)
            os.rename(out_file, base + ".mp3")
    else:
        video_stream = yt.streams.filter(adaptive=True, res=quality, type="video").first()
        audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()

        if not video_stream or not audio_stream:
            messagebox.showwarning("Warning", f"No {quality} video/audio stream found for: {yt.title}")
            return

        filesize = video_stream.filesize
        video_path = video_stream.download(output_path=download_folder, filename=title + "_video.mp4")

        filesize = audio_stream.filesize
        audio_path = audio_stream.download(output_path=download_folder, filename=title + "_audio.mp4")

        final_output = os.path.join(download_folder, f"{title}.mp4")
        status_label.config(text="Merging video and audio...")

        # Merge using ffmpeg
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            final_output
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        os.remove(video_path)
        os.remove(audio_path)

def on_progress(stream, chunk, bytes_remaining):
    downloaded = filesize - bytes_remaining
    percent = int(downloaded / filesize * 100)
    progress_bar['value'] = percent
    status_label.config(text=f"Downloading... {percent}%")
    root.update_idletasks()

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        path_label.config(text=folder_selected)

def start_download_thread():
    threading.Thread(target=download_video).start()

# GUI Setup
root = Tk()
root.title("YouTube Downloader")
root.geometry("500x380")
root.resizable(False, False)

Label(root, text="YouTube URL:").pack(pady=5)
url_entry = Entry(root, width=60)
url_entry.pack(pady=5)

Label(root, text="Choose Quality:").pack(pady=5)
quality_var = StringVar(value="1080p")
quality_dropdown = ttk.Combobox(root, textvariable=quality_var, state="readonly")
quality_dropdown['values'] = ("1080p", "720p", "480p", "360p", "240p", "144p")
quality_dropdown.pack(pady=5)

Label(root, text="Download Type:").pack(pady=5)
type_var = StringVar(value="Video")
type_dropdown = ttk.Combobox(root, textvariable=type_var, state="readonly")
type_dropdown['values'] = ("Video", "Audio")
type_dropdown.pack(pady=5)

Button(root, text="Choose Download Folder", command=browse_folder).pack(pady=5)
path_label = Label(root, text=os.getcwd(), fg="blue")
path_label.pack()

Button(root, text="Start Download", command=start_download_thread, bg="green", fg="white").pack(pady=10)

# Progress Bar & Status
progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=10)

status_label = Label(root, text="Status: Waiting...", fg="black")
status_label.pack()

root.mainloop()
