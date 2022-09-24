from .suitik_dispatcher import SuitikDispatcher


def run():
    dispatcher = SuitikDispatcher()
    dispatcher.init()
    dispatcher.run()
