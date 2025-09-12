import json
import csv
import io
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam import pvalue

BRONZE_FIELDS = ["user_id", "session_id", "page_url", "timestamp", "referrer", "ip"]

class ParseCSVSafe(beam.DoFn):
    """Robust CSV parser:
    - Handles quoted fields and commas within quotes
    - Trims BOM and whitespace
    - Routes malformed rows to a dead-letter output
    """
    DEAD_LETTER_TAG = "dead_letter"

    def process(self, element):
        # Normalize newlines/whitespace + strip potential UTF-8 BOM
        line = element.lstrip("\ufeff").rstrip("\r\n")

        try:
            reader = csv.reader(io.StringIO(line))
            fields = next(reader, None)

            # Validate column count
            if not fields or len(fields) != len(BRONZE_FIELDS):
                raise ValueError(f"Bad column count: got {len(fields) if fields else 0}")

            record = dict(zip(BRONZE_FIELDS, fields))
            # Optional: normalize whitespace
            for k, v in record.items():
                record[k] = v.strip() if isinstance(v, str) else v

            yield record

        except Exception as e:
            # Send to DLQ with error context
            yield pvalue.TaggedOutput(self.DEAD_LETTER_TAG, {
                "error": str(e),
                "raw_line": element
            })

def run():
    options = PipelineOptions()
    with beam.Pipeline(options=options) as p:
        parsed = (
            p
            | "Read Bronze CSV" >> beam.io.ReadFromText(
                "data/bronze/clickstream/event_date=2025-08-29/sample_clickstream.csv",
                skip_header_lines=1
            )
            | "Parse CSV safely" >> beam.ParDo(ParseCSVSafe()).with_outputs(
                ParseCSVSafe.DEAD_LETTER_TAG, main="main"
            )
        )

        valid = parsed.main
        dlq = parsed.dead_letter  # dead-letter collection

        _ = (
            valid
            | "Valid → JSON" >> beam.Map(json.dumps)
            | "Write valid to Silver JSONL" >> beam.io.WriteToText(
                "data/silver/clickstream/events",
                file_name_suffix=".json",
                shard_name_template=""
            )
        )

        _ = (
            dlq
            | "DLQ → JSON" >> beam.Map(json.dumps)
            | "Write DLQ" >> beam.io.WriteToText(
                "data/silver/clickstream/dlq",
                file_name_suffix=".json",
                shard_name_template=""
            )
        )

if __name__ == "__main__":
    run()