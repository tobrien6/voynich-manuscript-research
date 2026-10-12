const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),
  vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),sandbox={Uint8Array,Number,Error};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(path.join(root,'research/image-index/msi-viewer/viewer.js'),'utf8'),sandbox);
const {toStored,stripExif,viewPixel}=sandbox.MSI_GEOMETRY;
let points=0;
const width=9,height=12,stored=Array.from({length:height},(_,y)=>Array.from({length:width},(_,x)=>`${x}:${y}`));
for (const orientation of [1,3]) for (const mode of ['stored','exif']) {
  const displayed=mode==='exif' && orientation===3 ? stored.slice().reverse().map(row=>row.slice().reverse()) : stored;
  for (let y=0;y<height;y++) for (let x=0;x<width;x++) {
    const [sx,sy]=toStored(x,y,width,height,mode,orientation);
    assert.equal(stored[sy][sx],displayed[y][x]);
    assert.deepEqual(Array.from(toStored(sx,sy,width,height,mode,orientation)),[x,y]);points++;
  }
}
for (const bad of [[-1,0,9,12,'stored',1],[9,0,9,12,'stored',1],[.5,0,9,12,'stored',1],
  [0,0,9,12,'unknown',1],[0,0,9,12,'stored',8]]) assert.throws(()=>toStored(...bad));
let projections=0;
for (const [cw,ch] of [[180,240],[300,200],[600,800]]) for (const zoom of [1,2,3]) {
  const scale=Math.min(cw/width,ch/height)*zoom,cx=4,cy=5.5;
  const left=(cw-width*scale)/2,top=(ch-height*scale)/2;
  for (let y=0;y<height;y++) for (let x=0;x<width;x++) {
    const px=left+(x+.5)*scale,py=top+(y+.5)*scale;
    assert.deepEqual(Array.from(viewPixel(px,py,cw,ch,width,height,zoom,cx,cy)),[x,y]);projections++;
  }
}
assert.equal(viewPixel(0,0,300,200,9,12,1,4,5.5),null);
assert.throws(()=>viewPixel(0,0,0,200,9,12,1,4,5.5));
const record=JSON.parse(fs.readFileSync(path.join(root,'research/image-index/multispectral-intake.json'),'utf8'));
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
let files=0;
if (process.argv[2]) for (const row of [...record.selected_images,...record.yale_references]) {
  const original=fs.readFileSync(path.join(process.argv[2],row.local_filename)),before=digest(original);
  const neutral=stripExif(original);
  assert.equal(before,row.metadata.sha256);assert.equal(digest(original),before);
  assert.equal(digest(neutral),row.metadata.jpeg_without_exif_sha256);files++;
}
for (const bad of [Buffer.from('html'),Buffer.from([255,216,0,255,217])]) assert.throws(()=>stripExif(bad));
console.log(`Verified ${points} independent grid mappings, ${projections} viewport projections and ${files} actual unchanged JPEG containers.`);
