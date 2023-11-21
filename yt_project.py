# Importing the necessary libraries
from googleapiclient.discovery import build
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import pymongo
import mysql.connector

# Building connection with youtube api
def api_connect():
    api_key = "AIzaSyCgzYhVkwLN_yEisqdXj2Iu14sL7786Srw"
    youtube = build("youtube", "v3", developerKey=api_key)
    return youtube

youtube = api_connect()


# Connection with mongodb atlas and creating a new database(youtube_data)
myclient = pymongo.MongoClient("mongodb+srv://kishore-0810:dbatlas123@cluster0.k3nng.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["youtube_data"]


# Connection with mysql database
my_database = mysql.connector.connect(host = "localhost",
                                      user = "root",
                                      password = "Kumar@08",
                                      database = "youtube_db")
my_cursor = my_database.cursor()


# Getting channel_details
def get_channel_info(channel_id):
    request = youtube.channels().list(part="snippet, contentDetails, statistics", id=channel_id)
    channel_data = request.execute()
    channel_details = {"Channel_Name": channel_data["items"][0]["snippet"].get("title"),
                       "Channel_Id": channel_data["items"][0].get("id"),
                       "Subscription_Count": channel_data["items"][0]["statistics"].get("subscriberCount"),
                       "Channel_Views": channel_data["items"][0]["statistics"].get("viewCount"),
                       "Channel_Description": channel_data["items"][0]["snippet"].get("description"),
                       "Playlist_Id": channel_data["items"][0]["contentDetails"]["relatedPlaylists"].get("uploads")
                       }
    return channel_details


# Getting video_ids
def get_video_ids(channel_id):
    request = youtube.channels().list(part="snippet, contentDetails, statistics", id=channel_id).execute()
    playlist_id = request["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(part="contentDetails, snippet", playlistId=playlist_id, maxResults=50,
                                               pageToken=next_page_token)
        playlistitems_data = request.execute()
        for item in playlistitems_data["items"]:
            video_ids.append(item["snippet"]["resourceId"]["videoId"])
        next_page_token = playlistitems_data.get("nextPageToken")
        if next_page_token is None:
            break
    return video_ids


# getting video_details
def get_video_info(video_ids):
    all_video_details = []
    for each_id in video_ids:
        video_id = each_id
        request = youtube.videos().list(part="snippet,contentDetails,statistics",
                                        id=video_id)
        video_data = request.execute()
        video_details = {"Video_Id": video_id,
                         "Video_Name": video_data["items"][0]["snippet"].get("title"),
                         "Video_Description": video_data["items"][0]["snippet"].get("description"),
                         "Tags": str(video_data["items"][0]["snippet"].get("tags")),
                         "PublishedAt": video_data["items"][0]["snippet"].get("publishedAt"),
                         "View_Count": video_data["items"][0]["statistics"].get("viewCount"),
                         "Like_Count": video_data["items"][0]["statistics"].get("likeCount","0"),
                         "Favorite_Count": video_data["items"][0]["statistics"].get("favoriteCount"),
                         "Comment_Count": video_data["items"][0]["statistics"].get("commentCount", "0"),
                         "Duration": video_data["items"][0]["contentDetails"].get("duration"),
                         "Thumbnail": video_data["items"][0]["snippet"]["thumbnails"]["default"].get("url"),
                         "Caption_Status": video_data["items"][0]["contentDetails"].get("caption")
                         }

        all_video_details.append(video_details)
    return all_video_details


# Getting comment_details
def get_comment_info(video_ids):
    all_comment_details = []

    for each_id in video_ids:
        try:
            video_id = each_id
            request = youtube.commentThreads().list(part="snippet,replies",
                                                videoId=video_id,
                                                maxResults=20)
            comment = request.execute()
            for item in comment["items"]:
                comment_details = {"Comment_Id": item["snippet"]["topLevelComment"].get("id"),
                               "Comment_Text": item["snippet"]["topLevelComment"]["snippet"].get("textDisplay"),
                               "Comment_Author": item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName"),
                               "Comment_PublishedAt": item["snippet"]["topLevelComment"]["snippet"].get("publishedAt")
                               }
                all_comment_details.append(comment_details)

        except:
            all_comment_details.append({})
    return all_comment_details


# Getting video_details with their respective comments_details
def get_video_and_comm_info(video_ids):
    all_video_details = {}
    for i, each_id in enumerate(video_ids, start=1):
        video_id = each_id
        request = youtube.videos().list(part="snippet,contentDetails,statistics",
                                        id=video_id)
        video_data = request.execute()
        video_details = {"Video_Id": video_id,
                         "Video_Name": video_data["items"][0]["snippet"].get("title"),
                         "Video_Description": video_data["items"][0]["snippet"].get("description"),
                         "Tags": str(video_data["items"][0]["snippet"].get("tags")),
                         "PublishedAt": video_data["items"][0]["snippet"].get("publishedAt"),
                         "View_Count": video_data["items"][0]["statistics"].get("viewCount"),
                         "Like_Count": video_data["items"][0]["statistics"].get("likeCount", "0"),
                         "Favorite_Count": video_data["items"][0]["statistics"].get("favoriteCount"),
                         "Comment_Count": video_data["items"][0]["statistics"].get("commentCount", "0"),
                         "Duration": video_data["items"][0]["contentDetails"].get("duration"),
                         "Thumbnail": video_data["items"][0]["snippet"]["thumbnails"]["default"].get("url"),
                         "Caption_Status": video_data["items"][0]["contentDetails"].get("caption"),
                         }

        all_comment_details = {}
        try:
            request = youtube.commentThreads().list(part="snippet,replies",
                                                    videoId=video_id,
                                                    maxResults=20)
            comment = request.execute()
            for j, item in enumerate(comment["items"], start=1):
                comment_details = {"Comment_Id": item["snippet"]["topLevelComment"].get("id"),
                                   "Comment_Text": item["snippet"]["topLevelComment"]["snippet"].get("textDisplay"),
                                   "Comment_Author": item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName"),
                                   "Comment_PublishedAt": item["snippet"]["topLevelComment"]["snippet"].get("publishedAt")
                                   }
                all_comment_details.update({f"comment_id_{j}": comment_details})
            video_details.update({"comments": all_comment_details})
            all_video_details.update({f"video_id_{i}": video_details})
        except:
            video_details.update({"comments": {}})
            all_video_details.update({f"video_id_{i}": video_details})

    return all_video_details


# Getting channel_details, video_details and comment_details altogether
@st.cache_data(show_spinner = False)
def channel_info(channel_id):
    ch_details = get_channel_info(channel_id)
    video_ids = get_video_ids(channel_id)
    vid_and_comm = get_video_and_comm_info(video_ids)
    channel_info = {"Channel_Name": ch_details}
    channel_info.update(vid_and_comm)
    return channel_info


# Upload into mongodb
def mongo_db_updation(channel_id):
    full_ch_details = channel_info(channel_id)
    mycoll = mydb["channel_details"]
    mycoll.insert_one({"full_channel_details": full_ch_details})
    return mycoll


# Retrieving channel_names and ids in mongodb collection
def channel_names_and_id():
    ch_names = []
    ch_id = []
    for i in mydb.channel_details.find():
        ch_names.append(i["full_channel_details"]["Channel_Name"]["Channel_Name"])
    for i in mydb.channel_details.find():
        ch_id.append(i["full_channel_details"]["Channel_Name"]["Channel_Id"])
    return ch_names, ch_id


# Table creation in  mysql database
def table_creation():
    query ='''CREATE TABLE if not exists channel( Channel_Name VARCHAR(255),
                                    Channel_Id VARCHAR(255) PRIMARY KEY,
                                    Subscription_Count INT,
                                    Channel_Views INT,
                                    Channel_Description TEXT,
                                    Playlist_Id VARCHAR(255)
                                    )'''
    my_cursor.execute(query)
    query = '''CREATE TABLE if not exists videos( Video_Id VARCHAR(255) primary key,
                                Channel_Id  VARCHAR(255) ,
                                Video_Name VARCHAR(255),
                                Video_Description TEXT,
                                Tags TEXT,
                                PublishedAt DATETIME,
                                View_Count INT,
                                Like_Count INT,
                                Favorite_Count INT,
                                Comment_Count INT,
                                Duration TIME,
                                Thumbnail VARCHAR(255),
                                Caption_Status VARCHAR(255),
                                foreign key(Channel_Id) references channel(Channel_Id)
                                )'''
    my_cursor.execute(query)
    query = '''CREATE TABLE if not exists comments(Comment_Id VARCHAR(255) primary key,
                                 Video_Id VARCHAR(255) , 
                                 Comment_Text TEXT,
                                 Comment_Author VARCHAR(255),
                                 Comment_PublishedAt DATETIME,
                                 foreign key(Video_Id) references videos(Video_Id)
                                 )'''
    my_cursor.execute(query)
    return "Tables created successfully"


# Inserting channel_details
def insert_into_channel(user_select):
    collection = mydb.channel_details
    for i in collection.find({'full_channel_details.Channel_Name.Channel_Name': user_select},{"_id" : 0}):
        ch_insert = i

    query ='''INSERT INTO channel( Channel_Name ,
                                   Channel_Id ,
                                   Subscription_Count ,
                                   Channel_Views ,
                                   Channel_Description ,
                                   Playlist_Id 
                                    ) 
                                    VALUES(%s, %s, %s, %s, %s, %s)'''
    tup = []
    for i in ch_insert["full_channel_details"]["Channel_Name"].values():
        tup.append(i)
    values = (tup[0],tup[1],tup[2],tup[3],tup[4],tup[5])
    my_cursor.execute(query, values)
    my_database.commit()
    return "inserted successfully"


# Inserting video_details
def insert_into_videos(user_select):
    collection = mydb.channel_details

    for i in collection.find({'full_channel_details.Channel_Name.Channel_Name': user_select},
                             {"_id": 0, "full_channel_details.Channel_Name.Channel_Id": 1}):
        Channel_Id = i['full_channel_details']['Channel_Name']['Channel_Id']

    for i in collection.find({'full_channel_details.Channel_Name.Channel_Name': user_select},
                             {"_id": 0, "full_channel_details.Channel_Name": 0}):
        vid_insert = i
    query = '''INSERT INTO videos( Video_Id,
                                      Channel_Id,
                                      Video_Name,
                                      Video_Description,
                                      Tags,
                                      PublishedAt,
                                      View_Count,
                                      Like_Count,
                                      Favorite_Count,
                                      Comment_Count,
                                      Duration,
                                      Thumbnail,
                                      Caption_Status
                                     ) 
                                    VALUES(%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)'''
    for i in vid_insert["full_channel_details"].values():
        i["PublishedAt"] = pd.to_datetime(i["PublishedAt"])
        i["Duration"] = parse_duration(i["Duration"])
        values = (i['Video_Id'],
                  Channel_Id,
                  i['Video_Name'],
                  i['Video_Description'],
                  i['Tags'],
                  i['PublishedAt'],
                  i['View_Count'],
                  i['Like_Count'],
                  i['Favorite_Count'],
                  i['Comment_Count'],
                  i['Duration'],
                  i['Thumbnail'],
                  i['Caption_Status'])
        my_cursor.execute(query, values)
        my_database.commit()
    return "inserted successfully"


# Inserting comment_details
def insert_into_comments(user_select):
    collection = mydb.channel_details
    for i in collection.find({'full_channel_details.Channel_Name.Channel_Name': user_select},
                             {"_id": 0, "full_channel_details.Channel_Name": 0}):
        comm_insert = i

    query = '''INSERT INTO comments( Comment_Id ,
                                    Video_Id,
                                    Comment_Text ,
                                    Comment_Author ,
                                    Comment_PublishedAt 
                                     )
                                VALUES(%s, %s, %s, %s, %s)'''

    for i in comm_insert["full_channel_details"].values():
        Video_Id = i["Video_Id"]
        for item in i["comments"].values():
            item["Comment_PublishedAt"] = pd.to_datetime(item.get("Comment_PublishedAt"))
            values = (
            item['Comment_Id'], Video_Id, item['Comment_Text'], item['Comment_Author'], item['Comment_PublishedAt'])
            my_cursor.execute(query, values)
            my_database.commit()
    return "inserted successfully"


# Transforming duration column in video_details to this format(hours:minutes:seconds)
def parse_duration(duration):
    duration_str = ""
    hours = 0
    minutes = 0
    seconds = 0

    # Remove 'PT' prefix from duration
    duration = duration[2:]

    # Check if hours, minutes, and/or seconds are present in the duration string
    if "H" in duration:
        hours_index = duration.index("H")
        hours = int(duration[:hours_index])
        duration = duration[hours_index + 1:]
    if "M" in duration:
        minutes_index = duration.index("M")
        minutes = int(duration[:minutes_index])
        duration = duration[minutes_index + 1:]
    if "S" in duration:
        seconds_index = duration.index("S")
        seconds = int(duration[:seconds_index])

    # Format the duration string
    if hours > 0 and hours < 10:
        duration_str += f"0{hours}:"
    elif hours >= 10:
        duration_str += f"{hours}:"
    else:
        duration_str += "00:"

    if minutes > 0 and minutes < 10:
        duration_str += f"0{minutes}:"
    elif minutes >= 10:
        duration_str += f"{minutes}:"
    else:
        duration_str += "00:"

    if seconds > 0 and seconds < 10:
        duration_str += f"0{seconds}"
    elif seconds >= 10:
        duration_str += f"{seconds}"
    else:
        duration_str += "00"

    return duration_str


# Streamlit setup
st.set_page_config(page_title='YouTube Project By kishore',layout="wide")

with st.sidebar:
    selected = option_menu(menu_title = None,
                           options = ['Menu',"Data Extraction And Mongodb Upload",'Data Migration To Sql','Data Analysis'],
                           icons = ['house-door-fill','tools','database-fill-up','pie-chart-fill'],
                           default_index = 0,
                           styles = {"nav-link": {"font-size": "18px", "text-align": "left", "margin": "2px" },
                                     "icon": {"color" : "orange", "font-size": "20px"},
                                     "nav-link-selected": {"background-color": "#0000FF"}}
                           )


# Menu page
if selected == 'Menu':
    st.title(':red[YouTube Data Harvesting and Warehousing]')
    st.markdown("In This  Project we would get YouTube Channel data from YouTube API with the help of 'Channel ID', We Will Store the channel data into Mongo DB Atlas as a Document then would migrate the data into Sql Records for Data Analysis")


# Data Extraction And Mongodb Upload page
if selected == "Data Extraction And Mongodb Upload":

    channel_id = st.text_input(":blue[ENTER A YOUTUBE CHANNEL ID]")

    if st.button("submit"):

        if len(channel_id) == 24:
            x = channel_info(channel_id)
            latest_iteration = st.empty()
            bar = st.progress(0)
            for i in range(100):
                latest_iteration.text(f'loading {i + 1}%')
                bar.progress(i + 1)
                time.sleep(0.1)
            latest_iteration.empty()
            bar.empty()
            if st.checkbox("Show Data", value = True):
                st.json(x["Channel_Name"])
                st.json(x["video_id_1"])
                st.json(x["video_id_2"])
        else:
            st.error("ERROR: INVALID CHANNEL ID")

    if st.button("Store In Mongodb"):
        ch_names, ch_id = channel_names_and_id()

        if len(channel_id) == 24:
            if channel_id in ch_id:
                st.error(":red[Error: The Given Channel_Id Already Exists]")
            else:
                mongodb_updation = mongo_db_updation(channel_id)
                with st.spinner('Uploading...'):
                    time.sleep(5)
                s = st.success("Uploaded Successfully", icon = "✅")
                time.sleep(10)
                s.empty()
        else:
            st.error("ERROR: INVALID CHANNEL ID")

# Data Migration To Sql page
if selected == "Data Migration To Sql":
    ch_names, ch_id = channel_names_and_id()
    st.markdown(":blue[SELECT A CHANNEL TO BEGIN TRANSFORMATION TO MYSQL]")
    user_select = st.selectbox(":red[select]", options = ch_names)

    if st.button("submit"):
        table = table_creation()
        query = '''select Channel_Name from channel'''
        my_cursor.execute(query)
        names = [i[0] for i in my_cursor.fetchall()]

        if user_select in names:
            st.error(f":red[ERROR]: channel details for ':red[{user_select}]' are already inserted in mysql")
        else:
            insert_into_channel(user_select)
            insert_into_videos(user_select)
            insert_into_comments(user_select)
            with st.spinner('Uploading...'):
                time.sleep(5)
            st.success(f"Data Migration To Sql for channel ':green[{user_select}]' Has Been Successfull", icon = "✅")


# Data Analysis page
if selected == "Data Analysis":

    queries = ["1.What are the Names of all the videos and their corresponding channels?",
               "2.Which channels have the most number of videos, and how many videos do they have?",
               "3.What are the top 10 most viewed videos and their respective channels ?",
               "4.How many comments were made on each video, and what are their corresponding video names?",
               "5.Which videos have the highest number of likes, and what are their corresponding channel names?",
               "6.What is the total number of likes for each video, and what are  their corresponding video names?",
               "7.What is the total number of views for each channel, and what are their corresponding channel names?",
               "8.What are the names of all the channels that have published videos in the year 2022?",
               "9.What is the average duration of all videos in each channel, and what are their corresponding channel names?",
               "10.Which videos have the highest number of comments, and what are their corresponding channel names?"]

    st.markdown(":blue[SELECT THE QUESTIONS GIVEN BELOW FOR ANALYSIS]")
    user = st.selectbox(":red[Select]", options = queries)
    st.markdown(":green[Solution:]")

    if user == "1.What are the Names of all the videos and their corresponding channels?":
        query_1 = '''SELECT videos.Video_Name, channel.Channel_Name
                     FROM videos INNER JOIN channel 
                     ON videos.Channel_Id = channel.Channel_Id'''
        my_cursor.execute(query_1)
        data_1 = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data_1, columns=my_cursor.column_names, index=range(1, len(data_1) + 1)))

    elif user == "2.Which channels have the most number of videos, and how many videos do they have?":
        query_2 = '''SELECT channel.Channel_Name, COUNT(videos.Video_Id) AS video_count
                     FROM channel
                     INNER JOIN videos ON channel.Channel_Id = videos.Channel_Id
                     GROUP BY channel.Channel_Id
                     ORDER BY video_count DESC'''
        my_cursor.execute(query_2)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))

    elif user == "3.What are the top 10 most viewed videos and their respective channels ?":
        query_3 = '''SELECT videos.Video_Name, channel.Channel_Name, videos.View_Count
                     FROM videos
                     INNER JOIN channel ON videos.Channel_Id = channel.Channel_Id
                     ORDER BY videos.View_Count DESC
                     LIMIT 10'''
        my_cursor.execute(query_3)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))

    elif user == "4.How many comments were made on each video, and what are their corresponding video names?":
        query_4 = '''SELECT videos.Video_Name, videos.Comment_Count 
                     FROM videos
                     ORDER BY videos.Comment_Count DESC'''
        my_cursor.execute(query_4)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))

    elif user == "5.Which videos have the highest number of likes, and what are their corresponding channel names?":
        query_5 = '''SELECT videos.Video_Name, channel.Channel_Name, videos.Like_Count
                     FROM videos
                     INNER JOIN channel ON videos.Channel_Id = channel.Channel_Id
                     ORDER BY videos.Like_Count DESC'''
        my_cursor.execute(query_5)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))

    elif user == "6.What is the total number of likes for each video, and what are  their corresponding video names?":
        query_6 = '''SELECT videos.Video_Name, SUM(videos.Like_Count) AS total_likes
                     FROM videos
                     GROUP BY videos.Video_Id'''
        my_cursor.execute(query_6)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))

    elif user == "7.What is the total number of views for each channel, and what are their corresponding channel names?":
        query_7 = '''SELECT Channel_Name, Channel_Views
                     FROM channel'''
        my_cursor.execute(query_7)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))

    elif user == "8.What are the names of all the channels that have published videos in the year 2022?":
        query_8 = '''SELECT DISTINCT channel.Channel_Name
                    FROM channel
                    INNER JOIN videos ON channel.Channel_Id = videos.Channel_Id
                    WHERE YEAR(videos.PublishedAt) = 2022'''
        my_cursor.execute(query_8)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))

    elif user == "9.What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        query_9 = '''SELECT channel.Channel_Name, AVG(TIME_TO_SEC(videos.Duration)) AS avg_duration
                     FROM channel
                     INNER JOIN videos ON channel.Channel_Id = videos.Channel_Id
                     GROUP BY channel.Channel_Id'''
        my_cursor.execute(query_9)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))

    elif user == "10.Which videos have the highest number of comments, and what are their corresponding channel names?":
        query_10 = '''SELECT videos.Video_Name, channel.Channel_Name,  videos.Comment_Count
                      FROM videos
                      INNER JOIN channel ON videos.Channel_Id = channel.Channel_Id
                      GROUP BY videos.Video_Id
                      ORDER BY videos.Comment_Count DESC'''
        my_cursor.execute(query_10)
        data = [i for i in my_cursor.fetchall()]
        st.write(pd.DataFrame(data, columns=my_cursor.column_names, index=range(1, len(data) + 1)))


# ----------------------x---------------------------x----------------------------x----------------------------x----------------------------








