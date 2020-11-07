#AIzaSyCj27PN_MW2zNJmp8INqfxbGDGNTRvpU9U
#AIzaSyCWnkA7oJOoN3_MLvcrKxfEIZRVS_js3EU
import streamlit as st
from apiclient.discovery import build
import pandas as pd
# Font
from matplotlib import pyplot as plt
import japanize_matplotlib
japanize_matplotlib.japanize()
from matplotlib import rcParams
plt.rcParams["font.size"] = 18
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
st.set_option('deprecation.showPyplotGlobalUse', False)


YOUTUBE_API_KEY = 'AIzaSyCWnkA7oJOoN3_MLvcrKxfEIZRVS_js3EU'

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


html_temp = """
    <div style="background-color:{};padding:10px;border-radius:10px">
    <h1 style="color:{};text-align:center;">Youtubeデータの確認</h1>
    </div>
    """
st.markdown(html_temp.format('royalblue','white'), unsafe_allow_html=True)
st.markdown("")


#numに入れた数字×5件の情報を取得
#その他のパラメーターはAPIから情報を取得するパラメータと同じ
def get_video_info(part, q, order, type, num):
    dic_list = []
    search_response = youtube.search().list(part=part,q=q,order=order,type=type)
    output = youtube.search().list(part=part,q=q,order=order,type=type).execute()

    #一度に5件しか取得できないため何度も繰り返して実行
    for i in range(num):        
        dic_list = dic_list + output['items']
        search_response = youtube.search().list_next(search_response, output)
        output = search_response.execute()

    df = pd.DataFrame(dic_list)
    #各動画毎に一意のvideoIdを取得
    df1 = pd.DataFrame(list(df['id']))['videoId']
    #各動画毎に一意のvideoIdを取得必要な動画情報だけ取得
    df2 = pd.DataFrame(list(df['snippet']))[['channelTitle','publishedAt','channelId','title','description']]
    ddf = pd.concat([df1,df2], axis = 1)

    return ddf

def get_statistics(id):
    statistics = youtube.videos().list(part = 'statistics', id = id).execute()['items'][0]['statistics']
    return statistics

def main():

    menu = ["Youtubeでデータを取り直す", "直近ダウンロードしたファイルで表示する"]

    choice = st.sidebar.radio("Menu", menu)


    if choice == "Youtubeでデータを取り直す":
        df = get_video_info(part='snippet',q='ボードゲーム',order='viewCount',type='video',num = 20)
        df_static = pd.DataFrame(list(df['videoId'].apply(lambda x : get_statistics(x))))
        df_output = pd.concat([df,df_static], axis = 1)
        df_output.to_csv("./youtube.csv")
        st.dataframe(df_output)


    if choice == "直近ダウンロードしたファイルで表示する":
        df_output = pd.read_csv("./youtube.csv")
        df_output['viewCount'] = df_output['viewCount'].astype(int)

        df_output.groupby('channelTitle').sum().sort_values(by = 'viewCount', ascending = False).plot( kind='bar', y = 'viewCount', figsize = (25,10), fontsize = 20)
        st.pyplot()


    #st.dataframe(df_output)
    #df_output['viewCount'] = df_output['viewCount'].astype(int)

    #df_output.groupby('channelTitle').sum().sort_values(by = 'viewCount', ascending = False).plot( kind='bar', y = 'viewCount', figsize = (25,10), fontsize = 20)
    #st.pyplot()

if __name__ == "__main__":
    main()