from youtube_statistics import YTstats

API_KEY = 'AIzaSyBD2iQAO6EFpiVdcKmt0-L5xEi6GyV75K8'
channel_id = "UCkZLRWeJemZ5GXb6PbMx70w"

#python_engineer_id = 'UCbXgNpp0jedKWcQiULLbDTA'
#channel_id = python_engineer_id

#yt = YTstats(API_KEY, channel_id)
#yt.get_channel_statistics()
#yt.get_channel_video_data()
#yt.dump()
yt = YTstats(API_KEY, channel_id)
yt.extract_all()
yt.dump()  # dumps to .json
