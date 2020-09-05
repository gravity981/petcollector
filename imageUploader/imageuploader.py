import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import base64


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

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)

            with open(event.src_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                pload = {'machine_id': 'Olivia', 'image': encoded_string}
                r = requests.post('https://httpbin.org/post', data=pload)
                print(r.text)


if __name__ == '__main__':
    w = Watcher()
    print("Start watcher on directory " + Watcher.DIRECTORY_TO_WATCH)
    w.run()