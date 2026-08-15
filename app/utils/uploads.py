from fastapi import UploadFile


class UploadTooLargeError(Exception):
    """Raised when an upload exceeds the configured size limit."""


async def read_upload_limited(
    file: UploadFile,
    max_size: int,
    chunk_size: int = 1024 * 1024,
) -> bytes:

    chunks: list[bytes] = []
    total_size = 0

    while True:

        chunk = await file.read(
            chunk_size
        )

        if not chunk:
            break

        total_size += len(chunk)

        if total_size > max_size:

            raise UploadTooLargeError(
                "Uploaded file exceeds the maximum allowed size."
            )

        chunks.append(chunk)

    return b"".join(chunks)