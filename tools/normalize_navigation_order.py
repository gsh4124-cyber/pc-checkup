from pathlib import Path
import re

ROOT = Path('dist')
LEGACY_ORIGIN = 'https://gsh4124-cyber.github.io/pc-checkup/'
PRODUCTION_ORIGIN = 'https://pc-checkup.pages.dev/'
ORDER = [
    'checkup.html',
    'keyboard.html',
    'mouse.html',
    'display.html',
    'speaker.html',
    'mic.html',
    'webcam.html',
]
NAV_RE = re.compile(r'(<nav class="navlinks">)([\s\S]*?)(</nav>)', re.I)
LINK_RE = re.compile(r'<a\s+href="([^"]+)"[^>]*>[\s\S]*?</a>', re.I)


def basename(href: str) -> str:
    return href.split('#', 1)[0].split('?', 1)[0].rstrip('/').split('/')[-1]


def reorder_nav(text: str, path: Path) -> str:
    m = NAV_RE.search(text)
    if not m:
        return text

    body = m.group(2)
    links = list(LINK_RE.finditer(body))
    if not links:
        return text

    by_base = {basename(x.group(1)): x.group(0) for x in links}
    if not all(name in by_base for name in ORDER):
        return text

    ordered = ''.join(by_base[name] for name in ORDER)
    extras = [x.group(0) for x in links if basename(x.group(1)) not in ORDER]
    ordered += ''.join(extras)
    return text[:m.start(2)] + ordered + text[m.end(2):]


changed = 0
full_nav_pages = 0
for path in sorted(ROOT.rglob('*.html')):
    text = path.read_text(encoding='utf-8')
    before = text
    if '<nav class="navlinks">' in text:
        m = NAV_RE.search(text)
        if m:
            found = {basename(x.group(1)) for x in LINK_RE.finditer(m.group(2))}
            if all(name in found for name in ORDER):
                full_nav_pages += 1
    text = reorder_nav(text, path)
    if text != before:
        path.write_text(text, encoding='utf-8')
        changed += 1

if full_nav_pages == 0:
    raise RuntimeError('No full PC navigation blocks found')

# Cloudflare Pages is the production origin. Earlier generators still emit the
# GitHub Pages origin, so normalize every deployable text asset at the final
# post-processing stage. This keeps canonical/hreflang/OG/JSON-LD/robots/
# sitemap consistent even when upstream locale generators differ.
origin_rewrites = 0
text_suffixes = {'.html', '.js', '.xml', '.txt', '.css', '.json'}
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.suffix.lower() not in text_suffixes:
        continue
    text = path.read_text(encoding='utf-8')
    if LEGACY_ORIGIN in text:
        new_text = text.replace(LEGACY_ORIGIN, PRODUCTION_ORIGIN)
        path.write_text(new_text, encoding='utf-8')
        origin_rewrites += 1

remaining = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.suffix.lower() not in text_suffixes:
        continue
    if LEGACY_ORIGIN in path.read_text(encoding='utf-8'):
        remaining.append(str(path))
if remaining:
    raise RuntimeError(f'Legacy GitHub Pages origin remains in deploy artifact: {remaining[:10]}')

# Prepare the standalone RefundProof submission build before pages.yml copies it
# into dist. Keep refund calculation logic unchanged; only improve input support
# and presentation. This intentionally fails the build if expected markers drift.
refundproof = Path('refundproof/wanted-demo.html')
if refundproof.exists():
    s = refundproof.read_text(encoding='utf-8')
    s = s.replace('WANTED_DEMO_V10', 'WANTED_DEMO_V11')
    s = s.replace('PDF·문서 올리기', '이미지·PDF·문서 올리기')
    s = s.replace(
        'PDF·TXT·MD를 지원합니다. 텍스트가 들어있는 PDF는 브라우저에서 바로 읽습니다.',
        'JPG·PNG·WEBP·PDF·TXT·MD를 지원합니다. 사진·스크린샷과 스캔 PDF는 OCR로 읽습니다.'
    )
    old_accept = 'accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"'
    new_accept = 'accept=".pdf,.txt,.md,.jpg,.jpeg,.png,.webp,application/pdf,image/jpeg,image/png,image/webp,text/plain,text/markdown"'
    if old_accept not in s:
        raise RuntimeError('RefundProof upload accept marker drifted')
    s = s.replace(old_accept, new_accept)

    old_pdf = "async function extractPdfText(file){const pdfjs=await import('https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.min.mjs');pdfjs.GlobalWorkerOptions.workerSrc='https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.min.mjs';const data=new Uint8Array(await file.arrayBuffer());const pdf=await pdfjs.getDocument({data}).promise;let text='';for(let p=1;p<=pdf.numPages;p++){const page=await pdf.getPage(p);const c=await page.getTextContent();text+=c.items.map(i=>i.str).join(' ')+'\\n'}if(text.trim().length<20)throw new Error('이 PDF에서 읽을 수 있는 텍스트가 거의 없습니다. 스캔 이미지 PDF는 현재 데모에서 지원하지 않습니다.');return text}"
    new_pdf = """let tesseractModule=null;
async function getTesseract(){if(tesseractModule)return tesseractModule;const t=await import('https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.esm.min.js');tesseractModule=t;return t}
async function ocrSource(source,label='이미지'){const t=await getTesseract();$('aiStatus').className='status';$('aiStatus').textContent=`${label}에서 글자를 읽고 있어요…`;const r=await t.recognize(source,'kor+eng',{logger:m=>{if(m.status==='recognizing text'&&m.progress!=null)$('aiStatus').textContent=`${label} OCR ${Math.round(m.progress*100)}%`}});const text=r?.data?.text||'';if(text.trim().length<8)throw new Error(`${label}에서 충분한 글자를 읽지 못했습니다. 더 선명한 이미지로 다시 시도해 주세요.`);return text}
async function extractImageText(file){return await ocrSource(file,'이미지')}
async function extractPdfText(file){const pdfjs=await import('https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.min.mjs');pdfjs.GlobalWorkerOptions.workerSrc='https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.min.mjs';const data=new Uint8Array(await file.arrayBuffer());const pdf=await pdfjs.getDocument({data}).promise;let text='';for(let p=1;p<=pdf.numPages;p++){const page=await pdf.getPage(p);const c=await page.getTextContent();text+=c.items.map(i=>i.str).join(' ')+'\\n'}if(text.trim().length>=20)return text;let ocr='';for(let p=1;p<=pdf.numPages;p++){const page=await pdf.getPage(p);const viewport=page.getViewport({scale:2});const canvas=document.createElement('canvas');canvas.width=Math.ceil(viewport.width);canvas.height=Math.ceil(viewport.height);const ctx=canvas.getContext('2d',{willReadFrequently:true});await page.render({canvasContext:ctx,viewport}).promise;ocr+=await ocrSource(canvas,`스캔 PDF ${p}/${pdf.numPages}페이지`)+'\\n'}return ocr}"""
    if old_pdf not in s:
        raise RuntimeError('RefundProof PDF reader marker drifted')
    s = s.replace(old_pdf, new_pdf)

    old_loader = "if(f.type==='application/pdf'||/\\.pdf$/i.test(f.name))text=await extractPdfText(f);else if(/text|markdown/.test(f.type)||/.+\\.(txt|md)$/i.test(f.name))text=await f.text();else throw new Error('현재 데모에서는 PDF, TXT, MD 파일을 지원합니다.');"
    new_loader = "if(f.type==='application/pdf'||/\\.pdf$/i.test(f.name))text=await extractPdfText(f);else if(/^image\\//.test(f.type)||/.+\\.(jpe?g|png|webp)$/i.test(f.name))text=await extractImageText(f);else if(/text|markdown/.test(f.type)||/.+\\.(txt|md)$/i.test(f.name))text=await f.text();else throw new Error('JPG, PNG, WEBP, PDF, TXT, MD 파일을 지원합니다.');"
    if old_loader not in s:
        raise RuntimeError('RefundProof document loader marker drifted')
    s = s.replace(old_loader, new_loader)

    if 'id="submission-polish"' not in s:
        polish = '''<style id="submission-polish">
:root{--accent:#6157e8;--accent2:#8b5cf6}html{background:#f5f6fb}body{background:radial-gradient(circle at 12% 0%,rgba(97,87,232,.14),transparent 31%),radial-gradient(circle at 88% 7%,rgba(139,92,246,.11),transparent 28%),linear-gradient(180deg,#f8f9fd 0,#f3f5fa 100%);color:#111827;min-height:100vh}main{max-width:1120px;padding:30px 18px 80px}.hero{padding:54px 20px 34px}.hero:before{content:'AI REFUND AUDIT';display:inline-flex;padding:7px 11px;border-radius:999px;background:rgba(255,255,255,.76);border:1px solid rgba(97,87,232,.16);box-shadow:0 8px 28px rgba(36,42,78,.08);color:#5955cf;font-size:10px;font-weight:900;letter-spacing:.12em;margin-bottom:18px}.hero h1{font-size:clamp(48px,8vw,78px);letter-spacing:-.055em;background:linear-gradient(135deg,#111827 10%,#4f46c8 58%,#8b5cf6 100%);-webkit-background-clip:text;background-clip:text;color:transparent}.hero p{color:#6b7280}.microflow span{padding:7px 10px;border:1px solid rgba(17,24,39,.08);background:rgba(255,255,255,.66);border-radius:999px}.layout{gap:18px}.card{background:rgba(255,255,255,.9);border:1px solid rgba(17,24,39,.075);border-radius:28px;box-shadow:0 18px 55px rgba(27,35,67,.075);padding:26px;backdrop-filter:blur(18px)}.resultcard{box-shadow:0 22px 64px rgba(80,70,180,.11)}.upload{border:1px solid #eaecf2;background:linear-gradient(180deg,#fff,#fafbfe);border-radius:18px;transition:.18s ease}.upload:hover{transform:translateY(-1px);border-color:#d9dcfb;box-shadow:0 10px 28px rgba(66,69,160,.07)}.filebtn{border:1px solid #e1e3f8;background:#f2f2ff;color:#5153c9;border-radius:12px}.primary{border-radius:15px;padding:15px 17px;background:linear-gradient(135deg,#5558e8,#755cf2 55%,#9258ed);box-shadow:0 12px 26px rgba(91,92,240,.24)}.primary:hover{transform:translateY(-1px);box-shadow:0 15px 32px rgba(91,92,240,.28)}.checkwrap{border-radius:18px;background:linear-gradient(180deg,#fbfbfd,#f7f8fb)}.mainamount{font-size:clamp(48px,7vw,66px);letter-spacing:-.055em}.comparebox,.result,.detailsbtn,.chip,.metric{border-radius:14px}@media(min-width:900px){.resultcard{position:sticky;top:18px}}@media(max-width:760px){main{padding:18px 12px 56px}.hero{padding:38px 10px 25px}.card{padding:18px;border-radius:22px}}
</style>'''
        s = s.replace('</head>', polish + '\n</head>', 1)

    refundproof.write_text(s, encoding='utf-8')

print(f'Normalized canonical PC navigation order on {full_nav_pages} pages; rewrote {changed} pages; production-origin rewrites {origin_rewrites}; RefundProof submission build prepared')
