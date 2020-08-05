import os
from dataclasses import dataclass

from kafkaconnect.config import ConnectConfig


@dataclass
class S3Config(ConnectConfig):
    """S3 Sink connector configuration"""

    name: str = os.getenv("KAFKA_CONNECT_NAME", "s3-sink")
    """Name of the connector.

    The connector name must be unique accross the cluster.
    """

    connector_class: str = "io.confluent.connect.s3.S3SinkConnector"
    """S3 Sink connector class"""

    format_class: str = "io.confluent.connect.s3.format.parquet.ParquetFormat"
    """The format class to use when writing data to the store."""

    parquet_codec: str = "snappy"
    """The Parquet compression codec to be used for output files."""

    schema_compatibility: str = os.getenv(
        "KAFKA_CONNECT_S3_SCHEMA_COMPATIBILITY", "NONE"
    )
    """The schema compatibility rule.

    The supported configurations are NONE, BACKWARD, FORWARD and FULL.
    """

    s3_bucket_name: str = os.getenv("KAFKA_CONNECT_S3_BUCKET_NAME", "")
    """The S3 Bucket."""

    s3_region: str = os.getenv("KAFKA_CONNECT_S3_REGION", "us-east-1")
    """The AWS region to be used the connector."""

    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    """The AWS access key ID used to authenticate personal AWS credentials."""

    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    """The secret access key used to authenticate personal AWS credentials."""

    topics_dir: str = os.getenv("TOPICS_DIR", "topics")
    """Top level directory to store the data ingested from Kafka."""

    storage_class: str = "io.confluent.connect.s3.storage.S3Storage"
    """The underlying storage layer."""

    flush_size: int = int(os.getenv("KAFKA_CONNECT_S3_FLUSH_SIZE", 1000))
    """Number of records written to store before invoking file commits."""

    rotate_interval_ms: int = int(
        os.getenv("KAFKA_CONNECT_S3_ROTATE_INTERVAL_MS", 60000)
    )
    """The time interval in milliseconds to invoke file commits."""

    partitioner_class: str = (
        "io.confluent.connect.storage.partitioner.TimeBasedPartitioner"
    )
    """The partitioner to use when writing data to the store."""

    partition_duration_ms: int = int(
        os.getenv("KAFKA_CONNECT_PARTITION_DURATION_MS", 3600000)
    )
    """The duration of a partition in ms. Used by TimeBasedPartitioner."""

    path_format: str = "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH"

    locale: str = "en-US"
    """The locale to use when partitioning with TimeBasedPartitioner."""

    timezone: str = os.getenv("KAFKA_CONNECT_S3_TIMEZONE", "UTC")
    """The timezone to use when partitioning with TimeBasedPartitioner."""

    timestamp_extractor: str = os.getenv(
        "KAFKA_CONNECT_TIMESTAMP_EXTRACTOR", "Record"
    )
    """The extractor determines how to obtain a timestamp from each record.

    Values can be Wallclock to use the system time when
    the record is processed, Record (default) to use the timestamp of the
    Kafka record denoting when it was produced or stored by the broker,
    RecordField to extract the timestamp from one of the fields in the
    record’s value as specified by the timestamp_field configuration property.
    """

    timestamp_field: str = os.getenv("KAFKA_CONNECT_TIMESTAMP_FIELD", "time")
    """The record field to be used as timestamp by the timestamp extractor."""
