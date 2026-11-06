"""Hash-bound new-app test runner, exact unique executed method IDs."""
import hashlib,json,os,pathlib,sys,time,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-auftrag02-evidence/implementation/final/browser')).parent
OUT.mkdir(parents=True,exist_ok=True)
def manifest():
    paths=[p for base in ['lumo_raumstudio','tests/raumstudio','scripts','docs/raumstudio'] for p in (ROOT/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
class Result(unittest.TextTestResult):
    ids=[]
    def startTest(self,test):self.ids.append(test.id());super().startTest(test)
before=manifest();start=time.time();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests/raumstudio'),pattern='test_*.py');runner=unittest.TextTestRunner(verbosity=2,resultclass=Result);result=runner.run(suite);after=manifest()
report={'passed':result.wasSuccessful() and before==after,'testsRun':result.testsRun,'uniqueMethods':len(set(result.ids)),'testIds':sorted(set(result.ids)),'failures':[{'test':t.id(),'trace':trace} for t,trace in result.failures],'errors':[{'test':t.id(),'trace':trace} for t,trace in result.errors],'skipped':[(t.id(),why) for t,why in result.skipped],'sourceUnchangedDuringRun':before==after,'elapsedSeconds':time.time()-start,'manifest':after,'physicalTouch':False,'installedHA':False,'hostImageBuild':False,'publication':False}
(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(OUT/'manifest.json').write_text(json.dumps(after,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('manifest','testIds','failures','errors')},ensure_ascii=False));sys.exit(0 if report['passed'] else 1)
