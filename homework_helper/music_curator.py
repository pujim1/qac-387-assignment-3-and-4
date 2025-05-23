import streamlit as st
from utilities import load_home_button
import pandas as pd
import numpy as np
from utilities import preform_clust,run_PCA
from spotipy_player import spotify_manager

def run_music_picker(current_state):
    '''wrapper for running our function picker

    Parameters
    ----------
    current_state=st.session_state,default=st.session_state
        The session state we recieve from whatever is handling the overarching file. Honestly Streamlit makes this
        an incredibly approachable way to scale the app because we can organize quite nicely into seperate modules
        in various different areas.
    
        
        
    Returns
    -------

    


    Notes
    -----




    Examples
    --------



    
    '''

    current_state=current_state if current_state is not None else st.session_state
    st.image('../resources/musicmaker.png')
    song = st.text_input("Can you give me a song your interested in?")
    artist = st.text_input("Many songs can have similar titles, so I also need the Artist")


    uploaded_df = st.file_uploader(label="If you have spotify data with features (before spotify went and ruined it) drop it here!")

    st.write('If you have a spotify developer account and would like to use our API function add your secret id and client id here: \n Note: you need to add the redirect url http://127.0.0.1:8888/callback/ ')
    Client_id=st.text_input('Client id')
    Secret_id=st.text_input('Secret id')

    if uploaded_df is not None:
        labels=create_labels(uploaded_df)
        uploaded_df['cluster_label']=labels
        st.write(f"All set! you can go put in your desired song and artist now :p")

        
    generate_button = st.button(label="GENERATE MY PLAYLIST!")
    load_home_button(current_state)
    if generate_button:
        if song and artist:
            if uploaded_df is None:
                uploaded_df = pd.read_csv('../resources/Cluster_assigned_music_df.csv')

            song_suggestions = grab_song_cluster_label(uploaded_df, song, artist)
            if song_suggestions.empty:
                st.write("No suggestions found.")
            else:
                st.subheader("🎵 Your Personalized Playlist 🎵")
                for idx, row in song_suggestions.iterrows():
                    if Client_id is not None and Secret_id is not None:
                        spotify_manager(song_suggestions,Client_id,Secret_id)
                    else:
                        spotify_manager(song_suggestions)
                    if st.session_state.page is not None:
                        track_name = row['name']
                        track_artist = row['artists']
                        track_url = f"https://open.spotify.com/track/{row['id']}"

                        st.markdown(f"**{idx + 1}. [{track_name} by {track_artist}]({track_url})**")
                        st.success("Song added to queue!")
                    if st.session_state.page is None:
                        st.session_state.page=None

                st.success("Enjoy your playlist!")

                        

        if not song or not artist:
            st.write('Sorry, you need to provide both a song and artist.')

    return 

def create_labels(uploaded_df):
    '''' sectioning off the label creation here

    Parameters
    ---------

    Returns
    -------

    Notes
    -----

    Examples
    -------


    '''

    if uploaded_df.shape[0]<100:
        test_embeddings = create_OpenAI_embeddings(uploaded_df)
        #im not even including an alternate here yet

    else:
        labels=create_regular_embeddings(uploaded_df)
        return labels
    
def cluster_music(dataframe):
    ''''takes music either in the built in dataframe or provided dataframe and assigns more similar music

    Parameters
    ----------
    dataframe:pd.DataFrame,default=~/Cluster_assigned_music_df.csv
        We include a dataframe with the package that has 1 million spotify songs so it should in theory cover a
        pretty wide spread of data but, alas music is very subjective and person-specific and as already shown 
        we cant really account for everythign right away

        This dataframe isnt actually clustered its just provided if we dont get this argument, but it is actually quite useful
        as a reference for what were doing with our data.
    
        
    Returns
    -------


    Notes
    -----


    Examples
    --------


    
    '''




    return
    
def create_OpenAI_embeddings(df):
    '''pre-processes dataframe by clustering embeddings of string representations of every columns 
    
    A little raunchy but its like 3AM and im exhausted

    Parameters
    ----------
    df:pd.DataFrame:Default=None
        Dataframe with music data we would like to process. It is very important that we do have feature data here
        as we are just turning everything into strings and using the API embedding model to cluster but, I mean in 
        reality I would rather use pca and k-means TBH

    Returns
    -------
    processed_df:pd.DataFrame,shape=(n_original_rows,n_original_columns+1)
        Original dataframe but, we add in a column with labels for each column 

        
    Notes
    -----


    Examples
    --------
    
    '''
    from langchain_openai import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.docstore.document import Document
    embedding_model = OpenAIEmbeddings()
    

    # Example: assuming df is your DataFrame
    # Combine all columns into one string per row
    combined_texts = df.astype(str).agg(' '.join, axis=1).to_numpy()


    # Initialize embedding model
    embedding_model = OpenAIEmbeddings()
    embeddings = embedding_model.embed_documents(combined_texts) 
    X_embeddings = np.array(embeddings)

    
    return X_embeddings

def create_regular_embeddings(dataframe):
    ''' I'll fill this in later

    Parameters
    ----------
    dataframe:df,
        music features basically im tired

    Returns
    -------


    Examples
    --------

    
    Notes
    -----

    
    '''

    #quick preprocessing of dates will split up later
    dataframe['release_date'] = dataframe['release_date'].str.replace('-', '').astype(float)

    #picking out just our features and hoping that people are providing spotify data
    just_metrics=dataframe[['explicit', 'danceability', 'energy',
       'key', 'loudness', 'mode', 'speechiness', 'acousticness',
       'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms',
       'time_signature', 'year', 'release_date']]
    
    X_pca, weights, explained_variance_ratio = run_PCA(just_metrics, 2)
    n_clusters = max(1, dataframe.shape[0] // 30)

    labels=preform_clust(X_pca, max_clusters=n_clusters)
    


    return labels

def grab_song_cluster_label(df, songtitle, artist):
    '''returns suggestions based on cluster label

    Parameters
    ----------
    df:pd.DataFrame,default='../resources/Cluster_assigned_music_df.csv'
        The dataframe with cluster labels, or song suggestions that would be useful to use in order
        to group the different genres into something good.
    
    songtitle:str,default='show me what you got'->default comes from kaggle as we know the song exists in the dataset
        A string denoting the songtitle the user is providing as interest. It would be nice to have this be in proper caps
        as it will slow the search time but its fine either way.

    artist:str,default='Limp Bizkit'
        A string denoting the artist the user is providing as interest. It would be nice to have this be in proper caps
        as it will slow the search time but its fine either way.

    
    Returns
    -------
    suggestions:pd.DataFrame,default=None
        A filtered dataframe with only similar suggestions

    
    Notes
    -----

    
    Examples
    --------


    '''
    try:
        artist_songs = df[df['artists'].str.contains(artist, case=False, na=False)]
        if artist_songs.shape[0] == 0:
            st.write("Aw we're sorry, the Artist is not available at this moment")
            return pd.DataFrame()  # return empty DataFrame

        track = artist_songs[artist_songs['name'].str.contains(songtitle, case=False, na=False)]
        if track.shape[0] == 0:
            st.write("Aw we're sorry, the Song is not available at this moment")
            return pd.DataFrame()

        cluster_label = track['cluster_label'].iloc[0]  # make sure to extract a scalar

        suggestions = df[df['cluster_label'] == cluster_label]
        return suggestions

    except Exception as e:
        st.write(f"Aw we're sorry, something went wrong: {e}")
        return pd.DataFrame()


if __name__=="__main__":

    print("running the file by itself")
    uploaded_df=uploaded_df=pd.read_csv('../resources/Cluster_assigned_music_df.csv')
    test_suggestions=grab_song_cluster_label(uploaded_df,'show me what you got',artist='limp bizkit')
    print(test_suggestions)
    





    
