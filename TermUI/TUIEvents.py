class TUIEvent:

    def __init__(self):
        pass

class TUIEventReactor():

    def __init__(self, reactorFunction):
        self.reactor = reactorFunction

    def __call__(self, event : TUIEvent):
        self.reactor(event)

class TUIInputEvent(TUIEvent):

    def __init__(self, key):
        self.key = key

class TUIInputEventReactor(TUIEventReactor):
    def __call__(self, event : TUIInputEvent):
        super().__call__(event)