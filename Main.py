import itertools
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# create a dict representation of skills field
elements = {
    "Alliance Stake 1": (0, 3), "Alliance Stake 2": (3, 0), "Alliance Stake 3": (3, 6), 
    "Ring 1": (0.5, 1), "Ring 2": (1, 1), "Ring 3": (1, 0.5),
    "Ring 4": (0.5, 5), "Ring 5": (1, 5), "Ring 6": (1, 5.5),
    "Ring 7": (2, 1), "Ring 8": (2, 5), "Ring 9": (2, 2), "Ring 10": (2, 4),
    "Ring 11": (3, 0.5), "Ring 12": (3, 3), "Ring 13": (3, 5.5),
    "Ring 14": (4, 1), "Ring 15": (4, 2), "Ring 16": (4, 4), "Ring 17": (4, 5),
    "Ring 18": (5, 0.5), "Ring 19": (5, 1), "Ring 20": (5, 5.5),
    "Ring 21": (5, 5), "Ring 22": (5.5, 5), "Ring 23": (5.5, 1),
    "Mobile Goal 1": (1, 2), "Mobile Goal 2": (1, 4),
    "Mobile Goal 3": (5, 3), "Mobile Goal 4": (5.5, 2), "Mobile Goal 5": (5.5, 4),
    "Positive Corner 1": (0, 0), "Positive Corner 2": (0, 6),
    "Positive Corner 3": (6, 0), "Positive Corner 4": (6, 6)
}

# make the dict a graph for calculations
G = nx.Graph()
for name, coord in elements.items():
    G.add_node(name, pos=coord)

# add weighted edges (distances)
for name1, pos1 in elements.items():
    for name2, pos2 in elements.items():
        if name1 != name2:
            distance = ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
            G.add_edge(name1, name2, weight=distance)

# use the travelling salesman algorithm to determine optimized route using nearest neighbor calculations
def tsp_nearest_neighbor(start, nodes, mobile_goals, positive_corners, alliance_stakes):
    path = [start]
    remaining = set(nodes)
    
    # for counting total scores + mogo possesion so you know when you can score
    current_mobile_goal = None
    rings_collected = 0
    total_points = 0  
    
    # track rings in mobile goals and alliance stakes
    mobile_goal_stacks = {goal: [] for goal in mobile_goals} 
    alliance_stake_stacks = {stake: [] for stake in alliance_stakes}  
    
    # go from alliance stake to mobile goal as first move and assume you score preload
    if mobile_goals:
        nearest_goal = min(mobile_goals, key=lambda node: G[start][node]['weight'])
        path.append(nearest_goal)
        total_points += 3
        mobile_goals.remove(nearest_goal)
        current_mobile_goal = nearest_goal  # you now have a mobile goal, so set ur mogo possesion to the one you got
    
    while remaining:
        current = path[-1]
        if remaining:
            # nearest neighbor ring
            nearest = min(remaining, key=lambda node: G[current][node]['weight'])
            path.append(nearest)
            remaining.remove(nearest)
            rings_collected += 1

            # if the ring is right in front of a stake, just score it on the neutral stake
            if nearest == "Ring 11" or nearest == "Ring 13":
                nearest_alliance_stake = min(alliance_stakes, key=lambda node: G[current][node]['weight'])
                path.append(nearest_alliance_stake)
                total_points += 3  # theres only one ring in front of it, which will be the only one on the stake, so top ring
        
        # go to the nearest neighbor positive corner after collecting 6 rings
        if rings_collected > 0 and rings_collected % 6 == 0:
            nearest_corner = min(positive_corners, key=lambda corner: G[current][corner]['weight'])
            path.append(nearest_corner)
            total_points += 16  # multiplier for pos corner
            positive_corners.remove(nearest_corner)  
            
            # search for next mogo to continue collecting rings
            if mobile_goals:
                nearest_goal = min(mobile_goals, key=lambda node: G[nearest_corner][node]['weight'])
                path.append(nearest_goal)
                mobile_goals.remove(nearest_goal)
                current_mobile_goal = nearest_goal  

                # calculate score
                if len(mobile_goal_stacks[current_mobile_goal]) == 0:  # if top ring
                    total_points += 3 
                else:
                    total_points += 1  
                mobile_goal_stacks[current_mobile_goal].append(nearest) 

        # if the ring is at an Alliance Stake
        if current in alliance_stakes:
            if len(alliance_stake_stacks[current]) == 0:  
                total_points += 3  
            else:
                total_points += 1  
            alliance_stake_stacks[current].append(nearest)  

    return path, total_points

# arr of what each point represents
rings = [key for key in elements.keys() if "Ring" in key]
mobile_goals = [key for key in elements.keys() if "Mobile Goal" in key]
positive_corners = [key for key in elements.keys() if "Positive Corner" in key]
alliance_stakes = [key for key in elements.keys() if "Alliance Stake" in key]

# start at alliance stake
start_point = "Alliance Stake 1"

# run algo
optimal_ring_order, total_points = tsp_nearest_neighbor(start_point, rings, mobile_goals, positive_corners, alliance_stakes)

print("total pts:", total_points)

# animate path
fig, ax = plt.subplots(figsize=(8, 8))
pos = nx.get_node_attributes(G, "pos")

nx.draw(G, pos, with_labels=True, node_size=500, node_color="lightblue", font_size=8, ax=ax)


path_edges = list(zip(optimal_ring_order, optimal_ring_order[1:]))
line, = ax.plot([], [], color="red", linewidth=2)

def update(frame):
    current_path = path_edges[:frame + 1]
    x_vals = []
    y_vals = []
    
    for edge in current_path:
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        x_vals.extend([x0, x1])
        y_vals.extend([y0, y1])
    
    line.set_data(x_vals, y_vals)
    return line,

ani = FuncAnimation(fig, update, frames=len(path_edges), interval=500, blit=True)

ani.save("optimal_path_animation.gif", writer="imagemagick", fps=2)
