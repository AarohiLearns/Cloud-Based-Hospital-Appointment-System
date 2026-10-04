import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    # Plain stdout logging: ECS/Fargate ships it to CloudWatch Logs automatically.
    logging.basicConfig(
        level=level,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
