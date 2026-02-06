"""API client for video generation with adaptive streaming."""
import json
import logging
from typing import Optional

import httpx
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from src.config import API_ENDPOINT, API_TOKEN, MODEL_NAME, REQUEST_TIMEOUT
from src.errors import APIError, StreamingError

logger = logging.getLogger(__name__)


def generate_video(
    prompt: str,
    model: str,
    img1_b64: Optional[str] = None,
    img2_b64: Optional[str] = None
) -> bytes:
    """
    Generate video from text prompt and optional images using adaptive streaming.

    Args:
        prompt: Text description for video generation
        model: Model ID to use for generation
        img1_b64: Base64-encoded first image (optional for T2V, required for I2V)
        img2_b64: Base64-encoded second image (optional, for first-last frame I2V)

    Returns:
        Complete video file as bytes

    Raises:
        APIError: If HTTP request fails (4xx/5xx status codes)
        StreamingError: If response parsing fails
    """
    # Build content array based on available inputs
    content = []

    # Add images if provided
    if img1_b64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img1_b64}"}
        })

    if img2_b64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img2_b64}"}
        })

    # Add text prompt
    content.append({
        "type": "text",
        "text": prompt
    })

    # Build API payload
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": content
        }],
        "stream": True
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    logger.info(f"Sending request to {API_ENDPOINT} with model {MODEL_NAME}")
    logger.debug(f"Prompt: {prompt}")

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            with client.stream("POST", API_ENDPOINT, json=payload, headers=headers) as response:
                # Check for HTTP errors
                if response.status_code >= 400:
                    # Read the response body for streaming responses
                    response.read()
                    error_text = response.text
                    logger.error(f"API error {response.status_code}: {error_text}")
                    raise APIError(
                        f"API request failed with status {response.status_code}: {error_text}"
                    )

                logger.info(f"Response status: {response.status_code}")
                content_type = response.headers.get("content-type", "").lower()
                logger.info(f"Content-Type: {content_type}")

                # Adaptive streaming based on content type
                video_data = _parse_streaming_response(response, content_type)

                if not video_data:
                    raise StreamingError("No video data received from API")

                logger.info(f"Successfully received {len(video_data)} bytes of video data")
                return video_data

    except httpx.TimeoutException as e:
        logger.error(f"Request timeout after {REQUEST_TIMEOUT} seconds")
        raise APIError(f"Request timeout: {e}")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise APIError(f"HTTP error: {e}")
    except Exception as e:
        if isinstance(e, (APIError, StreamingError)):
            raise
        logger.error(f"Unexpected error: {e}")
        raise StreamingError(f"Unexpected error during video generation: {e}")


def _parse_streaming_response(response: httpx.Response, content_type: str) -> bytes:
    """
    Parse streaming response with adaptive format detection.

    Args:
        response: HTTPX streaming response
        content_type: Content-Type header value

    Returns:
        Video data as bytes

    Raises:
        StreamingError: If parsing fails
    """
    # Determine content length for progress bar
    content_length = response.headers.get("content-length")
    total_size = int(content_length) if content_length else None

    # Strategy 1: Binary stream (application/octet-stream, video/*)
    if "octet-stream" in content_type or content_type.startswith("video/"):
        logger.info("Detected binary stream format")
        return _parse_binary_stream(response, total_size)

    # Strategy 2: Server-Sent Events (text/event-stream)
    elif "text/event-stream" in content_type:
        logger.info("Detected SSE format")
        return _parse_sse_stream(response, total_size)

    # Strategy 3: JSON stream (application/json, application/x-ndjson)
    elif "json" in content_type:
        logger.info("Detected JSON stream format")
        return _parse_json_stream(response, total_size)

    # Strategy 4: Unknown - try all strategies
    else:
        logger.warning(f"Unknown content type '{content_type}', attempting auto-detection")
        return _parse_unknown_stream(response, total_size)


def _parse_binary_stream(response: httpx.Response, total_size: Optional[int]) -> bytes:
    """Parse direct binary stream."""
    chunks = []
    downloaded = 0

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("Downloading video", total=total_size)

        for chunk in response.iter_bytes(chunk_size=8192):
            chunks.append(chunk)
            downloaded += len(chunk)
            progress.update(task, advance=len(chunk))

    return b"".join(chunks)


def _parse_sse_stream(response: httpx.Response, total_size: Optional[int]) -> bytes:
    """Parse Server-Sent Events stream."""
    video_chunks = []

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        DownloadColumn(),
    ) as progress:
        task = progress.add_task("Receiving SSE stream", total=total_size)

        buffer = ""
        line_count = 0
        for chunk in response.iter_text():
            buffer += chunk
            lines = buffer.split("\n")
            buffer = lines[-1]  # Keep incomplete line

            for line in lines[:-1]:
                line_count += 1
                line = line.strip()

                # DEBUG: Log all non-empty lines
                if line:
                    logger.info(f"SSE Line {line_count}: {line[:200]}")

                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        continue

                    try:
                        data = json.loads(data_str)
                        # DEBUG: Print ALL SSE events to see structure
                        logger.info(f"SSE event: {json.dumps(data, ensure_ascii=False)[:500]}")

                        # Extract video data from various possible locations
                        video_chunk = _extract_video_from_json(data)
                        if video_chunk:
                            logger.info(f"✓ Extracted {len(video_chunk)} bytes of video data")
                            video_chunks.append(video_chunk)
                            progress.update(task, advance=len(video_chunk))
                        else:
                            logger.warning(f"✗ No video data found in event. Keys: {list(data.keys())}")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse SSE JSON: {e}")
                        logger.warning(f"Problematic data: {data_str[:200]}")
                        continue

    if not video_chunks:
        raise StreamingError("No video data found in SSE stream")

    return b"".join(video_chunks)


def _parse_json_stream(response: httpx.Response, total_size: Optional[int]) -> bytes:
    """Parse newline-delimited JSON stream."""
    video_chunks = []

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        DownloadColumn(),
    ) as progress:
        task = progress.add_task("Receiving JSON stream", total=total_size)

        buffer = ""
        for chunk in response.iter_text():
            buffer += chunk
            lines = buffer.split("\n")
            buffer = lines[-1]  # Keep incomplete line

            for line in lines[:-1]:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    video_chunk = _extract_video_from_json(data)
                    if video_chunk:
                        video_chunks.append(video_chunk)
                        progress.update(task, advance=len(video_chunk))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON line: {e}")
                    continue

    if not video_chunks:
        raise StreamingError("No video data found in JSON stream")

    return b"".join(video_chunks)


def _parse_unknown_stream(response: httpx.Response, total_size: Optional[int]) -> bytes:
    """
    Auto-detect format by examining first chunk.

    Try strategies in order:
    1. Check if first bytes look like video magic numbers
    2. Try parsing as JSON
    3. Try parsing as SSE
    4. Fall back to raw binary
    """
    # Read first chunk to detect format
    first_chunk = None
    chunks_iter = response.iter_bytes(chunk_size=8192)

    try:
        first_chunk = next(chunks_iter)
    except StopIteration:
        raise StreamingError("Empty response received")

    # Check for common video file signatures (magic numbers)
    video_signatures = [
        b"\x00\x00\x00\x18ftypmp4",  # MP4
        b"\x00\x00\x00\x1cftypiso",  # MP4 variant
        b"RIFF",  # AVI (followed by size then "AVI ")
        b"\x1aE\xdf\xa3",  # WebM/MKV
    ]

    is_likely_video = any(first_chunk.startswith(sig) for sig in video_signatures)

    if is_likely_video:
        logger.info("Auto-detected binary video format")
        # Collect remaining chunks
        chunks = [first_chunk]
        downloaded = len(first_chunk)

        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
        ) as progress:
            task = progress.add_task("Downloading video", total=total_size, completed=downloaded)

            for chunk in chunks_iter:
                chunks.append(chunk)
                progress.update(task, advance=len(chunk))

        return b"".join(chunks)

    # Try parsing as text-based format
    try:
        text_data = first_chunk.decode("utf-8")

        # Check if it looks like SSE
        if text_data.strip().startswith("data:"):
            logger.info("Auto-detected SSE format")
            # Re-create response iteration with first chunk
            video_chunks = []
            buffer = text_data

            for chunk in chunks_iter:
                buffer += chunk.decode("utf-8")
                lines = buffer.split("\n")
                buffer = lines[-1]

                for line in lines[:-1]:
                    line = line.strip()
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            continue
                        try:
                            data = json.loads(data_str)
                            video_chunk = _extract_video_from_json(data)
                            if video_chunk:
                                video_chunks.append(video_chunk)
                        except json.JSONDecodeError:
                            continue

            if video_chunks:
                return b"".join(video_chunks)

        # Check if it looks like JSON
        if text_data.strip().startswith("{"):
            logger.info("Auto-detected JSON format")
            video_chunks = []
            buffer = text_data

            for chunk in chunks_iter:
                buffer += chunk.decode("utf-8")
                lines = buffer.split("\n")
                buffer = lines[-1]

                for line in lines[:-1]:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        video_chunk = _extract_video_from_json(data)
                        if video_chunk:
                            video_chunks.append(video_chunk)
                    except json.JSONDecodeError:
                        continue

            if video_chunks:
                return b"".join(video_chunks)

    except UnicodeDecodeError:
        pass

    # Fall back to binary
    logger.info("Falling back to raw binary stream")
    chunks = [first_chunk]
    for chunk in chunks_iter:
        chunks.append(chunk)

    return b"".join(chunks)


def _extract_video_from_json(data: dict) -> Optional[bytes]:
    """
    Extract video data from JSON object.

    Tries multiple common field names and encoding formats.
    Also handles video URLs that need to be downloaded.
    """
    import re

    # Common field names for video data
    possible_fields = [
        "video",
        "data",
        "content",
        "file",
        "video_data",
        "video_content",
        "binary",
        "base64",
    ]

    # Common field names for URLs
    url_fields = [
        "url",
        "video_url",
        "download_url",
        "file_url",
        "uri",
        "content",  # Also check content field for URLs
    ]

    def extract_url_from_html(text: str) -> Optional[str]:
        """Extract URL from HTML video tag or plain text."""
        if not isinstance(text, str):
            return None

        # Try to extract from <video src='...'> or <video src="...">
        match = re.search(r"<video[^>]+src=['\"]([^'\"]+)['\"]", text)
        if match:
            return match.group(1)

        # Check if it's a plain URL
        if text.startswith("http"):
            return text

        return None

    # Also check nested in choices/delta pattern (ChatGPT-style)
    if "choices" in data:
        for choice in data["choices"]:
            if "delta" in choice:
                # Check for URLs first (including in content field)
                for field in url_fields:
                    if field in choice["delta"]:
                        value = choice["delta"][field]
                        url = extract_url_from_html(value)
                        if url:
                            logger.info(f"Found video URL in delta.{field}")
                            return _download_video_from_url(url)

                # Then check for direct data
                for field in possible_fields:
                    if field in choice["delta"] and field != "content":
                        return _decode_video_data(choice["delta"][field])

            if "message" in choice:
                # Check for URLs first
                for field in url_fields:
                    if field in choice["message"]:
                        value = choice["message"][field]
                        url = extract_url_from_html(value)
                        if url:
                            logger.info(f"Found video URL in message.{field}")
                            return _download_video_from_url(url)

                # Then check for direct data
                for field in possible_fields:
                    if field in choice["message"] and field != "content":
                        return _decode_video_data(choice["message"][field])

    # Check top level for URLs first
    for field in url_fields:
        if field in data:
            value = data[field]
            url = extract_url_from_html(value)
            if url:
                logger.info(f"Found video URL in field '{field}'")
                return _download_video_from_url(url)

    # Check top level for direct data
    for field in possible_fields:
        if field in data and field != "content":
            return _decode_video_data(data[field])

    return None


def _download_video_from_url(url: str) -> Optional[bytes]:
    """
    Download video from a URL (e.g., Google Cloud Storage signed URL).

    Args:
        url: Full URL to download video from

    Returns:
        Video bytes or None if download fails
    """
    logger.info(f"Downloading video from URL...")
    logger.debug(f"Full URL: {url}")

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(url)

            if response.status_code == 200:
                video_bytes = response.content
                logger.info(f"✓ Successfully downloaded {len(video_bytes)} bytes ({len(video_bytes)/1024/1024:.2f} MB)")
                return video_bytes
            else:
                logger.error(f"Failed to download video: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return None

    except Exception as e:
        logger.error(f"Error downloading video from URL: {e}")
        return None


def _decode_video_data(value: any) -> Optional[bytes]:
    """
    Decode video data from various formats.

    Handles:
    - Raw bytes
    - Base64-encoded strings
    - Hex-encoded strings
    """
    if isinstance(value, bytes):
        return value

    if isinstance(value, str):
        # Try base64 decode
        try:
            import base64
            return base64.b64decode(value)
        except Exception:
            pass

        # Try hex decode
        try:
            return bytes.fromhex(value)
        except Exception:
            pass

    return None
