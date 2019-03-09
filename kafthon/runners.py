from typing import Any, Optional
from abc import ABCMeta, abstractmethod

import docker

from .utils import get_cls_path
from .serializers import BaseSerializer, MsgpackSerializer


class BaseRunner(metaclass=ABCMeta):
    def __init__(self, serializer: Optional[BaseSerializer] = None):
        self._serializer = serializer or MsgpackSerializer()

    @abstractmethod
    def run(self, runnable_cls, init_data) -> Any:
        pass

        # init_data = (args, kwargs)
        # if self._serializer is not None:
        #     init_data = self._serializer.serialize(init_data)
        # return self.deploy_service(runnable_cls, init_data)


class LocalRunner(BaseRunner):
    def run(self, runnable_cls, init_data):
        args, kwargs = init_data
        return runnable_cls(*args, **kwargs)


class DockerContainerRunner(BaseRunner):
    default_docker_kwargs = dict(
        detach=True,
        network=None,
        auto_remove=True,
        restart_policy=docker.types.RestartPolicy()
    )

    def __init__(self, *args, docker_kwargs=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_docker_kwargs = self.merge_docker_kwargs(
            self.default_docker_kwargs,
            docker_kwargs
        )
        self._docker_client = docker.from_env()

    @staticmethod
    def merge_docker_kwargs(*kwarg_dicts):
        env = {}
        final_kwargs = {}

        for d in kwarg_dicts:
            if d:
                env.update(
                    d.get('environment', {})
                )
                final_kwargs.update(d)

        final_kwargs['environment'] = env
        return final_kwargs

    def run(self, runnable_cls, init_data, docker_kwargs=None):
        instance_name = f'runnable_{runnable_cls.__name__.lower()}'

        docker_kwargs = self.merge_docker_kwargs(
            self.default_docker_kwargs,
            docker_kwargs,
            dict(
                environment=dict(
                    KAFTHON_INIT_DATA=MsgpackSerializer.serialize(init_data, as_base64=True)
                )
            )
        )

        try:
            self._docker_client.containers.get(instance_name).remove(force=True)
        except docker.errors.NotFound:
            pass

        return self._docker_client.containers.run(
            name=instance_name,
            command=[
                'python',
                '-m', 'kafthon.start_runnable',
                get_cls_path(runnable_cls)
            ],
            **docker_kwargs
        )


# class DockerSwarmRunner(BaseRunner):
#     default_docker_kwargs = dict(
#         env=os.environ.copy(),
#         neworks=(),
#         restart_policy=docker.types.RestartPolicy()
#     )

#     def __init__(self, *args, docker_kwargs=None, **kwargs):
#         super().__init__(*args, **kwargs)

#         self._docker_kwargs = {**self.default_docker_kwargs, **(docker_kwargs or {})}
#         self._docker_client = docker.DockerClient()

#     def deploy_service(self, runnable_cls, *args, docker_kwargs=None, **kwargs):
#         instance_name = f'runnable_{runnable_cls.__name__.lower()}'

#         docker_kwargs = {**self._docker_kwargs, **docker_kwargs}

#         try:
#             self.services.get(instance_name).remove()
#             self.containers.get(instance_name).remove(force=True)
#         except docker.errors.NotFound:
#             pass

#         self.containers.run(
#             name=instance_name,
#             command=[
#                 'python',
#                 '-m', 'kafthon.start_runnable',
#                 get_cls_path(runnable_cls)
#             ],
#             **docker_kwargs
#         )
