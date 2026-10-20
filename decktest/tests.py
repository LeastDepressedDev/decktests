from __future__ import annotations

from . import fnc

class TestTrace:

    VER_RT_FAIL = "FAIL: RUNTIME FAIL"
    VER_ALL_GOOD = "COMPLETED: ALL GOOD"
    VER_MISMATCH = "FAIL: ANWSER MISMATCH"
    VER_ERR_MISMATCH = "FAIL: ERROR MISMATCH"

    def __init__(self, code: int, verdict: str, trace: str, raw: str):
        self.ecode = code
        self.verdict = verdict
        self.trace = trace
        self.raw = raw

    def __str__(self) -> str:
        pass


        
class TestSection:
    def __init__(self, name, full_test_name=False, break_on_fail=False, log_completed=False):
        self.name = name
        self.tests: list[Test] = []
        self.results: list[tuple[Test, TestTrace, int]] = []
        self.logcmp = log_completed
        self.rtout = break_on_fail
        self.ftest = full_test_name

    def run(self, app: fnc.Application) -> int:
        self.results.clear()
        index = 0
        for test in self.tests: 
            res = (test, test.__apply__(app), index)
            if self.logcmp or res[1].verdict != TestTrace.VER_ALL_GOOD: self.log(index, res)
            self.results.append(res)
            if self.rtout and res[1].verdict != TestTrace.VER_ALL_GOOD: break
            index+=1
        
        if not self.rtout:
            errs = list(filter(lambda v: v[1].verdict!=TestTrace.VER_ALL_GOOD, self.results))
            coted=len(self.tests)-len(errs)
            print(f"\n\nFinal Verdict: {coted}/{len(self.tests)} tests passed. ({(coted/len(self.tests)*100):.3f}%)\nErrors: ")
            for err in errs: print(f"\t{err[2]} - {err[1].verdict}")

        if len(errs)!=0: return 1
        else: return 0


    def log(self, num: int, pr: tuple[Test, TestTrace]):
        print(num, " -> ", sep='', end='')
        if self.ftest: print(self.name, ".", sep='', end='')
        print(pr[0].name, ": ", sep='', end='')
        print(pr[1].verdict)
        if pr[1].verdict==TestTrace.VER_RT_FAIL:
            print(f"Exit code: {pr[1].ecode}", f"Stack trace: {pr[1].trace}", sep='\n')
        if pr[1].verdict in [TestTrace.VER_RT_FAIL, TestTrace.VER_MISMATCH]:
            print(f"\tExpected: {pr[0].exp.replace('\n', '\\n')}", f"\tGot: {pr[1].raw.replace('\n', '\\n')}", sep='\n')
        if pr[1].verdict==TestTrace.VER_ERR_MISMATCH:
            print(pr[1].trace)
        print()


class Test:
    def __init__(self, name: str):
        self.exp = None
        self.exp_err = None
        self.name = name
        self.__insl = []
        self.stdin = ""

    def expect(self, expected: str) -> Test:
        self.exp = expected
        return self

    def expect_error(self, code: int, stderr: str, stdout: str = None) -> Test:
        self.exp_err = (code, stderr)
        return self

    def cmd_line(self, instr: str) -> Test:
        self.__insl = instr
        return self
    
    def input(self, stdin: str) -> Test:
        self.stdin = stdin
        return self

    @staticmethod
    def make_errout_composite(out: str, err: str) -> str:
        return f"\n\tStdout: {out}\n\n\tSterr: {err}"
    
    def __apply__(self, app: fnc.Application) -> TestTrace:
        outp = app.call_single(self.__insl, self.stdin)
        if outp.code==0:
            if self.exp != None:
                if outp.out==self.exp:
                    return TestTrace(0, TestTrace.VER_ALL_GOOD, None, outp.out)
                else:
                    return TestTrace(0, TestTrace.VER_MISMATCH, f"Expected output: {self.exp}", outp.out)
            else:
                return TestTrace(0, TestTrace.VER_MISMATCH, f"Was not expecting to work correctly!!!", outp.out)
        else:
            if self.exp_err != None:
                if self.exp_err[0]==outp.code:
                    if self.exp_err[1] is not None and self.exp_err[1]==outp.err or self.exp_err[1] is None:
                        return TestTrace(0, TestTrace.VER_ALL_GOOD, None, outp.out)
                    else:
                        return TestTrace(0, TestTrace.VER_ERR_MISMATCH, f"Expected different error body:\n{self.exp_err[1]}\n\nGot:\n{outp.err}", Test.make_errout_composite(outp.out, outp.err))
                else:
                    return TestTrace(0, TestTrace.VER_ERR_MISMATCH, f"Expected error code: {self.exp_err[0]}, got: {outp.code}", Test.make_errout_composite(outp.out, outp.err))
            else:
                return TestTrace(outp.code, TestTrace.VER_RT_FAIL, outp.err, outp.out)

    def run_test_single(self, app: fnc.Application) -> TestTrace:
        print(f"Running test{['...', ': '+self.name][self.name is not None]}")
        print(self.__apply__(app))

    def wrap_up(self, sec: TestSection):
        sec.tests.append(self)
