import streamlit as st
import json
import pandas as pd

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
    wc = WordCloud(background_color="white", font_path=r"./msgothic.ttc", width=1920,height=1080)
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



def channel_status(file):
    st.header("チャンネル名：{}".format(file[:-5]))
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
        try:
            description = video[1]["description"]
        except:
            description = ""
        title = video[1]["title"]
        
        #channeltitle = video[1]["channelTitle"]
        viewcount = int(video[1]["viewCount"])
        likecount = int(video[1]["likeCount"])
        dislikecount = int(video[1]["dislikeCount"])
        #st.write(dislikecount)
        try:
            commentcount = int(video[1]["commentCount"])
        except:
            commentcount = int(0)
        #st.write(commentcount)
        tag = video[1].get('tags')
        relevanttopicids = video[1].get("relevantTopicIds")
        categoryid = video[1]["categoryId"]

        stats.append([published_at, title, description, viewcount,likecount,dislikecount,commentcount,
                        relevanttopicids, tag, categoryid])

    df = pd.DataFrame(stats, columns=["published_at", "title","description", 
                                        "viewcount", "likecount", "dislikecount", "commentcount",
                                        "relevanttopicids", "tag", "categoryid"])
    df = df.sort_values('published_at').reset_index(drop=True)
    
    st.write("### 動画と再生回数、および、コメント数の上位順(日付順)")
    values = st.slider(
    '再生回数の最少と最大でビデオを選択',  df.loc[:, "viewcount"].min(), df.loc[:, "viewcount"].min(), (df.loc[:, "viewcount"].min(), df.loc[:, "viewcount"].max()))
    st.write('#### 1本のビデオあたりの再生回数: {:,} 回 ~ {:,} 回'.format(values[0], values[1]))


    df = df.loc[ (df.loc[:, "viewcount"]>=values[0]) & (df.loc[:, "viewcount"]<=values[1]),: ]

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


    st.pyplot()

    #t = Tokenizer()
    if st.checkbox("元データを確認する"):
        st.write( df.loc[ (df.loc[:, "viewcount"]>=values[0]) & (df.loc[:, "viewcount"]<=values[1]),: ] )


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
