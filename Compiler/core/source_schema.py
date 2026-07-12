"""Source schema definition for compiler inputs."""

SOURCE_JSON_SCHEMA = {
    "type": "object",
    "required": [
        "schema",
        "identity",
        "authority",
        "context",
    ],
    "properties": {
        "schema": {"type": "string"},
        "identity": {
            "type": "object",
            "required": ["id", "title", "version"],
        },
        "authority": {
            "type": "object",
            "required": [
                "authoritative",
                "class",
                "source",
            ],
        },
        "context": {
            "type": "object",
            "required": ["scope"],
        },
    },
    "additionalProperties": True,
}