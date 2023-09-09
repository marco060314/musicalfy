import spotipy
import base64
import pandas as pd
import requests
import matplotlib.pyplot as plt
import html
#import mpld3
#from mpld3 import plugins
#from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.preprocessing import MinMaxScaler
import math
from io import BytesIO
#import chart_studio.plotly as py
from flask import Flask, render_template, redirect, request,session
app = Flask(__name__)

app.secret_key = '02ac351eecbc4a83982e1309d0c9e683'
username = ''
scope = 'user-read-recently-played, user-top-read'
redirect_uri = "https://marcow125.pythonanywhere.com/api_callback"
API_BASE = 'https://accounts.spotify.com'
client_id = 'f5ee56f23f5d4bb5b2d579703a097ae1'
client_secret = '02ac351eecbc4a83982e1309d0c9e683'
SHOW_DIALOG = True

@app.route("/",methods=['POST', 'GET'])
def check():
    try:
        global logo
        print(logo)
    except:
        logo = 0
    print("LOGO STATUS: LOGO: ", logo)
    #try:

    #    token = session["toke"]
    #except:
    #    logo = 0

    if (logo == 0):
        return render_template("home.html", loggedin = 0)
    if (logo == 1):

        token = session["toke"]
        sp = spotipy.Spotify(auth=token)
        def get_streamings() -> dict:
            sp = spotipy.Spotify(auth=token)
            features = sp.current_user_recently_played()
            return features

        def get_features(id) -> dict:
            sp = spotipy.Spotify(auth=token)
            features = sp.audio_features(id)
            return features
        def lstring(m):
            s = ""
            for x in m:
                s+=x
                s+=", "
            s=s[:-2]
            return s

        def display_plot(music_feature, title):
            fig=plt.figure(figsize=(8,6))
            categories=list(music_feature.columns)
            N=len(categories)
            value=list(music_feature.mean())
            value+=value[:1]
            angles=[n/float(N)*2*math.pi for n in range(N)]
            angles+=angles[:1]
            plt.polar(angles, value)
            plt.fill(angles,value,alpha=0.3)
            plt.title(title, size=20)
            plt.xticks(angles[:-1],categories, size=10)
            plt.yticks(color='grey',size=7)
            #plt.show()
            tmpfile = BytesIO()
            fig.savefig(tmpfile, format='png')
            check = base64.b64encode(tmpfile.getvalue())
            encoded = check.decode('utf-8')
            return encoded

        def get_similarity(similarity, counter, t, df, df1):
            top_genre = []
            if counter == 1:
                for x in df[similarity]:
                    for i in x:
                        top_genre.append(i)

                recent_genre = []
                for x in df1[similarity]:
                    for i in x:
                        recent_genre.append(i)
            else:
                for x in df[similarity]:
                    top_genre.append(x)

                recent_genre = []
                for x in df1[similarity]:
                    recent_genre.append(x)

            top_count = []
            for x in top_genre:
                counter = 0
                for i in range(len(top_count)):
                    if x == top_count[i][0]:
                        top_count[i][1] += 1
                        counter = 1
                if counter == 0:
                    top_count.append([x,1])
            top_count.sort(key=lambda x : x[1])
            top_count.reverse()

            recent_count = []
            for x in recent_genre:
                counter = 0
                for i in range(len(recent_count)):
                    if x == recent_count[i][0]:
                        recent_count[i][1] += 1
                        counter = 1
                if counter == 0:
                    recent_count.append([x,1])
            recent_count.sort(key=lambda x : x[1])
            recent_count.reverse()
            ans = []
            for x in range(1,len(top_count)):
                for i in range(1,len(recent_count)):
                    if top_count[x][0] == recent_count[i][0]:
                        ans.append(top_count[x][0])
            return ans

        def get_unique(unique, counter, t):
            top_genre = []
            if counter == 1:
                for x in df[unique]:
                    for i in x:
                        top_genre.append(i)

                recent_genre = []
                for x in df1[unique]:
                    for i in x:
                        recent_genre.append(i)
            else:
                for x in df[unique]:
                    top_genre.append(x)

                recent_genre = []
                for x in df1[unique]:
                    recent_genre.append(x)

            top_count = []
            for x in top_genre:
                counter = 0
                for i in range(len(top_count)):
                    if x == top_count[i][0]:
                        top_count[i][1] += 1
                        counter = 1
                if counter == 0:
                    top_count.append([x,1])
            top_count.sort(key=lambda x : x[1])
            top_count.reverse()

            recent_count = []
            for x in recent_genre:
                counter = 0
                for i in range(len(recent_count)):
                    if x == recent_count[i][0]:
                        recent_count[i][1] += 1
                        counter = 1
                if counter == 0:
                    recent_count.append([x,1])
            recent_count.sort(key=lambda x : x[1])
            recent_count.reverse()
            ans = []
            for x in range(1,t):
                if not any(recent_count[x][0] in sublist for sublist in top_count):
                    ans.append(recent_count[x][0])
            return ans

        streams = get_streamings()
        data1 = []
        ids = []

        for x in streams['items']:
            album = sp.album(x['track']["album"]["external_urls"]["spotify"])
            artist = sp.artist(x['track']['artists'][0]['external_urls']['spotify'])
            ids.append(x['track']['id'])

            if len(album['genres']) == 0:
                data1.append([x['track']['album']['artists'][0]['name'],
                            x['track']['album']['name'],
                            x['track']['name'],
                            x['track']['duration_ms'],
                            artist['genres'],
                            x['track']['popularity'],
                            ids[-1]])
            else:
                data1.append([x['track']['album']['artists'][0]['name'],
                            x['track']['album']['name'],
                            x['track']['name'],
                            x['track']['duration_ms'],
                            album['genres'],
                            x['track']['popularity'],
                            ids[-1]])

        song_met={'title':[],'album':[], 'artist':[], 'genre':[],
                'duration':[], 'pop':[], 'id':[]}

        song_meta={'id':[]}

        for song_id in ids:
            song_meta['id'].append(song_id)


        # check the song feature
        features = sp.audio_features(song_meta['id'])
        # change dictionary to dataframe
        features_df=pd.DataFrame.from_dict(features)

        # convert milliseconds to mins
        # duration_ms: The duration of the track in milliseconds.
        # 1 minute = 60 seconds = 60 × 1000 milliseconds = 60,000 ms
        genre2 = [[]]

        for x in range(len(data1)):
            song_met['artist'].append(data1[x][0])
            song_met['genre'].append(lstring(data1[x][4]))
            genre2[0].append(data1[x][4])
            song_met['album'].append(data1[x][1])
            song_met['title'].append(data1[x][2])
            song_met['duration'].append(round(data1[x][3]/60000,2))
            song_met['pop'].append(data1[x][5])
            song_met['id'].append('http://open.spotify.com/track/'+data1[x][6])



        df1 = pd.DataFrame.from_dict(song_met)

        features = sp.audio_features(song_meta['id'])

        features_df=pd.DataFrame.from_dict(features)


        music_feature = features_df[['danceability','energy', 'loudness', 'acousticness',
                'instrumentalness','liveness', 'valence', 'tempo']]
        min_max_scaler = MinMaxScaler()
        music_feature.loc[:]=min_max_scaler.fit_transform(music_feature.loc[:])
        #music_feature = np.array(music_feature)
        #graph = display_plot(music_feature, "title")
        #return render_template('home.html',  tables=[music_feature.to_html(classes='data')], titles=df1.columns.values)
        #return display_plot(music_feature, "title")

        def get_moststreams(time) -> dict:
            sp = spotipy.Spotify(auth=token)
            try:
                features = sp.current_user_top_tracks(time_range=time)
                return features
            except:
                return None

        streams = get_moststreams("long_term")
        data = []
        ids = []
        for x in streams['items']:
            album = sp.album(x["album"]["external_urls"]["spotify"])
            artist = sp.artist(x['artists'][0]['external_urls']['spotify'])
            ids.append(x['id'])
            if len(album['genres']) == 0:
                data.append([x['album']['artists'][0]['name'],
                            x['album']['name'],
                            x['name'],
                            x['duration_ms'],
                            artist['genres'],
                            x['popularity'],
                            ids[-1]])
            else:
                data.append([x['album']['artists'][0]['name'],
                            x['album']['name'],
                            x['name'],
                            x['duration_ms'],
                            album['genres'],
                            x['popularity'],
                            ids[-1]])

        song_met1={'title':[],'album':[], 'artist':[], 'genre':[],
                'duration':[], 'pop':[], 'id':[]}

        song_meta={'id':[]}

        for song_id in ids:
            song_meta['id'].append(song_id)
        features = sp.audio_features(song_meta['id'])
        features_df=pd.DataFrame.from_dict(features)
        features_df['duration_ms']=features_df['duration_ms']/60000
        music_feature1 = features_df[['danceability','energy', 'loudness', 'acousticness',
                'instrumentalness','liveness', 'valence', 'tempo']]

        min_max_scaler = MinMaxScaler()
        music_feature1.loc[:]=min_max_scaler.fit_transform(music_feature1.loc[:])
        genrel = [[]]
        for x in range(len(data)):
            song_met1['artist'].append(data[x][0])
            song_met1['genre'].append(lstring(data[x][4]))
            genrel[0].append(data[x][4])
            song_met1['album'].append(data[x][1])
            song_met1['title'].append(data[x][2])
            song_met1['duration'].append(round(data[x][3]/60000,2))
            song_met1['pop'].append(data[x][5])
            song_met1['id'].append('http://open.spotify.com/track/'+data[x][6])
        df = pd.DataFrame.from_dict(song_met1)
        similar_genre = get_similarity(0, 1, 10, genrel, genre2)
        similar_artist = get_similarity('artist', 0, 10, df, df1)

        def most_frequent(l, n):
            m = []
            ans = []
            for x in range(len(l)):
                m.append(l[x][n])
            result = sorted(m, key = m.count, reverse = True)
            for x in range(len(result)-1):
                if result[x] != result[x+1]:
                    ans.append(result[x+1])
            ans.insert(0, result[0])
            return ans[0:3]



        def get_avg(m, n):
            total = 0
            for x in range(len(m)):
                total+=m[x][n]
            total = total / len(m)
            return total

        def get_avg1(m, n):
            total = 0
            for x in range(len(m[n])):
                total+=m[n][x]
            total = total / len(m[n])
            return total

        def txt(n):
            n1 = get_avg1(music_feature, n)
            print(n1)
            n2 = get_avg1(music_feature1, n)
            string1 = ""
            if n1 > n2:
                string1 = "you recently began to listen to songs with more " + n
            else:
                string1 = "you recently began to listen to songs with less " + n
            return string1

        def make_clickable(url, name):
            return '<a href="{}">{}</a>'.format(url,name)

        #for x in range(len(artists)):
            #if artists[x] not in count:

        df['title'] = df.apply(lambda x: make_clickable(x['id'], x['title']), axis=1)
        df1['title'] = df1.apply(lambda x: make_clickable(x['id'], x['title']), axis=1)
        df.drop('id', axis=1, inplace=True)
        df1.drop('id', axis=1, inplace=True)

        df_html = df[0:20].to_html(classes='data', header="true", index=False, justify="center")
        #df_html = markupsafe.Markup(df_html)
        df_html = html.unescape(df_html)
        df_html1 = df1[0:20].to_html(classes='data', header="true", index=False, justify="center")
        #df_html = markupsafe.Markup(df_html)
        df_html1 = html.unescape(df_html1)





        similar_genre = "You kept listening to " + lstring(similar_genre)
        similar_artist = "You kept listening to " + lstring(similar_artist)

        if (get_avg(data, 5) > get_avg(data1, 5)):
            popularity_str = "You recently preferred music that was more popular"
        else:
            popularity_str = "You recently preferred music that was less popular"

        artist_most = "Your top 3 artists were " + lstring(most_frequent(data, 0))
        energy_str = txt("energy")
        dance_str = txt("danceability")
        tempo_str = txt("tempo")
        loudness_str = txt("loudness")
        unique_artist  = ""
        unique_genre = ""
        return render_template('home.html', loggedin = 1, img_data = display_plot(music_feature, "Recently Played"), table_html=df_html, titles=df1.columns.values, img_data2 = display_plot(music_feature1, "Most Played"), tables1=df_html1, titles1=df.columns.values, trend_genre = similar_genre, trend_genre1 = unique_genre, trend_artist = similar_artist, trend_artist1 = unique_artist, avg_popularity = popularity_str, most_artist = artist_most, energy_str = energy_str, dance_str = dance_str, tempo_str = tempo_str, loudness_str = loudness_str)

@app.route("/login")
def verify():

    auth_url = f'{API_BASE}/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}&show_dialog={SHOW_DIALOG}'
    global logo
    logo = 1
    return redirect(auth_url)


@app.route("/api_callback")
def api_callback():
    session.clear()
    global logo
    logo = 1
    print("logo SWITCHED ", logo)
    code = request.args.get('code')

    auth_token_url = f"{API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":"https://marcow125.pythonanywhere.com/api_callback",
        "client_id":client_id,
        "client_secret":client_secret
        })

    res_body = res.json()
    print(res.json())
    session["toke"] = res_body.get("access_token")

    return redirect("/")


@app.route("/logout")
def logout():
    global logo
    logo = 0
    return redirect("/")
