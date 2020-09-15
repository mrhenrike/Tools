import json
import uuid
from datetime import datetime

class Request(object):
    """Manages tasks"""
    def __init__(self):
        super(Request, self).__init__()

    def new(self, json_request):
        self.newrequest = {}
        self.request_id = str(uuid.uuid4())
        self.json_request = json_request
        self.offline = []
        self.not_found = []
        self.targets = []
        self.date = str(datetime.now().year)+str(datetime.now().month).zfill(2)+str(datetime.now().day)+str(datetime.now().hour)+str(datetime.now().minute)+str(datetime.now().second).zfill(2)

        with open('bots.json','r') as botsfile:
            botsObj = json.load(botsfile)
        onlinebots = [bot["bot_id"] for bot in botsObj if bot["online"] == "True"]
        offlinebots = [bot["bot_id"] for bot in botsObj if bot["online"] == "False"]
        for target in self.json_request["targets"]:
            if target in onlinebots:
                self.targets.append(target)
            elif target in offlinebots:
                self.targets.append(target)
                self.offline.append(target)
            else:
                self.not_found.append(target)
        if len(self.targets) == 0:
            self.newrequest["error"] = "no _targets"
            return self.newrequest, self.offline, self.not_found
        else:
            self.newrequest["request_id"] = self.request_id
            self.newrequest["date"] = self.date
            self.newrequest["targets"] = self.targets
            self.newrequest["request_type"] = self.json_request["request_type"]
            self.newrequest["arguments"] = self.json_request["arguments"]
            self.newrequest["status"] = "new"
            self.newrequest["tasks"] = []
            for target in self.targets:
                self.newrequest["tasks"].append({"task_id":str(uuid.uuid4()),"bot_id":target,"status":"not_done", "data":[]})
            with open('requests.json','r') as requestsfile:
                requestsObj = json.load(requestsfile)

            requestsObj.append(self.newrequest)

            with open('requests.json','w') as requestsfile:
                json.dump(requestsObj, requestsfile, indent=4)

        return self.newrequest, self.offline, self.not_found
