PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tessera</title>
<style>
:root{--bg:#12100e;--panel:#1b1816;--panel2:#221e1b;--line:#322b26;--text:#eae3d8;--mute:#8f857a;--copper:#c8793a;--sage:#8fae6a;--brick:#cf5a4a;--gold:#d9a441}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--text);font:14px/1.45 "Segoe UI Variable","Segoe UI",system-ui,sans-serif}
.mono{font-family:"Cascadia Mono",Consolas,monospace;font-variant-numeric:tabular-nums}
header{display:flex;align-items:center;justify-content:space-between;padding:16px 28px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:14px}
.brand h1{font:600 22px Georgia,"Times New Roman",serif;letter-spacing:.3em;margin:0}
.brand small{display:block;color:var(--mute);letter-spacing:.08em;font-size:12px}
.chips{display:flex;gap:10px;align-items:center}
.chip{border:1px solid var(--line);padding:4px 11px;border-radius:999px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute)}
.chip.sim{color:var(--gold);border-color:#5b4a26}
.dot{width:8px;height:8px;border-radius:50%;background:var(--sage);display:inline-block;margin-right:7px;animation:pulse 1.6s infinite}
@keyframes pulse{50%{opacity:.3}}
main{padding:22px 28px;max-width:1500px;margin:0 auto}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:18px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 18px}
.kpi span{display:block;color:var(--mute);font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.kpi b{font:600 30px Georgia,serif}
.grid{display:grid;grid-template-columns:1.65fr 1fr;gap:18px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:18px}
.panel h2{margin:0 0 12px;font:600 11px "Segoe UI",sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
.launch{display:flex;flex-wrap:wrap;gap:8px}
button{background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:6px;padding:7px 12px;font:inherit;font-size:12px;cursor:pointer}
button:hover:not(:disabled){border-color:var(--copper);color:#fff}
button:disabled{opacity:.35;cursor:default}
button.primary{background:var(--copper);border-color:var(--copper);color:#1a120b;font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}
.cred{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:14px;display:flex;gap:14px}
.cred.active{border-color:#4b5a37}
.cred.denied{border-color:#6b3a33}
.ring{position:relative;width:96px;height:96px;flex:none}
.ring svg{width:96px;height:96px;transform:rotate(-90deg)}
.ring circle{fill:none;stroke-width:7}
.ring .bg{stroke:var(--line)}
.ring .fg{stroke:var(--sage);stroke-linecap:round}
.ring .lbl{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.lbl b{font-size:16px}
.lbl i{font-style:normal;font-size:10px;color:var(--mute);letter-spacing:.12em}
.info{min-width:0;flex:1}
.info .t{font-weight:600}
.info .s{color:var(--mute);font-size:12px;margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tag{display:inline-block;font-size:10px;letter-spacing:.1em;padding:2px 7px;border-radius:4px;border:1px solid var(--line);margin:0 4px 4px 0;text-transform:uppercase;color:var(--mute)}
.tag.allow{color:var(--sage);border-color:#4b5a37}
.tag.restrict{color:var(--gold);border-color:#5b4a26}
.tag.deny{color:var(--brick);border-color:#6b3a33}
.row{display:flex;gap:6px;margin-top:6px;flex-wrap:wrap}
.empty{color:var(--mute);padding:8px 0}
.bar{margin:12px 0}
.bar .n{display:flex;justify-content:space-between;font-size:12px;margin-bottom:5px}
.bar .tr{height:8px;background:var(--line);border-radius:4px;overflow:hidden}
.bar .f{height:100%;border-radius:4px}
.note{color:var(--mute);font-size:11px;margin:12px 0 0}
.al{display:flex;gap:10px;padding:7px 0;border-bottom:1px solid var(--line);font-size:12px;align-items:baseline}
.al:last-child{border-bottom:0}
.al .tm{color:var(--mute);width:70px;flex:none}
.sev{font-size:10px;letter-spacing:.1em;text-transform:uppercase;width:62px;flex:none}
.sev.critical{color:var(--brick)}.sev.high{color:var(--gold)}.sev.medium{color:var(--mute)}
table{width:100%;border-collapse:collapse;table-layout:fixed}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);font-size:12px}
th{color:var(--mute);font-size:11px;letter-spacing:.1em;text-transform:uppercase;font-weight:600}
td.d{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--mute)}
td.e.bad{color:var(--brick)}td.e.ok{color:var(--sage)}td.e.warn{color:var(--gold)}
@media(max-width:1100px){.grid{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(2,1fr)}}
</style></head><body>
<header>
  <div class="brand">
    <svg width="32" height="32" viewBox="0 0 30 30"><rect x="3" y="3" width="24" height="24" rx="5" fill="none" stroke="#c8793a" stroke-width="2"/><circle cx="15" cy="15" r="4" fill="#c8793a"/></svg>
    <div><h1>TESSERA</h1><small>Task-bound credential control</small></div>
  </div>
  <div class="chips"><span class="chip sim">Simulated cloud</span><span class="chip"><i class="dot"></i><span id="live">LIVE</span></span></div>
</header>
<main>
<section class="kpis">
  <div class="kpi"><span>Active credentials</span><b id="k_active">0</b></div>
  <div class="kpi"><span>Denied</span><b id="k_denied">0</b></div>
  <div class="kpi"><span>Decoy hits</span><b id="k_hits">0</b></div>
  <div class="kpi"><span>Avg revoke time</span><b id="k_ms">-</b></div>
  <div class="kpi"><span>Runs total</span><b id="k_total">0</b></div>
</section>
<div class="grid">
  <div>
    <section class="panel"><h2>Scenarios</h2><div class="launch" id="launch"></div></section>
    <section class="panel"><h2>Live credentials</h2>
      <div class="cards" id="cards"></div>
      <div class="empty" id="empty">No runs yet. Press "Start run" above.</div>
    </section>
  </div>
  <div>
    <section class="panel"><h2>Exposure after task ends (log scale)</h2><div id="bars"></div>
      <p class="note">Baseline bars are calculated from each run's task time. Revoke time comes from the simulated cloud, so real AWS will be slower.</p>
    </section>
    <section class="panel"><h2>Alerts</h2><div id="alerts"></div></section>
  </div>
</div>
<section class="panel"><h2>Audit trail</h2>
  <table><thead><tr><th style="width:90px">Time</th><th style="width:170px">Event</th><th>Details</th></tr></thead><tbody id="audit"></tbody></table>
</section>
</main>
<script>
var C = 2 * Math.PI * 42;
var cards = {}, order = '', current = [];
var SC = [
  ['manual', 'Start run (revoke by hand)', 1],
  ['allow_revoke', 'Allow + revoke'],
  ['high_restrict', 'High vuln -> restrict'],
  ['critical_deny', 'Critical -> deny'],
  ['fix_deploy', 'Fix deploy -> restrict'],
  ['replay_decoy', 'Replay -> decoy'],
  ['orphan_reaper', 'Orphan -> reaper'],
  ['scan_fail_prod', 'Scan fail prod -> deny'],
  ['wildcard_deny', 'Wildcard -> deny']
];
function $(id){return document.getElementById(id);}
function mk(tag, cls, text){var e=document.createElement(tag); if(cls)e.className=cls; if(text!==undefined)e.textContent=text; return e;}
function sv(tag, attrs){var e=document.createElementNS('http://www.w3.org/2000/svg',tag); for(var k in attrs)e.setAttribute(k,attrs[k]); return e;}
function post(u,b){return fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});}
function fmtLeft(rem){if(rem>=60){var m=Math.floor(rem/60),s=Math.floor(rem%60);return m+':'+(s<10?'0':'')+s;}return rem.toFixed(1)+'s';}
function fmtDur(v){if(v===null||v===undefined)return '-';if(v>=60)return (v/60).toFixed(1)+' min';if(v>=1)return v.toFixed(1)+' s';return (v*1000).toFixed(2)+' ms';}
function fmtTime(ts){return new Date(ts*1000).toLocaleTimeString();}

function build(){
  var el=mk('div','cred');
  var ring=mk('div','ring');
  var s=sv('svg',{viewBox:'0 0 100 100'});
  s.appendChild(sv('circle',{'class':'bg',cx:50,cy:50,r:42}));
  var fg=sv('circle',{'class':'fg',cx:50,cy:50,r:42});
  fg.style.strokeDasharray=C;
  s.appendChild(fg); ring.appendChild(s);
  var lbl=mk('div','lbl'); var big=mk('b','mono','--'); var small=mk('i','','');
  lbl.appendChild(big); lbl.appendChild(small); ring.appendChild(lbl);
  var info=mk('div','info'); var t=mk('div','t'); var sub=mk('div','s'); var tags=mk('div','tags'); var row=mk('div','row');
  var bRev=mk('button','primary','Revoke now'); bRev.dataset.act='revoke';
  var bRep=mk('button','','Replay as attacker'); bRep.dataset.act='replay';
  row.appendChild(bRev); row.appendChild(bRep);
  info.appendChild(t); info.appendChild(sub); info.appendChild(tags); info.appendChild(row);
  el.appendChild(ring); el.appendChild(info);
  return {el:el,fg:fg,big:big,small:small,t:t,sub:sub,tags:tags,row:row,bRev:bRev,bRep:bRep};
}

function paint(c, r){
  c.el.className='cred '+r.state;
  c.el.dataset.run=r.run_id;
  c.t.textContent=r.stage+' / '+r.environment;
  c.sub.textContent=r.state==='denied' ? (r.reasons[0]||'') : (r.target||'');
  c.tags.textContent='';
  c.tags.appendChild(mk('span','tag '+r.outcome,r.outcome));
  c.tags.appendChild(mk('span','tag mono',r.run_id));
  if(r.decoy_hits>0) c.tags.appendChild(mk('span','tag deny','decoy hit x'+r.decoy_hits));
  c.row.style.display = r.state==='denied' ? 'none' : '';
  c.bRev.disabled = r.state!=='active';
  c.bRep.disabled = !r.replayable;
  if(r.state==='revoked'){
    c.fg.style.strokeDashoffset=C; c.fg.style.stroke='#8f857a';
    c.big.textContent=(r.revoke_ms!==null ? r.revoke_ms.toFixed(2) : '0')+' ms'; c.small.textContent='REVOKED';
  } else if(r.state==='expired'){
    c.fg.style.strokeDashoffset=C; c.fg.style.stroke='#d9a441';
    c.big.textContent='TTL'; c.small.textContent='EXPIRED';
  } else if(r.state==='denied'){
    c.fg.style.strokeDashoffset=0; c.fg.style.stroke='#cf5a4a';
    c.big.textContent='X'; c.small.textContent='DENIED';
  }
}

function tick(){
  var now=Date.now()/1000;
  current.forEach(function(r){
    if(r.state!=='active'||!cards[r.run_id]) return;
    var c=cards[r.run_id];
    var rem=Math.max(0,r.expires_at-now);
    var f=r.ttl>0 ? rem/r.ttl : 0;
    c.fg.style.strokeDashoffset=C*(1-f);
    c.fg.style.stroke = f<0.2 ? '#c8793a' : '#8fae6a';
    c.big.textContent=fmtLeft(rem); c.small.textContent='LEFT';
  });
  requestAnimationFrame(tick);
}

function bars(e){
  var box=$('bars'); box.textContent='';
  if(!e||e.n===0){box.appendChild(mk('div','empty','Finish a run to see exposure numbers.'));return;}
  var rows=[['B0 static key (1 h)',e.static,'#cf5a4a'],['B1 OIDC default (15 min)',e.oidc,'#d9a441'],['B2 Vault TTL (15 min)',e.vault,'#d9a441'],['Tessera (measured)',e.tessera,'#8fae6a']];
  rows.forEach(function(x){
    var v=x[1]||0;
    var row=mk('div','bar'); var n=mk('div','n');
    n.appendChild(mk('span','',x[0])); n.appendChild(mk('span','mono',fmtDur(x[1])));
    var tr=mk('div','tr'); var f=mk('div','f');
    f.style.width=Math.max(1.5,Math.log10(1+v)/Math.log10(3601)*100)+'%';
    f.style.background=x[2];
    tr.appendChild(f); row.appendChild(n); row.appendChild(tr); box.appendChild(row);
  });
}

function alerts(a){
  var box=$('alerts'); box.textContent='';
  var out=[];
  a.slice().reverse().forEach(function(e){
    var sev=null,msg=null;
    if(e.event==='DECOY_HIT'){sev='critical';msg='Decoy credential used: '+e.action+' from '+e.source;}
    else if(e.event==='DECOY_ISSUED'){sev='critical';msg='Dead token replayed, decoy issued (run '+e.run_id+')';}
    else if(e.event==='reaped'){sev='high';msg='Orphaned credential reaped by TTL backstop ('+e.count+')';}
    else if(e.event==='manifest_rejected'){sev='medium';msg='Manifest rejected: '+e.reason;}
    else if(e.event==='decision'&&e.outcome==='deny'){sev='medium';msg='Access denied: '+(e.reasons||[]).join(', ');}
    if(msg&&out.length<8) out.push([e.ts,sev,msg]);
  });
  if(!out.length){box.appendChild(mk('div','empty','No alerts.'));return;}
  out.forEach(function(x){
    var r=mk('div','al'); r.appendChild(mk('span','tm mono',fmtTime(x[0]))); r.appendChild(mk('span','sev '+x[1],x[1])); r.appendChild(mk('span','',x[2])); box.appendChild(r);
  });
}

function audit(a){
  var tb=$('audit'); tb.textContent='';
  a.slice(-14).reverse().forEach(function(e){
    var cls='e';
    if(e.event==='DECOY_HIT'||e.event==='DECOY_ISSUED'||e.event==='manifest_rejected'||(e.event==='decision'&&e.outcome==='deny')) cls+=' bad';
    else if(e.event==='revoked') cls+=' ok';
    else if(e.event==='reaped') cls+=' warn';
    var kv=Object.keys(e).filter(function(k){return k!=='ts'&&k!=='event';}).map(function(k){return k+'='+(typeof e[k]==='object'?JSON.stringify(e[k]):e[k]);}).join('  ');
    var tr=document.createElement('tr');
    tr.appendChild(mk('td','mono',fmtTime(e.ts))); tr.appendChild(mk('td',cls+' mono',e.event)); tr.appendChild(mk('td','d mono',kv));
    tb.appendChild(tr);
  });
}

function render(s){
  var k=s.kpis;
  $('k_active').textContent=k.active; $('k_denied').textContent=k.denied;
  $('k_hits').textContent=k.decoy_hits; $('k_total').textContent=k.total;
  $('k_ms').textContent=k.avg_revoke_ms===null ? '-' : k.avg_revoke_ms.toFixed(2)+' ms';
  current=s.runs;
  var ids=s.runs.map(function(r){return r.run_id;}).join(',');
  var seen={};
  s.runs.forEach(function(r){
    seen[r.run_id]=1;
    if(!cards[r.run_id]) cards[r.run_id]=build();
    paint(cards[r.run_id],r);
  });
  Object.keys(cards).forEach(function(id){if(!seen[id]){cards[id].el.remove();delete cards[id];}});
  if(ids!==order){order=ids; s.runs.forEach(function(r){$('cards').appendChild(cards[r.run_id].el);});}
  $('empty').style.display=s.runs.length?'none':'block';
  bars(s.exposure); alerts(s.audit); audit(s.audit);
}

async function refresh(){
  try{
    var r=await fetch('/v1/state'); var s=await r.json(); render(s); $('live').textContent='LIVE';
  }catch(e){$('live').textContent='OFFLINE';}
}

SC.forEach(function(x){
  var b=mk('button',x[2]?'primary':'',x[1]);
  b.onclick=async function(){
    b.disabled=true;
    var old=b.textContent;
    b.textContent='Running...';
    await post('/v1/demo/scenario',{name:x[0]});
    refresh(); setTimeout(refresh,700);
    setTimeout(function(){b.disabled=false;b.textContent=old;},2500);
  };
  $('launch').appendChild(b);
});

$('cards').addEventListener('click',async function(ev){
  var b=ev.target.closest('button'); if(!b||b.disabled) return;
  var run=b.closest('.cred').dataset.run;
  if(b.dataset.act==='revoke') await post('/v1/completions',{run_id:run,status:'manual_revoke'});
  if(b.dataset.act==='replay') await post('/v1/demo/replay',{run_id:run});
  refresh();
});

refresh(); setInterval(refresh,1000); requestAnimationFrame(tick);
</script></body></html>"""