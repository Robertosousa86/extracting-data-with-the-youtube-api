from googleapiclient.discovery import build
from decouple import config
import pandas as pd

api_service_name = "youtube"
api_version = "v3"
api_key = config("API_KEY")

# Get credentials and create an API client
youtube = build(api_service_name, api_version, developerKey=api_key)

channels_ids = [
    "UCJQJAI7IjbLcpsjWdSzYz0Q",
    "UC1VZDEtGNxfQzh7EYcD2frg",
    "UC34RhwFiRdaXbWokrVPnmhw",
]


def get_channel_stats(youtube, channels_ids):
    all_data = []

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics", id=",".join(channels_ids)
    )

    response = request.execute()

    for item in response["items"]:
        data = {
            "channelName": item["snippet"]["title"],
            "channelDescription": item["snippet"]["publishedAt"],
            "subscribers": item["statistics"]["subscriberCount"],
            "totalVideos": item["statistics"]["videoCount"],
            "totalViews": item["statistics"]["viewCount"],
            "playlistId": item["contentDetails"]["relatedPlaylists"]["uploads"],
        }

        all_data.append(data)

    return pd.DataFrame(all_data)


def get_videos_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="contentDetails", playlistId=playlist_id, maxResults=50
    )
    response = request.execute()

    videos_ids = []

    for i in range(len(response["items"])):
        videos_ids.append(response["items"][i]["contentDetails"]["videoId"])

    next_page_token = response.get("nextPageToken")
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            response = request.execute()

            for i in range(len(response["items"])):
                videos_ids.append(response["items"][i]["contentDetails"]["videoId"])

                next_page_token = response.get("nextPageToken")
    return pd.DataFrame(videos_ids)


def get_comments_in_videos(youtube, videos_ids):
    all_comments = []

    for video_id in videos_ids:
        try:
            request = youtube.commentThreads().list(
                part="snippet, replies", videoId=video_id
            )
            response = request.execute()

            comments_in_video = [
                comment["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            ]

            for comment in response:
                comments_in_video_info = {
                    "video_id": video_id,
                    "comments": comments_in_video,
                }

                all_comments.append(comments_in_video_info)
        except:
            print("Could not get comments for video " + video_id)

    return pd.DataFrame(all_comments)
