import asyncio

tasks = []

def init_delayed_bg_task(delay, task, thread_id, cycle_on_init, intercept_task = None):
    tasks[thread_id] = {"running": False, "delay": delay, "call": task, "interception": intercept_task}
    print(thread_id)
    if cycle_on_init:
        run_task(thread_id)

def run_task(thread_id):
    tasks[thread_id]["running"] = True
    if tasks[thread_id]["interception"]:
        asyncio.create_task(cycle_task_with_intercept(thread_id))
    else:
        asyncio.create_task(cycle_task(thread_id))

async def cycle_task(thread_id):
    while tasks[thread_id]["running"]:
        tasks[thread_id]["call"]()
        await asyncio.sleep(tasks[thread_id]["delay"])
        
async def cycle_task_with_intercept(thread_id):
    while tasks[thread_id]["running"]:
        tasks[thread_id]["interception"](thread_id, tasks[thread_id]["call"])
        await asyncio.sleep(tasks[thread_id]["delay"])

def stop_task(thread_id):
    tasks[thread_id]["running"] = False
    del tasks[thread_id]

def is_running(thread_id):
    return tasks[thread_id]["running"]
