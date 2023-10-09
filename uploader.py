from tqdm import tqdm
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
import concurrent.futures

# Load the credentials from the downloaded JSON file
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    "secret.json",
    ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
)

#http://localhost:56889/?state=SzgUA0Ig7lO5VVPCnLWvk2RSfqD8Er&code=4/0AfJohXnGuJwKqMCaniY4yuwvU5Dzy2v8ekwueVo9embWrN2ZMaKfFJxUDi8LmPJE8ffaLw&scope=https://www.googleapis.com/auth/youtube.upload
# Run the OAuth 2.0 flow to obtain credentials
credentials = flow.run_local_server(port=0)

# Build the YouTube API client
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video(file_path, title):
    print("Starting video upload for:", title)

    body = {
        "snippet": {
            "title": title,
            "categoryId": "20"
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }
    media = MediaFileUpload(file_path, mimetype="video/x-matroska", resumable=True, chunksize=1 * 1024 * 1024)
    try:
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        file_size = media.size()
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Uploading {title}", ascii=True)

        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            progress_bar.update(media.chunksize())
        
        print("Upload completed for:", title)
        return response['id']
    except Exception as e:
        print(f"Error uploading {title}: {e}")
        return None


def add_to_playlist(video_id, playlist_id):
    playlist_item = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": video_id
            }
        }
    }
    youtube.playlistItems().insert(
        part=",".join(playlist_item.keys()),
        body=playlist_item
    ).execute()

letter_to_playlist_id = {
    "s": "PLiWT7_d-ANHX5lBx_Zpguzl-5zIajniCT", # solo dota
    "g": "PLiWT7_d-ANHWHbOekKG2xk5AoiDZNZWIl", # good content
    "d": "PLiWT7_d-ANHUSuENDcRIW5IFxl03wsa1v", # dota
    "t": "PLiWT7_d-ANHWBuVNRgMcP8LxgBTfMzyld", # trackmania
    "c": "PLiWT7_d-ANHWExcOXb_98FdtwWBwB8ZQe", # cs2
    "h": "PLiWT7_d-ANHWCx1BfNH2OsV15gynaexu4", # hades
}

letter_to_name = {
    "s": "solo dota", # solo dota
    "g": "good content", # good content
    "d": "czosnki vods", # dota
    "t": "trackmania", # trackmania
    "c": "cs2", # cs2
    "h": "hades", # hades
}


def upload_and_add_to_playlist(video_path):
    title = video_path.split("/")[-1].replace(".mkv", "")
    upload_title = (" ").join(title.split(" ")[1:])
    video_id = upload_video(video_path, upload_title)
    if len(title) >= 1:
        code = title.split(" ")[0]
        for letter in code:
            playlist_id = letter_to_playlist_id[letter]
            add_to_playlist(video_id, playlist_id)

    return upload_title

video_paths = ["D:/videos/d Jedna gra do divine 2023-09-11.mkv",
"D:/videos/sd tusk z snapfire nie wyszlo 2023-09-08.mkv",
"D:/videos/sd sutko gyro 2023-09-08.mkv",
"D:/videos/sd I wanted this game to eend 2023-09-08.mkv"]
    

#def callback(future):
#    result = future.result()  # This will get the return value of your function
#    print(f"Completed upload for: {result}")

#with concurrent.futures.ThreadPoolExecutor() as executor:
#    futures = [executor.submit(upload_and_add_to_playlist, video_path) for video_path in video_paths]
#    for future in futures:
#        future.add_done_callback(callback)

for pth in video_paths:
    upload_and_add_to_playlist(pth)

            
