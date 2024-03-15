import asyncio
import sys
import time
import traceback

import cv2

from cameratokeyboard.app.detector import Detector
from cameratokeyboard.app.ui import UI
from cameratokeyboard.config import Config


class App:
    """
    Runs the app and takes care of inter-module communication
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._cap = cv2.VideoCapture(config.video_input_device)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.resolution[0])
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.resolution[1])

        self._detector = Detector(config)

        self._ui = UI(window_size=config.resolution, fps=config.app_fps)

        self._throttler = RepeatingKeysThrottler(delay=config.repeating_keys_delay)

        self._detected_frame = None

    async def run(self):
        """
        The main run loop
        """
        detect_task = asyncio.create_task(self._detect())
        await self._ui.run()
        detect_task.cancel()

    async def _detect(self):
        while True:
            success, frame = self._cap.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            try:
                self._detected_frame = self._detector.detect(frame)
                self._broadcast_new_data()

                if self._detected_frame.down_keys:
                    for key in self._detected_frame.down_keys:
                        self._on_key_down(key)

            except Exception as e:  # pylint: disable=broad-except
                print(e)
                traceback.print_exc()
                sys.exit(1)

            await asyncio.sleep(0.01)

    def _broadcast_new_data(self):
        self._ui.update_data(
            detected_frame_data=self._detected_frame,
        )

    def _start_calibration(self, on_calibration_complete: callable):
        if not self._detected_frame or not self._detected_frame.requires_calibration:
            return
        self._detected_frame.start_calibration(on_calibration_complete)

    def _on_key_down(self, key: str) -> None:
        if not self._throttler.key_press_allowed(key):
            return

        self._ui.update_text(key)


class RepeatingKeysThrottler:
    """
    Sets the rhythm for repeating keys.
    """

    def __init__(self, delay: float = 0.5):
        self._delay = delay
        self._keys = {}

    def key_press_allowed(self, key: str) -> bool:
        """
        Checks if key has been pressed in the last `delay` seconds or not. If not, returns
        True and updates the last press time for the key. If yes, returns False.
        """
        current_time = time.time()
        if key in self._keys and current_time - self._keys[key] < self._delay:
            return False

        self._keys[key] = current_time
        return True
