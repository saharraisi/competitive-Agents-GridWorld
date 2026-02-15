# Smart Agent Game

A graphical multi-agent grid game where two intelligent agents, **Bob** and **Patrick**, compete to collect orbs and place them into holes on a 7×7 board. Agents have limited perception, a fixed number of moves, and can sabotage each other by removing opponent orbs from holes. 
## Related Work
This project is a continuation of the previous work:
**[Cooperative Agents GridWorld](https://github.com/saharraisi/Cooperative-Agents-GridWorld.git)** and The main difference is that, in this project, agents are **competitive** rather than cooperative.

<img width="523" height="540" alt="Screenshot 2026-02-15 at 16 01 19" src="https://github.com/user-attachments/assets/86a12a97-2a19-4e79-98bc-8d84f4a9f0e1" />



---

## Features

- **Autonomous Agents:** Each agent explores the grid, discovers orbs and holes, and makes decisions independently.  
- **Limited Perception:** Agents can only see the 8 neighboring cells around them.  
- **Competitive Gameplay:** Agents can sabotage each other by removing orbs placed by the opponent.  
- **Graphical Interface:** Real-time visualization of the grid, agents, orbs, and holes with distinct icons.  
- **Move Budget:** Each agent has a limited number of moves to complete its objective.  
- **Statistics:** Tracks filled and empty holes, free orbs, moves, orbs placed, and sabotages.  

---

## How It Works

1. The grid is initialized with randomly placed orbs and holes.  
2. Agents start at random locations with no prior knowledge of the environment.  
3. Agents move, pick up orbs, place them into holes, and can sabotage opponents.  
4. Game ends when all holes are filled or agents run out of moves.  
5. Final statistics summarize the outcome and agent performance.


### Example Output

An example of the program output is shown below:

<img width="682" height="683" alt="Screenshot 2026-02-15 at 16 12 31" src="https://github.com/user-attachments/assets/28907084-bdf3-4157-8d88-3058097777d2" />



