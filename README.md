The Game of Life, also known as Conway's Game of Life or simply Life, is a cellular automaton devised by 
the British mathematician John Horton Conway in 1970. Its evolution is determined by its initial state, 
requiring no further input. One interacts with the Game of Life by creating an initial configuration and 
observing how it evolves. The rules of the simulation are as follows.

---- Rules ----
- Any live cell with fewer than two live neighbours dies, as if by underpopulation.
- Any live cell with two or three live neighbours lives on to the next generation.
- Any live cell with more than three live neighbours dies, as if by overpopulation.
- Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

In my representation of Conway's Game of Life Simulation, the normal rules apply. But in addition, if a cell
is alive, it's colored black. If a cell died last step, the cell is colored red; If the cell died 2 steps ago, 
the cell is colored orange; if it died three steps ago, the cell is colored yellow. Anything after that is uncolored

To run the program follow this link: [https://lucasbixby.github.io/game-of-life ](https://lucasbixby.github.io/Game-of-Life-Simulation/)
