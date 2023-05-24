from polyaxon.deploy.operators.cmd_operator import CmdOperator
from polyaxon.exceptions import PolyaxonOperatorException


class DockerOperator(CmdOperator):
    CMD = "docker"

    @classmethod
    def params(cls, args):
        params = [cls.CMD] + args
        return params

    @classmethod
    def check(cls):
        command_exist = cls.execute(args=["version"])
        if not command_exist:
            return False
        return True

    @classmethod
    def execute(cls, args, stream=False, output_only: bool = True):
        params = cls.params(args)
        return cls._execute(
            params=params, env=None, stream=stream, output_only=output_only
        )

    @classmethod
    def set_volume(cls, volume):
        args = ["volume", "create", "--name={}".format(volume)]
        if not volume:
            raise PolyaxonOperatorException(
                "docker", args, None, None, "Volume name was not provided"
            )
        return cls.execute(args)
