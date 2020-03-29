class Node:
    # - neigbours: [1,2,...]
    def __init__(self, neighbours):
        self.neighbours = neighbours
        self.visited = False

    # várias implementações dependendo do algoritmo
    # returns e.g. [(dst0, msg0), (dst1, msg1), ....]

    def createMsg(self, msg):
        return msg

    def handle(self, msg):
        res = []
        if not self.visited:
            # print("visited!", self.neighbours)
            for i in self.neighbours:
                res.append((i, msg))
            self.visited = True
        return res


class BroadcastNode(Node):
    def __init__(self, neighbours, id, fanout):
        super().__init__(neighbours)
        if fanout > len(self.neighbours) or fanout == 0:
            self.fanout = len(self.neighbours)
        else:
            self.fanout = fanout
        self.id = id

    def handle(self, emsg):
        res = []
        rootid = emsg.identifier.rootid
        seqid = emsg.identifier.seqid
        payload = emsg.payload
        if not self.visited:
            if self.fanout < len(self.neighbours):
                for i in self.neighbours[self.fanout:-1]:
                    res.append(LazyMessage((self.id, i), rootid, seqid))
            for i in self.neighbours[:self.fanout - 1]:
                res.append(EagerMessage((self.id, i), rootid, seqid, payload))
            self.visited = True
        return res


class TimeoutNode(BroadcastNode):
    # - neigbours: [1,2,...]
    def __init__(self, neighbours, id, fanout, timeout=30):
        super().__init__(neighbours, id, fanout)
        self.timeout = timeout
        self.msgCount = 0
        self.eventCount = 0
        self.messages = {}
        self.cachedMessages = {}
        self.pulledMessages = {}
        self.innerEvents = {}

    # message to be passed on handleEager
    def createMsg(self, payload):
        self.msgCount += 1
        self.messages[self.msgCount] = payload
        return EagerMessage((None, self.id), self.id, self.msgCount, payload)

    def handleEager(self, eagerMsg):
        if self.fanout < len(self.neighbours):
            
            self.cachedMessages[eagerMsg.identifier] = eagerMsg.payload
        res = super().handle(eagerMsg)
        return res

    def handleLazy(self, lazyMsg):
        self.eventCount += 1
        self.innerEvents[self.eventCount] = SendRequest((self.id, lazyMsg.participants[0]), lazyMsg.rootid,
                                                        lazyMsg.seqid)
        return Timeout(self.id, self.eventCount)

    def handleTimeout(self, eventId):
        action = self.innerEvents[eventId]
        return action

    def handleSendRequest(self, sendReq):
        if sendReq.rootid == self.id:
            return PayloadDelivery(sendReq, self.messages[sendReq.seqid])
        else:
            return PayloadDelivery(sendReq, self.messages[(sendReq.rootid, sendReq.seqid)])
        
    def handlePayload(self, pDelivery):
        self.pulledMessages[pDelivery]
        


class Event:
    # participants = (src, dst)
    def __init__(self, participants):
        self.participants = participants

    def getSrc(self):
        return self.participants[0]

    def getDst(self):
        return self.participants[1]


class Timeout(Event):
    def __init__(self, nodeId, eventId):
        super().__init__((nodeId, nodeId))
        self.eventId = eventId


class Identifier:
    def __init__(self, rootid, seqid):
        self.rootid = rootid
        self.seqid = seqid
        
    #def __hash__(self):
     #   return hash((self.rootid, self.seqid))

    #def __eq__(self, other):
     #   return (self.rootid, self.seqid) == (other.rootid, other.seqid)

    #def __ne__(self, other):
     #   return not(self == other)


class LazyMessage(Event):
    def __init__(self, participants, rootid, seqid):
        super().__init__(participants)
        self.identifier = Identifier(rootid, seqid)


class EagerMessage(LazyMessage):
    def __init__(self, participants, rootid, seqid, payload):
        super().__init__(participants, rootid, seqid)
        self.payload = payload


class PayloadDelivery(EagerMessage):
    def __init__(self, sr, payload):
        # direction switch
        participants = (sr.participants[1], sr.participants[0])
        super().__init__(participants, sr.rootid, sr.seqid, payload)


class SendRequest(LazyMessage):
    def __init__(self, participants, rootid, seqid):
        super().__init__(participants, rootid, seqid)

