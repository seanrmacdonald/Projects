## Summary
This python file utilizes API requests from Google, Yelp and Foursquare to give a list of the most popular areas
in a given area.

For the program to work, the user will need the following API keys / IDs saved as environmental variables


### Yelp API information
yelp client ID => save as 'YELP_ID' 
yelp api key => save as 'YELP_API_KEY' 
    
### Google API information
google api key => save as 'G_API_KEY' 

### Foursquare API information
foursquare id => save as 'FS_ID' 
foursquare secret => save as 'FS_SECRET' 

## Process
The program takes an input for the location.  The input can be text, lat/long, address, landmark, etc.  The input is run through the Google Places API to return a lat/long.

The next input is the search radius.  It is recommended to keep the radius under 5000 m for expediant results.

The lat/long and radius are then used as inputs in the Yelp and Foursquare API requests.  These return places of interest within the search radius and combines them into a single list.

Then utilizing the Google Maps API, the most efficient order to visit each location is given along with the total duration to drive from each location to the next.
