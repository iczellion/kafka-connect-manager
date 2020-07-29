""" CLI to create the InfluxDB Sink connector
https://docs.lenses.io/connectors/sink/influx.html
"""

__all__ = ["create_influxdb_sink"]

import json
import time

import click

from kafkaconnect.config import Config
from kafkaconnect.connect import Connect
from kafkaconnect.influxdb_sink.config import InfluxConfig
from kafkaconnect.topics import Topic

influx_config = InfluxConfig()


@click.command("influxdb-sink")
@click.option(
    "-n",
    "--name",
    "name",
    required=False,
    default=InfluxConfig.name,
    show_default=True,
    help=(
        "Name of the connector. Alternatively set via the "
        "$KAFKA_CONNECT_NAME env var."
    ),
)
@click.option(
    "-i",
    "--influxdb_url",
    "connect_influx_url",
    required=False,
    default=InfluxConfig.connect_influx_url,
    show_default=True,
    help=(
        "InfluxDB connection URL. Alternatively set via the "
        "$KAFKA_CONNECT_INFLUXDB_URL env var."
    ),
)
@click.option(
    "-d",
    "--database",
    "connect_influx_db",
    required=False,
    default=InfluxConfig.connect_influx_db,
    show_default=True,
    help=(
        "InfluxDB database name. The database must exist at InfluxDB. "
        "Alternatively set via the $KAFKA_CONNECT_DATABASE env var."
    ),
)
@click.option(
    "-t",
    "--tasks-max",
    "tasks_max",
    required=False,
    default=InfluxConfig.tasks_max,
    show_default=True,
    help=(
        "Number of Kafka Connect tasks. Alternatively set via the "
        "$KAFKA_CONNECT_TASKS_MAX env var."
    ),
)
@click.option(
    "-u",
    "--username",
    "connect_influx_username",
    required=False,
    default=InfluxConfig.connect_influx_username,
    show_default=True,
    help=(
        "InfluxDB username. Alternatively set via the "
        "$KAFKA_CONNECT_INFLUXDB_USERNAME env var. "
        "Use '-' for unauthenticated users."
    ),
)
@click.option(
    "-p",
    "--password",
    "connect_influx_password",
    required=InfluxConfig.connect_influx_password,
    default="",
    show_default=True,
    help=(
        "InfluxDB password. Alternatively set via the "
        "$KAFKA_CONNECT_INFLUXDB_PASSWORD env var."
    ),
)
@click.option(
    "-r",
    "--topic-regex",
    "topic_regex",
    required=False,
    default=Config.topic_regex,
    show_default=True,
    help=(
        "Regex for selecting topics. Alternatively set via the "
        "$KAFKA_CONNECT_TOPIC_REGEX env var."
    ),
)
@click.option(
    "--dry-run",
    is_flag=True,
    help=(
        "Show the InfluxDB Sink Connector configuration but do not create "
        "the connector."
    ),
)
@click.option(
    "--auto-update",
    is_flag=True,
    help=(
        "Check for new topics and update the connector. See also the "
        "--check-interval option."
    ),
)
@click.option(
    "-v",
    "--validate",
    is_flag=True,
    help=("Validate the connector configuration before creating."),
)
@click.option(
    "-c",
    "--check-interval",
    "check_interval",
    required=False,
    default=Config.check_interval,
    show_default=True,
    help=(
        "The interval, in milliseconds, to check for new topics and update"
        "the connector."
    ),
)
@click.option(
    "-e",
    "--excluded_topics",
    "excluded_topics",
    required=False,
    default=Config.excluded_topics,
    show_default=True,
    help=(
        "Comma separated list of 'problematic' topics to exclude from "
        "selection. Alternatively set via the "
        "$KAFKA_CONNECT_EXCLUDED_TOPICS env var."
    ),
)
@click.option(
    "--timestamp",
    "timestamp",
    required=False,
    default="sys_time()",
    show_default=True,
    help=("Timestamp to use when recording a message in InfluxDB."),
)
@click.option(
    "--error-policy",
    "connect_influx_error_policy",
    type=click.Choice(["NOOP", "THROW", "RETRY"]),
    required=False,
    default=InfluxConfig.connect_influx_error_policy,
    show_default=True,
    help=(
        "Specifies the action to be taken if an error occurs while "
        "inserting the data. There are three available options, NOOP, "
        "the error is swallowed, THROW, the error is allowed to propagate "
        "and RETRY. For RETRY the Kafka message is redelivered up to a "
        "maximum number of times specified by the --max-retries option. "
        "The retry interval is specified by the --retry-interval option. "
        "Alternatively set via the $KAFKA_CONNECT_ERROR_POLICY env var."
    ),
)
@click.option(
    "--max-retries",
    "connect_influx_max_retries",
    default=InfluxConfig.connect_influx_max_retries,
    show_default=True,
    help=(
        "The maximum number of times a message is retried. Only valid when "
        "the --error-policy is set to RETRY. Alternatively set via the "
        "$KAFKA_CONNECT_MAX_RETRIES env var."
    ),
)
@click.option(
    "--retry-interval",
    "connect_influx_retry_interval",
    default=InfluxConfig.connect_influx_retry_interval,
    show_default=True,
    help=(
        "The interval, in milliseconds between retries. Only valid when "
        "the --error-policy is set to RETRY. Alternatively set via the "
        "$KAFKA_CONNECT_RETRY_INTERVAL env var."
    ),
)
@click.option(
    "--progress-enabled",
    "connect_progress_enabled",
    default=InfluxConfig.connect_progress_enabled,
    show_default=True,
    help=(
        "Enables the output for how many records have been processed. "
        "Alternatively set via the $KAFKA_CONNECT_PROGRESS_ENABLED env var."
    ),
)
@click.pass_context
def create_influxdb_sink(
    ctx,
    name,
    connect_influx_url,
    connect_influx_db,
    tasks_max,
    connect_influx_username,
    connect_influx_password,
    topic_regex,
    dry_run,
    auto_update,
    validate,
    check_interval,
    excluded_topics,
    timestamp,
    connect_influx_error_policy,
    connect_influx_max_retries,
    connect_influx_retry_interval,
    connect_progress_enabled,
):
    """Create an instance of the InfluxDB Sink connector.

    Topics are discovered from Kafka, use the --topic-regex and
    --excluded_topics options to help in selecting the topics
    that you want to write to InfluxDB. To check for new topics and update
    the connector configuration use the
    --auto-update and --check-interval options.
    option.
    """
    config = ctx.parent.obj["config"]
    connect = Connect(connect_url=config.connect_url)
    click.echo("Discoverying Kafka topics...")
    # List topics from Kafka
    topics = Topic(config.broker_url, topic_regex, excluded_topics).names
    n = 0 if not topics else len(topics)
    click.echo(f"Found {n} topics.")
    # Connector configuration
    influx_config = InfluxConfig(
        connect_influx_url=connect_influx_url,
        connect_influx_db=connect_influx_db,
        tasks_max=tasks_max,
        connect_influx_username=connect_influx_username,
        connect_influx_password=connect_influx_password,
        connect_influx_error_policy=connect_influx_error_policy,
        connect_influx_max_retries=connect_influx_max_retries,
        connect_influx_retry_interval=connect_influx_retry_interval,
        connect_progress_enabled=connect_progress_enabled,
    )

    if topics:
        influx_config.update_topics(topics)
        influx_config.update_influx_kcql(timestamp)
        if validate:
            click.echo(
                connect.validate(
                    name=influx_config.connector_class,
                    connect_config=influx_config.asjson(),
                )
            )
            return 0
        if dry_run:
            click.echo(influx_config.asjson())
            return 0
        validate = connect.validate(
            name=influx_config.connector_class,
            connect_config=influx_config.asjson(),
        )
        error_count = json.loads(validate)["error_count"]
        click.echo(f"Validation returned {error_count} error(s).")
        if error_count > 0:
            click.echo(
                "Use the --validate option to return the validation results."
            )
            return 0
        click.echo(f"Uploading {name} connector configuration...")
        connect.create_or_update(
            name=name, connect_config=influx_config.asjson()
        )
    if auto_update:
        while True:
            time.sleep(int(check_interval) / 1000)
            try:
                # List topics from Kafka
                current_topics = Topic(
                    config.broker_url, topic_regex, excluded_topics
                ).names
                new_topics = list(set(current_topics) - set(topics))
                if new_topics:
                    click.echo("Found new topics, updating the connector...")
                    influx_config.update_topics(current_topics)
                    influx_config.update_influx_kcql(timestamp)
                    connect.create_or_update(
                        name=name, connect_config=influx_config.asjson()
                    )
                    topics = current_topics
            except KeyboardInterrupt:
                raise click.ClickException("Interruped.")
    return 0
