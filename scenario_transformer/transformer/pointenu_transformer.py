from typing import Dict, Tuple
from enum import Enum
from dataclasses import dataclass
import lanelet2
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs import Position, LanePosition, WorldPosition
from scenario_transformer.transformer import Transformer
from scenario_transformer.tools.geometry import Geometry


@dataclass
class PointENUTransformerConfiguration:
    supported_position: 'PointENUTransformer.SupportedPosition'
    lanelet_map: LaneletMap
    projector: lanelet2.projection.MGRSProjector


class PointENUTransformer(Transformer):
    """
    We are using LanePosition instead of WorldPosition below reason.
    - InternalError: The specified WorldPosition = [87040.4, 41553.1, 0] could not be approximated to the proper Lane. Perhaps the WorldPosition points to a location where multiple lanes overlap, and there are at least two or more candidates for a LanePosition that can be approximated to that WorldPosition. This issue can be resolved by strictly specifying the location using LanePosition instead of WorldPosition
    """
    configuration: PointENUTransformerConfiguration

    class SupportedPosition(Enum):
        Lane = 1
        World = 2

    Source = Tuple[PointENU, float]
    Target = Position

    def __init__(self, configuration: PointENUTransformerConfiguration):
        self.configuration = configuration

    def transform(self, source: Source) -> Target:
        if self.configuration.supported_position == PointENUTransformer.SupportedPosition.Lane:
            return Position(lanePosition=self.transformToLanePosition(source))
        return Position(worldPosition=self.transformToWorldPosition(source))

    def transformToLanePosition(self, source: Source) -> LanePosition:
        lanelet_map = self.configuration.lanelet_map
        projector = self.configuration.projector

        projected_point = Geometry.project_UTM_to_lanelet(projector=projector,
                                                          pose=source[0])
        lanelet = Geometry.find_lanelet(lanelet_map, projected_point)
        # Discard heading value
        lane_position = Geometry.lane_position(lanelet=lanelet,
                                               basic_point=projected_point,
                                               heading=0.0)
        return lane_position

    def transformToWorldPosition(self, source: Source) -> WorldPosition:
        pose = Geometry.utm_to_WGS(pose=source[0])
        projected_point = Geometry.project_UTM_to_lanelet(
            projector=self.configuration.projector,
            pose=source[0])
        # Discard heading value
        return WorldPosition(x=projected_point.x, y=projected_point.y, z=projected_point.z, h=0.0)