# coding:utf-8

from src.models import db
from src.models.proxy_model import ProxyModel
from src.models.platform_model import PlatformModel,PLATFORM_TYPE
from src.models.account_model import AccountModel,AccountRelationship
from src.models.upload_setting_model import UploadSettingModel,BROWSER_TYPE,WAIT_POLICY_TYPE
from src.models.youtube_video_model import YoutubeVideoModel,VIDEO_SETTINGS

from src.models.task_model import TaskModel,TASK_STATUS
from src.customid import *
import random



db.connect()
# db.create_tables([ProxyModel, PlatformModel], safe=True)
db.create_tables([ProxyModel,AccountModel,AccountRelationship,PlatformModel,UploadSettingModel,YoutubeVideoModel,TaskModel])



print('inital supported platforms')
PlatformModel.add_platform(platform_data={
"name":"youtube",
"type":1,
"server":'www.youtube.com'

}

)
PlatformModel.add_platform(platform_data=
{
"name":"tiktok",
"type":2,
"server":None
}
)
PlatformModel.add_platform(platform_data=
{
"name":"instagram",
"type":3,
"server":None
}
)


PlatformModel.add_platform(platform_data=
{
"name":"twitter",
"type":4,
"server":None
}
)
PlatformModel.add_platform(platform_data=
{
"name":"facebook",
"type":5,
"server":None
}
)
PlatformModel.add_platform(platform_data=
{
"name":"douyin",
"type":6,
"server":None
}
)
PlatformModel.add_platform(platform_data=
{
"name":"视频号",
"type":7,
"server":None
}
)
PlatformModel.add_platform(platform_data=
{
"name":"小红书",
"type":8,
"server":None
}
)
PlatformModel.add_platform(platform_data=
{
"name":"unknown",
"type":100,
"server":None
}
)
print('add test datas')
