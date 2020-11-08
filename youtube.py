#AIzaSyCj27PN_MW2zNJmp8INqfxbGDGNTRvpU9U
#AIzaSyCWnkA7oJOoN3_MLvcrKxfEIZRVS_js3EU
import streamlit as st
from apiclient.discovery import build
import pandas as pd
import json
# Font
from matplotlib import pyplot as plt
import japanize_matplotlib
from matplotlib import cm

from youtube_statistics import YTstats

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

    menu = ["Youtubeでデータを取り直す", "直近ダウンロードしたファイルで表示する", "チャンネルの状況を確認する"]

    choice = st.sidebar.radio("Menu", menu)


    if choice == "Youtubeでデータを取り直す":
        passcode = st.text_input("Pass codeを入力してください")
        if passcode == "1234567890":
            df = get_video_info(part='snippet',q='ボードゲーム',order='viewCount',type='video',num = 20)
            df_static = pd.DataFrame(list(df['videoId'].apply(lambda x : get_statistics(x))))
            df_output = pd.concat([df,df_static], axis = 1)
            df_output.to_csv("./youtube.csv")
            yt = YTstats(YOUTUBE_API_KEY, channel_id)
            yt.extract_all()
            yt.dump()  # dumps to .json
            st.dataframe(df_output)
        else:
            st.write("やり直してください")

    elif choice == "直近ダウンロードしたファイルで表示する":
        df_output = pd.read_csv("./youtube.csv")
        df_output['viewCount'] = df_output['viewCount'].astype(int)

        df_output.groupby('channelTitle').sum().sort_values(by = 'viewCount', ascending = False).plot( kind='bar', y = 'viewCount', figsize = (25,10), fontsize = 20)
        st.pyplot()

    elif choice == "チャンネルの状況を確認する":
        st.header("チャンネル状況")
        file = "紗綾ちゃんねる〜saaya_channel〜.json"
        data = None
        with open(file, "r") as f:
            data = json.load(f)
        
        channel_id, stats = data.popitem()
        #st.write(stats)
        channel_stats = stats["channel_statistics"]
        video_stats = stats["video_data"]
        st.write('総視聴回数: {:,}'.format(int(channel_stats["viewCount"])))
        st.write('チャンネル登録者数: {:,}'.format( int(channel_stats["subscriberCount"])))
        st.write('ビデオの数: {:,}'.format(int(channel_stats["videoCount"])))
        
        #st.write(len(video_stats))
        #sorted_vid = sorted(video)
        stats = []
        for video in video_stats.items():
            #st.write(video)
            video_id = video[0]
            title = video[1]["title"]
            #tag = video[2]['tags'] #ToDoタグを取りたい
            #channeltitle = video[1]["channelTitle"]
            viewcount = int(video[1]["viewCount"])
            likecount = int(video[1]["likeCount"])
            dislikecount = int(video[1]["dislikeCount"])
            commentcount = int(video[1]["commentCount"])

            stats.append([title, viewcount,likecount,dislikecount,commentcount])

        df = pd.DataFrame(stats, columns=["title", "viewcount", "likecount", "dislikecount", "commentcount"])
        st.write(df)
        fig = plt.figure(figsize=(10,10))
        #ax1 = fig.add_subplot(111)
        fig, ax1 = plt.subplots()
        plt.xticks(rotation=90)
        plt.tick_params(labelsize=7)
 
        # ax1とax2を関連させる
        ax2 = ax1.twinx()
        
        # それぞれのaxesオブジェクトのlines属性にLine2Dオブジェクトを追加
        ax1.bar(df["title"], df["viewcount"], color=cm.Set1.colors[1], label="視聴回数")
        ax2.plot( df["title"], df["commentcount"] , color=cm.Set1.colors[0], label="コメント数")
        #plt.xticks(rotation=45)
        # 凡例
        # グラフの本体設定時に、ラベルを手動で設定する必要があるのは、barplotのみ。plotは自動で設定される＞
        handler1, label1 = ax1.get_legend_handles_labels()
        handler2, label2 = ax2.get_legend_handles_labels()
        # 凡例をまとめて出力する
        ax1.legend(handler1 + handler2, label1 + label2, loc=2, borderaxespad=0.)
        
        pageview_max = 3 * max(df["viewcount"])
        register_max = 1.2 * max(df["commentcount"])
        ax1.set_ylim([0, pageview_max])
        ax2.set_ylim([0, register_max])
        #plt.setp( ax1[1].xaxis.get_majorticklabels(), rotation=70 )

        
        st.pyplot()

    #st.dataframe(df_output)
    #df_output['viewCount'] = df_output['viewCount'].astype(int)

    #df_output.groupby('channelTitle').sum().sort_values(by = 'viewCount', ascending = False).plot( kind='bar', y = 'viewCount', figsize = (25,10), fontsize = 20)
    #st.pyplot()

if __name__ == "__main__":
    main()