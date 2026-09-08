import os
import subprocess

class ApplicationNotFound(RuntimeError): pass

class Result:
    def __init__(self, code, out, err):
        self.code = code
        self.out = out
        self.err = err

class Application:
    def __init__(self, path: str):
        self._app = path

    def call_single(self, kvargs: list[str], inlines: str, isoutputatext=True) -> Result:
        if not os.path.exists(self._app): raise ApplicationNotFound(f"{self._app} not present in current fs.")
        hProc = subprocess.run([self._app, *kvargs], capture_output=True, input=inlines, text=isoutputatext)
        return Result(hProc.returncode, hProc.stdout, hProc.stderr)