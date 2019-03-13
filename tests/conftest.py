from .distributed.kafka_runner import kafka_runner


def pytest_sessionstart(session):
    kafka_runner.run()


def pytest_sessionfinish(session, exitstatus):
    kafka_runner.remove_container()
