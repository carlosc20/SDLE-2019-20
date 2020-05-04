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

class Neighbour:
    def __init__(self, id, ntype):
        self.ack = False
        self.id = id
        self.ntype = ntype

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
        self.acknowledgments = {}
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
            acks = {}
            for i in self.neighbours[self.fanout:]:
                if i != emsg.participants[0]:
                    res.append(LazyMessage((self.id, i), rootid, seqid))
                    acks[i] = Neighbour(i, 'lazy')
            for i in self.neighbours[:self.fanout]:
                if i != emsg.participants[0]:
                    res.append(EagerMessage((self.id, i), rootid, seqid, payload))
                    acks[i] = Neighbour(i, 'eager')
            # havendo loss pode ser necessário reenviar
            print("caching", self.id)
            self.cachedMessages[emsg.identifier] = emsg.payload
            self.acknowledgments[emsg.identifier] = acks 
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
        ack = None
        if eagerMsg.getSrc() is not None:
            ack = Acknowledgment(eagerMsg.participants, eagerMsg.identifier)
        return (res, ack)

    def handleLazy(self, lazyMsg):
        # se não recebi já uma lazy
        # TODO ver se cobre caso em que lazy recebe lazy
        if lazyMsg.identifier not in self.lazyWait and not lazyMsg.identifier in self.cachedMessages:
            print("lazy arrived", self.id)
            self.eventCount += 1
            self.innerEvents[self.eventCount] = SendRequest((self.id, lazyMsg.participants[0]), lazyMsg.identifier.rootid,
                                                            lazyMsg.identifier.seqid)
            self.lazyWait.append(lazyMsg.identifier)
            print("eventCount: ", self.eventCount)
        return (Timeout(self.id, self.eventCount, self.timeout), Acknowledgment(lazyMsg.particpants, lazyMsg.identifier))

    def handleTimeout(self, eventId):
        action = self.innerEvents[eventId]
        print("handle timeout")
        return action

    def handleSendRequest(self, sendReq):
        print("handle sendRequest")
        return PayloadDelivery(sendReq, self.cachedMessages[sendReq.identifier])


    # lidar com o payload como se fosse uma eager? iria depender se queremos que o nodo envia as coisas
    def handlePayload(self, pDelivery):
        print("handle payload")
        self.cachedMessages[pDelivery.identifier] = pDelivery.payload

    def handleAck(self, ack):
        print("handle ack")
        self.acknowledgments[ack.identifier][ack.participants[0]].ack = True

    def handleGarbageCollection(self):
        print("handle garbagecollection")
        res = []
        ackedMessages = len(self.acknowledgments)
        toRemove = []
        for ident, neighbours in self.acknowledgments.items():
            count = 0
            total = len(neighbours)
            for n in neighbours.values():
                if n.ack is False:
                    if n.ntype == 'lazy':
                        res.append(LazyMessage((self.id, n.id), ident.rootid, ident.seqid))
                    else:
                        payload = self.cachedMessages[ident]
                        res.append(EagerMessage((self.id, n.id), ident.rootid, ident.seqid, payload))
                else:
                    count+=1
            if count == total:
                ackedMessages-=1
                self.cachedMessages.pop(ident)
                toRemove.append(ident)
        for ident in toRemove:
            self.acknowledgments.pop(ident)
        # ainda existem msg por retirar
        timeout = None
        ## só funciona para uma msg, quando estiver confirmada em todos acaba o programa
        if ackedMessages != 0:
            timeout = self.createGarbageCollectionEvent()
        return (res, timeout) 
    
    def createGarbageCollectionEvent(self):
        self.eventCount += 1
        self.innerEvents[self.eventCount] = GarbageCollection(self.id)
        timeout = Timeout(self.id, self.eventCount, 1000)
        return timeout
   
        

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

class GarbageCollection(Event):
    def __init__(self, nodeId):
        super().__init__((nodeId, nodeId))
        self.time = 0

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


class Acknowledgment(Event):
    def __init__(self, participants, identifier):
        super().__init__((participants[1],participants[0]))
        self.identifier = identifier

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

