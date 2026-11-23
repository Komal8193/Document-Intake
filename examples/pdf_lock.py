"""Is a PDF locked with a password that must be typed to open it? (found in my review, Nov 2026)

A brokerage statement often arrives with an "open" password. Before this check such a file was accepted
as "Received" but could never be read, by the AI or by staff without the client's password. Now it is
refused at upload with plain words, so the client sends an unlocked copy.

Only an open password counts. Many PDFs carry permission settings (no printing, no copying) but open
without a password; those are accepted as before.

PDFium opens the file in a separate, limited process (the same limits as the paper reader), so a hostile
PDF can't take the server's memory or time. Anything unexpected (a crash, a time-out, a damaged file)
counts as "not locked": the upload goes on as before and staff see the file.
"""

import multiprocessing
import os
import re
import resource

# In the full project these come from the upload checker:
# CHUNK = read size, _matches(file, pattern) = search the file in parts.
from filecheck import CHUNK, _matches  # noqa: F401 (not included in this showcase)

# The PDF key that every password or permission setting needs, also when written with #xx escapes, which
# PDF allows in names (for example /Encr#79pt; PDFium honours them). A PDF without it can't be locked.
ENCRYPT = re.compile(rb"/(?:E|#45)(?:n|#6[eE])(?:c|#63)(?:r|#72)(?:y|#79)(?:p|#70)(?:t|#74)")
# Only "needs a password" refuses. Certificate-based or unknown security (other codes) is accepted.
FPDF_ERR_PASSWORD = 4
WAIT_SECONDS = 20
# The paper reader's limits (512 MB, 15 s): up to 3 uploads are checked at once on a 512 MB server.
MEMORY_BYTES = 512 * 1024 * 1024
CPU_SECONDS = 15


def may_be_locked(f) -> bool:
    """Quick look for the key, read in parts. Most PDFs stop here."""
    return _matches(f, ENCRYPT)


def _child(connection, data: bytes) -> None:
    try:
        with open(os.devnull, "w") as sink:
            os.dup2(sink.fileno(), 1)
            os.dup2(sink.fileno(), 2)
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
        resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS + 1))
        import pypdfium2 as pdfium

        try:
            pdfium.PdfDocument(data).close()
            connection.send(False)
        except pdfium.PdfiumError as exc:
            connection.send(getattr(exc, "err_code", None) == FPDF_ERR_PASSWORD)
    except Exception:
        connection.send(False)
    finally:
        connection.close()


def needs_password(data: bytes) -> bool:
    """True only when PDFium says the file needs a password to open."""
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe()
    process = context.Process(target=_child, args=(child, data))
    process.start()
    child.close()
    try:
        if parent.poll(WAIT_SECONDS):
            try:
                return bool(parent.recv())
            except EOFError:
                pass
        return False
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=2)
        if process.is_alive():
            process.kill()
            process.join()
        parent.close()


def locked(f) -> bool:
    """f: the whole uploaded PDF (at most 25 MB), positioned anywhere."""
    if not may_be_locked(f):
        return False
    f.seek(0)
    data = b"".join(iter(lambda: f.read(CHUNK), b""))
    return needs_password(data)
