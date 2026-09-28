#!/usr/bin/env python3
"""在临时输出目录编译并运行卷一第二章的正文工程与题解。"""
import argparse,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'01-基础通识'
PROJECTS=['class-basics-demo','lambda-move-demo','smart-pointer-demo','stl-container-demo','thread-coordination-demo','memory-lifetime-demo']
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 rows=[]
 with tempfile.TemporaryDirectory(prefix='cpp-chapter-check-') as temp:
  work=Path(temp);sources=[]
  for project in PROJECTS:sources += sorted((ROOT/'examples'/project).glob('*.cpp'))
  text=(ROOT/'answers.tex').read_text().split(r'\section*{第二章')[1].split(r'\section*{第三章')[0]
  for name,code in re.findall(r'% answer-code: ([^\n]+)\s*\\begin\{tcpp\}(.*?)\\end\{tcpp\}',text,re.S):
   path=work/('answer-'+name);path.write_text(code.strip()+'\n');sources.append(path)
  for index,source in enumerate(sources):
   binary=work/f'run-{index}';standard='c++20' if source.stem=='designated' else 'c++17'
   command=['g++','-std='+standard,'-Wall','-Wextra','-pthread',str(source),'-o',str(binary)]
   compile_result=subprocess.run(command,text=True,capture_output=True)
   row={'source':str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else source.name,'compile':compile_result.returncode,'diagnostics':compile_result.stderr}
   if compile_result.returncode==0:
    run=subprocess.run(['timeout','5s' if source.stem!='deadlock' else '1s',str(binary)],input='(())()\n' if source.name=='answer-parentheses.cpp' else 'armor camera armor\n',text=True,capture_output=True)
    row.update(run=run.returncode,stdout=run.stdout,stderr=run.stderr)
   rows.append(row)
  versions=subprocess.run(['g++','--version'],capture_output=True,text=True).stdout.splitlines()[0]
  args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps({'compiler':versions,'results':rows},ensure_ascii=False,indent=2)+'\n')
  failed=[r for r in rows if r['compile'] or r.get('run') not in ([0,124] if r['source'].endswith('/deadlock.cpp') else [0,2] if r['source']=='answer-wait_timeout.cpp' else [0])]
  print(f'{versions}: {len(rows)} 个程序，{len(failed)} 个非预期失败。结果：{args.output}')
  for row in failed:print(json.dumps(row,ensure_ascii=False))
  if failed:raise SystemExit(1)
if __name__=='__main__':main()
