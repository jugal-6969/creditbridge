import { useState, useRef } from "react";

const PROFILES={
  "Jugal Bhagat — 8 months":{name:"Jugal Bhagat",nat:"Indian",visa:"Employment",employer:"Keeta Technologies LLC",salary:12500,rent:4,sal:4,telco:3,util:4,ejari:0.7,telco_mo:8,exp:0.52,wps:true,months_in_uae:8,has_ejari:true,has_dewa:true,bank_balance:7716,bank_name:"Emirates NBD",cibil:731},
  "Radhika Chopra — 5 months":{name:"Radhika Chopra",nat:"Indian",visa:"Employment",employer:"ENOC Group",salary:8200,rent:3,sal:3,telco:2,util:3,ejari:0.4,telco_mo:5,exp:0.68,wps:true,months_in_uae:5,has_ejari:false,has_dewa:false,bank_balance:3420,bank_name:"Mashreq",cibil:680},
  "Dua Aamir — 14 months":{name:"Dua Aamir",nat:"Pakistani",visa:"Freelance",employer:"Self-employed",salary:18000,rent:4,sal:3,telco:4,util:4,ejari:1.2,telco_mo:14,exp:0.41,wps:false,months_in_uae:14,has_ejari:true,has_dewa:true,bank_balance:12100,bank_name:"ADCB",cibil:null}
};
const BANKS=[
  {name:"RAK Bank",min:580,rate:"3.99%",product:"Personal Loan",max:"AED 250,000",note:"Expat-friendly · fast approval"},
  {name:"NBF",min:600,rate:"4.25%",product:"Personal Loan",max:"AED 300,000",note:"Sharia-compliant option available"},
  {name:"Vio Bank",min:550,rate:"4.50%",product:"Credit Builder Loan",max:"AED 100,000",note:"Digital-first · lowest threshold"},
  {name:"Ruya",min:620,rate:"3.75%",product:"Islamic Finance",max:"AED 200,000",note:"Islamic banking · profit-rate model"}
];
const SOURCES=[
  {src:"UAE Pass",sub:"Identity verified"},
  {src:"Open Banking API",sub:"Transactional data"},
  {src:"WPS / Ministry of Labour",sub:"Salary & employment"},
  {src:"DEWA",sub:"Utility payments"},
  {src:"Ejari / RERA",sub:"Rental records"},
  {src:"AECB Report",sub:"Thin-file check"}
];
const TXNS=[
  {desc:"Salary credit",merchant:"Keeta Technologies LLC",amount:12500,date:"Apr 1",cat:"Income"},
  {desc:"DEWA bill",merchant:"Dubai Electricity & Water",amount:-320,date:"Apr 3",cat:"Utilities"},
  {desc:"Carrefour",merchant:"Mall of Emirates",amount:-287,date:"Apr 5",cat:"Food"},
  {desc:"Ejari rent",merchant:"RERA",amount:-3800,date:"Apr 7",cat:"Housing"},
  {desc:"du Telecom",merchant:"Postpaid plan",amount:-199,date:"Apr 9",cat:"Utilities"}
];
const SPEND=[
  {n:"Housing",v:3800,c:"#00c97a"},
  {n:"Food",v:287,c:"#6366f1"},
  {n:"Utilities",v:519,c:"#a855f7"},
  {n:"Shopping",v:145,c:"#f59e0b"}
];

const GROQ_API_KEY = "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";

const BG="#07090f",CARD="#0d1117",BORDER="#1c2333",ACCENT="#00c97a",TEXT="#e2e8f0",MUTED="#64748b",WARN="#f59e0b",DANGER="#ef4444",INDIGO="#6366f1";

function calcScore(p,aecb,cibil){
  const ir=p.exp<=0.4?4:p.exp<=0.6?3:p.exp<=0.8?2:1;
  const te=p.ejari>=3?4:p.ejari>=1?3:p.ejari>=0.5?2:1;
  const tt=p.telco_mo>=36?4:p.telco_mo>=12?3:p.telco_mo>=6?2:1;
  const rE=p.has_ejari?p.rent:Math.max(1,p.rent-1);
  const uE=p.has_dewa?p.util:Math.max(1,p.util-1);
  const cB=(p.cibil&&cibil)?Math.min(30,Math.round((p.cibil-600)/10)):0;
  const aB=aecb?10:0;
  const raw=rE*0.28+p.sal*0.22+te*0.12+ir*0.15+p.telco*0.10+tt*0.07+uE*0.06;
  return Math.min(850,Math.round(300+((raw-1)/3)*550)+cB+aB);
}
function tier(s){return s>=700?["Low Risk",ACCENT]:s>=550?["Moderate Risk",WARN]:["High Risk",DANGER];}

const css=`
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body,html{background:${BG};font-family:'DM Sans',sans-serif;color:${TEXT};}
.app{max-width:440px;margin:0 auto;padding:0 16px 80px;}
.bt{font-size:22px;font-weight:700;color:${TEXT};} .bt span{color:${ACCENT};}
.sh{font-size:10px;font-weight:600;color:${MUTED};letter-spacing:1px;text-transform:uppercase;margin:18px 0 8px;}
.card{background:${CARD};border:1px solid ${BORDER};border-radius:16px;padding:16px 18px;margin-bottom:12px;}
.card-a{border-left:3px solid ${ACCENT};border-radius:0 16px 16px 0;}
.row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid ${BORDER};}
.row:last-child{border-bottom:none;}
.rl{font-size:13px;color:${MUTED};} .rv{font-size:13px;font-weight:600;color:${TEXT};}
.pill{display:inline-block;padding:3px 11px;border-radius:20px;font-size:11px;font-weight:600;}
.btn{background:${ACCENT};color:#000;border:none;border-radius:12px;padding:12px 20px;font-size:14px;font-weight:700;width:100%;cursor:pointer;font-family:'DM Sans',sans-serif;}
.btn:hover{opacity:0.85;}
.btn-g{background:transparent;color:${MUTED};border:1px solid ${BORDER};border-radius:12px;padding:9px 16px;font-size:12px;font-weight:600;cursor:pointer;font-family:'DM Sans',sans-serif;}
.btn-g:hover{border-color:${ACCENT};color:${ACCENT};}
.tab-bar{display:flex;overflow-x:auto;gap:4px;padding:0 0 12px;scrollbar-width:none;}
.tab-bar::-webkit-scrollbar{display:none;}
.tab{padding:6px 13px;border-radius:20px;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;border:1px solid ${BORDER};color:${MUTED};background:transparent;}
.tab.act{background:${ACCENT};color:#000;border-color:${ACCENT};}
.input{background:#131924;border:1px solid ${BORDER};border-radius:12px;color:${TEXT};font-size:13px;padding:10px 13px;width:100%;font-family:'DM Sans',sans-serif;outline:none;}
.input:focus{border-color:${ACCENT};}
.uzone{border:1.5px dashed ${BORDER};border-radius:14px;padding:22px;text-align:center;cursor:pointer;margin-bottom:10px;}
.uzone:hover{border-color:${ACCENT};}
.alert{background:#0d1117;border:1px solid ${BORDER};border-radius:12px;padding:12px 14px;font-size:13px;color:${MUTED};margin-bottom:12px;line-height:1.7;}
.cu{background:${ACCENT};color:#000;padding:9px 13px;border-radius:14px 14px 3px 14px;font-size:13px;margin:5px 0;margin-left:18%;line-height:1.6;}
.cb{background:#131924;color:#a8bbd4;padding:9px 13px;border-radius:14px 14px 14px 3px;font-size:13px;margin:5px 0;margin-right:18%;line-height:1.6;}
.fi{display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:12px;border:1px solid ${BORDER};margin-bottom:7px;}
.fi-d{border-color:${ACCENT};background:rgba(0,201,122,0.04);}
.pb{height:4px;background:${BORDER};border-radius:2px;overflow:hidden;margin-top:5px;}
.pf{height:100%;border-radius:2px;transition:width 0.3s;}
.brow{display:flex;align-items:center;gap:10px;padding:12px 14px;border-radius:12px;border:1px solid ${BORDER};background:${CARD};margin-bottom:8px;}
.brow-ok{border-color:${ACCENT};background:rgba(0,201,122,0.04);}
`;

function ScoreGauge({score}){
  const [,col]=tier(score);
  const pct=(score-300)/550,R=78,cx=98,cy=92;
  const s1=Math.PI*0.85,e1=Math.PI*2.15,tot=e1-s1,ang=s1+tot*pct;
  const x1=cx+R*Math.cos(s1),y1=cy+R*Math.sin(s1),x2=cx+R*Math.cos(e1),y2=cx+R*Math.sin(e1);
  const px=cx+R*Math.cos(ang),py=cy+R*Math.sin(ang),la=tot*pct>Math.PI?1:0;
  return(
    <svg viewBox="0 0 196 110" style={{width:"100%",maxWidth:260,display:"block",margin:"0 auto"}}>
      <path d={`M${x1},${y1} A${R},${R} 0 1 1 ${x2},${y2}`} fill="none" stroke={BORDER} strokeWidth="10" strokeLinecap="round"/>
      <path d={`M${x1},${y1} A${R},${R} 0 ${la} 1 ${px},${py}`} fill="none" stroke={col} strokeWidth="10" strokeLinecap="round"/>
      <circle cx={px} cy={py} r="5" fill={col}/>
      <text x={cx} y={cy-2} textAnchor="middle" fill={col} fontSize="28" fontWeight="700" fontFamily="DM Sans">{score}</text>
      <text x={cx} y={cy+14} textAnchor="middle" fill={MUTED} fontSize="10" fontFamily="DM Sans">out of 850</text>
      <text x="28" y="108" fill={MUTED} fontSize="9" fontFamily="DM Sans">300</text>
      <text x="158" y="108" fill={MUTED} fontSize="9" fontFamily="DM Sans">850</text>
    </svg>
  );
}

export default function CreditBridge(){
  const [screen,setScreen]=useState("login");
  const [profile,setProfile]=useState(null);
  const [score,setScore]=useState(null);
  const [tab,setTab]=useState(0);
  const [chat,setChat]=useState([]);
  const [chatInput,setChatInput]=useState("");
  const [passportDone,setPassportDone]=useState(false);
  const [fetchStep,setFetchStep]=useState(-1);
  const [aecb,setAecb]=useState(false);
  const [cibil,setCibil]=useState(false);
  const [bankConn,setBankConn]=useState(false);
  const [callbackBank,setCallbackBank]=useState(null);
  const [selEid,setSelEid]=useState(Object.keys(PROFILES)[0]);
  const [pin,setPin]=useState("");
  const [aiLoading,setAiLoading]=useState(false);
  const chatBottom=useRef(null);

  function recompute(p,a,c){setScore(calcScore(p,a,c));}

  function doLogin(){
    if(pin!=="123456"){alert("Incorrect PIN. Use 123456 for demo.");return;}
    const p=PROFILES[selEid];
    setProfile(p);setScreen("fetch");setFetchStep(0);
    let step=0;
    const iv=setInterval(()=>{
      step++;setFetchStep(step);
      if(step>=SOURCES.length){clearInterval(iv);setTimeout(()=>{setScore(calcScore(p,false,false));setScreen("app");},400);}
    },600);
  }

  async function sendChat(q){
    const newChat=[...chat,{role:"user",text:q}];
    setChat(newChat);setChatInput("");setAiLoading(true);
    const sys=`You are a concise UAE credit advisor for CreditBridge. User: ${profile.name}, ${profile.nat}, ${profile.visa} visa, salary AED ${profile.salary}/mo, ${profile.months_in_uae} months in UAE. CreditBridge score: ${score}/850. AECB uploaded: ${aecb}. CIBIL uploaded: ${cibil}. Bank connected: ${bankConn}. Shared accommodation (no personal Ejari/DEWA): ${!profile.has_ejari||!profile.has_dewa}. Keep answers under 80 words. Be specific and practical.`;
    try{
      const res=await fetch("https://api.groq.com/openai/v1/chat/completions",{
        method:"POST",
        headers:{"Content-Type":"application/json","Authorization":"Bearer "+GROQ_API_KEY},
        body:JSON.stringify({model:"llama-3.3-70b-versatile",max_tokens:150,messages:[{role:"system",content:sys},{role:"user",content:q}]})
      });
      const data=await res.json();
      const reply=data.choices?.[0]?.message?.content||"Sorry, couldn't get a response. Check your API key.";
      setChat([...newChat,{role:"bot",text:reply}]);
    }catch(e){
      setChat([...newChat,{role:"bot",text:"Connection error. Check the Groq API key in the code."}]);
    }
    setAiLoading(false);
    setTimeout(()=>{chatBottom.current?.scrollIntoView({behavior:"smooth"});},50);
  }

  if(screen==="login") return(
    <div className="app"><style>{css}</style>
      <div style={{textAlign:"center",padding:"32px 0 20px"}}>
        <div style={{width:52,height:52,background:"#131924",border:`1px solid ${BORDER}`,borderRadius:14,display:"flex",alignItems:"center",justifyContent:"center",margin:"0 auto 12px",fontSize:22}}>💳</div>
        <div className="bt">Credit<span>Bridge</span></div>
        <div style={{fontSize:13,color:MUTED,marginTop:4}}>No UAE credit history? We build it from scratch.</div>
      </div>
      <div className="alert"><strong style={{color:TEXT}}>Who is CreditBridge for?</strong><br/>You just arrived in UAE. You have a job, pay rent — but UAE banks have <strong style={{color:TEXT}}>zero record of you.</strong> CreditBridge reads your real financial behaviour and gives you a score banks can act on.</div>
      <div className="card">
        <div className="sh" style={{margin:"0 0 10px"}}>Sign in with UAE Pass</div>
        <select className="input" value={selEid} onChange={e=>setSelEid(e.target.value)} style={{marginBottom:8}}>
          {Object.keys(PROFILES).map(k=><option key={k} value={k}>{k}</option>)}
        </select>
        <input className="input" type="password" value={pin} onChange={e=>setPin(e.target.value)} placeholder="UAE Pass PIN (demo: 123456)" style={{marginBottom:12}}/>
        <button className="btn" onClick={doLogin}>Continue with UAE Pass</button>
        <div style={{textAlign:"center",fontSize:11,color:MUTED,marginTop:6}}>Demo PIN: 123456</div>
      </div>
      <div className="sh">Data sources used for scoring</div>
      {SOURCES.map(({src,sub})=><div className="row" key={src}><span className="rl">{src}</span><span style={{fontSize:11,color:MUTED}}>{sub}</span></div>)}
    </div>
  );

  if(screen==="fetch") return(
    <div className="app"><style>{css}</style>
      <div style={{textAlign:"center",padding:"32px 0 18px"}}>
        <div style={{fontSize:17,fontWeight:600,color:TEXT}}>Building your profile</div>
        <div style={{fontSize:12,color:MUTED,marginTop:5}}>Pulling data for {profile?.name}</div>
      </div>
      {SOURCES.map(({src,sub},i)=>(
        <div key={src} className={`fi${fetchStep>i?" fi-d":""}`}>
          <span style={{fontSize:14}}>{fetchStep>i?"✅":fetchStep===i?"⏳":"○"}</span>
          <div><div style={{fontSize:12,fontWeight:500,color:TEXT}}>{src}</div><div style={{fontSize:11,color:fetchStep>i?ACCENT:MUTED}}>{sub}</div></div>
        </div>
      ))}
    </div>
  );

  const p=profile,sc=score;
  const [lbl,col]=tier(sc);
  const ini=p.name.split(" ").map(w=>w[0]).join("");
  const tabs=["Account","Score","Banks","Passport","AI Advisor"];

  return(
    <div className="app"><style>{css}</style>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"12px 0 14px",borderBottom:`1px solid ${BORDER}`,marginBottom:12}}>
        <div className="bt" style={{fontSize:18}}>Credit<span>Bridge</span></div>
        <div style={{display:"flex",gap:8,alignItems:"center"}}>
          <span style={{fontSize:11,color:MUTED}}>{p.name}</span>
          <div style={{width:30,height:30,borderRadius:"50%",background:"#131924",border:`1px solid ${BORDER}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:10,fontWeight:700,color:ACCENT}}>{ini}</div>
        </div>
      </div>

      <div className="tab-bar">{tabs.map((t,i)=><div key={t} className={`tab${tab===i?" act":""}`} onClick={()=>setTab(i)}>{t}</div>)}</div>

      {/* ACCOUNT */}
      {tab===0&&<div>
        {!bankConn?(
          <div className="card card-a">
            <div style={{fontSize:11,color:ACCENT,fontWeight:600,marginBottom:8}}>Connect your bank account</div>
            <div style={{fontSize:12,color:MUTED,lineHeight:1.7,marginBottom:12}}>Connecting via Open Banking pulls your salary, rent, and bill payment history — the strongest signal in your score.</div>
            <button className="btn" onClick={()=>{setBankConn(true);recompute(p,aecb,cibil);}}>Connect {p.bank_name} via Open Banking</button>
          </div>
        ):(
          <>
            <div style={{background:"linear-gradient(135deg,#0d1f35,#060f1e)",borderRadius:16,padding:20,marginBottom:14,border:`1px solid ${BORDER}`}}>
              <div style={{fontSize:10,fontWeight:700,letterSpacing:"0.12em",textTransform:"uppercase",color:ACCENT,marginBottom:10}}>{p.bank_name} · via Open Banking</div>
              <div style={{fontSize:11,color:MUTED,marginBottom:3}}>Available balance</div>
              <div style={{fontSize:30,fontWeight:700,color:TEXT,marginBottom:14}}>AED {p.bank_balance.toLocaleString()}</div>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-end"}}>
                <div><div style={{fontSize:10,color:MUTED,marginBottom:2}}>Card holder</div><div style={{fontSize:13,fontWeight:600,color:TEXT}}>{p.name}</div></div>
                <div style={{textAlign:"right"}}><div style={{fontSize:11,color:MUTED,fontFamily:"monospace"}}>**** **** **** 4821</div><div style={{fontSize:10,color:MUTED,marginTop:2}}>Exp 04/29</div></div>
              </div>
            </div>
            <div className="sh">3-month payment summary</div>
            {[["Salary credits","4 of 4 months",ACCENT],["Rent payments",p.has_ejari?"On time every month":"Via bank transfer (no Ejari)",p.has_ejari?ACCENT:WARN],["Utility bills",p.has_dewa?"All settled on time":"Paid by landlord",p.has_dewa?ACCENT:WARN],["Telecom","Postpaid — no missed payments",ACCENT]].map(([l,v,c])=>(
              <div className="row" key={l}><span className="rl">{l}</span><span style={{fontSize:13,fontWeight:600,color:c}}>{v}</span></div>
            ))}
            <div className="sh" style={{marginTop:16}}>Spending breakdown</div>
            <div className="card" style={{display:"flex",gap:16,alignItems:"center"}}>
              {(()=>{const total=SPEND.reduce((s,d)=>s+d.v,0);let cum=0;const paths=SPEND.map(d=>{const s=cum/total,e=(cum+d.v)/total;cum+=d.v;const a1=s*2*Math.PI-Math.PI/2,a2=e*2*Math.PI-Math.PI/2;const x1=60+50*Math.cos(a1),y1=60+50*Math.sin(a1),x2=60+50*Math.cos(a2),y2=60+50*Math.sin(a2);const la=a2-a1>Math.PI?1:0;return <path key={d.n} d={`M60,60 L${x1},${y1} A50,50 0 ${la} 1 ${x2},${y2} Z`} fill={d.c}/>;});return(<><svg viewBox="0 0 120 120" style={{width:90,flexShrink:0}}>{paths}<circle cx="60" cy="60" r="28" fill={CARD}/><text x="60" y="64" textAnchor="middle" fill={TEXT} fontSize="10" fontFamily="DM Sans">AED {(total/1000).toFixed(1)}k</text></svg><div style={{flex:1}}>{SPEND.map(d=><div key={d.n} style={{display:"flex",justifyContent:"space-between",marginBottom:5}}><div style={{display:"flex",alignItems:"center",gap:6}}><div style={{width:7,height:7,borderRadius:2,background:d.c}}/><span style={{fontSize:11,color:MUTED}}>{d.n}</span></div><span style={{fontSize:11,fontWeight:600,color:TEXT}}>AED {d.v.toLocaleString()}</span></div>)}</div></>);})()}
            </div>
            <div className="sh" style={{marginTop:16}}>Recent transactions</div>
            {TXNS.map((tx,i)=>{const pos=tx.amount>0;return(<div className="row" key={i}><div><div style={{fontSize:12,fontWeight:500,color:TEXT}}>{tx.desc}</div><div style={{fontSize:10,color:MUTED,marginTop:2}}>{tx.merchant} · {tx.date}</div></div><div style={{textAlign:"right"}}><div style={{fontSize:12,fontWeight:600,color:pos?ACCENT:TEXT}}>{pos?"+":"-"}AED {Math.abs(tx.amount).toLocaleString()}</div><div style={{fontSize:10,color:MUTED,marginTop:1}}>{tx.cat}</div></div></div>);})}
          </>
        )}
      </div>}

      {/* SCORE */}
      {tab===1&&<div>
        <ScoreGauge score={sc}/>
        <div style={{textAlign:"center",marginBottom:6}}><span className="pill" style={{background:col===ACCENT?"rgba(0,201,122,0.1)":col===WARN?"rgba(245,158,11,0.12)":"rgba(239,68,68,0.12)",color:col===ACCENT?"#0a7a4a":col===WARN?"#b45309":"#b91c1c"}}>{lbl}</span></div>
        <div style={{textAlign:"center",fontSize:12,color:MUTED,marginBottom:14}}>{p.months_in_uae} months in UAE · {p.wps?"WPS registered":"Self-employed"}</div>
        <div className="sh">Step 1 — Upload AECB report</div>
        <div style={{fontSize:12,color:MUTED,lineHeight:1.7,marginBottom:8}}>Buy at <strong style={{color:TEXT}}>aecb.ae</strong> for AED 84. OCR extracts the data. Adds <strong style={{color:ACCENT}}>+10 pts</strong>.</div>
        {!aecb?(<div className="uzone" onClick={()=>{setAecb(true);recompute(p,true,cibil);}}><div style={{fontSize:20,marginBottom:5}}>📄</div><div style={{fontSize:12,color:MUTED}}>Tap to upload AECB PDF</div><div style={{fontSize:10,color:BORDER,marginTop:3}}>Click to simulate in demo</div></div>)
        :(<div className="card" style={{borderColor:ACCENT,background:"rgba(0,201,122,0.04)",marginBottom:10}}><div style={{fontSize:12,color:ACCENT,fontWeight:600}}>✅ AECB report uploaded · +10 pts added</div></div>)}
        {p.nat==="Indian"&&<>
          <div className="sh">Step 2 — Upload CIBIL report (India)</div>
          <div style={{fontSize:12,color:MUTED,lineHeight:1.7,marginBottom:8}}>Your Indian credit history counts. Adds up to <strong style={{color:ACCENT}}>+30 pts</strong> and activates your India Credit Passport.</div>
          {!cibil?(<div className="uzone" onClick={()=>{setCibil(true);recompute(p,aecb,true);}}><div style={{fontSize:20,marginBottom:5}}>🇮🇳</div><div style={{fontSize:12,color:MUTED}}>Tap to upload CIBIL PDF</div><div style={{fontSize:10,color:BORDER,marginTop:3}}>Click to simulate in demo</div></div>)
          :(<div className="card" style={{borderColor:ACCENT,background:"rgba(0,201,122,0.04)",marginBottom:10}}><div style={{fontSize:12,color:ACCENT,fontWeight:600}}>✅ CIBIL {p.cibil} uploaded · Powers India Passport ✓</div></div>)}
        </>}
        {(!p.has_ejari||!p.has_dewa)&&<div style={{background:"rgba(245,158,11,0.06)",border:"1px solid rgba(245,158,11,0.2)",borderRadius:12,padding:"10px 14px",marginBottom:12,fontSize:12,color:MUTED,lineHeight:1.7}}><strong style={{color:WARN}}>Shared accommodation detected.</strong> Open banking signals substitute for Ejari/DEWA — slightly lower weight, still counted.</div>}
        <div className="sh" style={{marginTop:4}}>Profile</div>
        {[["Monthly income",`AED ${p.salary.toLocaleString()}`],["Employer",p.employer],["Visa type",p.visa],["UAE tenure",`${p.months_in_uae} months`],["WPS registered",p.wps?"Yes":"No"],["Expense ratio",`${Math.round(p.exp*100)}%`]].map(([l,v])=><div className="row" key={l}><span className="rl">{l}</span><span className="rv">{v}</span></div>)}
        <div className="sh" style={{marginTop:14}}>Score factors</div>
        {[["Rent consistency",p.has_ejari?p.rent:Math.max(1,p.rent-1),!p.has_ejari?"no Ejari":null],["Salary regularity",p.sal,null],["Telecom",p.telco,null],["Utility payments",p.has_dewa?p.util:Math.max(1,p.util-1),!p.has_dewa?"no direct DEWA":null]].map(([fl,val,note])=>{
          const pct=(val/4)*100,c2=val>=3?ACCENT:val===2?WARN:DANGER;
          return(<div key={fl} style={{marginBottom:10}}><div style={{display:"flex",justifyContent:"space-between",marginBottom:3}}><span style={{fontSize:11,color:MUTED}}>{fl}{note&&<span style={{fontSize:10,color:WARN,marginLeft:5}}>({note})</span>}</span><span style={{fontSize:11,fontWeight:600,color:c2}}>{Math.round(pct)}%</span></div><div className="pb"><div className="pf" style={{width:`${pct}%`,background:c2}}/></div></div>);
        })}
      </div>}

      {/* BANKS */}
      {tab===2&&<div>
        <div className="card"><div style={{fontSize:10,color:MUTED,marginBottom:3}}>Your score</div><div style={{fontSize:34,fontWeight:700,color:col}}>{sc}</div><div style={{fontSize:12,color:MUTED,marginTop:2}}>{lbl} · {BANKS.filter(b=>sc>=b.min).length} of {BANKS.length} banks eligible</div></div>
        <div className="alert"><strong style={{color:TEXT}}>How bank matching works.</strong> CreditBridge is a referral gateway — not a lender. Submit a call-back request and a bank representative contacts you within 2 business days.</div>
        <div className="sh">Bank eligibility</div>
        {BANKS.map(b=>{const ok=sc>=b.min;const gap=b.min-sc;const pp=Math.min((sc/b.min)*100,100);return(<div key={b.name}><div className={`brow${ok?" brow-ok":""}`}><div style={{flex:1}}><div style={{fontSize:12,fontWeight:600,color:TEXT}}>{b.name}</div><div style={{fontSize:11,color:MUTED,marginTop:2}}>{b.product} · {b.rate} · up to {b.max}</div><div style={{fontSize:11,color:INDIGO,marginTop:2}}>{b.note}</div></div>{ok?<button className="btn" style={{width:"auto",padding:"7px 12px",fontSize:11}} onClick={()=>setCallbackBank(b.name)}>{callbackBank===b.name?"✅ Requested":"Request call-back"}</button>:<span className="pill" style={{background:"rgba(245,158,11,0.12)",color:WARN}}>+{gap} pts</span>}</div>{!ok&&<div className="pb" style={{marginBottom:8,marginTop:-3}}><div className="pf" style={{width:`${pp.toFixed(0)}%`,background:WARN}}/></div>}</div>);})}
        {callbackBank&&<div style={{background:"rgba(0,201,122,0.05)",border:"1px solid rgba(0,201,122,0.2)",borderRadius:12,padding:"12px 14px",marginTop:6,fontSize:12,color:MUTED,lineHeight:1.7}}>✅ <strong style={{color:TEXT}}>Call-back requested with {callbackBank}.</strong> A representative will contact you within 2 business days.</div>}
      </div>}

      {/* PASSPORT */}
      {tab===3&&<div>
        <div className="card card-a"><div style={{fontSize:11,color:ACCENT,fontWeight:600,marginBottom:7}}>Credit Passport</div><div style={{fontSize:12,color:MUTED,lineHeight:1.8}}>Leaving UAE? Your credit history should not die at the border. CreditBridge issues a portable score report accepted by partner financial institutions in your home country.</div></div>
        <div className="sh">Partner bureaus</div>
        {[{flag:"🇮🇳",name:"India",bureau:"CIBIL",live:true},{flag:"🇵🇰",name:"Pakistan",bureau:"eCIB",live:false},{flag:"🇵🇭",name:"Philippines",bureau:"CIC",live:false},{flag:"🇬🇧",name:"United Kingdom",bureau:"Experian UK",live:false}].map(c=>(
          <div className="row" key={c.name}><span className="rl">{c.flag} {c.name} · {c.bureau}</span><span className="pill" style={c.live?{background:"rgba(0,201,122,0.1)",color:"#0a7a4a"}:{background:"rgba(99,102,241,0.1)",color:"#4338ca"}}>{c.live?"Live":"Coming soon"}</span></div>
        ))}
        <div className="sh" style={{marginTop:16}}>India passport status</div>
        {!cibil?<div style={{background:"rgba(245,158,11,0.06)",border:"1px solid rgba(245,158,11,0.2)",borderRadius:12,padding:"12px 14px",marginBottom:12,fontSize:12,color:MUTED,lineHeight:1.7}}><strong style={{color:WARN}}>CIBIL not uploaded.</strong> Go to <strong style={{color:TEXT,cursor:"pointer"}} onClick={()=>setTab(1)}>Score tab → Step 2</strong> to upload your CIBIL report and activate your India Credit Passport.</div>
        :<div className="card" style={{borderColor:ACCENT,background:"rgba(0,201,122,0.04)",marginBottom:12}}><div style={{fontSize:12,color:ACCENT,fontWeight:600}}>✅ India Credit Passport ready</div><div style={{fontSize:11,color:MUTED,marginTop:3}}>CIBIL {p.cibil} mapped · Accepted at CIBIL partner institutions in India.</div></div>}
        {!passportDone?<button className="btn" onClick={()=>setPassportDone(true)}>Generate my Credit Passport</button>
        :<div style={{borderRadius:16,overflow:"hidden",border:`1px solid ${BORDER}`,marginTop:14}}>
          <div style={{background:"linear-gradient(135deg,#0d2535,#060f1e)",padding:"20px 18px"}}>
            <div style={{fontSize:9,color:ACCENT,letterSpacing:"0.12em",textTransform:"uppercase",marginBottom:8}}>CreditBridge Credit Passport</div>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
              <div><div style={{fontSize:18,fontWeight:700,color:TEXT}}>{p.name}</div><div style={{fontSize:12,color:MUTED,marginTop:3}}>{p.nat} · {p.visa} Visa</div></div>
              <div style={{textAlign:"right"}}><div style={{fontSize:30,fontWeight:700,color:col}}>{sc}</div><div style={{fontSize:10,color:MUTED}}>/ 850</div></div>
            </div>
          </div>
          <div style={{background:CARD,padding:"16px 18px"}}>
            {[["Rating",lbl],["UAE tenure",`${p.months_in_uae} months`],["Issued","April 2026"],["Valid until","April 2027"],["Passport ID",`CB-${String(Math.abs([...p.name].reduce((s,c)=>s+c.charCodeAt(0),0))%100000).padStart(5,"0")}`]].map(([l,v])=><div className="row" key={l}><span className="rl">{l}</span><span className="rv">{v}</span></div>)}
            <div style={{marginTop:10,fontSize:11,color:MUTED}}>{cibil?"✅ India (CIBIL) · ":""}Coming soon: 🇵🇰 Pakistan · 🇵🇭 Philippines · 🇬🇧 UK</div>
          </div>
        </div>}
      </div>}

      {/* AI ADVISOR */}
      {tab===4&&<div>
        <div className="card card-a"><div style={{fontSize:11,color:ACCENT,fontWeight:600,marginBottom:7}}>AI Financial Advisor</div><div style={{fontSize:12,color:MUTED,lineHeight:1.8}}>Score: <strong style={{color:TEXT}}>{sc}/850</strong> · {lbl} · {p.months_in_uae} months in UAE. Powered by Groq (llama-3.3-70b). Ask anything about your score, banks, or building credit faster.</div></div>
        {chat.length===0&&<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:7,marginBottom:14}}>
          {["How do I improve my score?","Which bank should I apply to?","What is the AECB report?","How does CIBIL help my score?"].map((q,i)=>(
            <button key={i} className="btn-g" style={{fontSize:11,padding:"9px 10px",textAlign:"left"}} onClick={()=>sendChat(q)}>{q}</button>
          ))}
        </div>}
        <div style={{minHeight:80,marginBottom:10}}>
          {chat.map((msg,i)=><div key={i} className={msg.role==="user"?"cu":"cb"}>{msg.text}</div>)}
          {aiLoading&&<div className="cb" style={{color:MUTED}}>Thinking…</div>}
          <div ref={chatBottom}/>
        </div>
        <div style={{display:"flex",gap:7}}>
          <input className="input" value={chatInput} onChange={e=>setChatInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&chatInput.trim())sendChat(chatInput.trim());}} placeholder="Ask about your score, banks, or credit building…" style={{flex:1}}/>
          <button className="btn" style={{width:"auto",padding:"0 14px"}} onClick={()=>chatInput.trim()&&sendChat(chatInput.trim())}>↑</button>
        </div>
      </div>}

      <div style={{marginTop:28,textAlign:"center"}}>
        <button className="btn-g" onClick={()=>{setScreen("login");setProfile(null);setScore(null);setTab(0);setChat([]);setPassportDone(false);setFetchStep(-1);setAecb(false);setCibil(false);setBankConn(false);setCallbackBank(null);setPin("");}}>Sign out</button>
        <div style={{fontSize:10,color:MUTED,marginTop:6}}>CreditBridge v4 · Dubai · Not a regulated credit bureau.</div>
      </div>
    </div>
  );
}
