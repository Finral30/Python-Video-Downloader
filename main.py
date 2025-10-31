from pytube import YouTube

try:
    url = "https://www.youtube.com/watch?v=xIkTWaOpiRQ"
    yt = YouTube(url)
    
    print(f"Title: {yt.title}")
    print("Downloading...")

    video = yt.streams.get_highest_resolution()
    video.download()

    print("Download completed!")

except Exception as e:
    print("An error occurred:", e)
