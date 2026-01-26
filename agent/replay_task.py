from .action import BaseAction, BaseComposeAction

class ReplayTask(BaseComposeAction):
    type: str = "replay_task"
    steps: list[BaseAction]
    id: str = None
    domain: str = None
    instruction: str = None

    def __init__(self, steps=None, id="", domain="", instruction=""):
        super().__init__(steps=steps, id=id, domain=domain, instruction=instruction)
        self.steps = steps if steps is not None else []
        self.id = id
        self.domain = domain
        self.instruction = instruction

    def __repr__(self):
        repr_str = f"ReplayTask(id={self.id}, domain={self.domain}, instruction={self.instruction}, steps=[\n"
        for step in self.steps:
            repr_str += f"  {step}\n"
        repr_str += "])"
        return repr_str

    @staticmethod
    def from_json(data: dict) -> 'ReplayTask':
        task = ReplayTask()
        task.steps = [BaseAction.from_json(step) for step in data.get('steps', [])]
        task.id = data.get('id', "")
        task.domain = data.get('domain', "")
        task.instruction = data.get('instruction', "")

        # Build graph
        for i, step in enumerate(task.steps):
            task.append_graph(
                graph_description=f"step_{i}_{step.__class__.__name__}",
                graph=step
            )
        task.commit_end_node()
        return task

    def next_step(self) -> BaseAction:
        if self.steps:
            return self.steps.pop(0)
        return None
    
    def visualize_graph(self, filename: str = None, directory: str = ".", 
                  format: str = "pdf", view: bool = False,
                  vertical: bool = True, display_node_groups: bool = True):        
        if filename is None or len(filename) == 0:
            if self.id is not None and len(self.id) > 0:
                filename = self.id
            else:
                filename = self.__class__.__name__
        super().visualize_graph(
            vertical=vertical, 
            display_node_groups=display_node_groups, 
            filename=filename, 
            directory=directory, 
            format=format, 
            view=view
        )

