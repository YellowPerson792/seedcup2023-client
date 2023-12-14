from resp import *
from req import *
from collections import deque
import heapq
import math
import sys

action_Req = {
    'up': ActionType.MOVE_UP,
    'down': ActionType.MOVE_DOWN,
    'left': ActionType.MOVE_LEFT,
    'right': ActionType.MOVE_RIGHT,
    'silent': ActionType.SILENT,
    'place': ActionType.PLACED,
}

class Anlz(object):  
    
    bomb_info = []
    actions = []
    state = {
        'fight': False,
        'self_shield': False,
        'dying': False,
        'enemy_godness': False,
        'self_godness': False,
    }
    
    def __init__(self) -> None:
        pass   

    def codebox(self, actionResp: ActionResp, ) -> None:
        
        map=actionResp.map
        
        def return_blocktype(m, n):
            sloct=actionResp.map[m*19+n]
            if not len(sloct.objs):
                return 0
            for obj in sloct.objs:
                if obj.type == ObjType.Player:
                    for obj in sloct.objs:
                        if obj.type == ObjType.Bomb:
                            return obj.type
                    return 0                    
            for obj in sloct.objs:
                if obj.type == ObjType.Bomb:
                    return obj.type
            return sloct.objs[0].type      

        def standable(u, v, ignore_bomb=False):    
            if ignore_bomb == False:
                if return_blocktype(u, v) in [ObjType.Null, ObjType.Item]:
                    return True
                else:
                    return False  
            elif ignore_bomb == True:
                if return_blocktype(u, v) in [ObjType.Null, ObjType.Item, ObjType.Bomb]:
                    return True
                else:
                    return False

        def player_bomb_exist(p, q):
            player_exists = False
            bomb_exists = False
            for obj in map[p*19+q].objs:
                if obj.type == ObjType.Player:
                    player_exists = True
                if obj.type == ObjType.Bomb:
                    bomb_exists = True
            return player_exists and bomb_exists         
        
        def return_walkable_direction(p, q, ignore_bomb=False):
            numls=list(range(1,18))
            directions = {'right': False, 'down': False, 'left': False, 'up': False}
            if standable(p, q) or player_bomb_exist(p, q):
                if p==0 and q==0:
                    if standable(p,q+1, ignore_bomb):
                        directions['right'] = True
                    if standable(p+1,q, ignore_bomb):
                        directions['down'] = True
                elif p==0 and q==18:    
                    if standable(p,q-1, ignore_bomb):
                        directions['left'] = True
                    if standable(p+1,q, ignore_bomb):
                        directions['down'] = True
                elif p==18 and q==0:    
                    if standable(p-1,q, ignore_bomb):
                        directions['up'] = True
                    if standable(p,q+1, ignore_bomb):
                        directions['right'] = True 
                elif p==18 and q==18:    
                    if standable(p,q-1, ignore_bomb):
                        directions['left'] = True
                    if standable(p-1,q, ignore_bomb):
                        directions['up'] = True
                elif p in numls and q==0:
                    if standable(p,q+1, ignore_bomb):
                        directions['right'] = True
                    if standable(p-1,q, ignore_bomb):
                        directions['up'] = True
                    if standable(p+1,q, ignore_bomb):
                        directions['down'] = True
                elif p in numls and q==18:
                    if standable(p,q-1, ignore_bomb):
                        directions['left'] = True
                    if standable(p-1,q, ignore_bomb):
                        directions['up'] = True
                    if standable(p+1,q, ignore_bomb):
                        directions['down'] = True
                elif p==0 and q in numls:
                    if standable(p,q+1, ignore_bomb):
                        directions['right'] = True
                    if standable(p,q-1, ignore_bomb):
                        directions['left'] = True
                    if standable(p+1,q, ignore_bomb):
                        directions['down'] = True
                elif p==18 and q in numls:
                    if standable(p,q+1, ignore_bomb):
                        directions['right'] = True
                    if standable(p,q-1, ignore_bomb):
                        directions['left'] = True
                    if standable(p-1,q, ignore_bomb):
                        directions['up'] = True
                else:
                    if standable(p,q+1, ignore_bomb):
                        directions['right'] = True
                    if standable(p+1,q, ignore_bomb):
                        directions['down'] = True
                    if standable(p,q-1, ignore_bomb):
                        directions['left'] = True
                    if standable(p-1,q, ignore_bomb):
                        directions['up'] = True          
                
            result = [direction for direction, value in directions.items() if value]
            return result
                
        def direction_to_coord(m, n, dir):
            # 定义四个方向
            directions = {
                'right': (0, 1),
                'down': (1, 0),
                'left': (0, -1),
                'up': (-1, 0)
            }
            dx, dy = directions[dir]
            new_coord = (m + dx, n + dy)
            return new_coord
        
        def direction_to_delta(direction):
            if direction == 'up':
                return -1, 0
            if direction == 'down':
                return 1, 0
            if direction == 'left':
                return 0, -1
            if direction == 'right':
                return 0, 1
            return 0, 0  # 如果方向无效，返回 (0, 0)
        
        def opposite(direction):
            opposites = {'right': 'left', 'down': 'up', 'left': 'right', 'up': 'down'}
            return opposites[direction]
        
        def get_direction(self_position, next_coord):
            x, y = self_position
            next_x, next_y = next_coord
            dx = next_x - x
            dy = next_y - y
            if dx > 0:
                return 'down'
            elif dx < 0:
                return 'up'
            elif dy > 0:
                return 'right'
            elif dy < 0:
                return 'left'
    
        def search_way_bfs(start_coord, path, last_direction, ignore_bomb=False):   # 寻路函数
            queue = deque([(start_coord, path, last_direction)])
            visited_coords = set([start_coord])
            paths = []

            while queue:
                start_coord, path, last_direction = queue.popleft()
                directions = return_walkable_direction(*start_coord, ignore_bomb)
                if last_direction is not None:
                    directions = [direction for direction in directions if direction != opposite(last_direction)]
                if not directions:
                    if path not in paths:
                        paths.append(path)
                    continue
                for direction in directions:
                    new_path = path.copy()
                    new_path.append(direction)  # 添加方向到 new_path
                    new_coord = direction_to_coord(*start_coord, direction)
                    if new_coord not in visited_coords:
                        visited_coords.add(new_coord)
                        queue.append((new_coord, new_path, direction))        
            return paths
        
        # def searchway_dfs(start_coord, path, last_direction, ignore_bomb=False):   # 寻路函数
        #     stack = [(start_coord, path, last_direction)]
        #     visited_coords = set([start_coord])
        #     paths = []

        #     while stack:
        #         start_coord, path, last_direction = stack.pop()
        #         directions = return_walkable_direction(*start_coord, ignore_bomb)
        #         if last_direction is not None:
        #             directions = [direction for direction in directions if direction != opposite(last_direction)]
        #         if not directions:
        #             if path not in paths:
        #                 paths.append(path)
        #             continue
        #         for direction in directions:
        #             new_path = path.copy()
        #             new_path.append(direction)  # 添加方向到 new_path
        #             new_coord = direction_to_coord(*start_coord, direction)
        #             if new_coord not in visited_coords:
        #                 visited_coords.add(new_coord)
        #                 stack.append((new_coord, new_path, direction))  
        #     return paths
        
        def paths_to_coords(start_coord, paths): # 将方向表示的路径转换为坐标表示的路径
            coords_list = []
            if len(paths):
                for path in paths:
                    coords = [start_coord]
                    for direction in path:
                        delta = direction_to_delta(direction)
                        last_coord = coords[-1]
                        new_coord = (last_coord[0] + delta[0], last_coord[1] + delta[1])
                        coords.append(new_coord)
                    coords_list.append(coords)
            else:
                coords = [start_coord]
                coords_list.append(coords)
            return coords_list
        
        def get_coords_list(start_coord, bomb_range_with_round, ignore_bomb=False, ignore_bomb_range=False): # 获取所有路径
            bomb_range = bomb_range_with_round.keys()
            paths = search_way_bfs(start_coord, [], None, ignore_bomb)
            coords_list = paths_to_coords(start_coord, paths)
            
            new_coords_list = coords_list.copy()
            if ignore_bomb_range == False:
                for i, coords in enumerate(coords_list):
                    entered_bomb_range = False
                    for coord in coords:
                        if coord in bomb_range:
                            if entered_bomb_range:
                                new_coords = coords[:coords.index(coord)]
                                new_coords_list[i] = new_coords
                                break
                        else:
                            entered_bomb_range = True
            return new_coords_list
            
        # def get_coords_list_dfs(start_coord, bomb_range_with_round, ignore_bomb_range=False): # 获取所有路径(DFS)
        #     paths_no_bomb = searchway_dfs(start_coord, [], None, ignore_bomb=False)
        #     paths_with_bomb = searchway_dfs(start_coord, [], None, ignore_bomb=True)
        #     coords_list_no_bomb = paths_to_coords(start_coord, paths_no_bomb)
        #     coords_list_with_bomb = paths_to_coords(start_coord, paths_with_bomb)
            
        def heuristic(a, b):
            ax, ay = a
            bx, by = b
            return abs(ax - bx) + abs(ay - by)

        def a_star(start, goal, bomb_range, ignore_bomb=False, ignore_bomb_range=False):
            queue = []
            heapq.heappush(queue, (0, start))
            scores = {start: 0}
            came_from = {start: None}

            while queue:
                _, current = heapq.heappop(queue)

                if current == goal:
                    path = []
                    while current is not None:
                        path.append(current)
                        current = came_from[current]
                    path.reverse()  # reverse the path to start from the beginning
                    
                    if ignore_bomb_range == True:
                        return path
                    elif ignore_bomb_range == False:
                        in_bomb_range = True
                        for coord in path:
                            if coord not in bomb_range:
                                in_bomb_range = False
                                continue
                            if coord in bomb_range and in_bomb_range == False:
                                path = []
                                break
                            if coord in bomb_range:
                                continue
                        return path

                for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # right, down, left, up
                    neighbor = (current[0] + direction[0], current[1] + direction[1])
                    if 0 <= neighbor[0] <= 18 and 0 <= neighbor[1] <= 18:
                        if standable(neighbor[0], neighbor[1], ignore_bomb):  # check if neighbor is passable
                            tentative_score = scores[current] + 1
                            if neighbor not in scores or tentative_score < scores[neighbor]:
                                scores[neighbor] = tentative_score
                                priority = tentative_score + heuristic(goal, neighbor)
                                heapq.heappush(queue, (priority, neighbor))
                                came_from[neighbor] = current

            return []  # return None if there is no path to the goal
                                
        def get_present_round():
            present_round = actionResp.round
            return present_round
        
        def get_self_position(self_id):  # 获取自己的坐标
            for loct in map:
                for obj in loct.objs:
                    if obj.type == ObjType.Player and obj.property.player_id == self_id:
                        return (loct.x, loct.y)
            return None
        
        def get_nearest_enemy_position(self_position):   # 获取敌人的坐标
            player_id = actionResp.player_id
            enemy_coord = []
            distances = []
            for loct in map:
                for obj in loct.objs:
                    if obj.type == ObjType.Player and obj.property.player_id != player_id:
                        enemy_coord.append((loct.x, loct.y))
            
            for coord in enemy_coord:
                distance = abs(coord[0] - self_position[0]) + abs(coord[1] - self_position[1])
                distances.append(distance)
            
            if distances:
                min_distance = min(distances)
                nearest_enemy_coord = enemy_coord[distances.index(min_distance)]
                return nearest_enemy_coord

            return None
        
        def get_nearest_enemy_id(enemy_position): # 获取最近的敌人的 id
            if enemy_position is not None:
                for obj in map[enemy_position[0]*19+enemy_position[1]].objs:
                    if obj.type == ObjType.Player and obj.property.player_id != self_id:
                        enemy_id = obj.property.player_id
                        return enemy_id
            return None
        
        def get_all_players_properties():  # 获取所有玩家的属性
            properties = {}
            for loct in map:
                for obj in loct.objs:
                    if obj.type == ObjType.Player:
                        properties[obj.property.player_id] = obj.property

            return properties
        
        def get_bomb_info(bomb_info, map):  # 获取所有炸弹的坐标
            old_bomb_id_list = []
            new_bomb_id_list = []
            if len(bomb_info):
                for bomb in bomb_info:
                    old_bomb_id_list.append(bomb['id'])
            for map in map:
                for obj in map.objs:
                    if obj.type == ObjType.Bomb:
                        coord = (map.x, map.y)
                        bomb_id = obj.property.bomb_id
                        new_bomb_id_list.append(bomb_id)
                        if bomb_id not in old_bomb_id_list:
                            bomb_info.append({'position': coord, 'id': bomb_id, 'place_round': present_round-1, \
                                'player': obj.property.player_id, 'range': obj.property.bomb_range})
                        elif bomb_id in old_bomb_id_list:
                            if coord != bomb_info[old_bomb_id_list.index(bomb_id)]['position']:
                                bomb_info[old_bomb_id_list.index(bomb_id)]['position'] = coord
            
            def remove_unused_bombs(bomb_info, new_id_list):
                for bomb in bomb_info.copy():
                    if bomb['id'] not in new_id_list:
                        bomb_info.remove(bomb)
                return bomb_info
            bomb_info = remove_unused_bombs(bomb_info, new_bomb_id_list)
                    
        def get_bomb_range(bomb_info):  # 获取所有炸弹的爆炸范围     # 要加入对炸弹运动的考虑
            bomb_ranges = set()
            bomb_range_with_explode_round = {}
            if len(bomb_info):
                for bomb in bomb_info:
                    x = bomb['position'][0]
                    y = bomb['position'][1]
                    self_in_bomb = False
                    explode_round = bomb['place_round'] + 5
                    bomb_range = bomb['range']
                    for direction in [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
                        if direction == (0, 0):
                            self_in_bomb = True
                        for i in range(1, bomb_range + 1):
                            new_position_x = x + i * direction[0]
                            new_position_y = y + i * direction[1]
                            new_position = (new_position_x, new_position_y)
                            if 0 <= new_position_x < 19 and 0 <= new_position_y < 19:
                                if self_in_bomb == True and new_position not in bomb_ranges:
                                    bomb_ranges.add((new_position_x, new_position_y))
                                    bomb_range_with_explode_round[new_position] = explode_round
                                if self_in_bomb == False and new_position not in bomb_ranges:
                                    _continue = False
                                    _continue = \
                                        not any(obj.type == ObjType.Bomb for obj in map[new_position_x * 19 + new_position_y].objs) and \
                                        not any(obj.type == ObjType.Block for obj in map[new_position_x * 19 + new_position_y].objs)
                                    if _continue == True:
                                        bomb_ranges.add(new_position)
                                        bomb_range_with_explode_round[new_position] = explode_round
                                    else:
                                        break

            # 过滤 bomb_range_with_explode_round 列表，只保留 explode_round 最小的元素
            filtered_bomb_range_with_explode_round = {}
            if len(bomb_range_with_explode_round):
                for new_position, explode_round in bomb_range_with_explode_round.items():
                    if new_position not in filtered_bomb_range_with_explode_round or explode_round < filtered_bomb_range_with_explode_round[new_position]:
                        filtered_bomb_range_with_explode_round[new_position] = explode_round

            return filtered_bomb_range_with_explode_round
        
        def get_surounding_block_property(coord, map): # 检查周围的方块
            x, y = coord
            directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
            blocks_property = {}
            for direction, (dx, dy) in directions.items():
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < 19 and 0 <= new_y < 19:
                    block_properties = [obj.property for obj in map[new_x * 19 + new_y].objs]
                    blocks_property[direction] = block_properties
            return blocks_property
        
        def check_removable(coord, map): # 检查周围可移除的方块
            blocks_property = get_surounding_block_property(coord, map)
            for block_properties in blocks_property.values():
                for property in block_properties:
                    if hasattr(property, 'removable') and property.removable:
                        return True
            return False
        
        def calculate_distance(start_coord, target, ignore_bomb=False, ignore_bomb_range=False): # 计算目标点到当前位置的距离
            distance = float('inf')
            path_to_target = a_star(start_coord, target, [], ignore_bomb, ignore_bomb_range)
            if path_to_target:
                distance = len(path_to_target) - 1
            return distance
            
            # exit_flag = False
            # for coords in coords_list:
            #     if exit_flag:
            #         break
            #     count = -1
            #     for coord in coords:
            #         count += 1
            #         if coord == target:
            #             exit_flag = True
            #             break
            # return count
            
        def cal_distance(start_coord, target_coord):
            return abs(start_coord[0] - target_coord[0]) + abs(start_coord[1] - target_coord[1])
            
        def calculate_required_round(start_coord, target_coord, property):
            distance = calculate_distance(start_coord, target_coord)
            require_round = distance // property.speed + 1
            return require_round
        
        def cal_required_round(start_coord, target_coord, property):
            distance = cal_distance(start_coord, target_coord)
            require_round = distance // property.speed + 1
            return require_round
        
        def get_attack_range(): 
            enemy_x, enemy_y = enemy_position  
            attack_coords_list = \
            [(enemy_x + dx, enemy_y + dy) for dx in range(-2, 3) for dy in range(-2 + abs(dx), 3 - abs(dx))]
            return attack_coords_list
        
        def is_reachable(coord, bomb_range):
            path = a_star(self_position, coord, bomb_range)
            if path:
                return True
            return False
        
        def get_check_range(start_point, speed, bomb_range):
            
            square_coords = [(start_point[0] + dx, start_point[1] + dy) 
                                 for dx in range(-speed, speed + 1) 
                                 for dy in range(-speed, speed + 1)
                                 if 0 <= start_point[0] + dx < 19 and 0 <= start_point[1] + dy < 19]
            
            # Filter out the coordinates that you can't reach
            reachable_coords = [coord for coord in square_coords if is_reachable(coord, bomb_range)]
            return reachable_coords
        
        def get_no_godness_coord(godness_enemy_position, bomb_range):   # 获取远离女神的安全坐标
            
            def get_farthest_coord_from_enemy():

                check_range = get_check_range(self_position, self_property.speed, bomb_range)

                # Check if there are any reachable coordinates
                if check_range:
                    # Find the coordinate that is farthest from the enemy
                    farthest_coord = max(check_range, key=lambda coord: cal_distance(coord, godness_enemy_position))
                else:
                    # If there are no reachable coordinates, return None
                    farthest_coord = None

                return farthest_coord

            no_godness_point = get_farthest_coord_from_enemy()
            return no_godness_point
            
            # coords_list_from_enemy, _ = get_coords_list(enemy_position, bomb_range_with_round)
            # enemy_coords = []
            # escape_coords = []
            # no_godness_target_coord = None
            # for coords in coords_list_from_enemy:
            #     if self_position in coords:
            #         enemy_coords = coords
            #         break
            # if self_position in enemy_coords:
            #     self_coord_idx = enemy_coords.index(self_position)
            #     escape_coords = enemy_coords[self_coord_idx:]
            #     if len(escape_coords) > self_property.speed:
            #         no_godness_target_coord = escape_coords[self_property.speed]
            #         return no_godness_target_coord
            #     else:
            #         no_godness_target_coord = escape_coords[-1]
            #         return no_godness_target_coord
            # return None
            
        def get_bomb_block_point(coords_list, map, bomb_info, imagin_place): # 获取放炸弹的坐标(收集资源阶段)
            bomb_positions = set(bomb['position'] for bomb in bomb_info)
            bomb_block_coord_list = []
            start_coord = coords_list[0][0]
            for coords in coords_list:
                for coord in (coords[1:] if imagin_place else coords):
                    if check_removable(coord, map) and forseen_bomb_place_escapable(coord, bomb_info) and self_position not in bomb_positions:
                        bomb_block_coord_list.append(coord)
                        break
            min_distance = float('inf')
            nearest_bomb_block_coord = None
            for bomb_block_coord in bomb_block_coord_list:
                distance = cal_distance(start_coord, bomb_block_coord)
                if distance <= min_distance:
                    min_distance = distance
                    nearest_bomb_block_coord = bomb_block_coord
            return nearest_bomb_block_coord
                        
        def find_safe_coords(round, coords_list, bomb_range_with_round, property): # 寻找安全坐标
            safe_coords = []
            start_coord = coords_list[0][0]
            bomb_range = bomb_range_with_round.keys()
            if start_coord in bomb_range:
                for coords in coords_list:
                    for coord in coords:
                        reach_round = round + cal_required_round(start_coord, coord, property)
                        if coord in bomb_range:
                            bomb_round = bomb_range_with_round[coord]
                            if reach_round <= bomb_round:
                                continue
                            elif reach_round > bomb_round:
                                break
                        elif coord not in bomb_range:
                            safe_coords.append(coord)
                            break
            return safe_coords  
        
        # safe_coords = []
            # path_to_safe_coords = []
            # bomb_range = bomb_range_with_round.keys()
            # if start_coord in bomb_range:
            #     check_range = get_check_range(start_coord, 5, bomb_range)
            #     coords_not_in_bomb_range = [coord for coord in check_range if coord not in bomb_range]
            #     for coord in coords_not_in_bomb_range:
            #         path = a_star(start_coord, coord, bomb_range_with_round, ignore_bomb_range=True)
            #         path_to_safe_coords.append(path)
            #     for coords in path_to_safe_coords:
            #         for coord in coords:
            #             reach_round = round + cal_required_round(start_coord, coord, property)
            #             if coord in bomb_range:
            #                 bomb_round = bomb_range_with_round[coord]
            #                 if reach_round <= bomb_round:
            #                     continue
            #                 elif reach_round > bomb_round:
            #                     break
            #             elif coord not in bomb_range:
            #                 safe_coords.append(coord)
            #                 break
            # return safe_coords
        
        def find_best_safe_coord(safe_coords):
            # if not safe_coords:
            #     return None  # Return None if there are no safe coordinates

            # # Find the coordinate that is closest to start_coord
            # best_safe_coord = min(safe_coords, key=lambda coord: cal_required_round(start_coord, coord, property))

            # return best_safe_coord
            
            coords_sum_list = []
            for coord in safe_coords:
                forseen_coords_list = get_coords_list(coord, bomb_range_with_round)
                coords_sum = sum([len(coords) for coords in forseen_coords_list])
                coords_sum_list.append(coords_sum)
            if len(coords_sum_list):
                max_coords_sum_index = coords_sum_list.index(max(coords_sum_list))
                return safe_coords[max_coords_sum_index]
            return None
        
        def get_cut_points(bomb_info, bomb_range):        # 获取切路坐标
                    
            def get_surrounding_coords(enemy_coord):
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                surrounding_coords = []
                for dx, dy in directions:
                    x, y = enemy_coord[0] + dx, enemy_coord[1] + dy
                    if 0 <= x <= 18 and 0 <= y <= 18 and standable(x, y):
                        if forseen_bomb_place_escapable((x, y), bomb_info):
                            surrounding_coords.append((x, y))
                return surrounding_coords
                    
            def distance_to_self(coord):
                return (abs(coord[0] - self_position[0]) + abs(coord[1] - self_position[1]))

            cut_points = get_surrounding_coords(enemy_position)

            # Check if each cut_point is reachable, and remove it from cut_points if it is not
            # cut_points = [cut_point for cut_point in cut_points if is_reachable(cut_point, bomb_range)]

            # Sort cut_points according to the distance to yourself
            cut_points = sorted(cut_points, key=distance_to_self)

            return cut_points
        
        
        def get_push_bomb_point(bomb_info, coords_list_ignore_bomb): # 获取推炸弹的坐标
            bomb_positions = set(bomb['position'] for bomb in bomb_info)
            push_points = []
            push_point = None
            for coords in coords_list_ignore_bomb:
                for coord in coords[1:]:
                    if coord in bomb_positions:
                        push_points.append(coord)
                        break
            if len(push_points):
                push_point = push_points[0]
            return push_point
        
        # def get_random_point(coords_list, bomb_range_with_round):
        #     bomb_range = list(bomb_range_with_round.keys())
        #     # 创建一个新的列表，其中包含所有在 coords_list 中的坐标，但不在 bomb_range 中的坐标
        #     valid_coords = [coord for coords in coords_list for coord in coords if coord not in bomb_range and 0 <= coord[0] < 15 and 0 <= coord[1] < 15]
        #     # 从 valid_coords 中选择一个随机坐标
        #     random_point = random.choice(valid_coords) if valid_coords else None
        #     return random_point
                
        def get_fatal_points(bomb_info, bomb_range_with_round): # 获取必杀坐标
            
            # def modify_enemy_coords_list(original_coords_list, _coord):
            #     coords_list = original_coords_list.copy()
            #     for i, coords in enumerate(original_coords_list):
            #         for j, coord in enumerate(coords):
            #             if coord == _coord:
            #                 modified_coords = coords[:j+1]
            #                 coords_list[i] = modified_coords
            #     # print("敌人路径：", coords_list)
            #     return coords_list
                
            fatal_points = []
            coords_list_from_enemy = get_coords_list(enemy_position, bomb_range_with_round)
            for coords in coords_list_from_enemy:
                for coord in coords[1:]:
                    # forseen_coords_list = modify_enemy_coords_list(coords_list_from_enemy, coord)
                    forseen_bomb_info = get_forseen_bomb_info(coord, bomb_info)
                    forseen_bomb_range_with_round = get_bomb_range(forseen_bomb_info)
                    forseen_coords_list = get_coords_list(enemy_position, forseen_bomb_range_with_round)
                    enemy_safe_coords = find_safe_coords(present_round + 1, forseen_coords_list, forseen_bomb_range_with_round, \
                            nearest_enemy_property)
                    # print("坐标和敌人安全坐标：", coord, enemy_safe_coords)
                    if not enemy_safe_coords:
                        fatal_points.append(coord)
                        break
            # print("必杀坐标：", fatal_points)
            return fatal_points
        
        
        def get_nearest_fatal_point(start_coord, fatal_points):
            if not fatal_points:
                return None
            nearest_fatal_point = min(fatal_points, key=lambda point: cal_distance(start_coord, point))
            return nearest_fatal_point
                     
        def get_item_position_list(start_coord, bomb_range, map, forseen=False):
            item_position_list = []
            for map in map:
                coord = (map.x, map.y)
                for obj in map.objs:
                    if obj.type == ObjType.Item:
                        if is_reachable(coord, bomb_range):
                            item_position_list.append(coord)
            if forseen == True:
                for position in item_position_list:
                    if position == start_coord:
                        item_position_list.remove(position)
            return item_position_list
            
        def get_nearest_item_position(start_coord, item_position_list):
            if not item_position_list:
                return None  
            distances = [cal_distance(start_coord, item) for item in item_position_list]
            min_index = distances.index(min(distances))
            return item_position_list[min_index]

        def get_forseen_bomb_info(place_coord, bomb_info):
            forseen_bomb_info = bomb_info.copy()
            if place_coord is not None:
                requrid_round = cal_required_round(self_position, place_coord, self_property)
                place_round = present_round + requrid_round
                forseen_bomb_info.append({'position': place_coord, 'id': -1, 'place_round': place_round, \
                    'player': self_property.player_id, 'range': self_property.bomb_range})
            return forseen_bomb_info
        
        def get_forseen_target_point(forseen_coords_list, forseen_bomb_range_with_round, \
            forseen_bomb_info, forseen_round, cut_idx):
            
            start_coord = forseen_coords_list[0][0]
            forseen_bomb_range = forseen_bomb_range_with_round.keys()
            forseen_cut_points = get_cut_points(forseen_bomb_info, forseen_bomb_range)
            if len(forseen_cut_points) and cut_idx < len(forseen_cut_points):
                forseen_cut_point = (forseen_cut_points[cut_idx] if self.state['fight'] == True else None)
            else:
                forseen_cut_point = None
            # if forseen_cut_point is None:
            #     forseen_bomb_block_point = get_bomb_block_point(forseen_coords_list, map, forseen_bomb_info, imagin_place=True)    # 可能有问题
            # else:
            #     forseen_bomb_block_point = None
            forseen_bomb_block_point = get_bomb_block_point(forseen_coords_list, map, forseen_bomb_info, imagin_place=True)
            forseen_safe_coords = find_safe_coords(forseen_round, forseen_coords_list, forseen_bomb_range_with_round, self_property)
            forseen_best_safe_coord = find_best_safe_coord(forseen_safe_coords)
            forseen_item_list = get_item_position_list(start_coord, forseen_bomb_range, map, forseen=True)
            forseen_item_coord = get_nearest_item_position(start_coord, forseen_item_list)
            forseen_nearest_enemy_position = get_nearest_enemy_position(start_coord)
            forseen_enemy_position = (None if (start_coord == enemy_position) else forseen_nearest_enemy_position)
            no_godness_point = None
            forseen_push_bomb_point = None
            forseen_fatal_point = None
            forseen_target_point = select_and_combine_target_point(forseen_best_safe_coord, forseen_bomb_block_point, \
                        forseen_item_coord, forseen_enemy_position, no_godness_point, forseen_cut_point, forseen_push_bomb_point, forseen_fatal_point)
            return forseen_target_point
        
        def forseen_bomb_place_escapable(place_coord, bomb_info):      
            if place_coord is not None:
                requrid_round = cal_required_round(self_position, place_coord, self_property)
                place_round = present_round + requrid_round
                forseen_bomb_info = get_forseen_bomb_info(place_coord, bomb_info)
                bomb_range_with_round = get_bomb_range(forseen_bomb_info)
                forseen_start_coord = place_coord
                forseen_coords_list = []
                forseen_coords_list= get_coords_list(forseen_start_coord, bomb_range_with_round)
                forseen_safe_coords = []
                forseen_safe_coords = find_safe_coords(place_round, forseen_coords_list, bomb_range_with_round, self_property)
                if len(forseen_safe_coords):
                    return True
                return False
        
        def select_and_combine_target_point(best_safe_coord, bomb_block_point, item_coord, enemy_point, \
            no_godness_point, cut_point, push_bomb_point, fatal_point): # 刷新目标点
            target_point = {
                'fatal_point': None,       
                'cut_point': None,
                'push_bomb_point': None,
                'no_godness_point': None,
                'safe_point': None,
                'item_point': None,
                'bomb_block_point': None, 
                'enemy_point': None,
                }   
            if best_safe_coord is not None:
                target_point['safe_point'] = best_safe_coord
            if bomb_block_point is not None:
                target_point['bomb_block_point'] = bomb_block_point
            target_point['item_point'] = item_coord
            if self.state['fight'] == True:   
                target_point['enemy_point'] = enemy_point
            if no_godness_point is not None:
                target_point['no_godness_point'] = no_godness_point
            if cut_point is not None:
                target_point['cut_point'] = cut_point
            if push_bomb_point is not None:
                target_point['push_bomb_point'] = push_bomb_point
            if fatal_point is not None:
                target_point['fatal_point'] = fatal_point
            return target_point

        def transform_target_point_to_coords(target_type, start_coord, target_coord, bomb_range_with_round):
            target_coords = []
            bomb_range = bomb_range_with_round.keys()
            if target_type == 'push_bomb_point' or target_type == 'no_godness_point' or target_type == 'fatal_point':
                target_coords = a_star(start_coord, target_coord, bomb_range, ignore_bomb=True, ignore_bomb_range=True)
            elif target_type == 'enemy_point':
                target_coords = a_star(start_coord, target_coord, bomb_range, ignore_bomb=True, ignore_bomb_range=True)
            elif self.state['fight'] == True and self.state['self_shield'] == True:
                target_coords = a_star(start_coord, target_coord, bomb_range, ignore_bomb=True, ignore_bomb_range=True)
            else:
                target_coords = a_star(start_coord, target_coord, bomb_range)
            return target_coords
        
        def change_state(self_property, enemy_property, best_safe_coord, bomb_range): # 改变状态
            if self_position in bomb_range and best_safe_coord == None:
                self.state['dying'] = True
            else:
                self.state['dying'] = False
            
            if self.state['fight'] == False:
                path_to_enemy = a_star(self_position, enemy_position, [], ignore_bomb=True, ignore_bomb_range=True)
                if path_to_enemy:
                    self.state['fight'] = True
                
            if self.state['fight'] == True:
                if self_property.invincible_time > 0:
                    self.state['self_godness'] = True
                else:
                    self.state['self_godness'] = False
                if enemy_property.invincible_time > 0:
                    self.state['enemy_godness'] = True
                else:
                    self.state['enemy_godness'] = False
                if self_property.shield_time > 5:
                    self.state['self_shield'] = True
                else:
                    self.state['self_shield'] = False
        
        def create_action_list(state, action_list, coords_list, target_point, round, bomb_info, \
            bomb_range_with_round, recursion_times=0):
            
            max_action_times = self_property.speed
            left_action_times = max_action_times - len(action_list)
            start_coord = coords_list[0][0]
            
            target_types = [type for type in target_point.keys() if target_point[type] is not None]
            # target_point = transform_target_point_to_coords(start_coord, target_point, bomb_range)
            action_target_coords = []
            action_target_coord = None   
            
            if state['fight'] == False:
                priority_list = ['safe_point', 'item_point', 'bomb_block_point']
            
            if state['fight'] == True:
                priority_list = ['fatal_point', 'safe_point', 'item_point', 'cut_point' , 'bomb_block_point']
                
                if state['self_shield'] == True:
                    priority_list = ['fatal_point', 'item_point', 'cut_point', 'bomb_block_point', 'safe_point']
                
                if state['self_godness'] == True and self_property.invincible_time >= nearest_enemy_property.invincible_time:
                    priority_list = ['enemy_point', 'item_point', 'safe_point', 'bomb_block_point']
                elif state['self_godness'] == True and self_property.invincible_time < nearest_enemy_property.invincible_time:
                    priority_list = ['no_godness_point', 'safe_point', 'item_point', 'bomb_block_point']
                elif state['self_godness'] == False and state['enemy_godness'] == True:
                    priority_list = ['no_godness_point', 'safe_point', 'item_point', 'bomb_block_point']
                elif state['self_godness'] == False and state['enemy_godness'] == False and state['self_shield'] == False:
                    priority_list = ['fatal_point', 'safe_point', 'item_point', 'cut_point', 'bomb_block_point']
                
                if state['dying'] == True:
                    priority_list = ['push_bomb_point']
                    
            target_type = None
            for type in priority_list:
                if type in target_types:
                    target_type = type
                    target_coord = target_point[type]
                    # print("target_type, start_coord, target_coord: ", target_type, start_coord, target_coord)
                    action_target_coords = transform_target_point_to_coords(target_type, start_coord, target_coord, bomb_range_with_round)
                    break
            if len(action_target_coords):
                action_target_coord = action_target_coords[-1]
                
            print("行动的目标点及其类型：", action_target_coord, target_type)
            if action_target_coord is not None:
                distance_to_target = len(action_target_coords) - 1
                
                action_list_p = []  # 情况1：不能一次性到达目标点
                if distance_to_target >= left_action_times:
                    for i in range(left_action_times):
                        direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                        action_list_p.append(direction)
                    if target_point == 'no_godness_point':
                        action_list_p.insert(0, 'place')        
                    action_list.extend(action_list_p)
                
                elif distance_to_target < left_action_times: # 情况2：可以一次性到达目标点
                    action_times_p = distance_to_target
                    forseen_round = round + cal_required_round(start_coord, action_target_coord, self_property)
                    forseen_bomb_range_with_round = bomb_range_with_round
                    
                    if target_type == 'push_bomb_point':
                        for i in range(action_times_p):
                            direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                            action_list_p.append(direction)
                        forseen_bomb_info = bomb_info
                        forseen_coords_list = get_coords_list(action_target_coord, forseen_bomb_range_with_round)        #有必要？
                        forseen_target_point = get_forseen_target_point(forseen_coords_list, bomb_range_with_round, \
                            forseen_bomb_info, forseen_round, recursion_times)
                    elif target_type == 'no_godness_point':
                        for i in range(action_times_p):
                            direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                            action_list_p.append(direction)
                        forseen_bomb_info = bomb_info
                        forseen_coords_list = get_coords_list(action_target_coord, forseen_bomb_range_with_round)
                        forseen_target_point = get_forseen_target_point(forseen_coords_list, bomb_range_with_round, \
                            forseen_bomb_info, forseen_round, recursion_times)
                        action_list_p.insert(0, 'place')
                    elif target_type == 'cut_point':        # cut_point 有待改进
                        action_times_p += 1
                        for i in range(action_times_p):
                            if i < action_times_p - 1:
                                direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                                action_list_p.append(direction)
                            elif i == action_times_p - 1:
                                action_list_p.append('place')       
                        forseen_bomb_info = get_forseen_bomb_info(action_target_coord, bomb_info)
                        forseen_bomb_range_with_round = get_bomb_range(forseen_bomb_info)
                        forseen_coords_list = get_coords_list(action_target_coord, forseen_bomb_range_with_round)
                        forseen_target_point = get_forseen_target_point(forseen_coords_list, forseen_bomb_range_with_round, \
                            forseen_bomb_info, forseen_round, recursion_times)
                    elif target_type == 'bomb_block_point':
                        action_times_p += 1
                        for i in range(action_times_p):
                            if i < action_times_p - 1:
                                direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                                action_list_p.append(direction)
                            elif i == action_times_p - 1:
                                action_list_p.append('place')       
                        forseen_bomb_info = get_forseen_bomb_info(action_target_coord, bomb_info)
                        forseen_bomb_range_with_round = get_bomb_range(forseen_bomb_info)
                        forseen_coords_list = get_coords_list(action_target_coord, forseen_bomb_range_with_round)
                        forseen_target_point = get_forseen_target_point(forseen_coords_list, forseen_bomb_range_with_round, \
                            forseen_bomb_info, forseen_round, recursion_times)
                    else:
                        for i in range(action_times_p):
                            direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                            action_list_p.append(direction)
                        forseen_bomb_info = bomb_info
                        forseen_coords_list = get_coords_list(action_target_coord, forseen_bomb_range_with_round)
                        forseen_target_point = get_forseen_target_point(forseen_coords_list, bomb_range_with_round, \
                            forseen_bomb_info, forseen_round, recursion_times)
                    
                    if len(action_list_p):
                        action_list.extend(action_list_p)
                    if len(action_list) < max_action_times:
                        create_action_list(state, action_list, forseen_coords_list, forseen_target_point, \
                            forseen_round, forseen_bomb_info, forseen_bomb_range_with_round, recursion_times+1)
                    else:
                        action_list = action_list[:max_action_times]
            
                
        
        present_round = get_present_round()                         # 获取一些基本信息
        all_player_properties = get_all_players_properties()
       
        self_id = actionResp.player_id
        self_position = get_self_position(self_id) 
        try:
            self_property = all_player_properties[self_id] 
        except:
            exit("Game Over")
        enemy_position = get_nearest_enemy_position(self_position)
        nearest_enemy_id = get_nearest_enemy_id(enemy_position)
        nearest_enemy_property = all_player_properties[nearest_enemy_id]
        
        get_bomb_info(self.bomb_info, map)                           
        bomb_range_with_round = get_bomb_range(self.bomb_info)
        bomb_range = bomb_range_with_round.keys()
        
        start_coord = self_position                
        coords_list = get_coords_list(start_coord, bomb_range_with_round)        
        
        safe_coords = find_safe_coords(present_round, coords_list, bomb_range_with_round, self_property)
        best_safe_coord = find_best_safe_coord(safe_coords)
        
        change_state(self_property, nearest_enemy_property, best_safe_coord, bomb_range)

        item_list = get_item_position_list(self_position, bomb_range, map, forseen=False)
        item_coord = get_nearest_item_position(self_position, item_list)

        if self.state['fight'] == True:
            # attack_range = get_attack_range()
            if self.state['enemy_godness'] == True:
                no_godness_point = get_no_godness_coord(enemy_position, bomb_range)
            else:
                no_godness_point = None
            cut_points = get_cut_points(self.bomb_info, bomb_range)
            if len(cut_points):
                cut_point = cut_points[0]
            else:
                cut_point = None
        else:
            no_godness_point = None
            cut_point = None
            # attack_range = None
            
        # if cut_point is None:
        #     bomb_block_point = get_bomb_block_point(coords_list, map, self.bomb_info, imagin_place=False)
        # else:
        #     bomb_block_point = None
        bomb_block_point = get_bomb_block_point(coords_list, map, self.bomb_info, imagin_place=False)
        
        if self.state['dying'] == True:
            coords_list_ignore_bomb = get_coords_list(start_coord, bomb_range_with_round, ignore_bomb=True)
            push_bomb_point = get_push_bomb_point(self.bomb_info, coords_list_ignore_bomb)
        else:
            push_bomb_point = None
        
        fatal_point = None
        if self.state['fight'] == True and cal_required_round(start_coord, enemy_position, self_property) <= 1:
            fatal_points = get_fatal_points(self.bomb_info, bomb_range_with_round)
            fatal_point = get_nearest_fatal_point(start_coord, fatal_points)
        
        target_point = select_and_combine_target_point(best_safe_coord, bomb_block_point, item_coord, enemy_position, \
            no_godness_point, cut_point, push_bomb_point, fatal_point)
        
        action_list = []
        bomb_info = self.bomb_info
        create_action_list(self.state, action_list, coords_list, target_point, present_round, bomb_info, bomb_range_with_round)
        
        # if self.state['fight'] == True and self.state['self_godness'] == False and self.state['enemy_godness'] == False and \
        #     self_position in attack_range and forseen_bomb_place_escapable(self_position, self.bomb_info):
            
        #     action_list.insert(0, 'place')
        
        self.actions = action_list
        
        # print("致命点：", fatal_point)
        print("当前状态：", self.state)
        print("目标点：", target_point)
        print("行动列表：", action_list)
        print("切路坐标：", cut_point)
        print("目的安全坐标：", best_safe_coord)
        print("安全坐标：", safe_coords)
        print("开路坐标：", bomb_block_point)
        print("即将爆炸坐标及爆炸回合：\n", bomb_range_with_round)
        1
        # print("路径（方向表示）：")
        # for path in paths:
        #     print(path) 
        # print("路径（坐标表示）：")
        # for coords in coords_list:
        #     print(coords)
                 


    def action_req_send(self): # 发送行动请求
        return [action_Req[key] for key in self.actions]

        


