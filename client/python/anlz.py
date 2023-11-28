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
    
    player_bomb_positions = []
    coords_list = []
    actions = ['silent','silent']

    state = {
        'collect': False,
        'fight': False,
    }
    
    def __init__(self) -> None:
        pass   

    def codebox(self, actionResp: ActionResp) -> None:
        target_point = {        # 目标点
        'safe_point': None,
        'item_point': None,
        'lay_bomb_point': None, 
        'enemy_point': None,
    }   
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
            if blocktype(u,v) in [0,ObjType.Item]:
                return 1
            else:
                return 0  

        def play_bomb_exist(p, q):
            player_exists = False
            bomb_exists = False
            for obj in map[p*15+q].objs:
                if obj.type == ObjType.Player:
                    player_exists = True
                if obj.type == ObjType.Bomb:
                    bomb_exists = True
            return player_exists and bomb_exists         
        
        def sigfidway(p, q, is_in_bomb_range):
            numls=list(range(1,14))
            directions = {'right': False, 'down': False, 'left': False, 'up': False}
            if ifstad(p,q) or play_bomb_exist(p, q):
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
            if is_in_bomb_range == True:
                return result
            for direction in result:
                dx, dy = direction_to_delta(direction)
                new_coords = (p + dx, q + dy)
                if new_coords in bomb_range:
                    directions[direction] = False
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
            new_coords = (m + dx, n + dy)

            return new_coords
    
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

        def findway(coord, path, last_direction):   # 寻路函数
            queue = deque([(coord, path, last_direction)])
            visited_coords = set([coord])

            while queue:
                coord, path, last_direction = queue.popleft()
                is_in_bomb_range = coord in bomb_range
                directions = sigfidway(*coord, is_in_bomb_range)
                if last_direction is not None:
                    directions = [direction for direction in directions if direction != opposite(last_direction)]
                if not directions:
                    if path not in paths:
                        paths.append(path)
                    continue
                for direction in directions:
                    new_path = path.copy()
                    new_path.append(direction)  # 添加方向到 new_path
                    new_coord = caculat(*coord, direction)
                    if new_coord not in visited_coords:
                        visited_coords.add(new_coord)
                        queue.append((new_coord, new_path, direction))

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

        def paths_to_coords(coords_list, paths): # 将方向表示的路径转换为坐标表示的路径
            for path in paths:
                coords = [start_coord]
                for direction in path:
                    delta = direction_to_delta(direction)
                    last_coord = coords[-1]
                    new_coord = (last_coord[0] + delta[0], last_coord[1] + delta[1])
                    coords.append(new_coord)
                coords_list.append(coords)

        def opposite(direction):
            opposites = {'right': 'left', 'down': 'up', 'left': 'right', 'up': 'down'}
            return opposites[direction]
        
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
        
        def get_present_round():
            round = actionResp.round
            return round
        
        def get_bomb_positions(player_bomb_positions):  # 获取所有炸弹的坐标
            round = get_present_round()
            for i in range(len(map)):
                x = i // 15
                y = i % 15
                target_point = [obj.type for obj in map[i].objs]
                if 1 in target_point and 2 in target_point:
                    for obj in map[i].objs:
                        if obj.type == 1 or obj.type == 2:
                            player_id = obj.property.player_id
                            if (x, y, player_id) not in player_bomb_positions:
                                player_bomb_positions.append((x, y, player_id, round))
            # 转换为集合去除重复项，然后再转换回列表
            player_bomb_positions = list(set(player_bomb_positions))

        def get_bomb_range(player_bomb_positions):  # 获取所有炸弹的爆炸范围
            bomb_ranges = set()
            bomb_ranges_with_time = {}
            self_in_bomb = False
            for position in player_bomb_positions:
                player_id = position[2]
                explode_round = position[3] + 5
                for obj in map[15*position[0]+position[1]].objs:
                    if obj.property.player_id == player_id:
                        bomb_range = obj.property.bomb_range
                        for direction in [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
                            if direction == (0, 0):
                                self_in_bomb = True
                            for i in range(1, bomb_range + 1):
                                new_position_x = position[0] + i * direction[0]
                                new_position_y = position[1] + i * direction[1]
                                new_position = (new_position_x, new_position_y)
                                if 0 <= new_position_x < 15 and 0 <= new_position_y < 15:
                                    if self_in_bomb == True and new_position not in bomb_ranges:
                                        bomb_ranges.add((new_position_x, new_position_y))
                                        bomb_ranges_with_time[new_position] = explode_round
                                    if self_in_bomb == False and new_position not in bomb_ranges and \
                                        not any(obj.type == ObjType.Bomb for obj in map[new_position_x * 15 + new_position_y].objs) and \
                                        not any(obj.type == ObjType.Block for obj in map[new_position_x * 15 + new_position_y].objs):
                                        bomb_ranges.add(new_position)
                                        bomb_ranges_with_time[new_position] = explode_round

            # 过滤 bomb_ranges_with_time 列表，只保留 explode_round 最小的元素
            filtered_bomb_ranges_with_time = {}
            for new_position, explode_round in bomb_ranges_with_time.items():
                if new_position not in filtered_bomb_ranges_with_time or explode_round < filtered_bomb_ranges_with_time[new_position]:
                    filtered_bomb_ranges_with_time[new_position] = explode_round

            return list(bomb_ranges), filtered_bomb_ranges_with_time
        
        def remove_bombs(player_bomb_positions):
            for position in player_bomb_positions[:]:
                x, y = position[0], position[1]
                if not bomb_exists_at(x, y):
                    player_bomb_positions.remove(position)

        def bomb_exists_at(x, y):
            for obj in map[x * 15 + y].objs:
                if obj.type==2:
                    return True
            return False
            
        def check_surroundings(coord, map): # 检查周围的方块
            x, y = coord
            directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
            surroundings = {}
            for direction, (dx, dy) in directions.items():
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < 15 and 0 <= new_y < 15:
                    block_properties = [obj.property for obj in map[new_x * 15 + new_y].objs]
                    surroundings[direction] = block_properties
            return surroundings
        
        def check_removable_surroundings(coord, map): # 检查周围可移除的方块
            surroundings = check_surroundings(coord, map)
            for block_properties in surroundings.values():
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
        
        def get_attack_range(): # 获取攻击范围
            # self_bomb_range = get_self_bomb_range(get_self_position(), map)
            # -2 = -self_bomb_range-2
            # 3 = self_bomb_range + 3
            enemy_x, enemy_y = get_enemy_position()  # 假设这个函数返回敌人的坐标
            attack_coords_list = \
            [(enemy_x + dx, enemy_y + dy) for dx in range(-2, 3) for dy in range(-2 + abs(dx), 3 - abs(dx))]
            return attack_coords_list
        
        def get_lay_bomb_point(coords_list, map, player_bomb_positions, state): # 获取放炸弹的坐标(收集资源阶段)
            if state['fight'] == False: 
                result = None
                distance = float('inf')
                self_position = get_self_position()
                bomb_positions = [(position[0],position[1]) for position in player_bomb_positions]
                for coords in coords_list:
                    count = -1
                    coord_result = None
                    for coord in coords:
                        count += 1
                        if check_removable_surroundings(coord, map) and self_position not in bomb_positions:
                            coord_result = coord
                            break
                    if count <= distance:
                        distance = count
                        result = coord_result
                return result
            return None
        
        def find_safe_coords(coords_list, bomb_range_with_explode_round): # 找到最近的安全坐标
            safe_coords = []
            self_position = get_self_position()
            round = get_present_round()
            bomb_range = bomb_range_with_explode_round.keys()
            for coords in coords_list:
                for idx, coord in enumerate(coords):
                    if coord in bomb_range and idx + round <= bomb_range_with_explode_round[coord]:
                        continue
                    elif coord in bomb_range and idx + round > bomb_range_with_explode_round[coord]: 
                        break                    
                    safe_coords.append(coord)
                    break
            if self_position in safe_coords:
                return []
            return safe_coords  
        
        def find_best_safe_coord(safe_coords):
            max_coords_list = []
            safe_coords_idx = None 
            if len(safe_coords):
                for idx, coord in enumerate(safe_coords):
                    paths = []
                    findway(coord, [], None)
                    coords_list = []
                    paths_to_coords(coords_list, paths)
                    if len(coords_list) >= len(max_coords_list):
                        max_coords_list = coords_list
                        safe_coords_idx = idx
                if safe_coords_idx is not None:
                    best_safe_coord = safe_coords[safe_coords_idx]
                    return best_safe_coord
            return None
        
        def get_item_list(coords_list, map):
            item_list = []
            for coords in coords_list:
                for coord in coords:
                    if map[coord[0]*15+coord[1]].objs:
                        for obj in map[coord[0]*15+coord[1]].objs:
                            if obj.type == 4:
                                item_list.append(coord)
            return item_list
        
        def get_item_position(coords_list, items_list):
            if not items_list:
                return None  
            distances = [calculate_distance(coords_list, item) for item in items_list]
            min_index = distances.index(min(distances))
            return items_list[min_index]

        def refresh_target_point(target_point, best_safe_coord, lay_bomb_point, item_coord): # 刷新目标点
            if best_safe_coord is not None:
                target_point['safe_point'] = best_safe_coord
            target_point['lay_bomb_point'] = lay_bomb_point
            target_point['item_point'] = item_coord
            if self.state['fight'] == True:   
                target_point['enemy_point'] = get_enemy_position()

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
        
        def tarp_to_direction(target_point, coords_list): # 依据目标点生成行动方向
            self_position = get_self_position()
            if_place = judge_bomb_place(target_point)
            target_info = {}
            for idx, coords in enumerate(coords_list):
                for coord in coords:
                    for type, target_coord in target_point.items():
                        if coord == target_coord:
                            target_info[type] = {'idx': idx, 'coord': coord}
            
            def return_direction(type, target_info, coords_list):
                for target_type, target in target_info.items():
                    if target_type ==  type and len(coords_list[target['idx']]) >= 2:
                        direction1 = 'silent'
                        direction0 = get_direction(self_position, coords_list[target['idx']][1])
                        if calculate_distance(coords_list, target['coord']) >= 2:
                            direction1 = get_direction(coords_list[target['idx']][1], coords_list[target['idx']][2])
                        return [direction0, direction1] 
                return None
            
            safe_point_return = return_direction('safe_point', target_info, coords_list)
            enemy_point_return = return_direction('enemy_point', target_info, coords_list)
            item_point_return = return_direction('item_point', target_info, coords_list)
            bomb_point_return = return_direction('lay_bomb_point', target_info, coords_list)
            
            if safe_point_return is not None:
                return safe_point_return
            
            elif if_place == True:
                return ['place', 'silent']
            
            elif enemy_point_return is not None:
                return enemy_point_return
            
            elif item_point_return is not None:
                return item_point_return 
            
            elif bomb_point_return is not None:
                return bomb_point_return
            
            return ['silent', 'silent']
        
        def self_place_escapeable(bomb_positions):
            self_position = get_self_position()
            present_round = get_present_round()
            bomb_positions.append((self_position[0], self_position[1], actionResp.player_id, present_round))
            _, bomb_range_with_explode_round = get_bomb_range(bomb_positions)
            bomb_positions.pop()
            safe_coords = []
            safe_coords = find_safe_coords(coords_list, bomb_range_with_explode_round)
            if len(safe_coords):
                return True
            return False
        
        def judge_bomb_place(target_point):
            self_position = get_self_position()
            attack_range = get_attack_range()
            if self_position == target_point['lay_bomb_point'] and \
                self.state['fight'] == False and \
                self_place_escapeable(self.player_bomb_positions) == True:
                return True
            if self_position in attack_range and \
                self.state['fight'] == True and \
                self_place_escapeable(self.player_bomb_positions) == True:
                return True
            
        def change_state(coords_list): # 改变状态
            enemy_position = get_enemy_position()
            for coords in coords_list:
                if enemy_position in coords:
                    self.state['fight'] = True
                    return
            else:
                self.state['fight'] = False
                return
                    
                
        get_bomb_positions(self.player_bomb_positions)
        remove_bombs(self.player_bomb_positions)   
        bomb_range, bomb_range_with_explode_round = get_bomb_range(self.player_bomb_positions)
        
        paths = []
        coords_list = []
        start_coord = get_self_position()
        findway(start_coord, [], None)
        paths_to_coords(coords_list,paths)
        change_state(coords_list)

        lay_bomb_point = get_lay_bomb_point(coords_list, map, self.player_bomb_positions, self.state)
        
        safe_coords = find_safe_coords(coords_list, bomb_range_with_explode_round)
        best_safe_coord = find_best_safe_coord(safe_coords)
        
        item_list = get_item_list(coords_list, map)
        item_coord = get_item_position(coords_list, item_list)

        refresh_target_point(target_point, best_safe_coord, lay_bomb_point, item_coord)
        self.actions = tarp_to_direction(target_point, coords_list)
        
        print("行动类型：", [action_Req[key] for key in self.actions])
        print("目标点：", target_point)
        print("安全坐标：", safe_coords)
        print("最佳安全坐标：", best_safe_coord)
        print("可放炸弹的坐标：", lay_bomb_point)
        print("炸弹爆炸范围内坐标：\n", bomb_range)
        print("路径（方向表示）：")
        for path in paths:
            print(path) 
        # print("路径（坐标表示）：")
        # for coords in coords_list:
        #     print(coords)
                 


    def action_req_send(self): # 发送行动请求
        return [action_Req[key] for key in self.actions]

        


