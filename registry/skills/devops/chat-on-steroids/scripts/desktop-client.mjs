// Local-only Desktop MCP adapter. No dependencies, browser-storage access or private ChatGPT APIs.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash, randomUUID} from 'node:crypto';
const stateDir=process.env.COS_AGENT_STATE_DIR ?? path.join(os.homedir(),'.config','chat-on-steroids-agent');
const endpointFile=path.join(stateDir,'desktop-url');
function localUrl(text){
  const u=new URL(text.trim());
  if(u.protocol!=='http:' || !['127.0.0.1','[::1]'].includes(u.hostname) || u.username || u.password || u.hash || u.pathname==='/') throw Error('A literal-loopback HTTP Desktop MCP URL is required');
  return u.href;
}
const [command, tool, input]=process.argv.slice(2);
let endpoint;
try {
  if(command==='configure'){
    endpoint=localUrl(fs.readFileSync(0,'utf8'));
    fs.mkdirSync(stateDir,{recursive:true,mode:0o700});fs.chmodSync(stateDir,0o700);
    fs.writeFileSync(endpointFile,endpoint+'\n',{mode:0o600});fs.chmodSync(endpointFile,0o600);
    console.log(JSON.stringify({configured:true,fingerprint:createHash('sha256').update(endpoint).digest('hex').slice(0,16)}));
    process.exit(0);
  }
  if(!['status','schema','call'].includes(command))throw Error('Use configure, status, schema, or call TOOL JSON');
  if(!fs.existsSync(endpointFile))throw Error('Desktop endpoint is not configured; the owner must copy the local Desktop URL from the running app');
  if(process.platform!=='win32' && (fs.statSync(endpointFile).mode & 0o077))throw Error('Endpoint file must be owner-only (0600)');
  endpoint=localUrl(fs.readFileSync(endpointFile,'utf8'));
  if(command==='call' && !['observe','computer'].includes(tool))throw Error('Only Desktop observe/computer tools are permitted');
  let session, protocol='2025-06-18', sequence=0;
  async function rpc(method,params,notification=false){
    const id=notification?undefined:++sequence;
    const response=await fetch(endpoint,{method:'POST',redirect:'error',signal:AbortSignal.timeout(30000),
      headers:{'Content-Type':'application/json',Accept:'application/json, text/event-stream',...(session?{'mcp-session-id':session}:{}),'MCP-Protocol-Version':protocol},
      body:JSON.stringify({jsonrpc:'2.0',...(id?{id}:{}),method,params})});
    if(!response.ok)throw Error('Local Desktop MCP returned HTTP '+response.status);
    session=response.headers.get('mcp-session-id')??session;
    if(notification || response.status===204){await response.body?.cancel();return;}
    const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='',bytes=0;
    try{
      while(true){
        const {value,done}=await reader.read();if(done)break;
        bytes+=value.length;if(bytes>16*1024*1024)throw Error('Response exceeds the desktop output budget');
        buffer+=decoder.decode(value,{stream:true});
        const candidates=response.headers.get('content-type')?.includes('text/event-stream')
          ? buffer.split(/\r?\n/).filter(l=>l.startsWith('data:')).map(l=>l.slice(5).trim()) : [buffer];
        for(const text of candidates){
          let result;try{result=JSON.parse(text);}catch{continue;}
          if(result.id!==id)continue;
          if(result.error)throw Error('Desktop MCP error: '+String(result.error.message));
          return result.result;
        }
      }
      throw Error('No matching MCP response');
    }finally{await reader.cancel().catch(()=>{});}
  }
  const initialized=await rpc('initialize',{protocolVersion:protocol,capabilities:{},clientInfo:{name:'siso-desktop-client',version:'0.1.0'}});
  protocol=initialized.protocolVersion;
  await rpc('notifications/initialized',{},true);
  const advertised=await rpc('tools/list',{});
  const desktopTools=advertised.tools.filter(t=>['observe','computer'].includes(t.name));
  if(!desktopTools.length)throw Error('No Desktop tools are advertised at this endpoint');
  if(command==='call' && !desktopTools.some(t=>t.name===tool))throw Error('The requested Desktop tool is not currently enabled');
  if(command==='status')console.log(JSON.stringify({connected:true,tools:desktopTools.map(t=>t.name),os_permissions_verified:false}));
  else if(command==='schema')console.log(JSON.stringify(advertised.tools.filter(t=>['observe','computer'].includes(t.name)),null,2));
  else {
    const args=JSON.parse(input==='-'?fs.readFileSync(0,'utf8'):input??'{}');
    const result=await rpc('tools/call',{name:tool,arguments:args});
    const content=[];
    for(const block of result.content??[]){
      if(block.type!=='image'){content.push(block);continue;}
      if(!process.env.COS_OUTPUT_DIR){content.push({type:'text',text:'Image omitted: set COS_OUTPUT_DIR to a private evidence directory.'});continue;}
      const dir=path.resolve(process.env.COS_OUTPUT_DIR);fs.mkdirSync(dir,{recursive:true,mode:0o700});
      if(process.platform!=='win32' && (fs.statSync(dir).mode&0o077))throw Error('Image evidence directory must be owner-only');
      const extension={'image/png':'png','image/jpeg':'jpg','image/webp':'webp'}[block.mimeType];if(!extension)throw Error('Unsupported image MIME type');
      const filename=path.join(dir,randomUUID()+'.'+extension);fs.writeFileSync(filename,Buffer.from(block.data,'base64'),{mode:0o600,flag:'wx'});
      content.push({type:'text',text:'Image saved: '+filename});
    }
    let output=JSON.stringify({...result,content});
    output=output.replaceAll(endpoint,'[local Desktop endpoint]').replace(/([?&](?:code|access_token|refresh_token|id_token|client_secret)=)[^&\s"\\]+/gi,'$1[redacted]');
    for(const key of ['text','value','password'])if(typeof args[key]==='string' && args[key].length>=8)output=output.replaceAll(JSON.stringify(args[key]).slice(1,-1),'[input redacted]');
    console.log(output);
  }
}catch(error){
  let message=error instanceof Error?error.message:'Desktop client failed';
  if(endpoint)message=message.replaceAll(endpoint,'[local endpoint]');
  console.error(JSON.stringify({status:'blocked',error:message}));process.exitCode=1;
}
