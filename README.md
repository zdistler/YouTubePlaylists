Summary:
  This project adds new videos from YouTube channels to specified playlists. 
  For each 'Subscription' to a channel, one playlist is assigned and three different restriction types can be applied.
  Restrictions can be based on video titles, either to include or exclude videos with certain text in the title, or by the day of the week the video was published.
  
Functions:

  Add:
    Creates a new Subscription by specifying a YouTube channel by its username, choosing what playlist to add videos to, 
    and include any restrictions specific to that channel. 
    Entering a channel username will return the first option from a search result where the user selects whether it is the channel they intended.
    Selecting 'N' will prompt the user to enter a channel username again. Selecting 'Y' will continue with the Subscription setup. 
    The playlist is now chosen by entering its name. The playlist name needs to be exact except for capitalization. Restrictions can now be added.
    Restrictions are specified in three ways:
      Placing '!' in front of text to exclude videos with that text in the title.
      Placing 'date:' in front of a day of the week to include videos published on that day.
      All others are included videos with that text in the title.
    Restrictions are separated by commas.
    
  Remove:
    Removes a specified Subscription by providing the channel username. The username must be exact except for capitalization.
    
  Display:
    Displays all Subscriptions with their associated playlist and restrictions in a table. 
    
  Playlists:
    Displays all user created playlists in a table.
    
  Run:
    Finds videos from channels within a specified date range to add to playlists. 
    The date range is specified by selecting a 'back' number referring to the number of days back from today to start and a 'til' number for days back to end.
    For example: if the date is 4/16, setting 'back' to 3 and 'til' to 0 will provide videos from a date range of 4/13 through 4/16 both at 12:00 AM local time.
    Videos are then compared to the Subscription's restrictions. Restrictions are assessed in this order: 'exclude', 'date', 'include'. 
    If there are no 'date' or 'include' restrictions then all videos not removed by an 'exclude' restriction will be added to the Subscription's playlist.
  
  Stop:
    Stops the program and saves the current state of the Subscriptions.
