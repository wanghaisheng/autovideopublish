from peewee import TextField, BlobField, BooleanField, IntegerField, ForeignKeyField
from src.models import BaseModel, db
from src.config import generate_unique_hash
import time
from src.customid import CustomID
from src.models.youtube_video_model import YoutubeVideoModel
from src.models.platform_model import PLATFORM_TYPE
from src.models.upload_setting_model import UploadSettingModel
from src.models.account_model import AccountModel
from src.upload import uploadTask
from src.log import logger
from playhouse.shortcuts import model_to_dict
import json

from src.utils.tkutils import showinfomsg, find_key, askokcancelmsg, askquestionmsg


class TASK_STATUS:
    PENDING = 0
    FAILURE = 1
    SUCCESS = 2
    CANCEL = 3
    TASK_STATUS_TEXT = [
        (PENDING, "pending"),
        (FAILURE, "failure"),
        (SUCCESS, "success"),
        (CANCEL, "cancel"),
    ]


class SORT_BY_TYPE:
    ASC = 0
    DESC = 1
    SORT_BY_TYPE_TEXT = [(ASC, "Add DATE ASC"), (DESC, "Add DATE DESC")]


class TaskModel(BaseModel):
    id = BlobField(primary_key=True)
    platform = IntegerField(default=PLATFORM_TYPE.YOUTUBE)
    status = IntegerField(default=TASK_STATUS.PENDING)
    prorioty = BooleanField(default=False)
    video = ForeignKeyField(YoutubeVideoModel, backref="videos")
    # video upload use which proxy
    proxy = TextField(null=True)
    # video upload to
    username = TextField(null=True)
    is_deleted = BooleanField(default=False)  # Flag if the task is deleted

    setting = ForeignKeyField(UploadSettingModel, backref="settings")

    inserted_at = IntegerField()
    uploaded_at = IntegerField(null=True)

    @classmethod
    def add_task(cls, task_data, taskvideo, tasksetting):
        task = TaskModel(**task_data)
        task.inserted_at = int(time.time())  # Update insert_date
        # task.id = CustomID().to_bin()
        task.id = CustomID().to_bin()
        if taskvideo:
            task.video = taskvideo
        task.setting = tasksetting
        print("sync task platform to account binding platform")
        if task.setting.platform:
            if task.setting.account:
                print(
                    task.setting.account.platform, task.setting.platform, task.platform
                )
                task.platform = task.setting.account.platform
                task.setting.platform = task.setting.account.platform
            else:
                print("be caution!!!this account is not bind to any platform yet")
        else:
            print("be caution!!!this upload setting is not bind to any platform yet")

        task.save(force_insert=True)

        print("task add ok", task.id)
        return task

        # for user in TaskModel.select():
        #     print(user.name)
        # return True

    @classmethod
    def get_task_by_id(cls, id):
        return cls.get_or_none(cls.id == id)

    @classmethod
    def update_task(
        cls,
        id,
        videodata=None,
        settingdata=None,
        accountdata=None,
        taskdata=None,
        **kwargs,
    ):
        print(f"start to update task id:{id}")

        print(f"start to update task data:{taskdata}")
        print(f"start to update {accountdata} accountdata ")
        print(f"start to update {settingdata}  settingdata ")
        print(f"start to update {videodata} videodata ")

        try:
            task = cls.get_or_none(cls.id == id)
            vid = task.video
            settingid = task.setting
            accountid = task.setting.account
            if taskdata:
                task = TaskModel(**taskdata)
                print("before modify", task)

            else:
                for key, value in kwargs.items():
                    print(f"start to update field {key} to {value}")
                    # 由于entry获取的都是字符串变量值，对于bool型，需要手动转换

                    if key == "is_deleted":
                        print(f"sync status to is deleted :{value}")
                        if value == "0":
                            value = False
                        elif value == "1":
                            value = True
                        if value == True:
                            setattr(task, "status", 4)
                        elif value == False:
                            setattr(task, "status", 0)
                        print(
                            f"sync status to is deleted :{value} ----status:{getattr(task,'status')}"
                        )

                    setattr(task, key, value)

                    print(f"after modify field {key} {getattr(task,key)}")

            task.inserted_at = int(
                time.time()
            )  # Update insert_date                print(f'sync status to is deleted')

            if accountdata:
                print(f"sync account")

                account = AccountModel.update_account(
                    id=accountid, account_data=None, **accountdata
                )
                account.inserted_at = int(time.time())  # Update insert_date

                account.save()
            if settingdata:
                print(f"sync setting")

                setting = UploadSettingModel.update_uploadsetting(
                    id=settingid, settingdata=None, **settingdata
                )
                setting.inserted_at = int(time.time())  # Update insert_date

                setting.save()
            if videodata:
                print(f"sync video")

                video = YoutubeVideoModel.update_video(
                    id=vid, video_data=None, **videodata
                )
                video.inserted_at = int(time.time())  # Update insert_date

                video.save()

            task.save()
            # logger.info(
            #     f"row data:{json.dumps(model_to_dict(task), indent=4, sort_keys=True, default=str)}"
            # )
            print("end to update task data")

            return task
        except cls.DoesNotExist:
            return None

    @classmethod
    def delete_task(cls, id):
        try:
            task = cls.get(cls.id == id)
            task.delete_instance()
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    @classmethod
    def filter_tasks(
        cls,
        id=None,
        status=None,
        is_deleted=None,
        platform=None,
        uploaded_at=None,
        schedule_at=None,
        limit=None,
        setting=None,
        inserted_at=None,
        video_title=None,
        video_id=None,
        username=None,
        pageno=None,
        pagecount=None,
        start=None,
        end=None,
        data=None,
        ids=None,
        sortby=None,
    ):
        logger.info(
            f"filter_tasks query conditions \nusername: {username} platform:{platform} status:{status} video_title:{video_title} schedule_at:{schedule_at} video_id:{video_id} "
        )
        print(
            f"filter_tasks query conditions \nusername: {username} platform:{platform} status:{status} video_title:{video_title} schedule_at:{schedule_at} video_id:{video_id} "
        )
        query = TaskModel.select()
        counts = query.count()
        query = (
            TaskModel.select(
                TaskModel, YoutubeVideoModel, UploadSettingModel, AccountModel
            )
            .join(YoutubeVideoModel)  # Join favorite -> user (owner of favorite).
            .switch(TaskModel)
            .join(UploadSettingModel)  # Join favorite -> tweet
            .join(AccountModel)
        )  # Join tweet -> user
        if is_deleted is not None:
            if is_deleted in [0, 1]:
                is_deleted = True if is_deleted == 1 else False
                query = query.where(TaskModel.is_deleted == is_deleted)
            elif type(is_deleted) == bool:
                query = query.where(TaskModel.is_deleted == is_deleted)

            else:
                print(f"there is no support for status value yet:{status}")

        if status is not None:
            if type(status) == int:
                if status in dict(TASK_STATUS.TASK_STATUS_TEXT).keys():
                    query = query.where(TaskModel.status == status)

                else:
                    print(
                        f"there is no support for status value yet:{status}.by default we query all status"
                    )

            elif type(status) == str:
                if status in dict(TASK_STATUS.TASK_STATUS_TEXT).values():
                    status = find_key(dict(TASK_STATUS.TASK_STATUS_TEXT), status)
                else:
                    status = None
            else:
                print(
                    f"there is no support for status value yet:{status}.by default we query all status"
                )

        if sortby is not None:
            if type(sortby) == str:
                if sortby in dict(SORT_BY_TYPE.SORT_BY_TYPE_TEXT).values():
                    sortby = find_key(dict(SORT_BY_TYPE.SORT_BY_TYPE_TEXT), sortby)
                else:
                    sortby = 0

            elif type(sortby) == int:
                if sortby in dict(SORT_BY_TYPE.SORT_BY_TYPE_TEXT).keys() == False:
                    sortby = 0

        else:
            sortby = 0
        if sortby == 0:
            query = query.order_by(TaskModel.inserted_at.asc())

        elif sortby == 1:
            query = query.order_by(TaskModel.inserted_at.desc())

        if id is not None:
            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.

            query = query.where(TaskModel.id == id)
            print(f"show id task {ids}")
        if ids is not None:
            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.

            query = query.where(TaskModel.id.in_(ids))
            print(f"show ids task {ids}")
        if video_title is not None:
            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.

            query = (
                query
                # .join(YoutubeVideoModel,on=(TaskModel.video_id == YoutubeVideoModel.id))
                .where(YoutubeVideoModel.video_title.regexp(video_title))
            )
            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.
        if schedule_at is not None:
            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.

            query = query.where(YoutubeVideoModel.release_date.regexp(schedule_at))
            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.

        if video_id is not None:
            query = query.join(
                YoutubeVideoModel, on=(TaskModel.video == YoutubeVideoModel.id)
            ).where(YoutubeVideoModel.youtube_video_id == video_id)
            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.

        if platform is not None:
            if platform in dict(PLATFORM_TYPE.PLATFORM_TYPE_TEXT).keys():
                query = query.where(TaskModel.platform == platform)
            else:
                print(f"there is no support for platform value yet:{platform}")

        # 如果存在account 相关的查询参数，先找到对应的 setting id集合
        if username is not None:
            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.

            query = query.where(AccountModel.username.regexp(username))

            query = query.switch(
                TaskModel
            )  # <-- switch the "query context" back to ticket.

        # print("sql is", query)
        try:
            print("==total record counts===", len(list(query)), list(query))
            for i in list(query):
                print(i.platform)
            print("==per page counts===", pagecount)
            print("==page number===", pageno)

            counts = len(list(query))
            if pageno:
                query = query.paginate(pageno, pagecount)
                # print(f"==current pagi  {pageno} record counts===", len(list(query)))

            elif start and type(start) == int and type(start) == int:
                startpage = start / pagecount
                # and start<end
                # endpage=end/pagecount
                query = query.paginate(startpage, pagecount)
                # print(
                #     f"==current pagi start {start} record counts===", len(list(query))
                # )

            else:
                if pageno == None and start is None and end is None:
                    print(f"grab all records matching filters:{list(query)}")

            # print("before return result=========")
            # for i in list(query):
            #     print(i.platform)

            return list(query), counts

        except cls.DoesNotExist:
            query = None  # Set a default value or perform any other action

            return query, None
