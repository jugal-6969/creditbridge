import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { Redirect } from "wouter";
import { Layout } from "@/components/layout";
import { useGetProfile, getGetProfileQueryKey } from "@workspace/api-client-react";
import {
  PlusCircle, SendHorizontal, Receipt,
  ArrowDownLeft, ArrowUpRight, TrendingUp, Info,
  Wallet, Sparkles, ChevronRight,
} from "lucide-react";
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend,
} from "recharts";

// ─── Constants ───────────────────────────────────────────────────────────────

const ACCENT  = "hsl(170 100% 39%)";   // teal
const INDIGO  = "hsl(239 84% 67%)";    // indigo accent
const BORDER  = "hsl(217 32% 17%)";
const CARD    = "hsl(222 47% 11%)";
const MUTED   = "hsl(215 20% 55%)";
const FG      = "hsl(210 40% 98%)";

const TRANSACTIONS = [
  { id:1, description:"Salary Credit",   merchant:"Keeta Technologies LLC",          amount:+12500, date:"Apr 1, 2026",  category:"Income",    icon:ArrowDownLeft },
  { id:2, description:"DEWA Bill",        merchant:"Dubai Electricity & Water",        amount:-320,   date:"Apr 3, 2026",  category:"Utilities", icon:ArrowUpRight  },
  { id:3, description:"Carrefour",        merchant:"Carrefour Mall of Emirates",       amount:-287,   date:"Apr 5, 2026",  category:"Food",      icon:ArrowUpRight  },
  { id:4, description:"Ejari Rent",       merchant:"Real Estate Regulatory Agency",    amount:-3800,  date:"Apr 7, 2026",  category:"Housing",   icon:ArrowUpRight  },
  { id:5, description:"Noon Delivery",    merchant:"Noon.com",                         amount:-145,   date:"Apr 8, 2026",  category:"Shopping",  icon:ArrowUpRight  },
  { id:6, description:"Uber",             merchant:"Uber Technologies",                amount:-34,    date:"Apr 8, 2026",  category:"Transport", icon:ArrowUpRight  },
  { id:7, description:"du Telecom",       merchant:"du Postpaid Plan",                 amount:-199,   date:"Apr 9, 2026",  category:"Utilities", icon:ArrowUpRight  },
];

const SPENDING_DATA = [
  { name:"Housing",   value:3800, color:"hsl(170 100% 39%)" },
  { name:"Food",      value:287,  color:"hsl(217 90% 60%)"  },
  { name:"Utilities", value:519,  color:"hsl(280 60% 60%)"  },
  { name:"Shopping",  value:145,  color:"hsl(38 92% 50%)"   },
  { name:"Transport", value:34,   color:"hsl(340 70% 60%)"  },
];

const SCORE_SIGNALS = [
  { label:"On-time DEWA payment",  impact:"+8 pts",    done:true  },
  { label:"On-time Ejari rent",    impact:"+18 pts",   done:true  },
  { label:"On-time du Telecom",    impact:"+10 pts",   done:true  },
  { label:"Bill paid via wallet",  impact:"+5 pts each", done:false },
];

const AI_TIPS = [
  { icon:"⚡", text:"Pay your DEWA bill through the wallet every month — it's your highest-impact score signal at 28% weight." },
  { icon:"📱", text:"Switch to a postpaid du plan instead of prepaid. Consistent monthly payments add telecom tenure to your score faster." },
  { icon:"💸", text:"Your expense ratio is 52%. Bring it below 50% to unlock the next score tier and increase your micro-loan limit." },
];

// ─── Virtual Card ─────────────────────────────────────────────────────────────

function VirtualCard({ name }: { name: string }) {
  const initials = name.split(" ").map(w => w[0]).join("");
  return (
    <div
      className="relative rounded-2xl overflow-hidden select-none"
      style={{
        background: "linear-gradient(135deg, #0d1f35 0%, #091729 50%, #060f1e 100%)",
        border: `1px solid ${BORDER}`,
        minHeight: 200,
      }}
    >
      {/* Decorative blobs */}
      <div className="absolute top-0 right-0 w-64 h-64 rounded-full opacity-10"
        style={{ background: ACCENT, transform: "translate(40%,-40%)" }} />
      <div className="absolute bottom-0 left-0 w-48 h-48 rounded-full opacity-5"
        style={{ background: INDIGO, transform: "translate(-40%,40%)" }} />
      {/* Subtle grid lines */}
      <div className="absolute inset-0 opacity-5"
        style={{ backgroundImage:"linear-gradient(rgba(255,255,255,0.1) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.1) 1px,transparent 1px)", backgroundSize:"40px 40px" }} />

      <div className="relative p-6 flex flex-col gap-5">
        {/* Top row */}
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-bold tracking-[0.15em] uppercase" style={{ color: ACCENT }}>CreditBridge</p>
            <p className="text-xs mt-0.5" style={{ color: MUTED }}>Digital Wallet · UAE</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-5 rounded-sm opacity-60" style={{ background:"hsl(38 92% 60%)", border:"1px solid hsl(38 80% 50%)" }} />
            <div className="w-8 h-5 rounded-sm opacity-40 -ml-4" style={{ background:"hsl(0 80% 55%)", border:"1px solid hsl(0 70% 45%)" }} />
          </div>
        </div>

        {/* Balance */}
        <div>
          <p className="text-xs mb-1" style={{ color: MUTED }}>Available balance</p>
          <p className="text-3xl font-bold tracking-tight" style={{ color: FG }}>AED 7,716</p>
        </div>

        {/* Bottom row */}
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs mb-0.5" style={{ color: MUTED }}>Card holder</p>
            <p className="text-sm font-semibold" style={{ color: FG }}>{name}</p>
          </div>
          <div className="text-right">
            <p className="text-xs mb-0.5 font-mono tracking-widest" style={{ color: MUTED }}>**** **** **** 4821</p>
            <p className="text-xs" style={{ color: MUTED }}>Exp 04/29</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function WalletPage() {
  const { profileId } = useAuth();
  if (!profileId) return <Redirect to="/" />;

  const { data: profile } = useGetProfile(profileId, {
    query: { enabled: !!profileId, queryKey: getGetProfileQueryKey(profileId) },
  });

  const [applePayLinked,  setApplePayLinked]  = useState(true);
  const [googlePayLinked, setGooglePayLinked] = useState(false);

  const totalSpending = SPENDING_DATA.reduce((s, d) => s + d.value, 0);
  const totalDebit    = TRANSACTIONS.filter(t => t.amount < 0).reduce((s, t) => s + Math.abs(t.amount), 0);

  return (
    <Layout>
      <div className="space-y-5">

        {/* ── Header */}
        <div>
          <h1 className="text-2xl font-bold" style={{ color: FG }}>CreditBridge Wallet</h1>
          <p className="text-sm mt-1" style={{ color: MUTED }}>Every payment builds your credit score</p>
        </div>

        {/* ── Zero balance notice */}
        <div className="rounded-xl p-4 flex items-start gap-3"
          style={{ background:"rgba(99,102,241,0.06)", border:"1px solid rgba(99,102,241,0.22)" }}>
          <Info className="w-4 h-4 shrink-0 mt-0.5" style={{ color: INDIGO }} />
          <p className="text-xs leading-relaxed" style={{ color: MUTED }}>
            <span className="font-semibold" style={{ color: FG }}>Zero minimum balance.</span>{" "}
            No salary transfer required. Open instantly with your Emirates ID — no branch visit, no paperwork.
          </p>
        </div>

        {/* ── Virtual Card */}
        <VirtualCard name={profile?.name ?? "—"} />

        {/* ── Balance summary */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label:"Available",          value:`AED 7,716`,                    accent:true  },
            { label:"Spent this month",   value:`AED ${totalDebit.toLocaleString()}` },
            { label:"Money sent",         value:"AED 0"                                      },
          ].map(item => (
            <div key={item.label} className="rounded-xl p-3.5 border"
              style={{
                background: item.accent ? "rgba(0,201,167,0.06)" : CARD,
                borderColor: item.accent ? "rgba(0,201,167,0.25)" : BORDER,
              }}>
              <p className="text-xs mb-1" style={{ color: MUTED }}>{item.label}</p>
              <p className="text-sm font-bold" style={{ color: item.accent ? ACCENT : FG }}>{item.value}</p>
            </div>
          ))}
        </div>

        {/* ── Quick actions */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label:"Add Money",   Icon:PlusCircle      },
            { label:"Send Money",  Icon:SendHorizontal  },
            { label:"Pay Bills",   Icon:Receipt         },
          ].map(({ label, Icon }) => (
            <button key={label}
              className="flex flex-col items-center gap-2 p-4 rounded-xl border transition-all"
              style={{ background: CARD, borderColor: BORDER }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = "rgba(0,201,167,0.4)"; }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = BORDER; }}
            >
              <div className="w-10 h-10 rounded-full flex items-center justify-center"
                style={{ background:"rgba(0,201,167,0.1)" }}>
                <Icon className="w-5 h-5" style={{ color: ACCENT }} />
              </div>
              <span className="text-xs font-medium" style={{ color: MUTED }}>{label}</span>
            </button>
          ))}
        </div>

        {/* ── Linked payment services */}
        <div className="rounded-xl p-5 border" style={{ background: CARD, borderColor: BORDER }}>
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-4" style={{ color: MUTED }}>
            Linked Payment Services
          </h3>
          {[
            { name:"Apple Pay",  sub:"Tap to pay on iPhone & Apple Watch", linked:applePayLinked,  toggle:setApplePayLinked  },
            { name:"Google Pay", sub:"Tap to pay on Android devices",       linked:googlePayLinked, toggle:setGooglePayLinked },
          ].map(({ name, sub, linked, toggle }) => (
            <div key={name} className="flex items-center justify-between py-3.5 border-b last:border-0"
              style={{ borderColor: BORDER }}>
              <div>
                <p className="text-sm font-medium" style={{ color: FG }}>{name}</p>
                <p className="text-xs mt-0.5" style={{ color: MUTED }}>{sub}</p>
              </div>
              <button
                onClick={() => toggle(v => !v)}
                className="relative w-12 h-6 rounded-full transition-colors focus:outline-none"
                style={{ background: linked ? ACCENT : BORDER }}
              >
                <span className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                  style={{ transform: linked ? "translateX(24px)" : "translateX(0)" }} />
              </button>
            </div>
          ))}
        </div>

        {/* ── AI Recommendations */}
        <div className="rounded-xl p-5" style={{ background:"rgba(99,102,241,0.05)", border:"1px solid rgba(99,102,241,0.2)" }}>
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4 shrink-0" style={{ color: INDIGO }} />
            <h3 className="text-sm font-semibold" style={{ color: FG }}>AI Score Recommendations</h3>
          </div>
          <div className="space-y-3">
            {AI_TIPS.map((tip, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg"
                style={{ background:"rgba(99,102,241,0.06)", border:"1px solid rgba(99,102,241,0.12)" }}>
                <span className="text-base shrink-0">{tip.icon}</span>
                <p className="text-xs leading-relaxed" style={{ color: MUTED }}>{tip.text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── Spending breakdown */}
        <div className="rounded-xl p-5 border" style={{ background: CARD, borderColor: BORDER }}>
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-4" style={{ color: MUTED }}>
            This Month's Spending
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={SPENDING_DATA} cx="50%" cy="50%"
                innerRadius={52} outerRadius={80} paddingAngle={3} dataKey="value">
                {SPENDING_DATA.map((entry, i) => (
                  <Cell key={i} fill={entry.color} strokeWidth={0} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background:"#0d1117", border:`1px solid ${BORDER}`, borderRadius:"8px", color:FG }}
                formatter={(val: number) => [`AED ${val.toLocaleString()}`, ""]}
              />
              <Legend iconType="circle" iconSize={7}
                formatter={value => <span style={{ color:MUTED, fontSize:11 }}>{value}</span>} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-3 space-y-2.5">
            {SPENDING_DATA.map(item => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ background:item.color }} />
                  <span className="text-xs" style={{ color:MUTED }}>{item.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-24 h-1.5 rounded-full overflow-hidden" style={{ background: BORDER }}>
                    <div className="h-full rounded-full"
                      style={{ width:`${(item.value/totalSpending)*100}%`, background:item.color }} />
                  </div>
                  <span className="text-xs font-medium w-16 text-right" style={{ color:FG }}>
                    AED {item.value.toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Recent transactions */}
        <div className="rounded-xl p-5 border" style={{ background: CARD, borderColor: BORDER }}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color:MUTED }}>Recent Transactions</h3>
            <button className="flex items-center gap-1 text-xs font-medium" style={{ color:ACCENT }}>
              View all <ChevronRight className="w-3 h-3" />
            </button>
          </div>
          {TRANSACTIONS.map(tx => {
            const Icon = tx.icon;
            const isCredit = tx.amount > 0;
            return (
              <div key={tx.id} className="flex items-center gap-4 py-3.5 border-b last:border-0"
                style={{ borderColor: BORDER }}>
                <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
                  style={{ background: isCredit ? "rgba(0,201,167,0.1)" : "rgba(100,116,139,0.1)" }}>
                  <Icon className="w-4 h-4"
                    style={{ color: isCredit ? ACCENT : MUTED }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate" style={{ color:FG }}>{tx.description}</p>
                  <p className="text-xs mt-0.5" style={{ color:MUTED }}>{tx.merchant} · {tx.date}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-semibold"
                    style={{ color: isCredit ? ACCENT : FG }}>
                    {isCredit ? "+" : "-"}AED {Math.abs(tx.amount).toLocaleString()}
                  </p>
                  <span className="text-xs px-1.5 py-0.5 rounded-full"
                    style={{ background: isCredit ? "rgba(0,201,167,0.1)" : "rgba(100,116,139,0.08)", color: isCredit ? ACCENT : MUTED }}>
                    {tx.category}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── How this helps your score */}
        <div className="rounded-xl p-5"
          style={{ background:"rgba(0,201,167,0.04)", border:"1px solid rgba(0,201,167,0.18)" }}>
          <div className="flex items-start gap-3 mb-4">
            <TrendingUp className="w-5 h-5 shrink-0 mt-0.5" style={{ color:ACCENT }} />
            <div>
              <h3 className="text-sm font-semibold" style={{ color:FG }}>How this wallet builds your score</h3>
              <p className="text-xs mt-1 leading-relaxed" style={{ color:MUTED }}>
                Every on-time bill paid through the CreditBridge Wallet is counted as a positive signal
                in the scoring engine. Consistent wallet activity builds a richer payment history —
                faster than waiting for a bank statement.
              </p>
            </div>
          </div>
          <div className="space-y-0">
            {SCORE_SIGNALS.map(sig => (
              <div key={sig.label} className="flex items-center justify-between py-2.5 border-b last:border-0"
                style={{ borderColor:"rgba(0,201,167,0.1)" }}>
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full"
                    style={{ background: sig.done ? ACCENT : BORDER }} />
                  <span className="text-xs" style={{ color:MUTED }}>{sig.label}</span>
                </div>
                <span className="text-xs font-semibold" style={{ color:ACCENT }}>{sig.impact}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </Layout>
  );
}
