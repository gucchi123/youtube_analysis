#動画をアップロード順にする

#AIzaSyCj27PN_MW2zNJmp8INqfxbGDGNTRvpU9U
#AIzaSyCWnkA7oJOoN3_MLvcrKxfEIZRVS_js3EU
import streamlit as st
from apiclient.discovery import build
import pandas as pd
import json
import numpy as np
# Font
from matplotlib import pyplot as plt
import japanize_matplotlib
from matplotlib import cm

#ToDo requirements.txtに入れる
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud

from youtube_statistics import YTstats
import channel_status

japanize_matplotlib.japanize()
from matplotlib import rcParams
plt.rcParams["font.size"] = 18
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
st.set_option('deprecation.showPyplotGlobalUse', False)


YOUTUBE_API_KEY = 'AIzaSyBD2iQAO6EFpiVdcKmt0-L5xEi6GyV75K8'
channel_id = "UCYp373JfGNTCu_M9AGhg7tA"



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

    menu = ["検索キーワードでの上位閲覧チャネルの確認", 
            "自分のチャンネルの状況を確認", "他のチャンネルの状況を確認","Youtubeでデータを取り直す"]

    choice = st.sidebar.radio("Menu", menu)
    
    if choice == "検索キーワードでの上位閲覧チャネルの確認":
        
        df_output = pd.read_csv("./youtube.csv")
        search_text = pd.read_csv("./search.csv")
        st.write("### ***{}***と検索した時の上位チャンネル".format(search_text.columns[1]))
        st.write("検索キーワードを選びなおす際には、「Youtubeでデータを取り直す」を選択")
        #st.write(search_text)

        df_output['viewCount'] = df_output['viewCount'].astype(int)

        values = st.slider("上位何番目を除く", min_value=0, max_value=50, step=1)



        df_output.groupby('channelTitle').sum().sort_values(by = 'viewCount', ascending = False)[values:].plot( kind='bar', y = 'viewCount', figsize = (25,10), fontsize = 20)
        st.pyplot()

    elif choice == "自分のチャンネルの状況を確認":
        channel_status.channel_status("紗綾ちゃんねる〜saaya_channel〜.json")


    elif choice == "他のチャンネルの状況を確認":
        channel_target = ["こじはる", "ピンククラッカーズ" ,"森咲智美"]
        selected_channel = st.sidebar.radio("見たいチャンネルを選択", channel_target)
        if selected_channel == "こじはる":
            channel_status.channel_status("haruna_kojima's_cat_nap.json")
        elif selected_channel == "ピンククラッカーズ":
            #st.write("ピンククラッカーズ.json")
            channel_status.channel_status("ピンククラッカーズ.json")
        elif selected_channel == "森咲智美":
            st.write("こじはると同じものが出る")
            #channel_status.channel_status("森咲智美チャンネル  Tomomi Morisaki Channel.json")

    elif choice == "Youtubeでデータを取り直す":
        passcode = st.text_input("Pass codeを入力してください")
        if passcode == "1234567890":
            search_menu = ["美容", "グラビア", "日常", "ボードゲーム"] 
            search_target = st.radio("上位検索したいワード", search_menu)
            if st.checkbox("{}を検索した検索データの更新".format(search_target)):
                df_search = pd.DataFrame()
                df_search[search_target] = search_target
                df_search.to_csv("./search.csv")
                df = get_video_info(part='snippet',q=search_target,order='viewCount',type='video',num = 20)
                df_static = pd.DataFrame(list(df['videoId'].apply(lambda x : get_statistics(x))))
                df_output = pd.concat([df,df_static], axis = 1)
                df_output.to_csv("./youtube.csv")
                
            if st.checkbox("自分のチャンネルデータの更新"):
                channel_id = "UCYp373JfGNTCu_M9AGhg7tA"
                yt = YTstats(YOUTUBE_API_KEY, channel_id)
                yt.extract_all()
                yt.dump()  # dumps to .json
                st.write("データのダウンロードが完了しました")

            if st.checkbox("他のチャンネルデータの更新"):
                channel_id = "UCOjmYCnYlTcdoD2DKHvrV5g"
                yt = YTstats(YOUTUBE_API_KEY, channel_id)
                yt.extract_all()
                yt.dump()  # dumps to .json
                st.write("データのダウンロードが完了しました")

        else:
            st.write("やり直してください")


if __name__ == "__main__":
    main()