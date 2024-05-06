from typing import Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs import Position, LanePosition, WorldPosition, ScenarioObject, BoundingBox, Vehicle
from ads_scenario_transformer.transformer import Transformer
from ads_scenario_transformer.tools.geometry import Geometry


@dataclass
class PointENUTransformerConfiguration:
    supported_position: 'PointENUTransformer.SupportedPosition'
    lanelet_map: LaneletMap
    projector: MGRSProjector
    lanelet_subtypes: Set[str]
    scenario_object: Optional[ScenarioObject]


class PointENUTransformer(Transformer):
    """
    We are using LanePosition instead of WorldPosition below reason.
    - InternalError: The specified WorldPosition could not be approximated to the proper Lane. Perhaps the WorldPosition points to a location where multiple lanes overlap, and there are at least two or more candidates for a LanePosition that can be approximated to that WorldPosition. This issue can be resolved by strictly specifying the location using LanePosition instead of WorldPosition
    """
    configuration: PointENUTransformerConfiguration

    class SupportedPosition(Enum):
        Lane = 1
        World = 2

    Source = Tuple[PointENU, float]
    Target = Optional[Position]

    def __init__(self, configuration: PointENUTransformerConfiguration):
        self.configuration = configuration

    def transform(self, source: Source) -> Target:
        if self.configuration.supported_position == PointENUTransformer.SupportedPosition.Lane:
            lane_position = self.transformToLanePosition(source)
            return Position(lanePosition=self.transformToLanePosition(
                source)) if lane_position else None
        return Position(worldPosition=self.transformToWorldPosition(source))

    def transformToLanePosition(self,
                                source: Source) -> Optional[LanePosition]:
        lanelet_map = self.configuration.lanelet_map
        projector = self.configuration.projector
        lanelet_subtypes = self.configuration.lanelet_subtypes

        projected_point = Geometry.project_UTM_point_on_lanelet(
            projector=projector, point=source[0])
        lanelet = Geometry.find_lanelet(map=lanelet_map,
                                        basic_point=projected_point,
                                        subtypes=lanelet_subtypes)

        if lanelet:
            bounding_box = self.object_bouding_box(
                self.configuration.scenario_object)
            # Discard heading value
            lane_position = Geometry.nearest_lane_position(
                map=lanelet_map,
                lanelet=lanelet,
                basic_point=projected_point,
                entity_bounding_box=bounding_box,
                heading=0.0)
            return lane_position
        return None

    def transformToWorldPosition(self, source: Source) -> WorldPosition:
        projected_point = Geometry.project_UTM_point_on_lanelet(
            projector=self.configuration.projector, point=source[0])
        # Discard heading value
        return WorldPosition(x=projected_point.x,
                             y=projected_point.y,
                             z=projected_point.z,
                             h=0.0)

    def object_bouding_box(
            self, scenario_object: ScenarioObject) -> Optional[BoundingBox]:
        if scenario_object.entityObject.HasField("pedestrian"):
            return scenario_object.entityObject.pedestrian.boundingBox
        elif scenario_object.entityObject.HasField("vehicle"):
            return scenario_object.entityObject.vehicle.boundingBox
        elif scenario_object.entityObject.vehicle.vehicleCategory == Vehicle.Category.CAR:
            return scenario_object.entityObject.vehicle.boundingBox
        return None
