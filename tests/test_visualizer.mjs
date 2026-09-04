// MIT. Controller tests with a tiny DOM/canvas stub; not browser visual QA.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const html=fs.readFileSync(path.join(root,'visualize.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{textContent:'',value:id==='lags'?'128':'reference',listeners:{},addEventListener(event,fn){this.listeners[event]=fn},getBoundingClientRect(){return {width:850,height:240}},getContext(){return new Proxy({},{get:()=>()=>{}})},setAttribute(){},classList:{toggle(){}},click(){}});return elements.get(id)}
const context=vm.createContext({console,BigInt,Math,Number,String,Array,Uint8Array,Blob,URL,setTimeout,clearTimeout,document:{getElementById:element,querySelectorAll:()=>[],createElement:()=>element('created')},window:{devicePixelRatio:1,addEventListener(){}}});
vm.runInContext(script,context);
assert.equal(element('energy').textContent,'17,996');
assert.equal(element('merit').textContent,'7.283396');
assert.equal(element('peak').textContent,'32');
element('preset').listeners.change({target:{value:'rudin'}});
assert.equal(element('energy').textContent,'43,776');
assert.equal(element('verdict').textContent,'Valid data. Does not improve the reference.');
const raw=fs.readFileSync(path.join(root,'fixtures/baseline/sequence.txt'));
const file={size:raw.length,name:'<script>not executable</script>.txt',arrayBuffer:async()=>Uint8Array.from(raw).buffer};
await element('file').listeners.change({target:{files:[file],value:'file'}});
assert.equal(element('energy').textContent,'17,996');
assert.equal(element('source-name').textContent,file.name);
const bad={size:514,name:'bad.txt',arrayBuffer(){throw Error('must not read oversized file')}};
await element('file').listeners.change({target:{files:[bad],value:'file'}});
assert.match(element('error').textContent,/exactly 513 bytes/);
assert.equal(element('energy').textContent,'17,996');
console.log('Visualizer controller: reference, comparison, exact upload, unsafe-name text rendering and oversized rejection passed. No browser layout review claimed.');
