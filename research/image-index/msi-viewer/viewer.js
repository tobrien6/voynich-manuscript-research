"use strict";

function requireValue(condition, message) { if (!condition) throw new Error(message); }

function toStored(x, y, width, height, mode, orientation) {
  requireValue([x,y,width,height].every(Number.isInteger) && width>0 && height>0 &&
    x>=0 && x<width && y>=0 && y<height, "Pixel lies outside the image");
  requireValue(["stored","exif"].includes(mode) && [1,3].includes(orientation), "Unsupported display convention");
  return mode==="exif" && orientation===3 ? [width-1-x,height-1-y] : [x,y];
}

function stripExif(input) {
  const bytes = new Uint8Array(input), chunks=[];
  requireValue(bytes.length>=4 && bytes[0]===255 && bytes[1]===216 &&
    bytes.at(-2)===255 && bytes.at(-1)===217, "Original is not a framed JPEG");
  chunks.push(bytes.subarray(0,2));let at=2, found=false;
  while (at<bytes.length) {
    const start=at;requireValue(bytes[at]===255,"Invalid pre-scan marker");
    while (at<bytes.length && bytes[at]===255) at++;
    requireValue(at<bytes.length,"Truncated JPEG marker");const marker=bytes[at++];
    requireValue(![0,216,217].includes(marker),"Unexpected pre-scan marker");
    if (marker===218) {chunks.push(bytes.subarray(start));found=true;break;}
    requireValue(at+2<=bytes.length,"Truncated JPEG length");const length=(bytes[at]<<8)+bytes[at+1];
    requireValue(length>=2 && at+length<=bytes.length,"Truncated JPEG segment");
    const payload=at+2;
    const isExif=marker===225 && length>=8 &&
      [69,120,105,102,0,0].every((n,i)=>bytes[payload+i]===n);
    if (!isExif) chunks.push(bytes.subarray(start,at+length));at+=length;
  }
  requireValue(found,"JPEG has no start of scan");
  const result=new Uint8Array(chunks.reduce((n,c)=>n+c.length,0));let offset=0;
  for (const chunk of chunks) {result.set(chunk,offset);offset+=chunk.length;}
  return result;
}

function viewPixel(px, py, canvasWidth, canvasHeight, width, height, zoom, cx, cy) {
  requireValue([px,py,canvasWidth,canvasHeight,width,height,zoom,cx,cy].every(Number.isFinite) &&
    canvasWidth>0 && canvasHeight>0 && width>0 && height>0 && zoom>0,"Invalid viewport");
  const scale=Math.min(canvasWidth/width,canvasHeight/height)*zoom;
  const x=Math.floor((px-canvasWidth/2)/scale+cx+.5);
  const y=Math.floor((py-canvasHeight/2)/scale+cy+.5);
  return x>=0 && x<width && y>=0 && y<height ? [x,y] : null;
}

globalThis.MSI_GEOMETRY={toStored,stripExif,viewPixel};

async function sha256(bytes) {
  requireValue(globalThis.crypto?.subtle,"SHA-256 requires a local secure context");
  return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",bytes)),
    n=>n.toString(16).padStart(2,"0")).join("");
}

function makePanel(model, initial, number) {
  const section=document.createElement("section");section.className="panel";
  section.innerHTML=`<h2>View ${number}</h2><label class="choice">Image<select class="image-choice"></select></label>
    <div class="toolbar"><label>Orientation<select class="orientation"><option value="exif">EXIF display</option><option value="stored">Stored array</option></select></label>
    <label>Zoom<input class="zoom" type="range" min="1" max="12" step=".25" value="1"><output class="zoom-value">1×</output></label>
    <label>Center x<input class="cx" type="number" min="0" step=".5"></label><label>Center y<input class="cy" type="number" min="0" step=".5"></label><button class="reset">Fit image</button></div>
    <canvas tabindex="0" aria-label="Image viewport; drag to pan, arrow keys to move the center"></canvas>
    <p class="coordinates" aria-live="polite">Move the pointer over the image for pixel coordinates.</p>
    <p class="status" aria-live="polite">Loading original image…</p><p class="caption"></p>`;
  const q=selector=>section.querySelector(selector), select=q(".image-choice"),mode=q(".orientation"),
    zoom=q(".zoom"),cx=q(".cx"),cy=q(".cy"),canvas=q("canvas"),ctx=canvas.getContext("2d"),
    status=q(".status"),coordinates=q(".coordinates"),caption=q(".caption");
  for (const side of ["1r","116v"]) {
    const group=document.createElement("optgroup");group.label=side;
    for (const item of model.images.filter(i=>i.side===side)) {
      const option=document.createElement("option");option.value=item.id;
      option.textContent=`${item.name} · ${item.collection} · EXIF ${item.metadata.exif_orientation??"absent"}`;group.append(option);
    } select.append(group);
  }
  select.value=initial;let bitmap=null,current=null,url=null,generation=0,drag=null;
  function render() {
    const box=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
    const w=Math.round(box.width*dpr),h=Math.round(box.height*dpr);
    if (canvas.width!==w) canvas.width=w;if (canvas.height!==h) canvas.height=h;
    ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,w,h);
    if (!bitmap) return;
    const [iw,ih]=current.metadata.header_dimensions,scale=Math.min(w/iw,h/ih)*Number(zoom.value);
    ctx.save();ctx.translate(w/2,h/2);ctx.scale(scale,scale);
    ctx.translate(-Number(cx.value)-.5,-Number(cy.value)-.5);
    if (mode.value==="exif" && current.metadata.exif_orientation===3) {ctx.translate(iw,ih);ctx.rotate(Math.PI);}
    ctx.drawImage(bitmap,0,0);ctx.restore();q(".zoom-value").textContent=zoom.value+"×";
  }
  function reset() {
    if (!current) return;const [w,h]=current.metadata.header_dimensions;
    cx.value=(w-1)/2;cy.value=(h-1)/2;zoom.value="1";render();
  }
  function clearCoordinates() {coordinates.textContent="Move the pointer over the image for pixel coordinates.";}
  async function load() {
    const request=++generation;bitmap=null;current=null;if (url) {URL.revokeObjectURL(url);url=null;}
    for (const control of [mode,zoom,cx,cy,q(".reset")]) control.disabled=true;
    cx.value="";cy.value="";
    ctx.clearRect(0,0,canvas.width,canvas.height);clearCoordinates();caption.replaceChildren();
    status.textContent="Checking original file bytes…";status.dataset.state="loading";
    let localURL=null;
    try {
      const item=model.images.find(i=>i.id===select.value);requireValue(item,"Image selection is unknown");
      const [w,h]=item.metadata.header_dimensions;
      const link=document.createElement("a");link.href=item.url;link.target="_blank";link.rel="noopener";link.textContent="Provider source";
      caption.append(document.createTextNode(`Recorded source: ${item.name} · ${item.collection} · ${w} × ${h} · EXIF ${item.metadata.exif_orientation??"absent"} · `),link);
      const response=await fetch(item.asset);requireValue(response.ok,"Original image is unavailable");
      const raw=await response.arrayBuffer();requireValue(await sha256(raw)===item.metadata.sha256,"Original file hash differs; display blocked");
      const neutral=stripExif(raw);
      requireValue(await sha256(neutral)===item.metadata.jpeg_without_exif_sha256,"JPEG decoding-copy hash differs; display blocked");
      localURL=URL.createObjectURL(new Blob([neutral],{type:"image/jpeg"}));const image=new Image();image.src=localURL;await image.decode();
      requireValue(image.naturalWidth===item.metadata.header_dimensions[0] &&
        image.naturalHeight===item.metadata.header_dimensions[1],"Loaded dimensions differ; display blocked");
      if (request!==generation) {URL.revokeObjectURL(localURL);return;}
      current=item;bitmap=image;url=localURL;
      cx.max=w-1;cy.max=h-1;
      for (const control of [mode,zoom,cx,cy,q(".reset")]) control.disabled=false;
      status.textContent="Original and in-memory JPEG bytes verified. Display uses browser decoding; glyph review remains pending.";
      status.dataset.state="ready";reset();
    } catch (error) {
      if (localURL) URL.revokeObjectURL(localURL);
      if (request===generation) {bitmap=null;current=null;render();status.textContent=error.message;status.dataset.state="error";}
    }
  }
  select.addEventListener("change",load);
  mode.addEventListener("change",()=>{reset();clearCoordinates();});
  zoom.addEventListener("input",()=>{render();clearCoordinates();});q(".reset").addEventListener("click",()=>{reset();clearCoordinates();});
  for (const input of [cx,cy]) input.addEventListener("change",()=>{input.value=Math.max(0,Math.min(Number(input.max),Number(input.value)||0));render();clearCoordinates();});
  canvas.addEventListener("pointerdown",event=>{if (!bitmap) return;drag={x:event.clientX,y:event.clientY,cx:Number(cx.value),cy:Number(cy.value)};canvas.setPointerCapture(event.pointerId);});
  canvas.addEventListener("pointerup",()=>{drag=null;});canvas.addEventListener("pointercancel",()=>{drag=null;});
  canvas.addEventListener("pointermove",event=>{
    if (!bitmap) return;const box=canvas.getBoundingClientRect(),[w,h]=current.metadata.header_dimensions;
    if (drag) {const scale=Math.min(box.width/w,box.height/h)*Number(zoom.value);
      cx.value=Math.max(0,Math.min(w-1,drag.cx-(event.clientX-drag.x)/scale));
      cy.value=Math.max(0,Math.min(h-1,drag.cy-(event.clientY-drag.y)/scale));render();}
    const point=viewPixel((event.clientX-box.left)*canvas.width/box.width,(event.clientY-box.top)*canvas.height/box.height,
      canvas.width,canvas.height,w,h,Number(zoom.value),Number(cx.value),Number(cy.value));
    if (!point) {coordinates.textContent="Outside the image.";return;}
    const stored=toStored(...point,w,h,mode.value,current.metadata.exif_orientation??1);
    coordinates.textContent=`Displayed pixel: ${point.join(", ")} · Stored pixel: ${stored.join(", ")}`;
  });
  canvas.addEventListener("keydown",event=>{
    if (!bitmap || !["ArrowLeft","ArrowRight","ArrowUp","ArrowDown"].includes(event.key)) return;
    event.preventDefault();const amount=event.shiftKey?100:10;
    cx.value=Math.max(0,Math.min(Number(cx.max),Number(cx.value)+({ArrowLeft:-amount,ArrowRight:amount}[event.key]||0)));
    cy.value=Math.max(0,Math.min(Number(cy.max),Number(cy.value)+({ArrowUp:-amount,ArrowDown:amount}[event.key]||0)));render();clearCoordinates();
  });
  new ResizeObserver(render).observe(canvas);
  load();return section;
}

function initialize() {
  const model=JSON.parse(document.getElementById("model").textContent);
  document.getElementById("credit").textContent=model.credit;
  document.getElementById("citation").textContent=model.manuscript_citation;
  document.getElementById("provenance").textContent=JSON.stringify({parent_pr:model.parent_pr,
    parent_commit:model.parent_commit,original_parent_commit:model.original_parent_commit,
    dependency_status:model.dependency_status,input_sha256:model.input_sha256,
    images:model.images.map(i=>({id:i.id,side:i.side,name:i.name,metadata:i.metadata,decoded:i.decoded}))},null,2);
  document.getElementById("panels").append(makePanel(model,"1UBQfNp3pm8KfGjGCcAOCV1QXF_qQdjyE",1),
    makePanel(model,"17hqCyh3kaBU_7Twa0N2VKRZjqfmddFVL",2));
}

if (typeof document!=="undefined") initialize();
