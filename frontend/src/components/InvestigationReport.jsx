import { useMemo } from 'react';

import { downloadBlob, downloadComplaintPdf, downloadDossierPdf } from '../lib/api.js';
import { rupees, SEVERITY_BG, SEVERITY_LABEL, shortDate } from '../lib/format.js';
import SubmitToCommunity from './SubmitToCommunity.jsx';
import VerdictCard from './VerdictCard.jsx';

// Walk the trace events, plucking each tool_call/tool_result into a structured
// snapshot the report can render against. Tool *call* args matter as much as
// results — generate_complaint_letter's args carry the verdict numbers.
function extractFindings(events) {
  const findings = {
    priceLookup: null,
    alternatives: null,
    spurious: null,
    enforcement: null,
    community: null,
    complaintLetter: null,
    dossier: null,
    incident: null,         // verdict + submission source of truth
    finalText: null,
  };

  for (const evt of events) {
    if (evt.event === 'tool_call') {
      // generate_complaint_letter args are the structured verdict (charged
      // price + MRP + pharmacy details). We capture them on the call event so
      // the verdict card can render before the result lands.
      if (evt.data?.name === 'generate_complaint_letter') {
        findings.incident = { ...evt.data.args };
      }
    } else if (evt.event === 'tool_result') {
      const { name, result } = evt.data;
      if (name === 'drap_price_lookup' && result?.found) findings.priceLookup = result;
      else if (name === 'generic_alternatives') findings.alternatives = result;
      else if (name === 'spurious_alert_check') findings.spurious = result;
      else if (name === 'drap_enforcement_lookup' && result?.found) findings.enforcement = result;
      else if (name === 'get_pharmacy_reports') findings.community = result;
      else if (name === 'generate_complaint_letter') findings.complaintLetter = result;
      else if (name === 'generate_collective_dossier') findings.dossier = result;
    } else if (evt.event === 'final') {
      findings.finalText = evt.data?.text;
    }
  }

  // If the agent never called generate_complaint_letter (no overcharge), build
  // a green-verdict incident from the price lookup so VerdictCard still renders.
  if (!findings.incident && findings.priceLookup) {
    findings.incident = {
      medicine_name: findings.priceLookup.brand_name,
      strength: findings.priceLookup.strength,
      official_mrp_pkr: findings.priceLookup.mrp_pkr,
      charged_price_pkr: null,  // no overcharge known
    };
  }

  // Compute overcharge if we have both numbers
  if (findings.incident?.charged_price_pkr != null && findings.incident?.official_mrp_pkr) {
    const amt = findings.incident.charged_price_pkr - findings.incident.official_mrp_pkr;
    findings.incident.overcharge_amt_pkr = Math.round(amt * 100) / 100;
    findings.incident.overcharge_pct = Math.round((amt / findings.incident.official_mrp_pkr) * 1000) / 10;
  }

  return findings;
}

export default function InvestigationReport({ events }) {
  const findings = useMemo(() => extractFindings(events), [events]);
  const hasContent =
    findings.priceLookup ||
    findings.alternatives ||
    findings.enforcement ||
    findings.community ||
    findings.finalText;

  if (!hasContent) return null;

  const overcharged =
    findings.incident?.charged_price_pkr != null &&
    findings.incident?.official_mrp_pkr != null &&
    findings.incident.charged_price_pkr > findings.incident.official_mrp_pkr;

  return (
    <div className="space-y-4">
      <VerdictCard incident={findings.incident} />

      {findings.spurious?.alert && <SpuriousWarning data={findings.spurious} />}

      {findings.priceLookup && (
        <PriceCard price={findings.priceLookup} alternatives={findings.alternatives} />
      )}

      {findings.enforcement && <EnforcementCard data={findings.enforcement} />}

      {findings.community && <CommunityCard data={findings.community} />}

      {overcharged && <SubmitToCommunity incident={findings.incident} />}

      {(findings.complaintLetter || findings.dossier) && (
        <DownloadActions complaint={findings.complaintLetter} dossier={findings.dossier} />
      )}

      {findings.finalText && (
        <div className="card whitespace-pre-wrap text-sm leading-relaxed">
          <h3 className="mb-2 text-base">Agent summary</h3>
          {findings.finalText}
        </div>
      )}
    </div>
  );
}

function SpuriousWarning({ data }) {
  return (
    <div className="rounded-md border-2 border-red-500 bg-red-50 p-4">
      <div className="flex items-start gap-3">
        <span className="text-2xl">⚠️</span>
        <div>
          <div className="font-bold text-red-700">URGENT — DRAP COUNTERFEIT/SUBSTANDARD ALERT</div>
          <ul className="mt-2 space-y-1 text-sm text-red-900">
            {data.alerts.map((a, i) => (
              <li key={i}>
                <strong>{a.reason}</strong> · alerted {shortDate(a.alert_date)} · batch {a.batch_number}
                {' · '}
                <a href={a.source_url} className="underline" target="_blank" rel="noreferrer">
                  {a.drap_notice_ref}
                </a>
              </li>
            ))}
          </ul>
          <div className="mt-2 text-xs text-red-800">
            Do not consume. Report to DRAP. Seek a verified alternative.
          </div>
        </div>
      </div>
    </div>
  );
}

function PriceCard({ price, alternatives }) {
  return (
    <div className="card">
      <h3 className="text-base">Price verification</h3>
      <div className="mt-2 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <Stat label="DRAP MRP" value={rupees(price.mrp_pkr)} />
        <Stat label="Brand" value={`${price.brand_name} ${price.strength}`} />
        <Stat label="Manufacturer" value={price.manufacturer} />
        <Stat label="DRAP Reg #" value={price.reg_number} />
      </div>

      {alternatives?.alternatives?.length > 0 && (
        <div className="mt-4">
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Cheaper DRAP-registered alternatives ({price.active_ingredient})
          </h4>
          <table className="mt-2 w-full text-sm">
            <thead className="text-xs text-slate-500">
              <tr>
                <th className="py-1 text-left">Brand</th>
                <th className="py-1 text-left">Manufacturer</th>
                <th className="py-1 text-right">MRP</th>
                <th className="py-1 text-left">DRAP Reg #</th>
              </tr>
            </thead>
            <tbody>
              {alternatives.alternatives.map((a) => (
                <tr key={a.reg_number} className="border-t border-slate-100">
                  <td className="py-2 font-medium">{a.brand_name}</td>
                  <td className="py-2 text-slate-600">{a.manufacturer}</td>
                  <td className="py-2 text-right font-medium">{rupees(a.mrp_pkr)}</td>
                  <td className="py-2 font-mono text-xs text-slate-500">{a.reg_number}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function EnforcementCard({ data }) {
  const { violation_count, summary, violations } = data;
  return (
    <div className="card border-l-4 border-l-orange-500">
      <h3 className="text-base">Pharmacy enforcement history</h3>
      <p className="mt-1 text-xs text-slate-500">
        DRAP records — independently verifiable through the cited notice references.
      </p>

      <div className="mt-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <Stat label="Prior violations" value={violation_count} />
        <Stat label="Total fines" value={rupees(summary.total_fines_pkr)} />
        <Stat label="Earliest" value={shortDate(summary.earliest_violation)} />
        <Stat label="Latest" value={shortDate(summary.latest_violation)} />
      </div>

      <ul className="mt-4 space-y-3">
        {violations.map((v, i) => (
          <li key={i} className="rounded-md bg-slate-50 p-3 text-sm">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-medium">{v.violation_type.replace(/_/g, ' ')}</div>
                <div className="text-xs text-slate-500">{shortDate(v.violation_date)}</div>
              </div>
              <span className={`badge ${SEVERITY_BG[v.severity] || 'bg-slate-200'}`}>
                {SEVERITY_LABEL[v.severity] || v.severity}
              </span>
            </div>
            <div className="mt-1 text-slate-700">{v.description}</div>
            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600">
              {v.penalty_amount_pkr && <span>Fine: <strong>{rupees(v.penalty_amount_pkr)}</strong></span>}
              {v.suspension_days && <span>Suspension: <strong>{v.suspension_days} days</strong></span>}
              {v.penalty_type && !v.penalty_amount_pkr && !v.suspension_days && (
                <span>Penalty: <strong>{v.penalty_type.replace(/_/g, ' ')}</strong></span>
              )}
              <a href={v.source_url} target="_blank" rel="noreferrer" className="text-brand-500 underline">
                {v.drap_notice_ref}
              </a>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function CommunityCard({ data }) {
  const cls = data.classification || 'clean';
  const count = data.report_count ?? 0;
  return (
    <div className="card">
      <h3 className="text-base">Existing community signal (before your submission)</h3>
      <div className="mt-3 flex items-center justify-between">
        <div>
          <div className="text-3xl font-bold text-brand-500">{count}</div>
          <div className="text-xs text-slate-500">reports in last 30 days</div>
        </div>
        <span className={`badge ${SEVERITY_BG[cls]}`}>{SEVERITY_LABEL[cls] || cls}</span>
      </div>
      {cls === 'confirmed' && (
        <div className="mt-3 rounded bg-red-50 p-2 text-xs text-red-700">
          Threshold exceeded — collective dossier eligible for DRAP escalation.
        </div>
      )}
    </div>
  );
}

function DownloadActions({ complaint, dossier }) {
  async function handleComplaint() {
    const blob = await downloadComplaintPdf(complaint);
    downloadBlob(blob, 'pharmawatch-complaint.pdf');
  }
  async function handleDossier() {
    const blob = await downloadDossierPdf(dossier);
    downloadBlob(blob, 'pharmawatch-collective-dossier.pdf');
  }

  return (
    <div className="card flex flex-wrap gap-3">
      {complaint && (
        <button onClick={handleComplaint} className="btn-primary">
          📄 Download complaint letter (PDF)
        </button>
      )}
      {dossier && (
        <button onClick={handleDossier} className="btn-secondary">
          📋 Download collective dossier (PDF)
        </button>
      )}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-0.5 truncate font-semibold text-brand-500">{value}</div>
    </div>
  );
}
