from typing import Optional, Union, Set, List
import math
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.core import Lanelet, LaneletMap, GPSPoint, BasicPoint2d, BasicPoint3d, getId, Point3d, TrafficLight, Point2d
from lanelet2.geometry import distanceToCenterline2d, distance, findWithin3d, inside, length2d, findNearest, findWithin2d, to2D
from lanelet2.routing import RoutingGraph, Route, LaneletPath
from pyproj import Proj
from modules.common.proto.geometry_pb2 import PointENU, Point3D
from modules.map.proto.map_signal_pb2 import Signal
from openscenario_msgs import LanePosition, Orientation, ReferenceContext, BoundingBox
from ads_scenario_transformer.tools.vector_map_parser import VectorMapParser
from ads_scenario_transformer.builder.entities_builder import ASTEntityType


class Geometry:

    @staticmethod
    def find_nearest_traffic_light(
            map: LaneletMap, signal: Signal,
            projector: MGRSProjector) -> Optional[TrafficLight]:

        candidates = set()
        for point in signal.boundary.point:
            basic_point = Geometry.project_UTM_point_on_lanelet(
                point=point, projector=projector)
            basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)

            nearest_traffic_elements = findNearest(map.regulatoryElementLayer,
                                                   basic_point2d, 10)

            for traffic_element in nearest_traffic_elements:
                if isinstance(traffic_element[1], TrafficLight):
                    candidates.add(traffic_element)

        if not candidates:
            return None

        min_distance, nearest_traffic_light = min(
            (distance, traffic_light)
            for distance, traffic_light in candidates)
        return nearest_traffic_light

    @staticmethod
    def find_available_lanes(vector_map_parser: VectorMapParser,
                             start_point: BasicPoint3d,
                             end_point: BasicPoint3d,
                             entity_type: ASTEntityType) -> List[LaneletPath]:
        """
        Finds all available lanes between start_point and end_point trajectory. If start_point or end_point are placed on a lanelet where multiple lanelets are overlapped, it can return wrong set of lanelets.
        """

        def routing_graph(type: ASTEntityType) -> RoutingGraph:
            if type == ASTEntityType.PEDESTRIAN:
                return vector_map_parser.pedestrian_routing_graph
            elif type == ASTEntityType.BICYCLE:
                # Bicycle also uses vehicle routing graph
                return vector_map_parser.vehicle_routing_graph
            # ego, car
            return vector_map_parser.vehicle_routing_graph

        def find_paths(start_lanelet: Lanelet,
                       end_lanelet: Lanelet) -> List[LaneletPath]:
            paths = []
            if start_lanelet and end_lanelet:
                route: Route = target_graph.getRoute(start_lanelet,
                                                     end_lanelet, 0, True)
                if route:
                    return [route.shortestPath()]

                paths = target_graph.possiblePaths(
                    start_lanelet) + target_graph.possiblePaths(end_lanelet)

            elif start_lanelet:
                paths = target_graph.possiblePaths(start_lanelet)
            elif end_lanelet:
                paths = target_graph.possiblePaths(end_lanelet)
            return paths

        target_graph = routing_graph(entity_type)

        start_lanelets = Geometry.find_close_lanelets(
            map=vector_map_parser.lanelet_map,
            basic_point=start_point,
            entity_type=entity_type)

        end_lanelets = Geometry.find_close_lanelets(
            map=vector_map_parser.lanelet_map,
            basic_point=end_point,
            entity_type=entity_type)

        all_paths = []
        for start_lanelet in start_lanelets:
            for end_lanelet in end_lanelets:
                paths = find_paths(start_lanelet, end_lanelet)
                for path in paths:
                    all_paths.append(path)

        return all_paths

    @staticmethod
    def find_close_lanelets(map: LaneletMap, basic_point: BasicPoint3d,
                            entity_type: ASTEntityType) -> List[Lanelet]:
        found_lanes = findWithin3d(layer=map.laneletLayer,
                                   geometry=basic_point,
                                   maxDist=1)

        subtypes = entity_type.available_lanelet_subtype()
        if found_lanes:
            lanelets = [
                lanelet[1] for lanelet in found_lanes
                if "subtype" in lanelet[1].attributes
                and lanelet[1].attributes["subtype"] in subtypes
            ]

            if lanelets:
                return lanelets

        assert len(map.laneletLayer) > 20

        for nearby_count in [1, 10] + list(range(20, len(map.laneletLayer),
                                                 20)):
            basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)
            found_lanes_2d = findNearest(map.laneletLayer, basic_point2d,
                                         nearby_count)

            lanelets = [
                lanelet[1] for lanelet in found_lanes_2d
                if "subtype" in lanelet[1].attributes
                and lanelet[1].attributes["subtype"] in subtypes
            ]
            if lanelets:
                return lanelets

        raise ValueError(
            f"Could not find close lanelets for point {basic_point} type {entity_type} in the map"
        )
        return []

    @staticmethod
    def find_lanelet(map: LaneletMap,
                     basic_point: BasicPoint3d,
                     subtypes: Optional[Set[str]] = None) -> Optional[Lanelet]:
        found_lanes = findWithin3d(layer=map.laneletLayer,
                                   geometry=basic_point,
                                   maxDist=1)

        if subtypes:
            for lanelet in found_lanes:
                if "subtype" in lanelet[1].attributes and lanelet[
                        1].attributes["subtype"] in subtypes:
                    return lanelet[1]
        else:
            if found_lanes:
                return found_lanes[0][1]

        basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)
        found_lanes_2d = findNearest(map.laneletLayer, basic_point2d, 10)

        if subtypes:
            for lanelet in found_lanes_2d:
                if "subtype" in lanelet[1].attributes and lanelet[
                        1].attributes["subtype"] in subtypes:
                    return lanelet[1]
        else:
            if found_lanes_2d:
                return found_lanes_2d[0][1]

        return None

    @staticmethod
    def nearest_lane_position(map: LaneletMap,
                              lanelet: Lanelet,
                              basic_point: BasicPoint3d,
                              entity_bounding_box: BoundingBox,
                              heading=0.0) -> Optional[LanePosition]:
        point3d = Point3d(getId(), basic_point.x, basic_point.y, basic_point.z)
        basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)
        t_attribute = distanceToCenterline2d(lanelet, basic_point2d)

        if not inside(lanelet, basic_point2d):
            # If the point is not in lanelet, we find nearest one and use it
            nearest_point_in_lanelets = findNearest(map.pointLayer,
                                                    basic_point2d, 1)
            if not nearest_point_in_lanelets:
                return None

            nearest_point = nearest_point_in_lanelets[0][1]
            basic_point2d = BasicPoint2d(nearest_point.x, nearest_point.y)
            t_attribute = distanceToCenterline2d(lanelet, basic_point2d)

        point2d = Point2d(getId(), basic_point.x, basic_point.y)
        left = distance(to2D(lanelet.leftBound), point2d)
        right = distance(to2D(lanelet.rightBound), point2d)
        is_t_positive = left < right
        lane_width = distance(lanelet.centerline,
                              lanelet.leftBound) + distance(
                                  lanelet.centerline, lanelet.rightBound)

        if not is_t_positive:
            t_attribute = -t_attribute

        entity_width = entity_bounding_box.dimensions.width
        entity_length = entity_bounding_box.dimensions.length

        # If there is not enough space to place entity on the lane, simulator will fails.
        max_lane_width = (lane_width - entity_width) / 2
        min_lane_width = -max_lane_width
        t_attribute = min(max_lane_width, t_attribute)
        t_attribute = max(min_lane_width, t_attribute)

        max_s = max(math.floor(length2d(lanelet) - entity_length), 0)

        # Calculation of s attribute is simplified.
        # https://releases.asam.net/OpenDRIVE/1.6.0/ASAM_OpenDRIVE_BS_V1-6-0.html#_reference_line_coordinate_systems
        s_attribute = min(max_s, distance(lanelet.centerline[0], point3d))

        return LanePosition(
            roadId='',
            laneId=str(lanelet.id),
            s=s_attribute,
            offset=t_attribute,
            orientation=Orientation(
                h=heading,
                p=0,
                r=0,
                type=ReferenceContext.REFERENCECONTEXT_RELATIVE))

    @staticmethod
    def utm_to_WGS(point: Union[PointENU, Point3D], zone=10) -> GPSPoint:
        utm_proj = Proj(proj="utm", zone=zone, ellps="WGS84")
        lon, lat = utm_proj(point.x, point.y, inverse=True)
        return GPSPoint(lat=lat, lon=lon, ele=point.z)

    @staticmethod
    def project_UTM_point_on_lanelet(point: Union[PointENU, Point3D],
                                     projector: MGRSProjector,
                                     zone: int = 10) -> BasicPoint3d:
        gps_point = Geometry.utm_to_WGS(point, zone=zone)
        return projector.forward(gps_point)
