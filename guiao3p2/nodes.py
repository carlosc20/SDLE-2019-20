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
        self.msgCount = 0
        self.cachedMessages = {}
        # Ver melhor (vizinho, Identifier), se existe

    # message to be passed on handleEager
    def createMsg(self, payload):
        self.msgCount += 1
        return EagerMessage((None, self.id), self.id, self.msgCount, payload)


    def handle(self, emsg):
        res = []
        rootid = emsg.identifier.rootid
        seqid = emsg.identifier.seqid
        payload = emsg.payload

        # print(len(self.neighbours))
        # se ainda não guardei/transmiti esta msg
        # TODO se recebeu do vizinho não lhe manda

        #if emsg.identifier not in self.cachedMessages:
        print("eager arrived", self.id)
        if not emsg.identifier in self.cachedMessages:
            for i in self.neighbours[self.fanout:]:
                if i != emsg.participants[0]:
                    res.append(LazyMessage((self.id, i), rootid, seqid))
            for i in self.neighbours[:self.fanout]:
                if i != emsg.participants[0]:
                    res.append(EagerMessage((self.id, i), rootid, seqid, payload))
            # havendo loss pode ser necessário reenviar
            print("caching", self.id)
            self.cachedMessages[emsg.identifier] = emsg.payload
        return res


class TimeoutNode(BroadcastNode):
    # - neigbours: [1,2,...]
    def __init__(self, neighbours, id, fanout, timeout=30):
        super().__init__(neighbours, id, fanout)
        self.timeout = timeout
        self.msgCount = 0
        self.eventCount = 0
        self.lazyWait = []
        self.innerEvents = {}

    def handleEager(self, eagerMsg):
        res = super().handle(eagerMsg)
        return res

    def handleLazy(self, lazyMsg):
        # se não recebi já uma lazy
        if lazyMsg.identifier not in self.lazyWait and not lazyMsg.identifier in self.cachedMessages:
            print("lazy arrived", self.id)
            self.eventCount += 1
            self.innerEvents[self.eventCount] = SendRequest((self.id, lazyMsg.participants[0]), lazyMsg.identifier.rootid,
                                                            lazyMsg.identifier.seqid)
            self.lazyWait.append(lazyMsg.identifier)
            print("eventCount: ", self.eventCount)
        return Timeout(self.id, self.eventCount, self.timeout)

    def handleTimeout(self, eventId):
        action = self.innerEvents[eventId]
        print("handle timeout")
        return action

    def handleSendRequest(self, sendReq):
        print("handle sendRequest")
        return PayloadDelivery(sendReq, self.cachedMessages[sendReq.identifier])
        
    def handlePayload(self, pDelivery):
        print("handle payload")
        self.cachedMessages[pDelivery.identifier] = pDelivery.payload
        

class Event:
    # participants = (src, dst)
    def __init__(self, participants):
        self.participants = participants

    def getSrc(self):
        return self.participants[0]

    def getDst(self):
        return self.participants[1]


class Timeout(Event):
    def __init__(self, nodeId, eventId, time):
        super().__init__((nodeId, nodeId))
        self.eventId = eventId
        self.time = time


class Identifier:
    def __init__(self, rootid, seqid):
        self.rootid = rootid
        self.seqid = seqid
        
    def __hash__(self):
        return hash((self.rootid, self.seqid))

    def __eq__(self, other):
        return (self.rootid, self.seqid) == (other.rootid, other.seqid)

    def __ne__(self, other):
        return not(self == other)


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
        super().__init__(participants, sr.identifier.rootid, sr.identifier.seqid, payload)


class SendRequest(LazyMessage):
    def __init__(self, participants, rootid, seqid):
        super().__init__(participants, rootid, seqid)

