import unittest

from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs.position_pb2 import LanePosition


class TestProtocolBuffers(unittest.TestCase):

    def test_apollo_protocol_import(self):
        point1 = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        point2 = PointENU(x=587044.4300003723, y=4141550.060588833, z=0)

        self.assertEqual(point1.x, 587079.3045861976)
        self.assertEqual(point1.y, 4141574.299574421)
        self.assertEqual(point2.x, 587044.4300003723)
        self.assertEqual(point2.y, 4141550.060588833)

    def test_openscenario_protocol_import(self):
        position1 = LanePosition(laneId="154", s=10.9835, offset=-0.5042)
        position2 = LanePosition(laneId="108", s=35.266, offset=-1.1844)

        self.assertEqual(position1.laneId, "154")
        self.assertEqual(position1.s, 10.9835)
        self.assertEqual(position1.offset, -0.5042)
        self.assertEqual(position2.laneId, "108")
        self.assertEqual(position2.s, 35.266)
        self.assertEqual(position2.offset, -1.1844)


if __name__ == '__main__':
    unittest.main()
