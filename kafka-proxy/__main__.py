from .web import WEBServer


if __name__ == '__main__':
    import multiprocessing

    web = multiprocessing.Process(target=WEBServer().up)

    try:
        web.start()
    except KeyboardInterrupt:
        web.shutdown()
