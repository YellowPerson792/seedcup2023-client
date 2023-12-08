from resp import *
from req import *
from collections import deque

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
    actions = ['silent','silent']
    state = {
        'fight': False,
        'enemy_godness': False,
        'self_godness': False,
    }
    
    def __init__(self) -> None:
        pass   

    def codebox(self, actionResp: ActionResp, ) -> None:
        
        map=actionResp.map
        
        def blocktype(m,n):
            sloct=actionResp.map[m*15+n]
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

        def ifstad(u,v):    
            if blocktype(u,v) in [ObjType.Null, ObjType.Item]:
                return True
            else:
                return False  

        def player_bomb_exist(p, q):
            player_exists = False
            bomb_exists = False
            for obj in map[p*15+q].objs:
                if obj.type == ObjType.Player:
                    player_exists = True
                if obj.type == ObjType.Bomb:
                    bomb_exists = True
            return player_exists and bomb_exists         
        
        def sigfidway(p, q):
            numls=list(range(1,14))
            directions = {'right': False, 'down': False, 'left': False, 'up': False}
            if ifstad(p,q) or player_bomb_exist(p, q):
                if p==0 and q==0:
                    if (ifstad(p,q+1)):
                        directions['right'] = True
                    if (ifstad(p+1,q)):
                        directions['down'] = True
                elif p==0 and q==14:    
                    if (ifstad(p,q-1)):
                        directions['left'] = True
                    if (ifstad(p+1,q)):
                        directions['down'] = True
                elif p==14 and q==0:    
                    if (ifstad(p-1,q)):
                        directions['up'] = True
                    if (ifstad(p,q+1)):
                        directions['right'] = True 
                elif p==14 and q==14:    
                    if ifstad(p,q-1):
                        directions['left'] = True
                    if ifstad(p-1,q):
                        directions['up'] = True
                elif (p in numls) and (q==0):
                    if ifstad(p,q+1):
                        directions['right'] = True
                    if ifstad(p-1,q):
                        directions['up'] = True
                    if ifstad(p+1,q):
                        directions['down'] = True
                elif (p in numls) and (q==14):
                    if ifstad(p,q-1):
                        directions['left'] = True
                    if ifstad(p-1,q):
                        directions['up'] = True
                    if ifstad(p+1,q):
                        directions['down'] = True
                elif (p==0) and (q in numls):
                    if ifstad(p,q+1):
                        directions['right'] = True
                    if ifstad(p,q-1):
                        directions['left'] = True
                    if ifstad(p+1,q):
                        directions['down'] = True
                elif (p==14) and (q in numls):
                    if ifstad(p,q+1):
                        directions['right'] = True
                    if ifstad(p,q-1):
                        directions['left'] = True
                    if ifstad(p-1,q):
                        directions['up'] = True
                else:
                    if ifstad(p,q+1):
                        directions['right'] = True
                    if ifstad(p+1,q):
                        directions['down'] = True
                    if ifstad(p,q-1):
                        directions['left'] = True
                    if ifstad(p-1,q):
                        directions['up'] = True          
            
            result = [direction for direction, value in directions.items() if value]
            return result
                
        def caculat(m, n, dir):
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
    
        # def findway(coord, path, last_direction):   # 寻路函数
        #     if coord in visited_coords:  # 检查坐标是否已访问
        #         return
        #     visited_coords.add(coord)  # 添加坐标到已访问集合 
        #     is_in_bomb_range = False
        #     if coord in bomb_range:
        #         is_in_bomb_range = True        
        #     directions = sigfidway(*coord, is_in_bomb_range)
        #     if last_direction is not None:
        #         directions = [direction for direction in directions if direction != opposite(last_direction)]
        #     if not directions:
        #         if path not in paths:
        #             paths.append(path)
        #         return
        #     for direction in directions:
        #         new_path = path.copy()
        #         new_path.append(direction)  # 添加方向到 new_path
        #         new_coord = caculat(*coord, direction)
        #         findway(new_coord, new_path, direction) 

        def findway(start_coord, path, last_direction):   # 寻路函数
            queue = deque([(start_coord, path, last_direction)])
            visited_coords = set([start_coord])
            paths = []

            while queue:
                start_coord, path, last_direction = queue.popleft()
                directions = sigfidway(*start_coord)
                if last_direction is not None:
                    directions = [direction for direction in directions if direction != opposite(last_direction)]
                if not directions:
                    if path not in paths:
                        paths.append(path)
                    continue
                for direction in directions:
                    new_path = path.copy()
                    new_path.append(direction)  # 添加方向到 new_path
                    new_coord = caculat(*start_coord, direction)
                    if new_coord not in visited_coords:
                        visited_coords.add(new_coord)
                        queue.append((new_coord, new_path, direction))        
            return paths

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

        def opposite(direction):
            opposites = {'right': 'left', 'down': 'up', 'left': 'right', 'up': 'down'}
            return opposites[direction]
        
        def get_coords_list(start_coord, bomb_range_with_round): # 获取所有路径
            path = []
            paths = findway(start_coord, path, None)
            coords_list = paths_to_coords(start_coord, paths)
            bomb_range = bomb_range_with_round.keys()
            
            new_coords_list = coords_list.copy()
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
        
        def get_self_position():  # 获取自己的坐标
            player_id = actionResp.player_id
            for loct in map:
                for obj in loct.objs:
                    if obj.type == 1 and obj.property.player_id == player_id:
                        return (loct.x, loct.y)
            return None
        
        def get_enemy_position():   # 获取敌人的坐标
            player_id = actionResp.player_id
            for loct in map:
                for obj in loct.objs:
                    if obj.type == 1 and obj.property.player_id != player_id:
                        return (loct.x, loct.y)
            return None
        
        self_position = get_self_position()   
        enemy_position = get_enemy_position()
        
        def get_self_property():  # 获取自己的属性
            x = self_position[0]
            y = self_position[1]
            player_id = actionResp.player_id
            for obj in map[x*15+y].objs:
                if obj.type == ObjType.Player and obj.property.player_id == player_id:
                    return obj.property
            return None
                
        def get_enemy_property():  # 获取敌人的属性
            x = enemy_position[0]
            y = enemy_position[1]
            player_id = actionResp.player_id
            for obj in map[x*15+y].objs:
                if obj.type == ObjType.Player and obj.property.player_id != player_id:
                    return obj.property
            return None
        
        self_property = get_self_property()   
        enemy_property = get_enemy_property()

        def get_present_round():
            present_round = actionResp.round
            return present_round
        
        present_round = get_present_round() 
        
        def get_bomb_info(bomb_info):  # 获取所有炸弹的坐标
            old_bomb_id_list = []
            new_bomb_id_list = []
            if len(bomb_info):
                for bomb in bomb_info:
                    old_bomb_id_list.append(bomb['id'])
            for i in range(len(map)):
                coord_x = i // 15
                coord_y = i % 15
                coord = (coord_x, coord_y)
                point_type = [obj.type for obj in map[i].objs]
                if ObjType.Bomb in point_type:
                    for obj in map[i].objs:
                        if obj.type == ObjType.Bomb:
                            bomb_id = obj.property.bomb_id
                            new_bomb_id_list.append(bomb_id)
                    if bomb_id not in old_bomb_id_list:
                        bomb_info.append({'position': (coord_x, coord_y), 'id': bomb_id, \
                            'place_round': present_round-1, 'player': obj.property.player_id})
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
                    if bomb['player'] == self_property.player_id:
                        bomb_range = self_property.bomb_range
                    elif bomb['player'] == enemy_property.player_id:
                        bomb_range = enemy_property.bomb_range
                    for direction in [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
                        if direction == (0, 0):
                            self_in_bomb = True
                        for i in range(1, bomb_range + 1):
                            new_position_x = x + i * direction[0]
                            new_position_y = y + i * direction[1]
                            new_position = (new_position_x, new_position_y)
                            if 0 <= new_position_x < 15 and 0 <= new_position_y < 15:
                                if self_in_bomb == True and new_position not in bomb_ranges:
                                    bomb_ranges.add((new_position_x, new_position_y))
                                    bomb_range_with_explode_round[new_position] = explode_round
                                if self_in_bomb == False and new_position not in bomb_ranges:
                                    _continue = False
                                    _continue = \
                                        not any(obj.type == ObjType.Bomb for obj in map[new_position_x * 15 + new_position_y].objs) and \
                                        not any(obj.type == ObjType.Block for obj in map[new_position_x * 15 + new_position_y].objs)
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

            return list(bomb_ranges), filtered_bomb_range_with_explode_round
        
        def get_surounding_block_property(coord, map): # 检查周围的方块
            x, y = coord
            directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
            blocks_property = {}
            for direction, (dx, dy) in directions.items():
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < 15 and 0 <= new_y < 15:
                    block_properties = [obj.property for obj in map[new_x * 15 + new_y].objs]
                    blocks_property[direction] = block_properties
            return blocks_property
        
        def check_removable(coord, map): # 检查周围可移除的方块
            blocks_property = get_surounding_block_property(coord, map)
            for block_properties in blocks_property.values():
                for property in block_properties:
                    if hasattr(property, 'removable') and property.removable:
                        return True
            return False
        
        def calculate_distance(coords_list, target): # 计算目标点到当前位置的距离
            exit_flag = False
            for coords in coords_list:
                if exit_flag:
                    break
                count = -1
                for coord in coords:
                    count += 1
                    if coord == target:
                        exit_flag = True
                        break
            return count
        
        def cal_distance_use_start_coord(start_coord, target_coord, bomb_range_with_round):
            coords_list = get_coords_list(start_coord, bomb_range_with_round)
            distance = calculate_distance(coords_list, target_coord)
            return distance
        
        def get_attack_range(): 
            enemy_x, enemy_y = enemy_position  
            attack_coords_list = \
            [(enemy_x + dx, enemy_y + dy) for dx in range(-2, 3) for dy in range(-2 + abs(dx), 3 - abs(dx))]
            return attack_coords_list
        
        def get_no_godness_coord(state, self_position, enemy_position, enemy_property, bomb_range_with_round, forseen): # 获取远离女神的安全坐标
            
            def get_enemy_godness_range(enemy_position, enemy_property):        # 改成直接远离敌人
                enemy_x, enemy_y = enemy_position 
                enemy_speed = enemy_property.speed
                ra = enemy_speed + 1
                godness_coords_list = \
                [(enemy_x + dx, enemy_y + dy) for dx in range((-ra+1), ra) for dy in range((-ra+1) + abs(dx), ra - abs(dx))]
                return godness_coords_list
            
            def get_no_godness_coords(coords_list, godness_range):
                no_godness_coords = []
                for coords in coords_list:
                    for coord in coords:
                        if coord not in godness_range:
                            no_godness_coords.append(coord)
                return no_godness_coords
                
            def get_nearest_no_godness_coord(no_godness_coords):
                    distances = [calculate_distance(coords_list, coord) for coord in no_godness_coords]
                    min_index = distances.index(min(distances))
                    return no_godness_coords[min_index]
                
            enemy_godness_range = get_enemy_godness_range(enemy_position, enemy_property)
            if state['enemy_godness'] == True and state['fight'] == True \
                and self_position in enemy_godness_range and forseen == False:
                
                no_godness_coords = get_no_godness_coords(coords_list, enemy_godness_range)
                nearest_no_godness_coord = get_nearest_no_godness_coord(no_godness_coords)
                return nearest_no_godness_coord
            else:
                return None
        
        def get_bomb_block_point(coords_list, map, bomb_info, state, imagin_place): # 获取放炸弹的坐标(收集资源阶段)
            bomb_positions = [bomb['position'] for bomb in bomb_info]
            bomb_block_coord_list = []
            if state['fight'] == False:
                for coords in coords_list:
                    for coord in (coords[1:] if imagin_place else coords):
                        if check_removable(coord, map) and forseen_bomb_place_escapable(coord, bomb_info) and self_position not in bomb_positions:
                            bomb_block_coord_list.append(coord)
                            break
                min_distance = float('inf')
                nearest_bomb_block_coord = None
                for bomb_block_coord in bomb_block_coord_list:
                    distance = calculate_distance(coords_list, bomb_block_coord)
                    if distance <= min_distance:
                        min_distance = distance
                        nearest_bomb_block_coord = bomb_block_coord
                return nearest_bomb_block_coord
            return None
                        
        def find_safe_coords(round, coords_list, bomb_range_with_round, property): # 找到最近的安全坐标
            safe_coords = []
            start_coord = coords_list[0][0]
            bomb_range = bomb_range_with_round.keys()
            if start_coord in bomb_range:
                for coords in coords_list:
                    for coord in coords:
                        reach_round = round + cal_required_round(coords_list, coord, property)
                        if coord in bomb_range:
                            bomb_round = bomb_range_with_round[coord]
                            if reach_round < bomb_round:
                                continue
                            elif reach_round >= bomb_round:
                                break
                        elif coord not in bomb_range:
                            safe_coords.append(coord)
                            break
                
                        if coord not in bomb_range:
                            safe_coords.append(coord)
                            break
            return safe_coords  
        
        def find_best_safe_coord(safe_coords, bomb_range_with_round):
            coords_sum_list = []
            for coord in safe_coords:
                forseen_coords_list = get_forseen_coords_list(coord, bomb_range_with_round)
                coords_sum = sum([len(coords) for coords in forseen_coords_list])
                coords_sum_list.append(coords_sum)
            if len(coords_sum_list):
                max_coords_sum_index = coords_sum_list.index(max(coords_sum_list))
                return safe_coords[max_coords_sum_index]
            return None
        
        # def get_fatal_bomb_enemy_points(bomb_info, bomb_range_with_round): # 获取必杀坐标
            
        #     def modify_enemy_coords_list(original_coords_list, _coord):
        #         coords_list = original_coords_list.copy()
        #         for i, coords in enumerate(original_coords_list):
        #             for j, coord in enumerate(coords):
        #                 if coord == _coord:
        #                     modified_coords = coords[:j+1]
        #                     coords_list[i] = modified_coords
        #         # print("敌人路径：", coords_list)
        #         return coords_list
                
        #     fatal_points = []
        #     coords_list_from_enemy = get_coords_list(enemy_position, bomb_range_with_round)
        #     for coords in coords_list_from_enemy:
        #         for coord in coords:
        #             forseen_coords_list = modify_enemy_coords_list(coords_list_from_enemy, coord)
        #             forseen_bomb_info = get_forseen_bomb_info(coord, bomb_info)
        #             _, forseen_bomb_range_with_round = get_bomb_range(forseen_bomb_info, 'forseen')
        #             enemy_safe_coords = find_safe_coords(present_round + 1, forseen_coords_list, forseen_bomb_range_with_round, enemy_property)
        #             # print("坐标和敌人安全坐标：", coord, enemy_safe_coords)
        #             if len(enemy_safe_coords) == 0:
        #                 fatal_points.append(coord)
        #     # print("必杀坐标：", fatal_points)
        #     return fatal_points
        
        # def get_nearest_fatal_point(coords_list, fatal_points):
        #     if not fatal_points:
        #         return None
        #     nearest_fatal_point = min(fatal_points, key=lambda point: calculate_distance(coords_list, point))
        #     return nearest_fatal_point
                     
        def get_item_position_list(coords_list, map, forseen):
            item_list = []
            for coords in coords_list:
                for coord in (coords[1:] if forseen else coords):
                    if map[coord[0]*15+coord[1]].objs:
                        for obj in map[coord[0]*15+coord[1]].objs:
                            if obj.type == 4:
                                item_list.append(coord)
            return item_list
        
        def get_nearest_item_position(coords_list, items_list):
            if not items_list:
                return None  
            distances = [calculate_distance(coords_list, item) for item in items_list]
            min_index = distances.index(min(distances))
            return items_list[min_index]

        def get_forseen_coords_list(target_coord, bomb_range_with_round):
            forseen_coords_list = []
            if target_coord is not None:
                forseen_start_coord = target_coord
                forseen_coords_list = get_coords_list(forseen_start_coord, bomb_range_with_round)
            return forseen_coords_list
        
        def get_forseen_bomb_info(place_coord, bomb_info):
            forseen_bomb_info = bomb_info.copy()
            if place_coord is not None:
                requrid_round = cal_required_round(coords_list, place_coord, self_property)
                place_round = present_round + requrid_round
                forseen_bomb_info.append({'position': place_coord, 'id': -1, 'place_round': place_round, 'player': self_property.player_id})  
            return forseen_bomb_info
        
        def get_attack_point(coords_list, forseen): # 待补全
            for coords in coords_list:
                for coord in (coords[1:] if forseen else coords):
                    if 1:
                        1
            return None
        
        def get_forseen_target_point(forseen_coords_list, forseen_bomb_range_with_round, \
            forseen_bomb_info, forseen_round):
            
            start_coord = forseen_coords_list[0][0]
            forseen_bomb_block_point = get_bomb_block_point(forseen_coords_list, map, forseen_bomb_info, self.state, imagin_place=True)    # 可能有问题
            forseen_safe_coords = find_safe_coords(forseen_round, forseen_coords_list, forseen_bomb_range_with_round, self_property)
            forseen_best_safe_coord = find_best_safe_coord(forseen_safe_coords, forseen_bomb_range_with_round)
            forseen_item_list = get_item_position_list(forseen_coords_list, map, forseen=True)
            forseen_enemy_position = (None if (start_coord == enemy_position) else enemy_position)
            no_godness_point = get_no_godness_coord(self.state, start_coord, enemy_position, enemy_property, bomb_range_with_round, forseen=True)
            forseen_target_point = select_and_combine_target_point(forseen_best_safe_coord, forseen_bomb_block_point, \
                        forseen_item_list, forseen_enemy_position, no_godness_point)
            return forseen_target_point
        
        def forseen_bomb_place_escapable(place_coord, bomb_info):       # 有问题?
            if place_coord is not None:
                requrid_round = cal_required_round(coords_list, place_coord, self_property)
                place_round = present_round + requrid_round
                forseen_bomb_info = get_forseen_bomb_info(place_coord, bomb_info)
                _, bomb_range_with_round = get_bomb_range(forseen_bomb_info)
                forseen_start_coord = place_coord
                forseen_coords_list = []
                forseen_coords_list = get_coords_list(forseen_start_coord, bomb_range_with_round)
                # print("预测放炸弹后的路径：", forseen_coords_list)
                forseen_safe_coords = []
                forseen_safe_coords = find_safe_coords(place_round, forseen_coords_list, bomb_range_with_round, self_property)
                if len(forseen_safe_coords):
                    # print("预测放炸弹后的安全坐标：", forseen_safe_coords)
                    return True
                # print("预测放炸弹后的安全坐标：", forseen_safe_coords)
                return False
        
        def select_and_combine_target_point(best_safe_coord, bomb_block_point, item_coord, enemy_point, no_godness_point): # 刷新目标点
            target_point = {        
                'safe_point': None,
                'item_point': None,
                'bomb_block_point': None, 
                'enemy_point': None,
                'no_godness_point': None,
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
            return target_point

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
        
        def cal_required_round(coords_list, target_coord, property):
            distance = calculate_distance(coords_list, target_coord)
            if distance % property.speed == 0:
                require_round = distance // property.speed
            else:
                require_round = distance // property.speed + 1
            return require_round
        
        def change_state(coords_list, self_property, enemy_property): # 改变状态
            if self_property.invincible_time > 0:
                self.state['self_godness'] = True
            else:
                self.state['self_godness'] = False
            
            if enemy_property.invincible_time > 0:
                self.state['enemy_godness'] = True
            else:
                self.state['enemy_godness'] = False
            for coords in coords_list:
                if enemy_position in coords:
                    self.state['fight'] = True
                    break
            else:
                self.state['fight'] = False
        
        def transform_target_point_to_coords(target_point, coords_list):
            target_coords = {}
            if len(coords_list):
                for coords in coords_list:
                    for coord in coords:
                        for type, target_coord in target_point.items():
                            if coord == target_coord:
                                target_coords[type] = coords[:coords.index(coord)+1]
            return target_coords
        
        def create_action_list(state, action_list, coords_list, target_point, round, bomb_info, bomb_range, bomb_range_with_round):
            max_action_times = self_property.speed
            left_action_times = max_action_times - len(action_list)
            has_gloves = self_property.has_gloves
            
            target_coords = transform_target_point_to_coords(target_point, coords_list)
            action_target_coords = []
            action_target_coord = None    # ['safe_point', 'no_godness_point', 'enemy_point', 'item_point', 'bomb_block_point']
            
            if state['fight'] == False:
                priority_list = ['safe_point', 'item_point', 'bomb_block_point']
            if state['fight'] == True:
                if state['self_godness'] == True and self_property.invincible_time >= enemy_property.invincible_time:
                    priority_list = ['enemy_point', 'safe_point', 'item_point', 'bomb_block_point']
                elif state['self_godness'] == True and self_property.invincible_time < enemy_property.invincible_time:
                    priority_list = ['no_godness_point', 'safe_point', 'item_point', 'bomb_block_point']
                elif state['self_godness'] == False and state['enemy_godness'] == True:
                    priority_list = ['no_godness_point', 'safe_point', 'item_point']
                elif state['self_godness'] == False and state['enemy_godness'] == False:
                    priority_list = ['safe_point', 'enemy_point', 'item_point', 'bomb_block_point']
                    
            target_type = None
            for type in priority_list:
                if type in target_coords and target_coords[type]:
                    action_target_coords = target_coords[type]
                    target_type = type
                    break
            if len(action_target_coords):
                action_target_coord = action_target_coords[-1]
            # print("至当前行动目标点的路径：", action_target_coords)
                
            if action_target_coord is not None:
                ditance_to_target = calculate_distance(coords_list, action_target_coord)
                # print("当前行动的目标点：", action_target_coord)
                # print("到当前行动目标点的距离：", ditance_to_target)
                
                action_list_p = []  # 情况1：不能一次性到达目标点
                if ditance_to_target >= left_action_times:
                    for i in range(left_action_times):
                        direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                        action_list_p.append(direction)
                    # print("action_list_1b:", action_list)
                    action_list.extend(action_list_p)
                    # print("action_list_1:", action_list)
                
                elif ditance_to_target < left_action_times: # 情况2：可以一次性到达目标点
                    action_times_p = ditance_to_target
                    # print("到当前行动目标点前可行动次数：", action_times_p)
                    forseen_round = round + cal_required_round(coords_list, action_target_coord, self_property)
                    forseen_bomb_range_with_round = bomb_range_with_round
                    
                    if target_type == 'bomb_block_point':
                        action_times_p += 1
                        for i in range(action_times_p):
                            if i < action_times_p - 1:
                                direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                                action_list_p.append(direction)
                            elif i == action_times_p - 1:
                                action_list_p.append('place')       # 在敌人前放炸弹明显迟钝，要改
                        forseen_bomb_info = get_forseen_bomb_info(action_target_coord, bomb_info)
                        forseen_bomb_range, forseen_bomb_range_with_round = get_bomb_range(forseen_bomb_info)
                        forseen_coords_list = get_forseen_coords_list(action_target_coord, forseen_bomb_range_with_round)
                        forseen_target_point = get_forseen_target_point(forseen_coords_list, forseen_bomb_range_with_round, \
                            forseen_bomb_info, forseen_round)
                    elif target_type != 'bomb_block_point':
                        for i in range(action_times_p):
                            direction = get_direction(action_target_coords[i], action_target_coords[i+1])
                            action_list_p.append(direction)
                        forseen_bomb_info = bomb_info
                        forseen_bomb_range = bomb_range
                        forseen_coords_list = get_forseen_coords_list(action_target_coord, forseen_bomb_range_with_round)
                        forseen_target_point = get_forseen_target_point(forseen_coords_list, bomb_range_with_round, \
                            forseen_bomb_info, forseen_round)
                    
                    # print("action_list_2b:", action_list)
                    action_list.extend(action_list_p)
                    # print("action_list_2:", action_list)
                    if len(action_list) < max_action_times:
                        create_action_list(state, action_list, forseen_coords_list, forseen_target_point, \
                            forseen_round, forseen_bomb_info, forseen_bomb_range, forseen_bomb_range_with_round)
                    else:
                        action_list = action_list[:max_action_times]
            
                
        get_bomb_info(self.bomb_info)
        bomb_range, bomb_range_with_round = get_bomb_range(self.bomb_info)
        
        start_coord = self_position
        coords_list = get_coords_list(start_coord, bomb_range_with_round)
        change_state(coords_list, self_property, enemy_property)

        bomb_block_point = get_bomb_block_point(coords_list, map, self.bomb_info, self.state, imagin_place=False)
        
        safe_coords = find_safe_coords(present_round, coords_list, bomb_range_with_round, self_property)
        best_safe_coord = find_best_safe_coord(safe_coords, bomb_range_with_round)
        
        item_list = get_item_position_list(coords_list, map, forseen=False)
        item_coord = get_nearest_item_position(coords_list, item_list)

        no_godness_point = get_no_godness_coord(self.state, self_position, enemy_position, enemy_property, bomb_range_with_round, forseen=False)

        # fatal_point = None
        # if self.state['fight'] == True and cal_required_round(coords_list, enemy_position, self_property) <= 1:
        #     fatal_point = get_nearest_fatal_point(coords_list, get_fatal_bomb_enemy_points(self.bomb_info, bomb_range_with_round))
        
        target_point = select_and_combine_target_point(best_safe_coord, bomb_block_point, item_coord, enemy_position, no_godness_point)
        
        action_list = []
        bomb_info = self.bomb_info
        create_action_list(self.state, action_list, coords_list, target_point, present_round, bomb_info, bomb_range, bomb_range_with_round)
        attack_range = get_attack_range()
        if self_position in attack_range and self.state['fight'] == True and forseen_bomb_place_escapable(self_position, bomb_info) == True:
            action_list.insert(0, 'place')
        
        self.actions = action_list
        
        # print("致命点：", fatal_point)
        print("目的安全坐标：", best_safe_coord)
        print("安全坐标：", safe_coords)
        print("开路坐标：", bomb_block_point)
        print("行动列表：", action_list)
        print("目标点：", target_point)
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

        


