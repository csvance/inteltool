import threading

tasks = []

MAX_TASKS = 1


def worker(task):
    task.run()


def spawn_task(task):
    while (len(tasks) >= MAX_TASKS):
        tasks.pop().join()
    t = threading.Thread(target=worker, args=[task])
    t.start()
    tasks.append(t)


def wait_tasks():
    while (len(tasks) > 0):
        tasks.pop().join()
