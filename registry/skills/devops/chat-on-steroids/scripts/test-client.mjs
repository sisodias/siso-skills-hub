// Local protocol/permission-boundary test. It never observes or controls a real desktop.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=process.argv[2];if(!dir)throw Error('Caller-owned fixture directory required');
const client=fileURLToPath(new URL('./desktop-client.mjs',import.meta.url));
const run=(args,input='')=>new Promise(resolve=>{
  const child=spawn(process.execPath,[client,...args],{env:{...process.env,COS_AGENT_STATE_DIR:dir},stdio:['pipe','pipe','pipe']});
  let stdout='',stderr='';child.stdout.on('data',d=>stdout+=d);child.stderr.on('data',d=>stderr+=d);child.on('exit',code=>resolve({code,stdout,stderr}));child.stdin.end(input);
});
assert.equal((await run(['status'])).code,1);
assert.equal((await run(['configure'],'https://example.com/secret')).code,1);
const server=createServer((req,res)=>{let b='';req.on('data',d=>b+=d);req.on('end',()=>{
  const m=JSON.parse(b);if(!m.id){res.writeHead(202);res.end();return;}
  const result=m.method==='initialize'?{protocolVersion:'2025-06-18',capabilities:{tools:{}},serverInfo:{name:'fixture',version:'1'}}:
    m.method==='tools/list'?{tools:[{name:'observe',inputSchema:{type:'object'}},{name:'computer',inputSchema:{type:'object'}}]}:
    {isError:true,content:[{type:'text',text:'Screen Recording permission is missing'}]};
  res.setHeader('Content-Type','application/json');res.end(JSON.stringify({jsonrpc:'2.0',id:m.id,result}));
});});
server.listen(0,'127.0.0.1');await new Promise(r=>server.once('listening',r));
try{
  const endpoint=`http://127.0.0.1:${server.address().port}/desktop/fixture-secret`;
  const configured=await run(['configure'],endpoint);assert.equal(configured.code,0);assert.ok(!configured.stdout.includes('fixture-secret'));
  assert.equal(fs.statSync(path.join(dir,'desktop-url')).mode&0o777,0o600);
  assert.equal(JSON.parse((await run(['status'])).stdout).os_permissions_verified,false);
  assert.equal((await run(['call','exec_command','{}'])).code,1);
  const denied=await run(['call','observe','{}']);assert.equal(JSON.parse(denied.stdout).isError,true);assert.match(denied.stdout,/permission is missing/);
  console.log('PASS local-only configuration, secret redaction, Desktop-only tool fence and explicit permission-denial result');
}finally{await new Promise(r=>server.close(r));}
