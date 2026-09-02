const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];

function setText(id, value){ const el=document.getElementById(id); if(el) el.textContent=value; }
function clamp(n,a,b){ return Math.min(Math.max(n,a),b); }

function initKeyboard(){
  const host=$("#keyboard");
  if(!host) return;
  const layout=[
    ["Escape","Esc"],["F1","F1"],["F2","F2"],["F3","F3"],["F4","F4"],["F5","F5"],["F6","F6"],["F7","F7"],["F8","F8"],["F9","F9"],["F10","F10"],["F11","F11"],["F12","F12"],
    ["Backquote","`"],["Digit1","1"],["Digit2","2"],["Digit3","3"],["Digit4","4"],["Digit5","5"],["Digit6","6"],["Digit7","7"],["Digit8","8"],["Digit9","9"],["Digit0","0"],["Minus","-"],["Equal","="],["Backspace","Backspace","w2"],
    ["Tab","Tab","w2"],["KeyQ","Q"],["KeyW","W"],["KeyE","E"],["KeyR","R"],["KeyT","T"],["KeyY","Y"],["KeyU","U"],["KeyI","I"],["KeyO","O"],["KeyP","P"],["BracketLeft","["],["BracketRight","]"],["Backslash","\\","w2"],
    ["CapsLock","Caps","w2"],["KeyA","A"],["KeyS","S"],["KeyD","D"],["KeyF","F"],["KeyG","G"],["KeyH","H"],["KeyJ","J"],["KeyK","K"],["KeyL","L"],["Semicolon",";"],["Quote","'"],["Enter","Enter","w2"],
    ["ShiftLeft","Shift","w2"],["KeyZ","Z"],["KeyX","X"],["KeyC","C"],["KeyV","V"],["KeyB","B"],["KeyN","N"],["KeyM","M"],["Comma",","],["Period","."],["Slash","/"],["ShiftRight","Shift","w2"],
    ["ControlLeft","Ctrl"],["MetaLeft","Win"],["AltLeft","Alt"],["Space","Space","w3"],["AltRight","Alt"],["MetaRight","Win"],["ContextMenu","Menu"],["ControlRight","Ctrl"]
  ];
  layout.forEach(([code,label,w])=>{
    const d=document.createElement("div");
    d.className="key"+(w?` ${w}`:"");
    d.dataset.code=code; d.textContent=label; host.appendChild(d);
  });
  let presses=0, repeats=0, unique=new Set(), current=new Set(), maxSimul=0;
  const update=()=>{
    setText("pressCount", presses);
    setText("repeatCount", repeats);
    setText("uniqueCount", unique.size);
    setText("maxSimul", maxSimul);
  };
  window.addEventListener("keydown", e=>{
    if(["Tab","Space","ArrowUp","ArrowDown"].includes(e.code)) e.preventDefault();
    if(e.repeat){ repeats++; } else { presses++; unique.add(e.code); current.add(e.code); maxSimul=Math.max(maxSimul,current.size); }
    const key=host.querySelector(`[data-code="${CSS.escape(e.code)}"]`); if(key) key.classList.add("active");
    setText("keyLog", `key: ${e.key}  |  code: ${e.code}  |  repeat: ${e.repeat ? "yes":"no"}`);
    update();
  }, {passive:false});
  window.addEventListener("keyup", e=>{
    current.delete(e.code);
    const key=host.querySelector(`[data-code="${CSS.escape(e.code)}"]`); if(key) key.classList.remove("active");
  });
  $("#resetKeyboard")?.addEventListener("click",()=>{
    presses=0; repeats=0; unique.clear(); current.clear(); maxSimul=0; $$(".key.active",host).forEach(x=>x.classList.remove("active")); setText("keyLog","키를 눌러보세요."); update();
  });
  update();
}

function initMouse(){
  const pad=$("#mousePad"); if(!pad) return;
  let left=0,right=0,middle=0,wheel=0,lastLeft=0,suspicious=0,minGap=Infinity;
  const refresh=()=>{
    setText("leftClicks",left); setText("rightClicks",right); setText("middleClicks",middle);
    setText("wheelCount",wheel); setText("doubleCount",suspicious);
    setText("minGap", Number.isFinite(minGap)?`${Math.round(minGap)} ms`:"—");
  };
  pad.addEventListener("contextmenu",e=>e.preventDefault());
  pad.addEventListener("mousedown",e=>{
    pad.classList.add("pressed");
    if(e.button===0){
      left++;
      const now=performance.now(), gap=lastLeft?now-lastLeft:Infinity;
      if(gap<80){ suspicious++; minGap=Math.min(minGap,gap); setText("mouseHint",`초고속 연속 입력 후보: ${Math.round(gap)} ms — 이것만으로 불량 판정하지 않습니다.`); }
      lastLeft=now;
    } else if(e.button===1) middle++; else if(e.button===2) right++;
    refresh();
  });
  window.addEventListener("mouseup",()=>pad.classList.remove("pressed"));
  pad.addEventListener("wheel",e=>{ e.preventDefault(); wheel += Math.sign(e.deltaY); refresh(); }, {passive:false});
  pad.addEventListener("mousemove",e=>{
    const r=pad.getBoundingClientRect(); setText("mousePos",`${Math.round(e.clientX-r.left)}, ${Math.round(e.clientY-r.top)}`);
  });
  $("#resetMouse")?.addEventListener("click",()=>{left=right=middle=wheel=suspicious=0;lastLeft=0;minGap=Infinity;setText("mouseHint","먼저 왼쪽 버튼을 한 번씩 천천히 눌러보세요. 한 번 눌렀는데 숫자가 두 번 오르는지가 핵심입니다.");refresh();});
  refresh();
}

let media = {micStream:null,micCtx:null,micRaf:null,camStream:null};

function mediaErrorMessage(err, kind){
  const label=kind==="camera" ? "카메라" : "마이크";
  if(!err) return `${label}를 사용할 수 없습니다.`;
  if(err.name==="NotAllowedError" || err.name==="SecurityError") return `${label} 권한이 차단되었습니다. 브라우저 주소창의 권한 설정을 확인하세요.`;
  if(err.name==="NotFoundError" || err.name==="DevicesNotFoundError") return `사용 가능한 ${label} 장치를 찾지 못했습니다.`;
  if(err.name==="NotReadableError" || err.name==="TrackStartError") return `${label}가 다른 프로그램에서 사용 중이거나 장치를 열 수 없습니다.`;
  if(err.name==="OverconstrainedError" || err.name==="ConstraintNotSatisfiedError") return `${label}의 요청 설정을 사용할 수 없습니다. 다른 장치를 선택해보세요.`;
  return `${label}를 사용할 수 없습니다. (${err.name || "알 수 없는 오류"})`;
}

async function initMic(){
  const start=$("#startMic"); if(!start) return;
  const stop=$("#stopMic"), canvas=$("#wave"), ctx2=canvas.getContext("2d");
  let analyser, data;
  function stopMic(){
    if(media.micRaf) cancelAnimationFrame(media.micRaf);
    media.micStream?.getTracks().forEach(t=>t.stop());
    media.micCtx?.close();
    media.micStream=media.micCtx=media.micRaf=null;
    $("#micMeter").style.width="0%"; setText("micStatus","정지됨");
  }
  stop.addEventListener("click",stopMic);
  start.addEventListener("click", async()=>{
    try{
      stopMic();
      const stream=await navigator.mediaDevices.getUserMedia({audio:true});
      media.micStream=stream;
      const AC=window.AudioContext||window.webkitAudioContext;
      const ac=new AC(); media.micCtx=ac;
      const source=ac.createMediaStreamSource(stream);
      analyser=ac.createAnalyser(); analyser.fftSize=1024; source.connect(analyser);
      data=new Uint8Array(analyser.fftSize);
      setText("micStatus","입력 감지 중");
      const devices=await navigator.mediaDevices.enumerateDevices();
      setText("micDevice", devices.find(d=>d.kind==="audioinput" && d.deviceId===stream.getAudioTracks()[0].getSettings().deviceId)?.label || stream.getAudioTracks()[0].label || "기본 마이크");
      const draw=()=>{
        analyser.getByteTimeDomainData(data);
        let sum=0; for(const v of data){ const n=(v-128)/128; sum+=n*n; }
        const rms=Math.sqrt(sum/data.length);
        const pct=clamp(rms*350,0,100);
        $("#micMeter").style.width=`${pct}%`;
        ctx2.clearRect(0,0,canvas.width,canvas.height);
        ctx2.beginPath(); ctx2.strokeStyle="#6ee7b7"; ctx2.lineWidth=2;
        data.forEach((v,i)=>{ const x=i/(data.length-1)*canvas.width; const y=v/255*canvas.height; i?ctx2.lineTo(x,y):ctx2.moveTo(x,y); });
        ctx2.stroke();
        media.micRaf=requestAnimationFrame(draw);
      }; draw();
    }catch(err){ setText("micStatus",mediaErrorMessage(err,"mic")); }
  });
}

async function initCam(){
  const start=$("#startCam"); if(!start) return;
  const video=$("#camVideo"), sel=$("#camSelect");
  async function stopCam(){
    media.camStream?.getTracks().forEach(t=>t.stop()); media.camStream=null; video.srcObject=null; setText("camStatus","정지됨");
  }
  async function startCam(deviceId){
    try{
      await stopCam();
      const constraints={video:deviceId?{deviceId:{exact:deviceId}}:true,audio:false};
      const stream=await navigator.mediaDevices.getUserMedia(constraints); media.camStream=stream; video.srcObject=stream;
      await video.play();
      const track=stream.getVideoTracks()[0], s=track.getSettings();
      setText("camStatus","카메라 정상 입력");
      setText("camResolution",`${s.width||video.videoWidth} × ${s.height||video.videoHeight}`);
      const devices=await navigator.mediaDevices.enumerateDevices();
      const cams=devices.filter(d=>d.kind==="videoinput");
      const current=track.getSettings().deviceId;
      sel.innerHTML="";
      cams.forEach((d,i)=>{ const o=document.createElement("option");o.value=d.deviceId;o.textContent=d.label||`카메라 ${i+1}`;if(d.deviceId===current)o.selected=true;sel.appendChild(o);});
    }catch(err){setText("camStatus",mediaErrorMessage(err,"camera"));}
  }
  start.addEventListener("click",()=>startCam(sel.value||undefined));
  $("#stopCam").addEventListener("click",stopCam);
  sel.addEventListener("change",()=>startCam(sel.value));
}

function initSpeaker(){
  if(!$("#speakerTool")) return;
  const AC=window.AudioContext||window.webkitAudioContext;
  let ac;
  async function play(pan){
    try{
      if(!AC) throw new Error("AudioContext unsupported");
      if(!ac) ac=new AC();
      if(ac.state==="suspended") await ac.resume();
      const osc=ac.createOscillator(), gain=ac.createGain();
      osc.type="sine";osc.frequency.value=440;gain.gain.value=.12;
      if(typeof ac.createStereoPanner==="function"){
        const panner=ac.createStereoPanner(); panner.pan.value=pan;
        osc.connect(gain).connect(panner).connect(ac.destination);
      }else{
        const merger=ac.createChannelMerger(2);
        const left=ac.createGain(), right=ac.createGain();
        left.gain.value=pan<=0 ? 1 : 0; right.gain.value=pan>=0 ? 1 : 0;
        gain.connect(left).connect(merger,0,0); gain.connect(right).connect(merger,0,1); merger.connect(ac.destination);
        osc.connect(gain);
      }
      osc.start();osc.stop(ac.currentTime+.8);
      setText("speakerStatus","테스트 톤 재생됨");
    }catch(err){
      setText("speakerStatus","이 브라우저에서는 오디오 테스트를 재생할 수 없습니다. 다른 브라우저에서 다시 시도하세요.");
    }
  }
  $("#playLeft").addEventListener("click",()=>play(-1));
  $("#playBoth").addEventListener("click",()=>play(0));
  $("#playRight").addEventListener("click",()=>play(1));
}

function initDisplay(){
  const layer=$("#screenLayer"); if(!layer) return;
  const colors=["#ffffff","#000000","#ff0000","#00ff00","#0000ff","#808080","#ffff00","#00ffff","#ff00ff"];
  const open=color=>{ layer.style.background=color;layer.classList.add("active");layer.requestFullscreen?.().catch(()=>{}); };
  $$(".color-btn").forEach((b,i)=>{b.style.background=colors[i%colors.length];b.addEventListener("click",()=>open(b.dataset.color));});
  $$(".screen-color").forEach(b=>b.addEventListener("click",()=>{layer.style.background=b.dataset.color;}));
  const close=()=>{layer.classList.remove("active"); if(document.fullscreenElement) document.exitFullscreen?.();};
  $("#closeScreen").addEventListener("click",close);
  document.addEventListener("fullscreenchange",()=>{ if(!document.fullscreenElement) layer.classList.remove("active"); });
  window.addEventListener("keydown",e=>{if(e.key==="Escape" && !document.fullscreenElement) layer.classList.remove("active");});
}

function initCheckup(){
  const list=$("#checklist"); if(!list) return;
  const key="pc-checkup-results-v1";
  const state=JSON.parse(localStorage.getItem(key)||"{}");
  const steps=["keyboard","mouse","display","speaker","mic","webcam"];
  const pages={keyboard:"keyboard.html",mouse:"mouse.html",display:"display.html",speaker:"speaker.html",mic:"mic.html",webcam:"webcam.html"};
  const update=()=>{
    const vals=steps.map(id=>state[id]).filter(Boolean), ok=vals.filter(v=>v==="ok").length,bad=vals.filter(v=>v==="bad").length;
    const done=vals.filter(v=>v==="ok"||v==="bad").length;
    setText("sumOk",ok);setText("sumBad",bad);setText("sumUnknown",6-done);
    setText("checkProgress",`${done} / 6 완료`);
    const bar=$("#checkProgressBar"); if(bar) bar.style.width=`${done/6*100}%`;
    const next=steps.find(id=>state[id]!=="ok"&&state[id]!=="bad");
    const nextBtn=$("#nextCheck");
    if(nextBtn){
      nextBtn.textContent=next ? "다음 미확인 검사 시작" : "전체 점검 완료";
      nextBtn.disabled=!next;
      nextBtn.dataset.href=next ? pages[next] : "";
    }
    localStorage.setItem(key,JSON.stringify(state));
  };
  $$(".checkitem",list).forEach(item=>{
    const id=item.dataset.id;
    $$(".pill",item).forEach(btn=>{
      if(state[id]===btn.dataset.value) btn.classList.add("active");
      btn.addEventListener("click",()=>{
        $$(".pill",item).forEach(x=>x.classList.remove("active"));
        btn.classList.add("active");state[id]=btn.dataset.value;update();
      });
    });
  });
  $("#resetCheckup").addEventListener("click",()=>{localStorage.removeItem(key);location.reload();});
  $("#printCheckup").addEventListener("click",()=>window.print());
  $("#nextCheck")?.addEventListener("click",e=>{ const href=e.currentTarget.dataset.href; if(href) location.href=href; });
  update();
}

document.addEventListener("DOMContentLoaded",()=>{
  initKeyboard();initMouse();initMic();initCam();initSpeaker();initDisplay();initCheckup();
});
window.addEventListener("beforeunload",()=>{
  media.micStream?.getTracks().forEach(t=>t.stop());
  media.camStream?.getTracks().forEach(t=>t.stop());
});
