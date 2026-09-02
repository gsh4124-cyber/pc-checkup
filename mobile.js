(()=>{
const $=s=>document.querySelector(s);
let camStream=null,micStream=null,audioCtx=null,raf=0,touchMax=0;
const tests=['touch','display','camera','mic','speaker','motion'];
const resultKey='device-checkup-mobile-results-v1';
let results={};
try{results=JSON.parse(localStorage.getItem(resultKey)||'{}')||{};}catch{results={};}

const friendly=(e,k)=>{
  const n=e?.name||'';
  if(['NotAllowedError','SecurityError'].includes(n)) return `${k} 권한이 차단되었습니다. 브라우저 권한 설정을 확인하세요.`;
  if(['NotFoundError','DevicesNotFoundError'].includes(n)) return `사용 가능한 ${k} 장치를 찾지 못했습니다.`;
  if(['NotReadableError','TrackStartError'].includes(n)) return `${k} 장치를 사용할 수 없습니다. 다른 앱이 사용 중인지 확인하세요.`;
  return `${k}를 시작하지 못했습니다${n?` (${n})`:''}.`;
};

function renderResults(){
  let ok=0,bad=0,done=0;
  tests.forEach(test=>{
    const state=results[test];
    if(state==='ok'){ok++;done++;}
    if(state==='bad'){bad++;done++;}
    document.querySelectorAll(`.mobile-result-actions[data-test="${test}"] .pill`).forEach(b=>b.classList.toggle('active',b.dataset.result===state));
    const card=document.querySelector(`[data-test-card="${test}"]`);
    if(card){card.classList.toggle('result-ok',state==='ok');card.classList.toggle('result-bad',state==='bad');}
  });
  const unknown=tests.length-done;
  $('#mobileOkCount').textContent=ok;
  $('#mobileBadCount').textContent=bad;
  $('#mobileUnknownCount').textContent=unknown;
  $('#mobileProgressText').textContent=`${done} / ${tests.length} 완료`;
  $('#mobileProgressBar').style.width=`${done/tests.length*100}%`;
}

document.querySelectorAll('.mobile-result-actions').forEach(group=>{
  group.addEventListener('click',e=>{
    const b=e.target.closest('[data-result]'); if(!b)return;
    const test=group.dataset.test;
    const value=b.dataset.result;
    if(value==='unknown') delete results[test]; else results[test]=value;
    localStorage.setItem(resultKey,JSON.stringify(results));
    renderResults();
  });
});
$('#resetMobileResults').onclick=()=>{results={};localStorage.removeItem(resultKey);renderResults();};
renderResults();

const touchLayer=$('#touchTestLayer'),touchGrid=$('#touchGrid');
let touchCells=[],visited=new Set();
function buildTouchGrid(){
  touchGrid.innerHTML='';visited.clear();touchCells=[];touchMax=0;
  const cols=8,rows=14,total=cols*rows;
  touchGrid.style.setProperty('--touch-cols',cols);
  touchGrid.style.setProperty('--touch-rows',rows);
  for(let i=0;i<total;i++){
    const c=document.createElement('div');c.className='touch-cell';c.dataset.cell=i;touchGrid.appendChild(c);touchCells.push(c);
  }
  updateTouchProgress();
}
function updateTouchProgress(){
  const total=touchCells.length||1,pct=Math.round(visited.size/total*100);
  $('#touchCoverage').textContent=`${pct}%`;
  $('#touchLayerProgress').textContent=`${pct}%`;
}
function markPoint(x,y){
  const el=document.elementFromPoint(x,y);
  const cell=el?.closest?.('.touch-cell');
  if(!cell)return;
  const id=cell.dataset.cell;
  if(!visited.has(id)){visited.add(id);cell.classList.add('visited');updateTouchProgress();}
}
function touchHandler(e){
  e.preventDefault();
  const list=e.touches||[];touchMax=Math.max(touchMax,list.length);$('#touchMax').textContent=touchMax;
  for(const t of list) markPoint(t.clientX,t.clientY);
}
['touchstart','touchmove'].forEach(x=>touchLayer.addEventListener(x,touchHandler,{passive:false}));
touchLayer.addEventListener('pointerdown',e=>{if(e.pointerType==='touch')markPoint(e.clientX,e.clientY);});
touchLayer.addEventListener('pointermove',e=>{if(e.pointerType==='touch'&&e.buttons!==0)markPoint(e.clientX,e.clientY);});
$('#startTouchTest').onclick=()=>{buildTouchGrid();touchLayer.classList.add('active');document.documentElement.requestFullscreen?.().catch(()=>{});};
$('#closeTouchTest').onclick=()=>{touchLayer.classList.remove('active');if(document.fullscreenElement)document.exitFullscreen?.();};

const layer=$('#mobileScreenLayer');
const setScreenColor=color=>{layer.style.background=color;};
document.querySelectorAll('[data-open-screen]').forEach(b=>b.onclick=()=>{setScreenColor(b.dataset.openScreen);layer.classList.add('active');document.documentElement.requestFullscreen?.().catch(()=>{});});
document.querySelectorAll('[data-set-screen]').forEach(b=>b.onclick=()=>setScreenColor(b.dataset.setScreen));
$('#closeScreen').onclick=()=>{layer.classList.remove('active');if(document.fullscreenElement)document.exitFullscreen?.();};
document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement){layer.classList.remove('active');touchLayer.classList.remove('active');}});

function stopCamera(status='카메라 종료'){
  camStream?.getTracks().forEach(t=>t.stop());camStream=null;$('#camVideo').srcObject=null;$('#camStatus').textContent=status;
}
async function camera(facing){
  stopCamera('카메라 전환 중');
  try{
    camStream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:facing}},audio:false});$('#camVideo').srcObject=camStream;await $('#camVideo').play().catch(()=>{});
    const s=camStream.getVideoTracks()[0].getSettings();$('#camStatus').textContent=`카메라 작동 중${s.width&&s.height?` · 입력 ${s.width}×${s.height}`:''}`;
  }catch(e){stopCamera(friendly(e,'카메라'));}
}
$('#frontCam').onclick=()=>camera('user');$('#backCam').onclick=()=>camera('environment');$('#stopCam').onclick=()=>stopCamera();

function stopMic(status='마이크 종료'){
  if(raf)cancelAnimationFrame(raf);raf=0;micStream?.getTracks().forEach(t=>t.stop());micStream=null;if(audioCtx){audioCtx.close().catch(()=>{});audioCtx=null;}$('#mobileMicMeter').style.width='0';$('#micStatus').textContent=status;
}
$('#startMic').onclick=async()=>{
  stopMic('마이크 시작 중');
  try{
    micStream=await navigator.mediaDevices.getUserMedia({audio:true});const C=window.AudioContext||window.webkitAudioContext;if(!C)throw new Error('AudioContext');audioCtx=new C();await audioCtx.resume?.();
    const src=audioCtx.createMediaStreamSource(micStream),an=audioCtx.createAnalyser();an.fftSize=512;src.connect(an);const data=new Uint8Array(an.fftSize);
    const draw=()=>{an.getByteTimeDomainData(data);let sum=0;for(const v of data){const x=(v-128)/128;sum+=x*x;}const rms=Math.sqrt(sum/data.length);$('#mobileMicMeter').style.width=`${Math.min(100,rms*350)}%`;raf=requestAnimationFrame(draw);};draw();$('#micStatus').textContent='마이크 입력 확인 중';
  }catch(e){stopMic(friendly(e,'마이크'));}
};
$('#stopMic').onclick=()=>stopMic();

$('#playTone').onclick=async()=>{
  try{const C=window.AudioContext||window.webkitAudioContext;if(!C)throw new Error('AudioContext');const c=new C();await c.resume();const o=c.createOscillator(),g=c.createGain();o.frequency.value=440;g.gain.value=.12;o.connect(g).connect(c.destination);o.start();o.stop(c.currentTime+.8);o.onended=()=>c.close();$('#toneStatus').textContent='테스트 톤 재생됨';}
  catch(e){$('#toneStatus').textContent='이 브라우저에서 테스트 톤을 재생하지 못했습니다.';}
};

const orient=()=>{$('#orientationText').textContent=matchMedia('(orientation: portrait)').matches?'세로':'가로';};orient();addEventListener('orientationchange',orient);addEventListener('resize',orient);
const vib='vibrate' in navigator;$('#vibrateSupport').textContent=vib?'이 브라우저는 진동 API를 지원합니다.':'이 브라우저는 진동 API를 지원하지 않습니다. 미지원은 기기 불량 판정이 아닙니다.';$('#vibrateBtn').disabled=!vib;$('#vibrateBtn').onclick=()=>navigator.vibrate?.([180,80,180]);

addEventListener('pagehide',()=>{stopCamera('카메라 종료');stopMic('마이크 종료');navigator.vibrate?.(0);});
})();