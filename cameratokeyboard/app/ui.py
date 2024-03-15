import asyncio
import time
from typing import Tuple

import pygame
import pygame_gui

from cameratokeyboard.types import FrameState
from cameratokeyboard.interfaces import IDetectedFrameData

DEFAULT_IMAGE = pygame.image.load("assets/nocam.png")
OUTLINE_COLORS = {
    FrameState.VALID: (4, 189, 84),
    FrameState.INITIALIZING: (99, 99, 99),
    FrameState.MISSING_MARKERS: (158, 22, 13),
    FrameState.MISSING_FINGERS: (252, 127, 10),
    FrameState.MISSING_THUMBS: (232, 214, 16),
}
FINGER_COLOR = (141, 16, 143)
THUMB_COLOR = (16, 77, 176)
MARKER_COLOR = (14, 150, 87)
COUNTDOWN_COLOR = (255, 255, 255)
MESSAGE_COLOR = (252, 127, 10)
CROP_MARGIN = 0.1
ASYNC_SLEEP = 0.01


class UI:
    """
    Represents the user interface.

    Attributes:
        This class doesn't have any public attributes.

    Methods:
        run: Runs the user interface loop.
        update_data: Updates the detected frame data.
        update_text: Updates the text displayed in the user interface text box.
    """

    def __init__(self, window_size: Tuple[int, int], fps: int) -> None:
        """
        Initializes the UI class.

        Args:
            window_size (Tuple[int, int]): The size of the window in pixels.
            fps (int): The refresh rate (per second) for the UI.

        Returns:
            None
        """

        pygame.init()
        pygame.display.set_caption("C2K")
        self._window_size = window_size
        self._fps = fps
        self._ui_window_surface = pygame.display.set_mode(self._window_size)
        self._ui_background = pygame.Surface(self._window_size)
        self._ui_background.fill(pygame.Color("#223333"))
        self._ui_manager = pygame_gui.UIManager(self._window_size)
        self._is_running = True

        self._text = ""
        self._ui_text_box = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((0, 0), self._text_frame_size),
            html_text=self._text,
            manager=self._ui_manager,
        )

        self._ui_image_surface = DEFAULT_IMAGE
        self._ui_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(
                (0, self._text_frame_size[1]), self._image_frame_size
            ),
            image_surface=self._ui_image_surface,
            manager=self._ui_manager,
        )

        self._task_scheduler = TaskScheduler()
        self._countdown_ends_at = None
        self._message = None

        self._detected_frame_data: IDetectedFrameData = None

    async def run(self):
        """
        Runs the user interface loop.

        This method updates the user interface, processes events, and handles calibration.
        It also updates the image, draws UI elements, and updates the display.
        """
        clock = pygame.time.Clock()

        while self._is_running:
            time_delta = clock.tick(self._fps) / 1000.0 - ASYNC_SLEEP

            self._process_events()
            self._task_scheduler.tick()
            self._handle_calibration()

            self._update_image()

            self._ui_manager.update(time_delta)
            self._ui_window_surface.blit(self._ui_background, (0, 0))
            self._ui_manager.draw_ui(self._ui_window_surface)

            pygame.display.update()
            await asyncio.sleep(ASYNC_SLEEP)

    def update_data(self, detected_frame_data: IDetectedFrameData):
        """
        Updates the data of the UI.
        """
        self._detected_frame_data = detected_frame_data

    def update_text(self, text: str):
        """
        Updates the text displayed in the user interface text box. text is the user's
        input.

        Args:
            text (str): The text to be added to the UI text box.
        """
        self._text += text
        self._ui_text_box.set_text(self._text)

    @property
    def _text_frame_size(self) -> Tuple[int, int]:
        return (self._window_size[0], self._window_size[1] // 3)

    @property
    def _image_frame_size(self) -> Tuple[int, int]:
        return (self._window_size[0], self._window_size[1] - self._text_frame_size[1])

    @property
    def _image_aspect_ratio(self) -> float:
        return self._image_frame_size[1] / self._image_frame_size[0]

    @property
    def _message_font(self):
        size = self._ui_image_surface.get_height() // 20
        return pygame.font.Font(None, size)

    @property
    def _countdown_font(self):
        size = self._ui_image_surface.get_height() // 5
        return pygame.font.Font(None, size)

    def _update_image(self):
        if (
            not self._detected_frame_data
            or self._detected_frame_data.current_frame is None
        ):
            self._ui_image_surface = DEFAULT_IMAGE
            return

        self._ui_image_surface = pygame.image.frombuffer(
            self._detected_frame_data.current_frame.tostring(),
            self._detected_frame_data.current_frame.shape[1::-1],
            "BGR",
        )

        self._draw_landmark_indicators()
        self._draw_keyboard_boundaries()

        # This fallen hero shall remain here forevermore, for without its heroic
        # sacrifices, this project would have been lost.
        # self._playground()

        self._crop_image()

        self._draw_countdown()
        self._draw_message()
        self._draw_state_box()
        self._draw_camera_angles()

        self._ui_image.set_image(self._ui_image_surface)

    def _crop_image(self):
        if (
            self._detected_frame_data.current_frame is None
            or not self._ui_image_surface
        ):
            return

        if not self._detected_frame_data.marker_coordinates or not all(
            self._detected_frame_data.marker_coordinates
        ):
            return

        image_width = self._ui_image_surface.get_width()
        image_height = self._ui_image_surface.get_height()

        left_most_marker_x = min(
            m.x for m in self._detected_frame_data.marker_coordinates
        )
        lowest_marker_y = max(m.y for m in self._detected_frame_data.marker_coordinates)

        crop_x = max(0, left_most_marker_x - CROP_MARGIN * image_width)
        crop_width = min(
            image_width - crop_x, image_width - crop_x - CROP_MARGIN * image_height
        )
        crop_height = crop_width * self._image_aspect_ratio
        crop_y = min(
            image_height - crop_height,
            max(0, lowest_marker_y - crop_height + CROP_MARGIN * image_height),
        )

        self._ui_image_surface = self._ui_image_surface.subsurface(
            pygame.Rect((crop_x, crop_y), (crop_width, crop_height))
        )

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_running = False
            self._ui_manager.process_events(event)

    def _handle_calibration(self):
        if (
            not self._detected_frame_data
            or self._task_scheduler.task_exists(self._start_calibration)
            or not self._detected_frame_data.requires_calibration
            or self._detected_frame_data.is_calibration_in_progress
        ):
            return

        self._message = (
            "Hold your hands in their resting position as if you're getting\n"
            "ready to type. The border around this area should be green\n"
            "for the calibration to progress. Calibrating in"
        )  # TODO: I18n
        self._countdown_ends_at = time.time() + 5.0  # TODO: Unhardcode this value
        self._task_scheduler.add_task_in(5.0, self._start_calibration, unique=True)

    def _start_calibration(self):
        if not self._detected_frame_data:
            return

        if (
            self._detected_frame_data.is_calibration_in_progress
            or not self._detected_frame_data.requires_calibration
        ):
            return

        self._detected_frame_data.start_calibration(self._show_calibration_done_message)
        self._message = "Calibrating..."  # TODO: I18n
        self._countdown_ends_at = None

    def _show_calibration_done_message(self):
        # TODO: I18n
        # TODO: Unhardcode message timeout value
        self._message = "Calibration done!"
        self._task_scheduler.add_task_in(3.0, self._clear_message)

    def _draw_state_box(self):
        pygame.draw.rect(
            self._ui_image_surface,
            OUTLINE_COLORS[self._detected_frame_data.state],
            self._ui_image_surface.get_rect(),
            8,  # TODO: Unhardcode this value
        )

    def _draw_camera_angles(self):
        angle = self._detected_frame_data.camera_angle
        margin = self._ui_image_surface.get_height() / 14
        height = 24
        texts = [
            f"Yaw:   {angle.yaw:.2f}°",
            f"Pitch: {angle.pitch:.2f}°",
        ]

        font = pygame.font.Font(None, height)
        for index, text in enumerate(texts):
            text_surface = font.render(text, True, (255, 255, 255))
            self._ui_image_surface.blit(
                text_surface,
                (
                    margin,
                    margin + height * index * 1.1,
                ),
            )

    def _draw_keyboard_boundaries(self):
        def point_between(p1, p2, length):
            fraction = length / ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
            return (
                p1[0] + (p2[0] - p1[0]) * fraction,
                p1[1] + (p2[1] - p1[1]) * fraction,
            )

        def draw_line(p1, p2):
            pygame.draw.line(
                self._ui_image_surface,
                MARKER_COLOR,
                p1,
                point_between(p1, p2, length=line_length),
                line_width,
            )

        if not self._detected_frame_data.marker_coordinates or not all(
            self._detected_frame_data.marker_coordinates
        ):
            return

        line_width = self._window_size[1] // 144
        line_length = self._window_size[1] // 20
        bottom_left = self._detected_frame_data.marker_coordinates[0].xy
        top_left = self._detected_frame_data.marker_coordinates[1].xy
        top_right = self._detected_frame_data.marker_coordinates[2].xy
        bottom_right = self._detected_frame_data.marker_coordinates[3].xy

        draw_line(bottom_left, top_left)
        draw_line(bottom_left, bottom_right)

        draw_line(top_left, top_right)
        draw_line(top_left, bottom_left)

        draw_line(top_right, top_left)
        draw_line(top_right, bottom_right)

        draw_line(bottom_right, top_right)
        draw_line(bottom_right, bottom_left)

    def _draw_landmark_indicators(self):
        radius = 6  # TODO: Unhardcode this value
        for finger in self._detected_frame_data.finger_coordinates or []:
            if finger is not None:
                pygame.draw.circle(
                    self._ui_image_surface, FINGER_COLOR, finger.xy, radius
                )
        for thumb in self._detected_frame_data.thumb_coordinates or []:
            if thumb is not None:
                pygame.draw.circle(
                    self._ui_image_surface, THUMB_COLOR, thumb.xy, radius
                )

        for down_finger in self._detected_frame_data.down_finger_coordinates or []:
            if down_finger is not None:
                # TODO: Unhardcode all the values here
                pygame.draw.circle(
                    self._ui_image_surface,
                    (0, 255, 255),
                    down_finger.xy,
                    radius + 6,
                    width=3,
                )

    def _draw_countdown(self):
        if self._countdown_ends_at and time.time() < self._countdown_ends_at:
            text = str(max(int(self._countdown_ends_at - time.time()), 0))
        elif (
            self._detected_frame_data.is_calibration_in_progress
            and self._detected_frame_data.calibration_progress
        ):
            text = f"{int(self._detected_frame_data.calibration_progress * 100)}%"
        else:
            return

        text_surface = self._countdown_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            center=(
                self._ui_image_surface.get_width() / 2,
                self._ui_image_surface.get_height() / 2,
            )
        )
        self._ui_image_surface.blit(text_surface, text_rect)

    def _draw_message(self):
        if not self._message:
            return

        text = self._message_font.render(self._message, True, (255, 255, 255))
        rect = text.get_rect(
            center=(
                self._ui_image_surface.get_width() / 2,
                self._ui_image_surface.get_height() / 3,
            )
        )

        self._ui_image_surface.blit(text, rect)

    def _clear_message(self):
        self._message = None


class TaskScheduler:
    """
    A simple task scheduler.
    """

    def __init__(self) -> None:
        self.tasks = []

    def add_task_at(self, at: float, task: callable, unique: bool = False):
        """
        Adds a task to the UI's task list at a specified time.

        Args:
            at (float): The time at which the task should be executed.
            task (callable): The task to be added.
            unique (bool, optional): If True, checks if the task already exists in the
                task list before adding it. Defaults to False.
        """
        if unique and self.task_exists(task):
            return

        self.tasks.append((at, task))

    def add_task_in(self, in_: float, task: callable, unique: bool = False):
        """
        Adds a task to be executed after a specified delay.

        Args:
            in_ (float): The delay in seconds before the task is executed.
            task (callable): The task to be executed.
            unique (bool, optional): If True, ensures that only one instance of the
                task is added. Defaults to False.
        """
        self.add_task_at(time.time() + in_, task, unique)

    def task_exists(self, task: callable):
        """
        Check if a task exists in the list of tasks.

        Args:
            task (callable): The task to check.

        Returns:
            bool: True if the task exists, False otherwise.
        """
        return task in (t for _, t in self.tasks)

    def tick(self):
        """
        Executes pending tasks that have reached their scheduled time.

        Note: The tasks are executed in reverse order to ensure that the tasks scheduled
        earlier are executed first.

        """
        for index, (task_time, task) in enumerate(reversed(self.tasks)):
            if time.time() >= task_time:
                task()
                self.tasks.pop(index)
