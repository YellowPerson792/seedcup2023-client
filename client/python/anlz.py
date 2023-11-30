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
        'collect': False,
        'fight': False,
    }
    
    def __init__(self) -> None:
        pass   

    def codebox(self, actionResp: ActionResp, ) -> None:
        target_point = {        # 目标点
        'safe_point': None,
        'item_point': None,
        'bomb_block_point': None, 
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

        def findway(start_coord, path, last_direction):   # 寻路函数
            queue = deque([(start_coord, path, last_direction)])
            visited_coords = set([start_coord])
            paths = []

            while queue:
                start_coord, path, last_direction = queue.popleft()
                is_in_bomb_range = start_coord in bomb_range
                directions = sigfidway(*start_coord, is_in_bomb_range)
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
            for path in paths:
                coords = [start_coord]
                for direction in path:
                    delta = direction_to_delta(direction)
                    last_coord = coords[-1]
                    new_coord = (last_coord[0] + delta[0], last_coord[1] + delta[1])
                    coords.append(new_coord)
                coords_list.append(coords)
            return coords_list

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
        
        self_position = get_self_position()     # 有空再改
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
        
        present_round = get_present_round() # 有空再改
        
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
                        bomb_info.append({'position': (coord_x, coord_y), 'id': bomb_id, 'place_round': present_round-1})
                    elif bomb_id in old_bomb_id_list:
                        if coord != bomb_info[old_bomb_id_list.index(bomb_id)]['position']:
                            bomb_info[old_bomb_id_list.index(bomb_id)]['position'] = coord
            print("炸弹信息：", bomb_info)
            
            def remove_unused_bombs(bomb_info, new_id_list):
                for bomb in bomb_info.copy():
                    if bomb['id'] not in new_id_list:
                        bomb_info.remove(bomb)
                return bomb_info
            bomb_info = remove_unused_bombs(bomb_info, new_bomb_id_list)
                    
            # for i in range(len(map)):
            #     x = i // 15
            #     y = i % 15
            #     target_point = [obj.type for obj in map[i].objs]
            #     if 1 in target_point and 2 in target_point:
            #         for obj in map[i].objs:
            #             if obj.type == 1 or obj.type == 2:
            #                 player_id = obj.property.player_id
            #                 if (x, y, player_id) not in bomb_positions_with_round:
            #                     bomb_positions_with_round.append((x, y, player_id, present_round))
            # # 转换为集合去除重复项，然后再转换回列表
            # bomb_positions_with_round = list(set(bomb_positions_with_round))

        def get_bomb_range(bomb_info, situation):  # 获取所有炸弹的爆炸范围
            bomb_ranges = set()
            bomb_range_with_explode_round = {}
            if len(bomb_info):
                for bomb in bomb_info:
                    x = bomb['position'][0]
                    y = bomb['position'][1]
                    self_in_bomb = False
                    explode_round = bomb['place_round'] + 5
                    if situation == 'real':
                        for obj in map[15*x+y].objs:
                            if obj.type == ObjType.Bomb:
                                bomb_range = obj.property.bomb_range
                    elif situation == 'forseen':
                        bomb_range = self_property.bomb_range
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
        
        # def remove_bombs(bomb_positions_with_round):
        #     for position in bomb_positions_with_round[:]:
        #         x, y = position[0], position[1]
        #         if not bomb_exists_at(x, y):
        #             bomb_positions_with_round.remove(position)

        # def bomb_exists_at(x, y):
        #     for obj in map[x * 15 + y].objs:
        #         if obj.type==2:
        #             return True
        #     return False
            
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
        
        def get_attack_range(): 
            enemy_x, enemy_y = enemy_position  # 假设这个函数返回敌人的坐标
            attack_coords_list = \
            [(enemy_x + dx, enemy_y + dy) for dx in range(-2, 3) for dy in range(-2 + abs(dx), 3 - abs(dx))]
            return attack_coords_list
        
        def get_bomb_block_point(coords_list, map, bomb_info, state): # 获取放炸弹的坐标(收集资源阶段)
            bomb_positions = [bomb['position'] for bomb in bomb_info]
            bomb_block_coord_list = []
            if state['fight'] == False:
                for coords in coords_list:
                    for coord in coords:
                        if check_removable(coord, map) and self_position not in bomb_positions:
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
                        
            # if state['fight'] == False: 
            #     result = None
            #     distance = float('inf')
            #     bomb_positions_with_round = [(position[0],position[1]) for position in bomb_positions_with_round]
            #     for coords in coords_list:
            #         count = -1
            #         coord_result = None
            #         for coord in coords:
            #             count += 1
            #             if check_removable(coord, map) and self_position not in bomb_positions_with_round:
            #                 coord_result = coord
            #                 break
            #         if count <= distance:
            #             distance = count
            #             result = coord_result
            #     return result
            # return None
        
        def find_safe_coords(coords_list, bomb_range_with_round): # 找到最近的安全坐标
            safe_coords = []
            start_coord = coords_list[0][0]
            bomb_range = bomb_range_with_round.keys()
            for coords in coords_list:
                for idx, coord in enumerate(coords):
                    if coord in bomb_range and idx + present_round <= bomb_range_with_round[coord]:
                        continue
                    elif coord in bomb_range and idx + present_round > bomb_range_with_round[coord]: 
                        break                    
                    safe_coords.append(coord)
                    break
            if start_coord in safe_coords:
                return []
            return safe_coords  
        
        def find_best_safe_coord(safe_coords):
            max_coords_list = []
            safe_coords_idx = None 
            if len(safe_coords):
                for idx, coord in enumerate(safe_coords):
                    paths = findway(coord, [], None)
                    coords_list = paths_to_coords(coord, paths)
                    # print("从安全点出发的路径：", coords_list)
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

        def forseen_bomb_place_escapable(place_coord, bomb_info):    
            if place_coord is not None:
                x = place_coord[0]
                y = place_coord[1]
                requrid_round = cal_required_round(coords_list, place_coord)
                place_round = present_round + requrid_round
                bomb_info.append({'position': (x, y), 'id': -1, 'place_round': place_round})  
                _, bomb_range_with_round = get_bomb_range(bomb_info, 'forseen')
                bomb_info.pop()
                forseen_start_coord = place_coord
                forseen_paths = []
                forseen_coords_list = []
                forseen_paths = findway(forseen_start_coord, [], None)
                forseen_coords_list = paths_to_coords(forseen_start_coord, forseen_paths)
                print("预测放炸弹后的路径：", forseen_coords_list)
                forseen_safe_coords = []
                forseen_safe_coords = find_safe_coords(forseen_coords_list, bomb_range_with_round)
                if len(forseen_safe_coords):
                    print("预测放炸弹后的安全坐标：", forseen_safe_coords)
                    return True
                print("预测放炸弹后的安全坐标：", forseen_safe_coords)
                return False
        
        def refresh_target_point(target_point, best_safe_coord, bomb_block_point, item_coord, bomb_info): # 刷新目标点
            if best_safe_coord is not None:
                target_point['safe_point'] = best_safe_coord
            bomb_block_escapalbe = forseen_bomb_place_escapable(bomb_block_point, bomb_info)
            if bomb_block_escapalbe == True:   
                target_point['bomb_block_point'] = bomb_block_point
            target_point['item_point'] = item_coord
            if self.state['fight'] == True:   
                target_point['enemy_point'] = enemy_position

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
        
        def cal_required_round(coords_list, target_coord):
            distance = calculate_distance(coords_list, target_coord)
            require_round = distance // self_property.speed
            return require_round
        
        def judge_bomb_place(target_point, bomb_info):
            attack_range = get_attack_range()
            if self_position == target_point['bomb_block_point'] and \
                self.state['fight'] == False and \
                forseen_bomb_place_escapable(self_position, bomb_info) == True:   
                return True
            if self_position in attack_range and \
                self.state['fight'] == True and \
                forseen_bomb_place_escapable(self_position, bomb_info) == True:
                return True
            
        def change_state(coords_list): # 改变状态
            for coords in coords_list:
                if enemy_position in coords:
                    self.state['fight'] = True
                    return
            else:
                self.state['fight'] = False
                return
        
        def tarp_to_direction(target_point, coords_list): # 依据目标点生成行动方向
            place = judge_bomb_place(target_point, self.bomb_info)
            target_info = {}
            max_action_times = self_property.speed
            has_gloves = self_property.has_gloves
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
            
            safe_point_direction = return_direction('safe_point', target_info, coords_list)
            enemy_point_direction = return_direction('enemy_point', target_info, coords_list)
            itme_point_direction = return_direction('item_point', target_info, coords_list)
            bomb_block_direction = return_direction('bomb_block_point', target_info, coords_list)
            
            if safe_point_direction is not None:
                return safe_point_direction
            
            elif place == True:
                return ['place', 'silent']
            
            elif enemy_point_direction is not None:
                return enemy_point_direction
            
            elif itme_point_direction is not None:
                return itme_point_direction 
            
            elif bomb_block_direction is not None:
                return bomb_block_direction
            
            return ['silent', 'silent']
              
                
        get_bomb_info(self.bomb_info)
        # remove_bombs(self.bomb_positions_with_round)   
        bomb_range, bomb_range_with_round = get_bomb_range(self.bomb_info, 'real')
        
        start_coord = self_position
        paths = findway(start_coord, [], None)
        coords_list = paths_to_coords(start_coord, paths)
        change_state(coords_list)

        bomb_block_point = get_bomb_block_point(coords_list, map, self.bomb_info, self.state)
        
        safe_coords = find_safe_coords(coords_list, bomb_range_with_round)
        best_safe_coord = find_best_safe_coord(safe_coords)
        
        item_list = get_item_list(coords_list, map)
        item_coord = get_item_position(coords_list, item_list)

        refresh_target_point(target_point, best_safe_coord, bomb_block_point, item_coord, self.bomb_info)
        self.actions = tarp_to_direction(target_point, coords_list)
        
        print("目标点：", target_point)
        print("行动类型：", [action_Req[key] for key in self.actions])
        print("安全坐标：", safe_coords)
        print("最佳安全坐标：", best_safe_coord)
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

        


