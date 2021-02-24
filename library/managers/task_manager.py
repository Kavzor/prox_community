import asyncio

class TaskManager:
    def __init__(self):
        self.tasks = {}

    def create_task(self, delay, task, thread_id, run = True):
        self.tasks[thread_id] = {"running": run, "delay": delay, "call": task}
        asyncio.create_task(self.cycle_task(thread_id))

    async def cycle_task(self, thread_id):
        while self.tasks[thread_id]["running"]:
            await self.tasks[thread_id]["call"]()
            await asyncio.sleep(self.tasks[thread_id]["delay"])
        del tasks[thread_id]
        #self.destroy_task(thread_id)
    
    def destroy(self):
        for task in self.tasks:
            self.tasks[task]["running"] = False
            while self.tasks[task] is not None:
                asyncio.sleep(1)

    def pause_task(self, thread_id):
        pass

    def resume_task(self, thread_id):
        pass

    def destroy_task(self, thread_id):
        self.tasks = [task for task in self.tasks if not task["name"] == thread_id]
