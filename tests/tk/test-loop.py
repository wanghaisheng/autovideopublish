from tkinter import *
from tkinter import messagebox
import asyncio
import threading
import random


def _asyncio_thread(async_loop):
    async_loop.run_until_complete(do_urls())


def _asyncio_thread_up(async_loop):
    async_loop.run_until_complete(do_videos())


def do_tasks(async_loop):
    """Button-Event-Handler starting the asyncio part."""
    threading.Thread(target=_asyncio_thread, args=(async_loop,)).start()


def do_ups(async_loop):
    threading.Thread(target=_asyncio_thread_up, args=(async_loop,)).start()


async def one_url(url):
    """One task."""
    sec = random.randint(1, 8)
    await asyncio.sleep(sec)
    return "url: {}\tsec: {}".format(url, sec)


async def do_urls():
    """Creating and starting 10 tasks."""
    tasks = [one_url(url) for url in range(10)]
    completed, pending = await asyncio.wait(tasks)
    results = [task.result() for task in completed]
    print("\n".join(results))


async def one_video(taskid, video, uploadsetting, account):
    sec = random.randint(1, 8)
    await asyncio.sleep(sec)
    return "taskid: {}\tsec: {}".format(taskid, sec)


async def do_videos():
    task = one_video(
        taskid="1111111",
        video={},
        uploadsetting={},
        account={},
    )
    tasks = [task]
    completed, pending = await asyncio.wait(tasks)
    results = [task.result() for task in completed]


def do_freezed():
    messagebox.showinfo(message="Tkinter is reacting.")


def main(async_loop):
    root = Tk()
    Button(master=root, text="Asyncio Tasks", command=lambda: do_ups(async_loop)).pack()
    Button(master=root, text="Freezed???", command=do_freezed).pack()
    root.mainloop()


if __name__ == "__main__":
    async_loop = asyncio.get_event_loop()
    main(async_loop)
