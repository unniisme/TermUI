class EventBus:
    def __init__(self, logger = None):
        self.bus = ()
        self.logger = logger

    def Invoke(self, *args, **kwargs):
        for f in self.bus:
            try:
                f(*args, **kwargs)
            except Exception as e:
                exc = EventBusException("", self, f, e)
                if self.logger:
                    self.logger.error(str(exc))
                else:
                    raise exc

    def __add__(self, other):
        newBus = EventBus(logger=self.logger)
        newBus.bus = self.bus + (other,)
        return newBus
    
    def __call__(self, *args, **kwargs):
        self.Invoke(*args, **kwargs)

class EventBusException(Exception):
    def __init__(self, message, obj, func, error):
        super().__init__(message)
        self.obj = obj
        self.func = func
        self.error = error

    def __str__(self):
        return f"{super().__str__()}\nobj : {self.obj}\
        func : {self.func}\nerror : {self.error}"