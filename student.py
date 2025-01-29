import asyncio
import json
import random
import websockets
from consts import Direction, Tiles
from collections import deque
from enum import IntEnum, unique
import os
import getpass

DIRECTION_KEY = {
    Direction.NORTH: "w",
    Direction.SOUTH: "s",
    Direction.EAST: "d",
    Direction.WEST: "a"
}

DIRECTION_DELTAS = {
    Direction.NORTH: (0, -1),
    Direction.SOUTH: (0, 1),
    Direction.EAST: (1, 0),
    Direction.WEST: (-1, 0)
}

exploration_direction = Direction.EAST
zigzag_row_start = True
var = 0
max_row_reach = 24
min_row_reach = 0
last_directions = deque(maxlen=3)

def movement(snake_head, snake_body, current_direction, map_width, map_height, traverse, visible_map, NEXT_POSITION, new_class, other_snakes_bodies):

    global zigzag_row_start, var, exploration_direction, max_row_reach, min_row_reach, last_directions

    if len(last_directions) >= 2:
        penultimate_direction = last_directions[-2]
        delta = DIRECTION_DELTAS[penultimate_direction]
        penultimate_position = (snake_head[0] + delta[0], snake_head[1] + delta[1])

    if exploration_direction == new_class.EAST:
        next_position = NEXT_POSITION["next_east"]
        pos_in_world = world_position(next_position, map_width, map_height, traverse)

        if not safe_movement(pos_in_world, snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies) or snake_head[0] + 1 >= map_width:
            if safe_movement(NEXT_POSITION["next_south"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                exploration_direction = new_class.SOUTH
            elif safe_movement(NEXT_POSITION["next_north"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                exploration_direction = new_class.NORTH
            else:
                exploration_direction = exploration_direction

    elif exploration_direction == new_class.WEST:
        next_position = NEXT_POSITION["next_west"]
        pos_in_world = world_position(next_position, map_width, map_height, traverse)
        
        if not safe_movement(pos_in_world, snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies) or snake_head[0] - 1 < 0:
            if safe_movement(NEXT_POSITION["next_south"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                exploration_direction = new_class.SOUTH
            elif safe_movement(NEXT_POSITION["next_north"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                exploration_direction = new_class.NORTH
            else:
                exploration_direction = exploration_direction

    elif exploration_direction == new_class.SOUTH:
        next_position = NEXT_POSITION["next_south"]
        pos_in_world = world_position(next_position, map_width, map_height, traverse)


        if snake_head[1] + 1 >= min_row_reach:
            
            if snake_head[0] == 0:
                if var < 4:
                    if safe_movement(NEXT_POSITION["next_south"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.SOUTH
                        var = var + 1
                    elif safe_movement(NEXT_POSITION["next_east"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    else:
                        exploration_direction = new_class.WEST
                        var = 0

                else:
                    if safe_movement(NEXT_POSITION["next_east"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    elif safe_movement(NEXT_POSITION["next_west"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    else:
                        exploration_direction = exploration_direction

            elif snake_head[0] == map_width - 1:
                if var < 5:
                    if safe_movement(NEXT_POSITION["next_south"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.SOUTH
                        var = var + 1
                    elif safe_movement(NEXT_POSITION["next_west"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    else:
                        exploration_direction = new_class.EAST
                        var = 0

                else:
                    if safe_movement(NEXT_POSITION["next_west"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    elif safe_movement(NEXT_POSITION["next_east"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    else:
                        exploration_direction = exploration_direction

            # Caso não esteja nas bordas
            else:
                if var < 5:
                    if safe_movement(penultimate_position, snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = penultimate_direction
                        var = var + 1
                    elif safe_movement((snake_head[0] + 1, snake_head[1]), snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    elif safe_movement((snake_head[0] - 1, snake_head[1]), snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    #elif safe_movement((snake_head[0], snake_head[1] + 1), snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                    #    exploration_direction = new_class.SOUTH
                    #    var = var + 1
                    else:
                        exploration_direction = exploration_direction
                else:
                    if safe_movement(NEXT_POSITION["next_west"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    elif safe_movement(NEXT_POSITION["next_east"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    else:
                        exploration_direction = exploration_direction
                
    
    elif exploration_direction == new_class.NORTH:
        next_position = NEXT_POSITION["next_north"]
        pos_in_world = world_position(next_position, map_width, map_height, traverse)
        
        if snake_head[1] - 1 <= max_row_reach - 1:
            
            if snake_head[0] == 0:
                if var < 3:
                    if safe_movement(NEXT_POSITION["next_north"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.NORTH
                        var = var + 1
                    elif safe_movement(NEXT_POSITION["next_east"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    else:
                        exploration_direction = new_class.WEST
                        var = 0

                else:
                    if safe_movement(NEXT_POSITION["next_east"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    elif safe_movement(NEXT_POSITION["next_west"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    else:
                        exploration_direction = exploration_direction

            elif snake_head[0] == map_width - 1:
                if var < 3:
                    if safe_movement(NEXT_POSITION["next_north"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.NORTH
                        var = var + 1
                    elif safe_movement(NEXT_POSITION["next_west"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    else:
                        exploration_direction = new_class.EAST
                        var = 0

                else:
                    if safe_movement(NEXT_POSITION["next_east"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    elif safe_movement(NEXT_POSITION["next_west"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    else:
                        exploration_direction = exploration_direction

            # Caso não esteja nas bordas
            else:
                if var < 3:
                    if safe_movement(penultimate_position, snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = penultimate_direction
                        var = var + 1
                    elif safe_movement((snake_head[0] + 1, snake_head[1]), snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    elif safe_movement((snake_head[0] - 1, snake_head[1]), snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    #elif safe_movement((snake_head[0], snake_head[1] + 1), snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                    #    exploration_direction = new_class.NORTH
                    #    var = var + 1
                    else:
                        exploration_direction = exploration_direction
                else:
                    if safe_movement(NEXT_POSITION["next_west"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.WEST
                        var = 0
                    elif safe_movement(NEXT_POSITION["next_east"], snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
                        exploration_direction = new_class.EAST
                        var = 0
                    else:
                        exploration_direction = exploration_direction

    return exploration_direction


def world_position(position, map_width, map_height, traverse):
    x, y = position

    if traverse:
        pos_in_world = (x % map_width, y % map_height)
    else:
        pos_in_world = (x, y)

    return pos_in_world



def safe_movement(next_position, snake_body, map_width, map_height, visible_map, traverse, other_snakes_bodies):
    
    pos_in_world = world_position(next_position, map_width, map_height, traverse)

    if pos_in_world is None:
        return False

    if pos_in_world in snake_body:
        return False

    if traverse == False and visible_map.get(pos_in_world) == Tiles.STONE:
        return False

    if pos_in_world not in visible_map:
        return False
    
    if visible_map[pos_in_world] == Tiles.SUPER: # temporário
        return False
    
    if visible_map[pos_in_world] == Tiles.SNAKE: # temporário
        return False

    return True


def serpentine_movement(snake_head, snake_body, current_direction, map_width, map_height, traverse, visible_map, other_snakes_bodies):

    global zigzag_row_start, var, exploration_direction, max_row_reach, min_row_reach, DIRECTION_DELTAS

    next_position = snake_head

    NEXT_POSITION = {
                "next_north": (snake_head[0], snake_head[1] - 1),
                "next_south": (snake_head[0], snake_head[1] + 1),
                "next_east": (snake_head[0] + 1, snake_head[1]),
                "next_west": (snake_head[0] - 1, snake_head[1])
            }

    if traverse:
        
        exploration_direction = movement(snake_head, snake_body, current_direction, map_width, map_height, traverse, visible_map, NEXT_POSITION, Direction, other_snakes_bodies)

    elif traverse == False:

        if (snake_head[1] == 23):
            zigzag_row_start = False
        
        if (snake_head[1] == 0):
            zigzag_row_start = True

        if zigzag_row_start == True:

            NEXT_POSITION = {
                "next_north": (snake_head[0], snake_head[1] - 1),
                "next_south": (snake_head[0], snake_head[1] + 1),
                "next_east": (snake_head[0] + 1, snake_head[1]),
                "next_west": (snake_head[0] - 1, snake_head[1])
            }

            exploration_direction = movement(snake_head, snake_body, current_direction, map_width, map_height, traverse, visible_map, NEXT_POSITION, Direction, other_snakes_bodies)

        else:

            @unique
            class CustomDirection(IntEnum):
                NORTH = 2
                EAST = 1
                SOUTH = 0
                WEST = 3
            
            DIRECTION_DELTAS = {
                Direction.NORTH: (0, 1),
                Direction.SOUTH: (0, -1),
                Direction.EAST: (1, 0),
                Direction.WEST: (-1, 0)
            }

            NEXT_POSITION = {
                "next_north": (snake_head[0], snake_head[1] + 1),
                "next_south": (snake_head[0], snake_head[1] - 1),
                "next_east": (snake_head[0] + 1, snake_head[1]),
                "next_west": (snake_head[0] - 1, snake_head[1])
            }

            exploration_direction = movement(snake_head, snake_body, current_direction, map_width, map_height, traverse, visible_map, NEXT_POSITION, CustomDirection, other_snakes_bodies)

    else:
        for direction, delta in DIRECTION_DELTAS.items():
            alternative_position = (snake_head[0] + delta[0], snake_head[1] + delta[1])
            if safe_movement(alternative_position, snake_body, map_width, map_height, visible_map, traverse):
                exploration_direction = direction
                next_position = alternative_position
                break
    
    next_position = world_position(next_position, map_width, map_height, traverse)

    return exploration_direction, next_position


def safe_astar(next_pos, snake_body, snake_tail, steps_to_goal, map_width, map_height, visible_map, traverse):
    pos_in_world = world_position(next_pos, map_width, map_height, traverse)

    if pos_in_world not in visible_map:
        return False

    if not traverse and visible_map[pos_in_world] == Tiles.STONE:
        return False
    
    if visible_map[pos_in_world] == Tiles.SUPER: # temporário
        return False

    if pos_in_world in snake_body:
        position_index = snake_body.index(pos_in_world)
        if position_index < len(snake_body) - steps_to_goal:
            return False
    return True

def astar(start, goal, map_data, snake_body, traverse, map_width, map_height):
    global var
    open_set = [(0, start)]
    came_from = {}
    cost_so_far = {start: 0}
    var = 0

    DIRECTION_DELTAS = {
        Direction.NORTH: (0, -1),
        Direction.SOUTH: (0, 1),
        Direction.EAST: (1, 0),
        Direction.WEST: (-1, 0)
    }

    while open_set:
        _, current = open_set.pop(0)

        if current == goal:
            path = []
            while current != start:
                current, direction = came_from[current]
                path.append(direction)
            path.reverse()
            return path

        for direction, delta in DIRECTION_DELTAS.items():
            next_pos = (current[0] + delta[0], current[1] + delta[1])
            next_pos = world_position(next_pos, map_width, map_height, traverse)

            if next_pos is None:
                continue

            steps_to_goal = cost_so_far[current] + 1

            if safe_astar(next_pos, snake_body, snake_body[-1], steps_to_goal, map_width, map_height, map_data, traverse):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos, map_width, map_height)
                    open_set.append((priority, next_pos))
                    open_set.sort()
                    came_from[next_pos] = (current, direction)

    return None

def heuristic(a, b, map_width, map_height):
    dx = min(abs(a[0] - b[0]), map_width - abs(a[0] - b[0]))
    dy = min(abs(a[1] - b[1]), map_height - abs(a[1] - b[1]))
    return dx + dy


def find_food(snake_head, visible_map, map_width, map_height, traverse):
    foods = []
    supers = []

    for (x, y), tile in visible_map.items():
        if not traverse and (x < 0 or x >= map_width or y < 0 or y >= map_height):
            continue

        if tile == Tiles.FOOD:
            foods.append((x, y))

    if foods:
        nearest_food = min(foods, key=lambda f: heuristic(snake_head, f, map_width, map_height))
        return nearest_food, "FOOD"


    return None, None

def get_snake_positions(visible_map, snake_tile):
    snake_positions = [pos for pos, tile in visible_map.items() if tile == snake_tile]
    return snake_positions  

def filter_self_snake(snake_body, all_snake_positions):
    return [pos for pos in all_snake_positions if pos not in snake_body]


def move_away_from_opponent(snake_head, opponent_body, map_width, map_height, visible_map, snake_body, traverse):
    """Calcula a direção para se mover para o mais longe possível da cobra adversária."""
    max_distance = -1
    best_direction = None

    for direction, delta in DIRECTION_DELTAS.items():
        next_pos = (snake_head[0] + delta[0], snake_head[1] + delta[1])
        next_pos = world_position(next_pos, map_width, map_height, traverse)

        if next_pos and safe_movement(next_pos, snake_body, map_width, map_height, visible_map, traverse, []):
           
            # Calcula a distância mínima de "next_pos" para todas as partes do corpo da cobra adversária
            min_distance_to_opponent = min(
                heuristic(next_pos, part, map_width, map_height) for part in opponent_body
            )
            if min_distance_to_opponent > max_distance:
                max_distance = min_distance_to_opponent
                best_direction = direction

    return best_direction

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        current_direction = Direction.EAST
        last_directions.append(current_direction)

        while True:
            try:
                state = json.loads(await websocket.recv())

                if not state.get("alive", True):
                    return

                if "body" not in state or not state["body"]:
                    await asyncio.sleep(0.1)
                    continue

                map_width, map_height = 48, 24
                snake_head = tuple(state["body"][0])
                snake_body = [tuple(part) for part in state["body"]]
                visible_map = {(int(x), int(y)): tile for x, rows in state["sight"].items() for y, tile in rows.items()}
                traverse = state.get("traverse", True)
                other_snakes_bodies = []

                food_position, food_type = find_food(snake_head, visible_map, map_width, map_height, traverse)
                # Pega as posições de partes de cobras visíveis no mapa
                all_snake_positions = get_snake_positions(visible_map, Tiles.SNAKE)
                opponent_positions = filter_self_snake(snake_body, all_snake_positions)

                # Se houver partes de cobras visíveis, atualiza a lógica
                if opponent_positions:
                    next_direction = move_away_from_opponent(
                        snake_head, opponent_positions, map_width, map_height, visible_map, snake_body, traverse
                    )

                elif food_position:
                    path_to_food = astar(snake_head, food_position, visible_map, snake_body, traverse, map_width, map_height)
                    if path_to_food:
                        next_direction = path_to_food.pop(0)
                        current_direction = next_direction
                else:
                    next_direction, _ = serpentine_movement(
                        snake_head, snake_body, current_direction, map_width, map_height, traverse, visible_map, other_snakes_bodies)

                last_directions.append(next_direction)

                key = DIRECTION_KEY[next_direction]
                await websocket.send(json.dumps({"cmd": "key", "key": key}))

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELOW
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))