import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from datetime import timedelta
import datetime
import pickle
from prettytable import PrettyTable
from Video import Video
from Playlist import Playlist
from Subscription import Subscription

# Files used to store client secret information, serialized subscriptions, and last run date
clientSecretsFile = "ClientSecret.json"
subscriptionsFile = "Subscriptions.txt"
lastUsedFile = "LastUsed.txt"

# Scopes used by app
scopes = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.force-ssl"]

# API service name and version
apiServiceName = "youtube"
apiVersion = "v3"

# Global variables
global youtube
playlists = []
subscriptions = []

# Authenticate Google account
def getAuthenticatedService():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        clientSecretsFile, scopes)
    flow.run_local_server(port = 8080,prompt = "consent")
    
    global youtube
    youtube = googleapiclient.discovery.build(
        apiServiceName, apiVersion, credentials = flow.credentials)

# Get all user created playlists
def findPlaylists():
    request = youtube.playlists().list(
            part="snippet",
            mine="true",
            maxResults = 200
            )

    response = request.execute()
    for item in response["items"]:
        title = item["snippet"]["title"]
        id = item["id"]
        playlists.append(Playlist(title, id))

    playlists.sort(key = playlistSorting)

# Sort playlists
def playlistSorting(playlist):
    return playlist.title.lower()

# Sort subscriptions
def subscriptionSorting(subscription):
    return subscription.username.lower()

# Get saved subscriptions from Subscriptions.txt file
def openSubscriptions():
    if os.stat(subscriptionsFile).st_size == 0:
        return
    with open(subscriptionsFile, "rb") as file:
        subscriptions.extend(pickle.load(file))

# Search for YouTube Channel and return their username and id
def channelVerification(channel):
    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=channel,
        type="channel"
    )
    response = request.execute()
    responseChannel = response["items"][0]
    channelId = responseChannel["id"]["channelId"]
    username = responseChannel["snippet"]["channelTitle"]

    print(username, channelId)
    
    return channelId, username

# User verification question
def getAnswer():
    answer = input("Is This Correct (Y/N): ")
    if answer.upper() == "Y":
        return True
    elif answer.upper() == "N":
        return False
    else:
        return getAnswer()

# Add a new subscription or add more restrictions to an existing subscription
def add():
    isChannelCorrect = False

    while isChannelCorrect == False:
        username = input("Channel Username (Enter cancel to leave): ")
        if username == "cancel":
            return False
        channelID, username = channelVerification(username)
        isChannelCorrect = getAnswer()

    for subscription in subscriptions:
        if subscription.username.lower() == username.lower():
            restrictions = subscription.addMoreRestrictions()
            if not restrictions:
                return False
            subscription.restrictions = restrictions
            return True

        if subscription.username.lower() > username.lower():
            break

    return addNewSubscription(username, channelID)

# Creates a new subscription 
def addNewSubscription(username, channelID):
    playlist = choosePlaylist()
    if not playlist:
        return False
    subscription = Subscription(username, channelID, playlist)
    restrictions = subscription.addRestrictions()
    if not restrictions:
        return False
    subscriptions.append(subscription)
    return True

# Specify a playlist to associate with a subscription
def choosePlaylist():
    chosenPlaylist = input("Playlist (Enter cancel to leave): ")
    if chosenPlaylist.lower() == "cancel":
        return False
    for playlist in playlists:
        if playlist.title.lower() == chosenPlaylist.lower():
            print("found playlist", playlist.title)
            return playlist
        if playlist.title.lower() > chosenPlaylist.lower():
            return choosePlaylist()

# Remove a subscription
def remove():
    channel = input("Enter Channel Username to remove (cancel to leave): ")
    if channel.lower() != "cancel":
        for subscription in subscriptions:
            if subscription.username.lower() > channel.lower():
                break
            if subscription.username.lower() == channel.lower():
                subscriptions.remove(subscription)
                print(channel, "removed")
                return
        print("No Subscription for that Channel")
        remove()

# Close the app and saves subscriptions
def stop():
        with open("Subscriptions.txt", "wb") as write:
            pickle.dump(subscriptions, write)

# Display all subscriptions with their associated playlist and restrictions in a table
def display():
    myTable = PrettyTable(["Channel", "Playlist", "Restrictions"])

    for subscription in subscriptions:
        restrictions = subscription.listRestrictions()

        myTable.add_row([subscription.username, subscription.playlist.title, restrictions[0]])
        if len(subscription.restrictions) > 1:
            for i in range(1, len(restrictions)):
                myTable.add_row(["", "", restrictions[i]])
    
    print(myTable)
    print("Total:",len(subscriptions))

# Displays all Playlists the user created
def listPlaylists():
    myTable = PrettyTable(["Playlist"])

    for playlist in playlists:
        myTable.add_row([playlist.title])
    print(myTable)

# Returns all activity from the specified channel within the specified timeframe
def activitiesRequest(backTime, tilTime, channelID, nextPageToken):
    request = youtube.activities().list(
        part="snippet,contentDetails",
        channelId=channelID,
        publishedAfter=backTime,
        publishedBefore=tilTime,
        pageToken=nextPageToken,
        maxResults=50
    )

    return request.execute()

# Searches for videos from subscriptions then adds them to subscription specific playlists
# depending on if the videos meet the restriction requirements
def run():
    total = 0
    back = None
    til = None
    
    with open(lastUsedFile, "r") as file:
        lastUsed = file.readline()

    print(lastUsed)

    while back == None:
        back = input("Enter days back (cancel to leave): ")
        if back.isnumeric() == True:
            back = int(back)
        elif back.lower() == "cancel":
            return "cancel"
        else:
            back = None
    while til == None:
        til = input("Enter days til (cancel to leave): ")
        if til.isnumeric() == True:
            til = int(til)
            if til >= back:
                print("Days til needs to be smaller than days back")
                til = None
        elif til.lower() == "cancel":
            return "cancel"
        else:
            til = None

    backTime = (datetime.datetime.now() - timedelta(days = back)).astimezone().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    tilTime = (datetime.datetime.now() - timedelta(days = til)).astimezone().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    for subscription in subscriptions:
        videos = []
        videosToAdd = []
        nextPage = True
        nextPageToken = None
        items = []

        while nextPage == True:
            response = activitiesRequest(backTime, tilTime, subscription.channelID, nextPageToken)
            items += response["items"]
            if "nextPageToken" in response.keys():
                nextPageToken = response["nextPageToken"]
            else:
                nextPage = False

        for item in items:
            if item["snippet"]["type"] != "upload":
                continue

            videoId = item["contentDetails"]["upload"]["videoId"]
            videoTitle = item["snippet"]["title"]
            videoDay = datetime.datetime.fromisoformat(item["snippet"]["publishedAt"]).weekday()
            videos.append(Video(videoId, videoTitle, videoDay))

        for video in videos:
            include = True

            for restriction in subscription.restrictions["exclude"]:
                if restriction.lower() in video.title.lower():
                    include = False
                    break

            if include == False:
                continue

            include = False
            
            for restriction in subscription.restrictions["date"]:
                if restriction == video.day:
                    include = True
                    break

            if include == True:
                videosToAdd.append(video)
                continue
            
            if len(subscription.restrictions["include"]) > 0:
                for restriction in subscription.restrictions["include"]:
                    if restriction.lower() in video.title.lower():
                        include = True
                        break
                
                if include == True:
                    videosToAdd.append(video)
            else:
                videosToAdd.append(video)

        for video in videosToAdd:
            print("    ", subscription.username, "|", video.title)
            addToPlaylist(video.id, subscription.playlist.id)

        total += len(videosToAdd)
            
    with open(lastUsedFile, 'w') as file:
        print(datetime.datetime.now().date() - timedelta(days = til), file = file)
        
    print(total)

    return True

# Adds a video to a playlist
def addToPlaylist(videoId, playlistId):
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=0,
        playlistId=playlistId
    )
    response = request.execute()
        
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": playlistId,
            "position": response["pageInfo"]["totalResults"],
            "resourceId": {
              "kind": "youtube#video",
              "videoId": videoId
            }
          }
        }
    )
    request.execute()

# Allows the user to select from options including add (add a new subscription), 
# remove (remove a subscription), display (display subscriptions with their playlists and restrictions),
# playlists (displays all user created playlists), 
# run (execute the search and adding of videos to playlists), stop (stop the app and save subscriptions)
def options():
    print("\noptions: add, remove, display, playlists, run, stop")
    selection = input("Selection: ").lower().strip()
    if selection == "add":
        sub = True
        while sub == True:
            sub = add()
            subscriptions.sort(key = subscriptionSorting)
        options()
    elif selection == "remove":
        remove()
        options()
    elif selection == "display":
        display()
        options()
    elif selection == "playlists":
        listPlaylists()
        options()
    elif selection == "run":
        result = run()
        if result == "cancel":
            options()
        else:
            stop()
    elif selection == "stop":
        stop()
    else:
        options()

if __name__ == '__main__':
    getAuthenticatedService()
    findPlaylists()
    openSubscriptions()
    options()