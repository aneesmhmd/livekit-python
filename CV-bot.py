import asyncio
import logging
from signal import SIGINT, SIGTERM
import os
from dotenv import load_dotenv
from livekit import  rtc
import numpy as np
import cv2

load_dotenv()

async def main(room: rtc.Room) -> None:

    video_stream = None
    tasks = set()

    @room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
       *_
    ):
        if track.kind == rtc.TrackKind.KIND_VIDEO:
            nonlocal video_stream
            if video_stream is not None:
                return
            video_stream = rtc.VideoStream(track, format=rtc.VideoBufferType.RGB24)
            task = asyncio.create_task(print_frame(video_stream))
            tasks.add(task)
            task.add_done_callback(tasks.remove)

    await room.connect(os.getenv("LIVEKIT_URL"), os.getenv("TOKEN"))
    logging.info("connected to room %s", room.name)

async def print_frame(video_stream: rtc.VideoStream):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    async for raw_frame in video_stream:
        frame_buffer = raw_frame.frame

        frame_array = np.frombuffer(frame_buffer.data, dtype=np.uint8)
        frame = frame_array.reshape(frame_buffer.height, frame_buffer.width, 3)
        print(f"Received frame: {frame.shape}")

        # Grayscale the frame
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        cv2.imshow('frame', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows() # Close the window


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.FileHandler("basic_room.log"), logging.StreamHandler()],
    )

    loop = asyncio.get_event_loop()
    room = rtc.Room(loop=loop)

    async def cleanup():
        await room.disconnect()
        loop.stop()

    asyncio.ensure_future(main(room))
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, lambda: asyncio.ensure_future(cleanup()))

    try:
        loop.run_forever()
    finally:
        loop.close()
