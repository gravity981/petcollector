import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import base64
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from time import sleep

executor = ThreadPoolExecutor(5)

def say_after(delay, what):
    sleep(delay)
    what = what.rstrip('~')
    print(what)
    try:
        with open(what, "rb") as image_file:
            base64_encoded_image = base64.b64encode(image_file.read())
            base64_message = base64_encoded_image.decode('utf-8')
            data = dict()
            data['machine_id'] = 'Olivia'
            data['image'] = base64_message
            r = requests.post('https://shrouded-inlet-73857.herokuapp.com/pint', json=data)
            print("Response: HTTP " + str(r.status_code))
    except FileNotFoundError:
        print('file not found, skip')


class Watcher:
    DIRECTORY_TO_WATCH = "/home/pi/camera_data"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            executor.submit(say_after, 0.3, event.src_path)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)





if __name__ == '__main__':
    w = Watcher()
    print("Start watcher on directory " + Watcher.DIRECTORY_TO_WATCH)
    w.run()
