from clipped.types.gcs import GcsPath
from clipped.types.s3 import S3Path
from clipped.types.uri import Uri
from clipped.types.wasb import WasbPath

from polyaxon.schemas.types.artifacts import V1ArtifactsType
from polyaxon.schemas.types.dockerfile import V1DockerfileType
from polyaxon.schemas.types.event import V1EventType
from polyaxon.schemas.types.file import V1FileType
from polyaxon.schemas.types.git import V1GitType
from polyaxon.schemas.types.tensorboard import V1TensorboardType

V1GcsType = GcsPath
V1S3Type = S3Path
V1UriType = Uri
V1WasbType = WasbPath
