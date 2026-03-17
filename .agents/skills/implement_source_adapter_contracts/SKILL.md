---
name: implement_source_adapter_contracts
description: Create a clean collector interface and source-adapter contract for weekly quantum site collection, including retries, caps, health reporting, and fallback modes.
---


    # Implement Source Adapter Contracts

    Use this skill when defining or refining the reusable interface for weekly source collectors.

    ## Contract requirements
    Each collector should expose a clear method that returns:
    - collected items
    - source health metadata
    - fallback mode used

    ## Every adapter must support
    - request timeout
    - retry count
    - per-source item cap
    - normalized source labels
    - graceful empty result handling
    - structured error reporting

    ## Recommended objects
    - `SourceConfig`
    - `SourceHealth`
    - `RawArticle`
    - `CollectorResult`

    ## Keep it simple
    - deterministic interfaces
    - no collector should know about LLM prompts
    - collectors should not decide final ranking

