from customtkinter import *
import yt_dlp
from CTkMessagebox import CTkMessagebox
import threading

def hook(d):
    if d['status'] == 'downloading':
        label.configure(text=f"{d['filename']} {d['_percent_str']}")
    elif d['status'] == 'finished':
        label.configure(text="Download complete!")

def fetch_formats_and_download(link, quality_selection):
    try:
        # Get video info to fetch available formats
        with yt_dlp.YoutubeDL({'noplaylist': True}) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            formats = info_dict.get('formats', [])
            
 
            available_qualities = {}
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4': # Prioritize mp4 for simplicity
                    quality_label = f'{f.get("format_note", f.get("format_id"))} - {f.get("resolution", "N/A")}'
                    available_qualities[quality_label] = f['format_id']
            
            if not available_qualities:
                CTkMessagebox(title="No MP4 Formats", message="No MP4 video formats found for this link.", icon="cancel")
                return


        if quality_selection == "Ask Me":

            quality_options = list(available_qualities.keys())
            quality_options.insert(0, "Select Quality") 
            

            quality_option_menu.configure(values=quality_options)
            quality_option_menu.set("Select Quality")
            
            CTkMessagebox(title="Select Quality", message="Please select your desired quality from the dropdown.", icon="info")
            return # Wait for the user to select from the dropdown
        
        # If a quality was selected (either from initial "best" or from the dropdown)
        selected_format_id = available_qualities.get(quality_selection, 'best[ext=mp4]') # Default to best mp4 if not found

        yt_opts = {
            'verbose': True,
            'format': selected_format_id,
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'progress_hooks': [hook]
        }
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.download(link)
            CTkMessagebox(title="Success", message="Download finished!", icon="check")
            label.configure(text="Download complete!")

    except yt_dlp.utils.DownloadError as e:
        CTkMessagebox(title="Download Error", message=f"Failed to download: {e}", icon="cancel")
        label.configure(text="Download failed.")
    except Exception as e: 
        CTkMessagebox(title="Error", message=f"An unexpected error occurred: {e}", icon="cancel")
        label.configure(text="Error occurred.")

def button_event():
    link = entry.get().strip()
    if not link:
        CTkMessagebox(title="Empty", message="The field is empty!", icon="cancel")
        return

    threading.Thread(target=fetch_formats_and_download, args=(link, quality_option_menu.get())).start()

def option_menu_callback(choice):
    link = entry.get().strip()
    if choice != "Select Quality" and link:
        threading.Thread(target=fetch_formats_and_download, args=(link, choice)).start()
    elif not link:
        CTkMessagebox(title="Empty", message="Please enter a video link first!", icon="cancel")
        quality_option_menu.set("Ask Me") # Reset if link is empty

app = CTk()
app.title('Youtube Video Downloader')
app.geometry("500x450px")

entry = CTkEntry(master=app, placeholder_text="Enter Your Youtube Video Link Here", width=300)
entry.place(relx=0.5, rely=0.4, anchor="center")
entry.bind("<Return>", lambda event: button_event()) # Use lambda to pass event


quality_options = ["Ask Me", "best"]
quality_option_menu = CTkOptionMenu(master=app, values=quality_options, command=option_menu_callback)
quality_option_menu.set("Ask Me") #
quality_option_menu.place(relx=0.5, rely=0.5, anchor="center")

button = CTkButton(app, text="Download Video", command=button_event)
button.place(relx=0.5, rely=0.6, anchor="center")

label = CTkLabel(master=app, text="Progress shown when downloading..")
label.place(relx=0.5, rely=0.7, anchor="center")

app.mainloop()