* **`networks/`**: Store all SUMO-specific XML files here (`.net.xml`, `.rou.xml`, `.add.xml`, `.sumocfg`). Keeping the simulation assets separated from the logic makes the repo much easier to navigate.
* **`src/`**: Main Python execution scripts.
    * **`src/agents/`**: If you plan to implement any algorithmic control logic, keep those classes here.
    * **`src/utils/`**: Helper scripts (e.g., parsing SUMO output files or generating random routes).