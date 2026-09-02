(()=>{
const $=s=>document.querySelector(s);
let camStream=null,micStream=null,audioCtx=null,raf=0,touchMax=0;

const friendly=(e,k)=>{
  const n=e?.name||'';
  if(['NotAllowedError','SecurityError'].includes(n)) return `${k} 권한이 차단되었습니다. 브라우저 권한 설정을 확인하세요.`;
  if(['NotFoundError','DevicesNotFoundError'].includes(n)) return `사용 가능한 ${k} 장치를 찾지 못했습니다.`;
  if(['NotReadableError','TrackStartError'].includes(n)) return `${k} 장치를 사용할 수 없습니다. 다른 앱이 사용 중인지 확인하세요.`;
  return `${k}를 시작하지 못했습니다${n?` (${n})`:''}.`;
};

const pad=$('#touchPad');
if(pad){
  const update=e=>{
    e.preventDefault();
    const n=e.touches?.length||0;
    touchMax=Math.max(touchMax,n);
    $('#touchCount').textContent=n;
    $('#touchMax').textContent=touchMax;
    $('#touchMsg').textContent=n?`${n}개 터치 감지 중`:'계속 다른 위치도 훑어보세요';
  };
  ['touchstart','touchmove','touchend','touchcancel'].forEach(x=>pad.addEventListener(x,update,{passive:false}));
}

const layer=$('#mobileScreenLayer');
const setScreenColor=color=>{ layer.style.background=color; };
document.querySelectorAll('[data-open-screen]').forEach(b=>b.onclick=()=>{
  setScreenColor(b.dataset.openScreen);
  layer.classList.add('active');
  document.documentElement.requestFullscreen?.().catch(()=>{});
});
document.querySelectorAll('[data-set-screen]').forEach(b=>b.onclick=()=>setScreenColor(b.dataset.setScreen));
$('#closeScreen').onclick=()=>{
  layer.classList.remove('active');
  if(document.fullscreenElement) document.exitFullscreen?.();
};
document.addEventListener('fullscreenchange',()=>{if(!document.fullscreenElement) layer.classList.remove('active');});

function stopCamera(status='카메라 종료'){
  camStream?.getTracks().forEach(t=>t.stop());
  camStream=null;
  $('#camVideo').srcObject=null;
  $('#camStatus').textContent=status;
}

async function camera(facing){
  stopCamera('카메라 전환 중');
  try{
    camStream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:facing}},audio:false});
    $('#camVideo').srcObject=camStream;
    await $('#camVideo').play().catch(()=>{});
    const s=camStream.getVideoTracks()[0].getSettings();
    $('#camStatus').textContent=`카메라 작동 중${s.width&&s.height?` · 입력 ${s.width}×${s.height}`:''}`;
  }catch(e){
    stopCamera(friendly(e,'카메라'));
  }
}

$('#frontCam').onclick=()=>camera('user');
$('#backCam').onclick=()=>camera('environment');
$('#stopCam').onclick=()=>stopCamera();

function stopMic(status='마이크 종료'){
  if(raf) cancelAnimationFrame(raf);
  raf=0;
  micStream?.getTracks().forEach(t=>t.stop());
  micStream=null;
  if(audioCtx){ audioCtx.close().catch(()=>{}); audioCtx=null; }
  $('#mobileMicMeter').style.width='0';
  $('#micStatus').textContent=status;
}

$('#startMic').onclick=async()=>{
  stopMic('마이크 시작 중');
  try{
    micStream=await navigator.mediaDevices.getUserMedia({audio:true});
    const C=window.AudioContext||window.webkitAudioContext;
    if(!C) throw new Error('AudioContext');
    audioCtx=new C();
    await audioCtx.resume?.();
    const src=audioCtx.createMediaStreamSource(micStream),an=audioCtx.createAnalyser();
    an.fftSize=512;
    src.connect(an);
    const data=new Uint8Array(an.fftSize);
    const draw=()=>{
      an.getByteTimeDomainData(data);
      let sum=0;
      for(const v of data){const x=(v-128)/128;sum+=x*x;}
      const rms=Math.sqrt(sum/data.length);
      $('#mobileMicMeter').style.width=`${Math.min(100,rms*350)}%`;
      raf=requestAnimationFrame(draw);
    };
    draw();
    $('#micStatus').textContent='마이크 입력 확인 중';
  }catch(e){
    stopMic(friendly(e,'마이크'));
  }
};
$('#stopMic').onclick=()=>stopMic();

$('#playTone').onclick=async()=>{
  try{
    const C=window.AudioContext||window.webkitAudioContext;
    if(!C) throw new Error('AudioContext');
    const c=new C();
    await c.resume();
    const o=c.createOscillator(),g=c.createGain();
    o.frequency.value=440;
    g.gain.value=.12;
    o.connect(g).connect(c.destination);
    o.start();
    o.stop(c.currentTime+.8);
    o.onended=()=>c.close();
    $('#toneStatus').textContent='테스트 톤 재생됨';
  }catch(e){
    $('#toneStatus').textContent='이 브라우저에서 테스트 톤을 재생하지 못했습니다.';
  }
};

const orient=()=>{$('#orientationText').textContent=matchMedia('(orientation: portrait)').matches?'세로':'가로';};
orient();
addEventListener('orientationchange',orient);
addEventListener('resize',orient);
const vib='vibrate' in navigator;
$('#vibrateSupport').textContent=vib?'이 브라우저는 진동 API를 지원합니다.':'이 브라우저는 진동 API를 지원하지 않습니다. 미지원은 기기 불량 판정이 아닙니다.';
$('#vibrateBtn').disabled=!vib;
$('#vibrateBtn').onclick=()=>{navigator.vibrate?.([180,80,180]);};

addEventListener('pagehide',()=>{
  stopCamera('카메라 종료');
  stopMic('마이크 종료');
  navigator.vibrate?.(0);
});
})();