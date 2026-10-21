// Executes the candidate MainScreen and real profile/panel/client modules in memory.
// Only React hooks, native views, and scheduling are controlled; no candidate files are written.
import fs from 'fs';
import path from 'path';
import vm from 'vm';
import assert from 'assert/strict';
import ts from 'typescript';

// Native views and the hook scheduler are controlled; App, ApiClient, ProfileStore
// and PanelController execute from source. The pending alert request keeps it inert.
function screen() {
const root = path.resolve(__dirname, '../../..');
const cache = new Map();
let cells: any[] = [], cursor=0, effects: any[] = [], intervals: any[] = [], dirty=false, now=0;
const same=(a: any[],b: any[])=>a&&b&&a.length===b.length&&a.every((x: any,i: number)=>Object.is(x,b[i]));
const react={
 createElement:(type: any, props: any, ...children: any[])=>({type,props:{...props,children}}), Fragment:'Fragment',
 useRef:(initial: any)=>{let i=cursor++;return cells[i]??(cells[i]={current:initial});},
 useState:(initial: any)=>{let i=cursor++;if(!(i in cells))cells[i]=initial;return [cells[i],(value: any)=>{const next=typeof value==='function'?value(cells[i]):value;if(!Object.is(next,cells[i]))dirty=true;cells[i]=next;}];},
 useCallback:(fn: any,deps: any[])=>{let i=cursor++;if(!cells[i]||!same(cells[i].deps,deps))cells[i]={fn,deps};return cells[i].fn;},
 useEffect:(fn: any,deps: any[])=>{let i=cursor++;if(!cells[i]||!same(cells[i].deps,deps)){cells[i]={deps};effects.push(fn);}},
};
const rn={StyleSheet:{create:(x: any)=>x},Linking:{},Pressable:'Pressable',ScrollView:'ScrollView',Text:'Text',TextInput:'TextInput',View:'View'};
function load(filename: string): any {
 filename=path.resolve(filename);if(!path.extname(filename)){filename=['.ts','.tsx','.json'].map(ext=>filename+ext).find(fs.existsSync)!;}
 if(cache.has(filename))return cache.get(filename).exports;
 const module: {exports: any}={exports:{}};cache.set(filename,module);
 if(filename.endsWith('.json')){module.exports=JSON.parse(fs.readFileSync(filename, 'utf8'));return module.exports;}
 let source=fs.readFileSync(filename,'utf8');if(filename.endsWith('/App.tsx'))source+='\nexport {MainScreen, PanelSection};';
 const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,esModuleInterop:true,target:ts.ScriptTarget.ES2022}}).outputText;
 const localRequire=(name: string)=>name==='react'?react:name==='react-native'?rn:name==='@amazon-devices/react-native-kepler'?{useTVEventHandler:()=>{}}:name.startsWith('.')?load(path.resolve(path.dirname(filename),name)):require(name);
 class Clock extends Date{static now(){return now;}}
 const context={require:localRequire,module,exports:module.exports,Date:Clock,console,URL,TextEncoder,AbortController,fetch,setInterval:(fn: any)=>{intervals.push(fn);return intervals.length;},clearInterval:()=>{},setTimeout:()=>1,clearTimeout:()=>{}};
 vm.runInNewContext(js,context,{filename});return module.exports;
}
const {MainScreen,PanelSection}=load(path.join(root,'vega-app/src/App.tsx'));
const {ApiClient}=load(path.join(root,'vega-app/src/net/apiClient.ts'));
let settings: any = {}, revision=1, requests: any[] = [], delayPanel=false, failPanel=false;
const envelope=(data: any,id='profile')=>({schemaVersion:1,id,revision,source:'manual',updatedAt:'2026-10-21T00:00:00Z',data});
const panel=()=>envelope({teamLeague:'unassigned/unassigned',scoringBasis:'halfPpr',rows:[],teamTotal:{value:10,source:'live',asOf:'1970-01-01T00:00:00Z'},progress:{value:null}},'panel');
const client=new ApiClient('http://127.0.0.1',{token:()=> 'fixture',fetch:async(url: string,init: any)=>{
 const u=new URL(url);requests.push({path:u.pathname,method:init.method,query:u.search});
 if(u.pathname==='/v1/profile'){
  if(init.method==='PUT'){settings=JSON.parse(init.body).data;revision++;}
  return {status:200,text:async()=>JSON.stringify(envelope(settings))};
 }
 if(u.pathname==='/v1/alerts')return new Promise(()=>{});
 if(u.pathname==='/v1/panel'){
  if(delayPanel)return new Promise(()=>{});
  if(failPanel)throw new Error('offline fixture');
  return {status:200,text:async()=>JSON.stringify(panel())};
 }
 throw new Error('unexpected path');
},timers:{setTimeout:()=>1,clearTimeout:()=>{}}});
const flatten=(x: any): any[]=>!x?[]:Array.isArray(x)?x.flatMap(flatten):typeof x==='object'?[x,...flatten(x.props?.children)]:[];
let tree: any;
function render(){cursor=0;dirty=false;tree=MainScreen({client});const run=effects;effects=[];run.forEach(fn=>fn());return tree;}
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
const button=(label: string)=>{const b=flatten(tree).find(x=>x.props?.label===label);assert.ok(b,'missing button '+label);return b;};
const section=()=>flatten(tree).find(x=>x.type===PanelSection);
return {render, flush, button, section, PanelSection, intervals, requests,
  editor: () => flatten(tree).find(x => x.type?.name === 'TeamLeagueEditor'),
  settings: () => settings, dirty: () => dirty,
  delayPanel: () => { delayPanel = true; },
  offlineAt: (time: number) => { failPanel = true; now = time; },
};
}

async function loadedScreen() {
  const app = screen();
  app.render(); await app.flush(); app.render();
  return app;
}

test('R-1 saved visibility applies to the live panel without restarting', async () => {
  const app = await loadedScreen();
  app.button('Panel visible: on').props.onPress(); app.render();
  await app.button('Save profile').props.onPress(); await app.flush(); app.render();
  expect(app.settings().panelPrefs.visible).toBe(false);
  expect(app.section().props.controller.visible).toBe(false);
});

test('R-1 saved team/league applies to the live panel without restarting', async () => {
  const app = await loadedScreen();
  app.editor().props.onChange({league: 'new-league', team: 'new-team'}); app.render();
  await app.button('Save profile').props.onPress(); await app.flush(); app.render();
  expect(app.settings().teamLeague.team).toBe('new-team');
  expect(app.section().props.controller.teamLeague).toBe('new-league/new-team');
  await app.intervals[0]();
  expect(app.requests.filter(x => x.path === '/v1/panel')[0].query).toContain('new-league');
});

test('R-2 only one panel request is outstanding while the backend is pending', async () => {
  const app = await loadedScreen(); app.delayPanel();
  app.intervals[0](); await app.flush();
  app.intervals[0](); await app.flush();
  expect(app.requests.filter(x => x.path === '/v1/panel')).toHaveLength(1);
});

test('R-3 held values render stale after a refresh fails', async () => {
  const app = await loadedScreen();
  await app.intervals[0](); await app.flush(); app.render();
  expect(JSON.stringify(app.PanelSection(app.section().props))).not.toContain('stale');
  app.offlineAt(61_000); await app.intervals[0](); await app.flush();
  expect(app.dirty()).toBe(true);
  app.render();
  expect(JSON.stringify(app.PanelSection(app.section().props))).toContain('stale 61s');
});

test('NBA panel headers show sport and basis while an untagged NFL header stays basis-only', async () => {
  const app = await loadedScreen();
  await app.intervals[0](); await app.flush(); app.render();
  const props = app.section().props;
  for (const [basis, sport, expected] of [
    ['nbaPoints', 'NBA', 'NBA · Points'],
    ['yahooLeague', 'NBA', 'NBA · Yahoo league scoring'],
    ['halfPpr', null, 'Half-PPR'],
  ]) {
    const rendered = app.PanelSection({...props, snapshot: {...props.snapshot, basis, sport}});
    const header = rendered.props.children[2].props.children[0];
    expect(header.props.children).toEqual([expected]);
  }
});
