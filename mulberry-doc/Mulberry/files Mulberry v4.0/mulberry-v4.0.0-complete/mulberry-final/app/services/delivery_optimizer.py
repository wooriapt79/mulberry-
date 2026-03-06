"""
Mulberry Phase 2 - Delivery Optimization Algorithm
인제군 험준한 지형 대응 배송 경로 최적화
A* 알고리즘 + 고도/도로 조건 가중치
"""

import asyncio
import heapq
import math
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from loguru import logger
import numpy as np


@dataclass
class Location:
    """위치 정보"""
    location_id: str
    name: str
    latitude: float
    longitude: float
    altitude_m: float = 0.0  # 고도 (미터)
    address: str = ""
    location_type: str = "customer"  # farm, customer, depot


@dataclass
class DeliveryOrder:
    """배송 주문"""
    order_id: int
    customer_location: Location
    farm_location: Location
    items: List[Dict[str, Any]]
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, URGENT, CRITICAL
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None


@dataclass
class Route:
    """배송 경로"""
    route_id: str
    waypoints: List[Location]
    total_distance_km: float
    total_time_minutes: float
    elevation_gain_m: float
    difficulty_score: float
    orders: List[DeliveryOrder] = field(default_factory=list)


@dataclass
class RoadSegment:
    """도로 구간"""
    from_location: str
    to_location: str
    distance_km: float
    road_type: str  # highway, main_road, mountain_road, dirt_road
    elevation_change_m: float
    average_speed_kmh: float
    difficulty: float  # 0.0-1.0 (0=easy, 1=very difficult)


class DeliveryOptimizer:
    """
    배송 최적화 엔진
    
    알고리즘:
    - A* (A-star) 최단 경로 탐색
    - 지형 가중치 (고도 차이, 도로 조건)
    - 시간 제약 (time windows)
    - 우선순위 배송
    """
    
    def __init__(self):
        """배송 최적화 엔진 초기화"""
        
        # 도로 네트워크 그래프
        self.road_network: Dict[str, List[RoadSegment]] = {}
        
        # 위치 데이터베이스
        self.locations: Dict[str, Location] = {}
        
        # 최적화 파라미터
        self.config = {
            "max_delivery_radius_km": 50,  # 최대 배송 반경
            "vehicle_speed_kmh": {
                "highway": 80,
                "main_road": 60,
                "mountain_road": 40,
                "dirt_road": 20
            },
            "elevation_penalty_factor": 1.5,  # 고도 차이 페널티
            "difficulty_penalty_factor": 2.0,  # 난이도 페널티
            "priority_boost": {
                "CRITICAL": 10.0,
                "URGENT": 5.0,
                "HIGH": 2.0,
                "NORMAL": 1.0,
                "LOW": 0.5
            }
        }
        
        # 인제군 지형 데이터 로드
        self._load_inje_terrain_data()
        
        logger.info("✅ Delivery Optimizer initialized")
    
    def _load_inje_terrain_data(self):
        """
        인제군 지형 데이터 로드
        
        실제로는 GIS 데이터베이스나 API에서 로드
        여기서는 샘플 데이터
        """
        # 샘플 위치 (인제군 주요 지점)
        sample_locations = [
            Location("depot", "배송 거점", 38.0697, 128.1709, 200, "인제읍"),
            Location("farm_1", "푸른골농원", 38.0850, 128.2100, 350, "기린면"),
            Location("farm_2", "청정농장", 38.1200, 128.1500, 450, "북면"),
            Location("customer_1", "어르신댁_1", 38.0800, 128.1900, 280, "기린면"),
            Location("customer_2", "어르신댁_2", 38.1100, 128.1700, 320, "북면"),
        ]
        
        for loc in sample_locations:
            self.locations[loc.location_id] = loc
        
        # 샘플 도로 네트워크
        sample_roads = [
            RoadSegment("depot", "farm_1", 8.5, "main_road", 150, 50, 0.3),
            RoadSegment("depot", "customer_1", 6.2, "main_road", 80, 55, 0.2),
            RoadSegment("farm_1", "customer_1", 3.8, "mountain_road", 70, 35, 0.5),
            RoadSegment("depot", "farm_2", 12.0, "mountain_road", 250, 40, 0.6),
            RoadSegment("farm_2", "customer_2", 4.5, "mountain_road", 120, 38, 0.5),
            RoadSegment("customer_1", "customer_2", 7.8, "main_road", 40, 52, 0.3),
        ]
        
        # 양방향 도로 구축
        for road in sample_roads:
            # A → B
            if road.from_location not in self.road_network:
                self.road_network[road.from_location] = []
            self.road_network[road.from_location].append(road)
            
            # B → A (역방향)
            reverse_road = RoadSegment(
                from_location=road.to_location,
                to_location=road.from_location,
                distance_km=road.distance_km,
                road_type=road.road_type,
                elevation_change_m=-road.elevation_change_m,  # 반대 방향
                average_speed_kmh=road.average_speed_kmh,
                difficulty=road.difficulty
            )
            
            if road.to_location not in self.road_network:
                self.road_network[road.to_location] = []
            self.road_network[road.to_location].append(reverse_road)
        
        logger.info(f"✅ Loaded {len(self.locations)} locations, {len(sample_roads)*2} road segments")
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Haversine 거리 계산 (km)
        
        Args:
            lat1, lon1: 시작점 위경도
            lat2, lon2: 끝점 위경도
            
        Returns:
            float: 거리 (km)
        """
        R = 6371  # 지구 반지름 (km)
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2
        )
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _calculate_terrain_cost(self, road: RoadSegment) -> float:
        """
        지형 비용 계산
        
        고려 요소:
        - 거리
        - 고도 변화 (오르막 페널티)
        - 도로 난이도
        - 도로 유형
        
        Args:
            road: 도로 구간
            
        Returns:
            float: 총 비용 (작을수록 좋음)
        """
        # 기본 거리 비용
        distance_cost = road.distance_km
        
        # 고도 변화 페널티 (오르막만)
        elevation_cost = 0
        if road.elevation_change_m > 0:
            # 100m 오를 때마다 추가 1km 비용
            elevation_cost = (road.elevation_change_m / 100) * self.config["elevation_penalty_factor"]
        
        # 도로 난이도 페널티
        difficulty_cost = road.difficulty * self.config["difficulty_penalty_factor"]
        
        # 총 비용
        total_cost = distance_cost + elevation_cost + difficulty_cost
        
        return total_cost
    
    def _calculate_time(self, road: RoadSegment) -> float:
        """
        구간 소요 시간 계산 (분)
        
        Args:
            road: 도로 구간
            
        Returns:
            float: 소요 시간 (분)
        """
        # 속도 조정 (고도 오르막 시 속도 감소)
        speed = road.average_speed_kmh
        
        if road.elevation_change_m > 0:
            # 100m 오를 때마다 속도 10% 감소
            speed_reduction = (road.elevation_change_m / 100) * 0.1
            speed *= (1 - min(speed_reduction, 0.5))  # 최대 50% 감소
        
        time_hours = road.distance_km / speed
        time_minutes = time_hours * 60
        
        return time_minutes
    
    async def find_optimal_route(
        self,
        start_location_id: str,
        end_location_id: str,
        priority: str = "NORMAL"
    ) -> Optional[Route]:
        """
        A* 알고리즘으로 최적 경로 탐색
        
        Args:
            start_location_id: 시작 위치 ID
            end_location_id: 목적지 위치 ID
            priority: 우선순위 (CRITICAL은 빠른 경로 우선)
            
        Returns:
            Route: 최적 경로
        """
        try:
            if start_location_id not in self.locations or end_location_id not in self.locations:
                logger.error("❌ Invalid location IDs")
                return None
            
            start_loc = self.locations[start_location_id]
            end_loc = self.locations[end_location_id]
            
            logger.info(f"🚚 Finding route: {start_loc.name} → {end_loc.name} (Priority: {priority})")
            
            # A* 알고리즘
            # Priority Queue: (f_score, g_score, current_location_id, path)
            pq = [(0, 0, start_location_id, [start_location_id])]
            visited: Set[str] = set()
            
            # g_score: 시작점부터의 실제 비용
            g_scores = {start_location_id: 0}
            
            while pq:
                f_score, g_score, current_id, path = heapq.heappop(pq)
                
                if current_id in visited:
                    continue
                
                visited.add(current_id)
                
                # 목적지 도착
                if current_id == end_location_id:
                    # 경로 구성
                    waypoints = [self.locations[loc_id] for loc_id in path]
                    
                    # 총 거리/시간 계산
                    total_distance = 0
                    total_time = 0
                    elevation_gain = 0
                    
                    for i in range(len(path) - 1):
                        from_id = path[i]
                        to_id = path[i + 1]
                        
                        # 해당 도로 구간 찾기
                        road = next(
                            (r for r in self.road_network.get(from_id, []) if r.to_location == to_id),
                            None
                        )
                        
                        if road:
                            total_distance += road.distance_km
                            total_time += self._calculate_time(road)
                            
                            if road.elevation_change_m > 0:
                                elevation_gain += road.elevation_change_m
                    
                    route = Route(
                        route_id=f"ROUTE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        waypoints=waypoints,
                        total_distance_km=round(total_distance, 2),
                        total_time_minutes=round(total_time, 1),
                        elevation_gain_m=round(elevation_gain, 1),
                        difficulty_score=round(g_score / total_distance, 2) if total_distance > 0 else 0
                    )
                    
                    logger.info(f"✅ Route found: {route.total_distance_km}km, {route.total_time_minutes}min, +{route.elevation_gain_m}m")
                    
                    return route
                
                # 이웃 노드 탐색
                for road in self.road_network.get(current_id, []):
                    neighbor_id = road.to_location
                    
                    if neighbor_id in visited:
                        continue
                    
                    # g_score 계산 (시작점부터의 실제 비용)
                    tentative_g = g_score + self._calculate_terrain_cost(road)
                    
                    # 우선순위 부스트 (긴급 배송은 비용 할인)
                    priority_factor = self.config["priority_boost"].get(priority, 1.0)
                    if priority_factor > 1.0:
                        tentative_g /= priority_factor
                    
                    if neighbor_id not in g_scores or tentative_g < g_scores[neighbor_id]:
                        g_scores[neighbor_id] = tentative_g
                        
                        # h_score 계산 (휴리스틱: 직선 거리)
                        neighbor_loc = self.locations[neighbor_id]
                        h_score = self._haversine_distance(
                            neighbor_loc.latitude,
                            neighbor_loc.longitude,
                            end_loc.latitude,
                            end_loc.longitude
                        )
                        
                        # f_score = g_score + h_score
                        f_score = tentative_g + h_score
                        
                        new_path = path + [neighbor_id]
                        heapq.heappush(pq, (f_score, tentative_g, neighbor_id, new_path))
            
            logger.warning(f"⚠️ No route found from {start_location_id} to {end_location_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Route finding error: {str(e)}")
            return None
    
    async def optimize_multi_delivery(
        self,
        orders: List[DeliveryOrder],
        depot_location_id: str = "depot"
    ) -> List[Route]:
        """
        다중 배송 최적화 (TSP 변형)
        
        Args:
            orders: 배송 주문 리스트
            depot_location_id: 출발/도착 거점
            
        Returns:
            list: 최적화된 경로 리스트
        """
        try:
            logger.info(f"🚚 Optimizing {len(orders)} deliveries...")
            
            # 우선순위별 정렬
            priority_order = ["CRITICAL", "URGENT", "HIGH", "NORMAL", "LOW"]
            orders_sorted = sorted(
                orders,
                key=lambda o: priority_order.index(o.priority)
            )
            
            routes = []
            current_location = depot_location_id
            
            for order in orders_sorted:
                # 1. 농장 → 픽업
                farm_route = await self.find_optimal_route(
                    current_location,
                    order.farm_location.location_id,
                    priority=order.priority
                )
                
                if farm_route:
                    farm_route.orders.append(order)
                    routes.append(farm_route)
                    current_location = order.farm_location.location_id
                
                # 2. 고객 → 배송
                customer_route = await self.find_optimal_route(
                    current_location,
                    order.customer_location.location_id,
                    priority=order.priority
                )
                
                if customer_route:
                    customer_route.orders.append(order)
                    routes.append(customer_route)
                    current_location = order.customer_location.location_id
            
            # 3. 거점으로 복귀
            return_route = await self.find_optimal_route(
                current_location,
                depot_location_id,
                priority="NORMAL"
            )
            
            if return_route:
                routes.append(return_route)
            
            # 총계
            total_distance = sum(r.total_distance_km for r in routes)
            total_time = sum(r.total_time_minutes for r in routes)
            
            logger.info(f"✅ Multi-delivery optimized: {len(routes)} routes, {total_distance:.1f}km, {total_time:.1f}min")
            
            return routes
            
        except Exception as e:
            logger.error(f"❌ Multi-delivery optimization error: {str(e)}")
            return []
    
    def add_location(self, location: Location):
        """위치 추가"""
        self.locations[location.location_id] = location
        logger.info(f"✅ Location added: {location.name}")
    
    def add_road(self, road: RoadSegment):
        """도로 추가"""
        if road.from_location not in self.road_network:
            self.road_network[road.from_location] = []
        
        self.road_network[road.from_location].append(road)
        logger.info(f"✅ Road added: {road.from_location} → {road.to_location}")


# ============================================
# 싱글톤 인스턴스
# ============================================

_delivery_optimizer_instance: Optional[DeliveryOptimizer] = None


def get_delivery_optimizer() -> DeliveryOptimizer:
    """
    싱글톤 Delivery Optimizer 인스턴스
    
    Returns:
        DeliveryOptimizer: 최적화 엔진
    """
    global _delivery_optimizer_instance
    
    if _delivery_optimizer_instance is None:
        _delivery_optimizer_instance = DeliveryOptimizer()
    
    return _delivery_optimizer_instance


# ============================================
# 테스트용 메인 함수
# ============================================

async def test_delivery_optimizer():
    """Delivery Optimizer 테스트"""
    optimizer = get_delivery_optimizer()
    
    # 1. 단일 경로 최적화
    logger.info("\n=== Test 1: Single Route ===")
    route = await optimizer.find_optimal_route("depot", "farm_1", priority="NORMAL")
    
    if route:
        logger.info(f"Route: {' → '.join([w.name for w in route.waypoints])}")
        logger.info(f"Distance: {route.total_distance_km}km")
        logger.info(f"Time: {route.total_time_minutes}min")
        logger.info(f"Elevation: +{route.elevation_gain_m}m")
    
    # 2. 다중 배송 최적화
    logger.info("\n=== Test 2: Multi-Delivery ===")
    
    orders = [
        DeliveryOrder(
            order_id=1,
            customer_location=optimizer.locations["customer_1"],
            farm_location=optimizer.locations["farm_1"],
            items=[{"product": "사과", "quantity": 10}],
            priority="URGENT"
        ),
        DeliveryOrder(
            order_id=2,
            customer_location=optimizer.locations["customer_2"],
            farm_location=optimizer.locations["farm_2"],
            items=[{"product": "배추", "quantity": 5}],
            priority="NORMAL"
        )
    ]
    
    routes = await optimizer.optimize_multi_delivery(orders)
    
    for i, route in enumerate(routes):
        logger.info(f"\nRoute {i+1}: {' → '.join([w.name for w in route.waypoints])}")
        logger.info(f"  Distance: {route.total_distance_km}km")
        logger.info(f"  Time: {route.total_time_minutes}min")


if __name__ == "__main__":
    asyncio.run(test_delivery_optimizer())
