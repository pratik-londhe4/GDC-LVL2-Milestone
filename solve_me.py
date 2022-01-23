from atexit import register
from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in self.current_items.keys():
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        if args[0] not in self.current_items.keys():
            self.current_items[args[0]] = args[1]
        else:
            priority = int(args[0])
            while str(priority) in self.current_items.keys():
                priority += 1
            for i in range(priority, int(args[0]), -1):
                prev = self.current_items.pop(str(i - 1))
                self.current_items[str(i)] = prev
            self.current_items[args[0]] = args[1]
        self.write_current()
        print(f'Added task: "{args[1]}" with priority {args[0]}')

    def done(self, args):
        if args[0] in self.current_items.keys():
            self.completed_items.append(self.current_items.pop(args[0]))
            self.write_completed()
            self.write_current()
            print("Marked item as done.")
        else:
            print(f"Error: no incomplete item with priority {args[0]} exists.")

    def delete(self, args):
        if args[0] in self.current_items.keys():
            self.current_items.pop(args[0])
            self.write_current()
            print(f"Deleted item with priority {args[0]}")
        else:
            print(
                f"Error: item with priority {args[0]} does not exist. Nothing deleted."
            )

    def ls(self):
        i = 1
        for key, val in sorted(self.current_items.items()):
            print(f"{i}. {val} [{key}]")
            i += 1

    def report(self):
        print(f"Pending : {len(self.current_items)}")
        i = 1
        for k, v in sorted(self.current_items.items()):
            print(f"{i}. {v} [{k}]")
            i += 1

        print(f"Completed : {len(self.completed_items)}")
        i = 1
        for e in sorted(self.completed_items)[:-1]:
            print(f"{i}. {e}")
            i += 1
        arr = sorted(self.completed_items)
        print(f"{len(self.completed_items)}. {arr[-1]}", end="")
    

    def render_pending_tasks(self):
        li_style = "font-family:monospace;font-size:30px;padding:5px;margin-left:2%;"
        add = f"<a href='/add'>Add new Tasks</a>"
        self.read_current()
        style = "font-family:monospace;color:orange;font-size:40px"
        output = f"<h1 style={style}>Pending Tasks:</h1><br><h3><ol>"
        for k, v in sorted(self.current_items.items(), key=lambda x: int(x[0])):
            output += f"<li style={li_style}>{v} [{k}]</li>"
        output += f"</ol></h3><a href='/completed'>Completed Tasks</a><br>{add}"
        return output

    def render_completed_tasks(self):
        li_style = "font-family:monospace;font-size:30px;padding:5px;margin-left:2%"

        self.read_completed()
        style = "font-family:monospace;color:green;font-size:40px"
        output = f"<h1 style={style}>Completed Tasks:</h1><br><h3><ol>"
        print(self.completed_items)
        for e in sorted(self.completed_items):
            output += f"<li style={li_style}>{e}</li>"
        output += f"</ol></h3><br><a href='/tasks'>Pending Tasks</a>"
        return output
    
    def render_form(self):
        button = f"<button type=submit>Add Task</button>"
        item = f"<label>Task</label><br><input type=text name=item ><br>"
        priority = f"<label>Priority</label><br><input type=number name=priority ><br>"
        pending = f"<a href='/tasks'>Pending Tasks</a>"
        completed = f"<a href='/completed'>Completed Tasks</a>"
        output = f"<form action=new method=GET>{item}{priority}<br>{button}</form>{pending}<br>{completed}"
        return output
    
    def get_parameters(self , query):
        query = query.replace("/new?" , '').split('&')
        
        params = {}
        for i in range(0 , len(query)):    
            temp = query[i].split('=')        
            params[temp[0]] = temp[1]
        return params
        


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        elif self.path == "/add":
            print(self.parse_request)
            content = task_command_object.render_form()
        
        elif "/new" in  self.path:
           params =  task_command_object.get_parameters(self.path)
           task_command_object.add([params["priority"] , params["item"]])
           content = "<h2>Task Added</h2><br><a href='/tasks'>Pending Tasks</a>"

        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())