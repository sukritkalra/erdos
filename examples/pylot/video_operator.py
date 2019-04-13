import cv2

from carla.image_converter import to_bgra_array

from erdos.op import Op
from erdos.utils import setup_logging


class VideoOperator(Op):
    def __init__(self, name, flags, log_file_name=None):
        super(VideoOperator, self).__init__(name)
        self._logger = setup_logging(self.name, log_file_name)
        self._flags = flags
        self._last_seq_num = -1

    @staticmethod
    def setup_streams(input_streams, filter_name=None):
        if filter_name:
            input_streams = input_streams.filter_name(filter_name)
        input_streams.add_callback(VideoOperator.display_frame)
        return []

    def display_frame(self, msg):
        if self._last_seq_num + 1 != msg.timestamp.coordinates[1]:
            self._logger.error('Expected msg with seq num {} but received {}'.format(
                (self._last_seq_num + 1), msg.timestamp.coordinates[1]))
            if self._flags.fail_on_message_loss:
                assert self._last_seq_num + 1 == msg.timestamp.coordinates[1]
        self._last_seq_num = msg.timestamp.coordinates[1]

        frame_array = to_bgra_array(msg.data)
        cv2.imshow(self.name, frame_array)
        cv2.waitKey(1)

    def execute(self):
        self.spin()
