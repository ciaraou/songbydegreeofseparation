import requests
import json
import time

TOKEN_URL = 'https://accounts.spotify.com/api/token'
SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search'
TR_ENDPOINT = 'https://api.spotify.com/v1/tracks/'
AR_ENDPOINT = 'https://api.spotify.com/v1/artists/'
REC_ENDPOINT = 'https://api.spotify.com/v1/recommendations'
TRF_ENDPOINT = 'https://api.spotify.com/v1/audio-features/'
#add id and secret here
CLI_ID = ''
CLI_SECRET = ''

#keep track of end track genres (based on artist via spotify)
endtr_genres = []
endtr_features = {}

#auth
payload = {'Content-Type': 'application/x-www-form-urlencoded',
        'grant_type': 'client_credentials',}

r = (requests.post(TOKEN_URL, auth=(CLI_ID, CLI_SECRET), data=payload)).json()
access_token = r.get('access_token')

# STDIN START AND END SONG
start_tr = "Maze of Memories"
et = "Feel Special"
# start_tr = raw_input("start song: ")
# et = raw_input("end song: ")
# start_tr_a = input("start song's artist: ")

# FIND URI OF START TRACK
q = {'q': start_tr, 'type': 'track'}
headers = {
    'Authorization': "Bearer "+access_token,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    }
r = (requests.get(SEARCH_ENDPOINT, params=q, headers=headers)).json()
prev_track = r.get('tracks').get('items')[0].get('uri') #change 0 in case of multiple songs

# FIND URI OF END TRACK
q = {'q': et, 'type': 'track'}
r = (requests.get(SEARCH_ENDPOINT, params=q, headers=headers)).json()
endtrack = r.get('tracks').get('items')[0].get('uri') #change 0 in case of multiple songs

# GET FEATURES OF END TRACK
r = (requests.get(TRF_ENDPOINT+endtrack[14:], headers=headers)).json()
# for feat in r:
#     endtr_features[feat] = r[feat]
endtr_features['target_valence'] = r['valence']
endtr_features['target_loudness'] = r['loudness']
endtr_features['target_energy'] = r['energy']
endtr_features['target_danceability'] = r['danceability']
endtr_features['target_acousticness'] = r['acousticness']

# for endtr_artists in r.get('tracks').get('items')[0].get('album').get('artists'):
#     artist_obj = (requests.get(AR_ENDPOINT+(endtr_artists.get('id')), headers=headers)).json()
#     endtr_genres = artist_obj.get('genres')


#generate playlist.
# limits aren't cheating because theoretically you could keep looking through
#      songs for some infinite amount, it just isn't possible in a program.
def gen_pl(prev_track): #TODO gen track with attributes valence, loudness, energy, danceability, acousticness.
    query = {'seed_tracks': prev_track[14:], } #limit param, tuneable track attributees, TODO add option to changee
    query.update(endtr_features)
    print(query)

    r = (requests.get(REC_ENDPOINT, params=query, headers=headers)).json()
    return r.get('tracks')

#print track info: link, track name, and song
def print_track_info(tr):
    print(TR_ENDPOINT+tr[14:])
    r = (requests.get(TR_ENDPOINT+tr[14:], headers=headers)).json()
    print("artist: " + r.get('album').get('artists')[0].get('name'))
    print("song: " + r.get('name'))
    re = (requests.get(TRF_ENDPOINT+tr[14:], headers=headers)).json()
    print(re)
    return r.get('name') + " by " + r.get('album').get('artists')[0].get('name')

#bredth first search
def bfs():
    visited = []
    queue = []
    parent = {}

    visited.append(prev_track)
    queue.append((prev_track, 0))
    parent[prev_track] = -1

    while queue:
        print("NEW!")
        pt = queue.pop(0)
        if pt[0] == endtrack:
            break;

        r = gen_pl(pt[0])
        rr = []
        for i in r:
            rr.append(i.get('uri'))

        for i in rr:
            if i not in visited:        #prioritize queue, based on genre etc
                print_track_info(i)
                reqres = (requests.get(TR_ENDPOINT+i[14:], headers=headers)).json()
                # for reqres_artists in reqres.get('album').get('artists'):
                #     artist_obj = (requests.get(AR_ENDPOINT+reqres_artists.get('id'), headers=headers)).json()
                    # if not set(endtr_genres).isdisjoint(artist_obj.get('genres')):
                    #     queue.append((i,pt[1]+1))
                    #     parent[i] = pt[0]

                #get artist id from pt[0]
                #get artist info, check genre list, if no genres match then discard
                #numerical prioritization? make a struct?
                queue.append((i,pt[1]+1))
                parent[i] = pt[0]
                visited.append(i)

    path = [endtrack]
    curr = endtrack
    while parent[curr] != -1:
        path.insert(0, parent[curr])
        curr = parent[curr]
    for i in path:
        print_track_info(i)
    print("It took " + str(len(path)) + " songs to get from " + start_tr + " to " + et)

start = time.time()
bfs()
end = time.time()
print(end)
print(start)
print(end-start)
