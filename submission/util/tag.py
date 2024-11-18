import re


def clear_s3_tag(tag_value: str):
    """Clear tag value to comply with S3 tag value rules."""
    val = re.sub(r"[^a-zA-Z0-9+\-=._:/@]", "_", tag_value)
    if len(val) > 256:
        val = val[:253] + "..."
    return val
