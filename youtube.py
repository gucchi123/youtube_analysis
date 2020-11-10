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


def get_nouns(sentence, noun_list):
    t = Tokenizer()
    for token in t.tokenize(sentence):
        split_token = token.part_of_speech.split(',')
        ## 一般名詞を抽出
        if split_token[0] == '名詞' and split_token[1] == '一般':
            noun_list.append(token.surface)

def depict_word_cloud(noun_list):
    ## 名詞リストの要素を空白区切りにする(word_cloudの仕様)
    noun_space = ' '.join(map(str, noun_list))
    ## word cloudの設定(フォントの設定)
    #wc = WordCloud(background_color="white", font_path=r"C:/WINDOWS/Fonts/msgothic.ttc", width=300,height=300)
    wc = WordCloud(background_color="white", font_path=r"./msgothic.ttc", width=300,height=300)
    wc.generate(noun_space)
    ## 出力画像の大きさの指定
    plt.figure(figsize=(5,5))
    ## 目盛りの削除
    plt.tick_params(labelbottom=False,
                    labelleft=False,
                    labelright=False,
                    labeltop=False,
                   length=0)
    ## word cloudの表示
    plt.imshow(wc)
    plt.show()



def main():

    menu = ["Youtubeでデータを取り直す", "検索キーワードでの上位閲覧チャネルの確認", 
            "自分のチャンネルの状況を確認", "他のチャンネルの状況を確認"]

    choice = st.sidebar.radio("Menu", menu)
    

    if choice == "Youtubeでデータを取り直す":
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

    elif choice == "検索キーワードでの上位閲覧チャネルの確認":
        
        df_output = pd.read_csv("./youtube.csv")
        search_text = pd.read_csv("./search.csv")
        st.write("### ***{}***と検索した時の上位チャンネル".format(search_text.columns[1]))
        st.write("検索キーワードを選びなおす際には、「Youtubeでデータを取り直す」を選択")
        #st.write(search_text)

        df_output['viewCount'] = df_output['viewCount'].astype(int)

        df_output.groupby('channelTitle').sum().sort_values(by = 'viewCount', ascending = False).plot( kind='bar', y = 'viewCount', figsize = (25,10), fontsize = 20)
        st.pyplot()

    elif choice == "自分のチャンネルの状況を確認":
        file = "紗綾ちゃんねる〜saaya_channel〜.json"
        st.header("チャンネル状況：{}".format(file[:-5]))
        data = None
        with open(file, "r") as f:
            data = json.load(f)
        
        channel_id, stats = data.popitem()
        #st.write(stats)
        channel_stats = stats["channel_statistics"]
        video_stats = stats["video_data"]
        st.write('総視聴回数: **{:,}**'.format(int(channel_stats["viewCount"])))
        st.write('チャンネル登録者数: **{:,}**'.format( int(channel_stats["subscriberCount"])))
        st.write('ビデオの数: **{:,}**'.format(int(channel_stats["videoCount"])))
        
        #st.write(len(video_stats))
        #sorted_vid = sorted(video)
        stats = []
        #sorted_video = sorted(video_stats.items(), key=lambda item: pd.datetime(item[1]["publishedAt"], format="%Y%m"), reverse=True)
        for video in video_stats.items():
            #st.write(video)
            video_id = video[0]
            published_at = video[1]["publishedAt"]
            description = video[1]["description"]
            title = video[1]["title"]
            
            #channeltitle = video[1]["channelTitle"]
            viewcount = int(video[1]["viewCount"])
            likecount = int(video[1]["likeCount"])
            dislikecount = int(video[1]["dislikeCount"])
            commentcount = int(video[1]["commentCount"])
            #st.write(video)
            tag = video[1].get('tags')
            relevanttopicids = video[1].get("relevantTopicIds")
            categoryid = video[1]["categoryId"]

            stats.append([published_at, title, description, viewcount,likecount,dislikecount,commentcount,
                            relevanttopicids, tag, categoryid])

        df = pd.DataFrame(stats, columns=["published_at", "title","description", 
                                            "viewcount", "likecount", "dislikecount", "commentcount",
                                            "relevanttopicids", "tag", "categoryid"])
        df = df.sort_values('published_at').reset_index(drop=True)
        
        fig = plt.figure(figsize=(10,10))
        #ax1 = fig.add_subplot(111)
        #plt.tick_params(labelsize=10)
        fig, ax1 = plt.subplots()
        plt.xticks(rotation=90)
        plt.tick_params(labelsize=7)
 
        # ax1とax2を関連させる
        ax2 = ax1.twinx()
        plt.tick_params(labelsize=7)
        # それぞれのaxesオブジェクトのlines属性にLine2Dオブジェクトを追加
        ax1.bar(df["title"], df["viewcount"], color=cm.Set1.colors[1], label="視聴回数")
        ax2.plot( df["title"], df["commentcount"] , color=cm.Set1.colors[0], label="コメント数")
        #plt.xticks(rotation=45)
        # 凡例
        # グラフの本体設定時に、ラベルを手動で設定する必要があるのは、barplotのみ。plotは自動で設定される＞
        handler1, label1 = ax1.get_legend_handles_labels()
        handler2, label2 = ax2.get_legend_handles_labels()
        # 凡例をまとめて出力する
        ax1.legend(handler1 + handler2, label1 + label2, loc=2, borderaxespad=0., fontsize=7)
        
        pageview_max = 2 * max(df["viewcount"])
        register_max = 1.2 * max(df["commentcount"])
        ax1.set_ylim([0, pageview_max])
        ax2.set_ylim([0, register_max])
        #plt.setp( ax1[1].xaxis.get_majorticklabels(), rotation=70 )

        st.write("### 動画と再生回数、および、コメント数の上位順")
        st.pyplot()

        #t = Tokenizer()
        if st.checkbox("元データを確認する"):
            st.write(df.iloc[:, :])


        if st.checkbox("タイトル文言を見る"):
            st.write("### タイトル単語")
            noun_list = []
            for sentence in list(df['title']):
                get_nouns(sentence, noun_list)

            plt.figure(figsize=(20,10))
            depict_word_cloud(noun_list)

            st.pyplot()

        if st.checkbox("動画の説明に使われている文言を見る"):
            st.write("### 動画の下に記載している単語")
            noun_list = []
            for sentence in list(df['description']):
                get_nouns(sentence, noun_list)

            depict_word_cloud(noun_list)
            st.pyplot()

    elif choice == "他のチャンネルの状況を確認":
        file = "haruna_kojima's_cat_nap.json"
        st.header("チャンネル状況：{}".format(file[:-5]))
        data = None
        with open(file, "r") as f:
            data = json.load(f)
        
        channel_id, stats = data.popitem()
        #st.write(stats)
        channel_stats = stats["channel_statistics"]
        video_stats = stats["video_data"]
        st.write('総視聴回数: **{:,}**'.format(int(channel_stats["viewCount"])))
        st.write('チャンネル登録者数: **{:,}**'.format( int(channel_stats["subscriberCount"])))
        st.write('ビデオの数: **{:,}**'.format(int(channel_stats["videoCount"])))
        
        #st.write(len(video_stats))
        #sorted_vid = sorted(video)
        stats = []
        #sorted_video = sorted(video_stats.items(), key=lambda item: pd.datetime(item[1]["publishedAt"], format="%Y%m"), reverse=True)
        for video in video_stats.items():
            #st.write(video)
            video_id = video[0]
            published_at = video[1]["publishedAt"]
            description = video[1]["description"]
            title = video[1]["title"]
            
            #channeltitle = video[1]["channelTitle"]
            viewcount = int(video[1]["viewCount"])
            likecount = int(video[1]["likeCount"])
            dislikecount = int(video[1]["dislikeCount"])
            commentcount = int(video[1]["commentCount"])
            #st.write(video)
            tag = video[1].get('tags')
            relevanttopicids = video[1].get("relevantTopicIds")
            categoryid = video[1]["categoryId"]

            stats.append([published_at, title, description, viewcount,likecount,dislikecount,commentcount,
                            relevanttopicids, tag, categoryid])

        df = pd.DataFrame(stats, columns=["published_at", "title","description", 
                                            "viewcount", "likecount", "dislikecount", "commentcount",
                                            "relevanttopicids", "tag", "categoryid"])
        df = df.sort_values('published_at').reset_index(drop=True)
        
        fig = plt.figure(figsize=(10,10))
        #ax1 = fig.add_subplot(111)
        #plt.tick_params(labelsize=10)
        fig, ax1 = plt.subplots()
        plt.xticks(rotation=90)
        plt.tick_params(labelsize=7)
 
        # ax1とax2を関連させる
        ax2 = ax1.twinx()
        plt.tick_params(labelsize=7)
        # それぞれのaxesオブジェクトのlines属性にLine2Dオブジェクトを追加
        ax1.bar(df["title"], df["viewcount"], color=cm.Set1.colors[1], label="視聴回数")
        ax2.plot( df["title"], df["commentcount"] , color=cm.Set1.colors[0], label="コメント数")
        #plt.xticks(rotation=45)
        # 凡例
        # グラフの本体設定時に、ラベルを手動で設定する必要があるのは、barplotのみ。plotは自動で設定される＞
        handler1, label1 = ax1.get_legend_handles_labels()
        handler2, label2 = ax2.get_legend_handles_labels()
        # 凡例をまとめて出力する
        ax1.legend(handler1 + handler2, label1 + label2, loc=2, borderaxespad=0., fontsize=7)
        
        pageview_max = 2 * max(df["viewcount"])
        register_max = 1.2 * max(df["commentcount"])
        ax1.set_ylim([0, pageview_max])
        ax2.set_ylim([0, register_max])
        #plt.setp( ax1[1].xaxis.get_majorticklabels(), rotation=70 )

        st.write("### 動画と再生回数、および、コメント数の上位順")
        st.pyplot()

        #t = Tokenizer()
        if st.checkbox("元データを確認する"):
            st.write(df.iloc[:, :])


        if st.checkbox("タイトル文言を見る"):
            st.write("### タイトル単語")
            noun_list = []
            for sentence in list(df['title']):
                get_nouns(sentence, noun_list)

            plt.figure(figsize=(20,10))
            depict_word_cloud(noun_list)

            st.pyplot()

        if st.checkbox("動画の説明に使われている文言を見る"):
            st.write("### 動画の下に記載している単語")
            noun_list = []
            for sentence in list(df['description']):
                get_nouns(sentence, noun_list)

            depict_word_cloud(noun_list)
            st.pyplot()

    #st.dataframe(df_output)
    #df_output['viewCount'] = df_output['viewCount'].astype(int)

    #df_output.groupby('channelTitle').sum().sort_values(by = 'viewCount', ascending = False).plot( kind='bar', y = 'viewCount', figsize = (25,10), fontsize = 20)
    #st.pyplot()

if __name__ == "__main__":
    main()