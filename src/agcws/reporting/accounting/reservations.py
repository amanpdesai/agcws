"""Read-only reconstruction of the published Flash reservation amendment."""

from agcws.search.providers.gemini import cost, settings

VERSION = "observed-input-full-output-reserve-v1"


def reservation_bound(response, reserved, arm):
    if not response or response.get("api_error") or not response.get("usage_unknown"):
        return reserved
    usage = response.get("usage_fields") or {}
    incoming = usage.get("prompt_token_count")
    if type(incoming) is not int or not 0 <= incoming <= 200000:
        return reserved
    outgoing = usage.get("candidates_token_count")
    limit = settings(arm)["max_output_tokens"]
    if outgoing is not None and (type(outgoing) is not int or not 0 <= outgoing <= limit):
        return reserved
    return min(reserved, cost(arm, incoming, limit))
