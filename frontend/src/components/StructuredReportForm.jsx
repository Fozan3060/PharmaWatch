import { useCallback, useEffect, useMemo, useState } from 'react';

import { searchMedicines, searchPharmacies } from '../lib/api.js';
import { PAKISTANI_CITIES } from '../lib/cities.js';
import { rupees } from '../lib/format.js';
import Combobox from './Combobox.jsx';

const TODAY = new Date().toISOString().slice(0, 10);

// Demo presets — clicking pre-fills the form with a known-good case.
const DEMO_MEDICINE = {
  reg_number: 'DRAP-001-CEF',
  brand_name: 'Ceftum',
  generic_name: 'Cefuroxime',
  active_ingredient: 'Cefuroxime',
  strength: '500mg',
  manufacturer: 'GlaxoSmithKline Pakistan',
  mrp_pkr: 640,
};

export default function StructuredReportForm({ onSubmit, disabled }) {
  const [medicine, setMedicine] = useState(null);
  const [medicineInput, setMedicineInput] = useState('');
  const [chargedPrice, setChargedPrice] = useState('');
  const [pharmacy, setPharmacy] = useState(null);
  const [pharmacyInput, setPharmacyInput] = useState('');
  const [city, setCity] = useState('');
  const [area, setArea] = useState('');
  const [date, setDate] = useState(TODAY);

  // When the user picks a pharmacy from autocomplete, auto-fill area + city
  // from the matched DRAP enforcement record (they can still override).
  useEffect(() => {
    if (pharmacy) {
      if (pharmacy.area) setArea(pharmacy.area);
      if (pharmacy.city) setCity(pharmacy.city);
    }
  }, [pharmacy]);

  const fetchMedicines = useCallback((q) => searchMedicines(q, 10), []);
  const fetchPharmacies = useCallback(
    (q) => searchPharmacies(q, city || undefined, 10),
    [city],
  );

  const chargedPriceNum = Number(chargedPrice);
  const livePreview = useMemo(() => {
    if (!medicine || !chargedPriceNum) return null;
    if (chargedPriceNum > medicine.mrp_pkr) {
      const amt = chargedPriceNum - medicine.mrp_pkr;
      return {
        kind: 'over',
        amt,
        pct: (amt / medicine.mrp_pkr) * 100,
      };
    }
    return { kind: 'within' };
  }, [medicine, chargedPriceNum]);

  const pharmacyName = pharmacy?.pharmacy_name || pharmacyInput.trim();
  const isPharmacyKnown = Boolean(pharmacy);
  const isPharmacyTypedButUnknown = !pharmacy && pharmacyInput.trim().length >= 3;

  const canSubmit =
    !disabled &&
    medicine &&
    chargedPriceNum > 0 &&
    pharmacyName.length >= 2 &&
    city &&
    date;

  function handleSubmit(e) {
    e.preventDefault();
    if (!canSubmit) return;
    onSubmit(buildAgentInput({
      medicine, chargedPrice: chargedPriceNum, pharmacyName, area, city, date,
    }));
  }

  function loadDemo() {
    setMedicine(DEMO_MEDICINE);
    setMedicineInput(`${DEMO_MEDICINE.brand_name} ${DEMO_MEDICINE.strength}`);
    setChargedPrice('1200');
    setPharmacy(null);
    setPharmacyInput('City Pharmacy');
    setArea('Saddar');
    setCity('Karachi');
    setDate(TODAY);
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-4">
      <div>
        <h3 className="text-base">Tell us what happened</h3>
        <p className="mt-1 text-xs text-slate-500">
          The medicine and pharmacy must be valid; the agent verifies everything against
          DRAP&rsquo;s public records before drafting your complaint. Anonymous by design.
        </p>
      </div>

      {/* Row 1: Medicine + price */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-[2fr_1fr]">
        <Field label="Medicine" hint="Pick from DRAP-registered medicines.">
          <Combobox
            id="medicine"
            inputValue={medicineInput}
            onInputChange={setMedicineInput}
            selected={medicine}
            onSelect={setMedicine}
            fetchOptions={fetchMedicines}
            getOptionKey={(m) => m.reg_number}
            getOptionLabel={(m) => `${m.brand_name} ${m.strength}`}
            renderOption={(m) => (
              <div className="flex justify-between">
                <span>
                  <span className="font-medium">{m.brand_name}</span>{' '}
                  <span className="text-slate-500">{m.strength}</span>
                  <span className="ml-2 text-xs text-slate-400">{m.manufacturer}</span>
                </span>
                <span className="text-xs font-medium text-brand-500">
                  MRP {rupees(m.mrp_pkr)}
                </span>
              </div>
            )}
            placeholder="Start typing — e.g. Ceftum"
            disabled={disabled}
            emptyHint={medicineInput ? 'No DRAP-registered match' : null}
          />
          {medicine && (
            <div className="mt-1 text-xs text-slate-600">
              ✓ DRAP MRP <strong>{rupees(medicine.mrp_pkr)}</strong> · Active ingredient:{' '}
              {medicine.active_ingredient} · Reg #{medicine.reg_number}
            </div>
          )}
        </Field>

        <Field label="Price you were charged (Rs.)" hint="Numeric only.">
          <input
            type="number"
            min="1"
            step="1"
            value={chargedPrice}
            onChange={(e) => setChargedPrice(e.target.value)}
            disabled={disabled}
            placeholder="1200"
            className="block w-full rounded-md border border-slate-300 p-2.5 text-sm shadow-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:bg-slate-100"
          />
        </Field>
      </div>

      {/* Live preview (verdict before submitting) */}
      {livePreview?.kind === 'over' && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          🚨 This is <strong>{rupees(livePreview.amt)}</strong> ({livePreview.pct.toFixed(1)}%)
          above the DRAP-registered MRP. The agent will dig deeper when you submit.
        </div>
      )}
      {livePreview?.kind === 'within' && (
        <div className="rounded-md border border-green-300 bg-green-50 p-3 text-sm text-green-700">
          ✅ This price is at or below the DRAP MRP. You can still submit to verify spurious
          alerts and surface alternatives.
        </div>
      )}

      {/* Row 2: Pharmacy + city */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-[2fr_1fr]">
        <Field
          label="Pharmacy name"
          hint="Type the name. We'll suggest matches from DRAP enforcement records."
        >
          <Combobox
            id="pharmacy"
            inputValue={pharmacyInput}
            onInputChange={setPharmacyInput}
            selected={pharmacy}
            onSelect={setPharmacy}
            fetchOptions={fetchPharmacies}
            getOptionKey={(p) => `${p.pharmacy_name}-${p.area}-${p.city}`}
            getOptionLabel={(p) => p.pharmacy_name}
            renderOption={(p) => (
              <div className="flex justify-between">
                <span>
                  <span className="font-medium">{p.pharmacy_name}</span>
                  <span className="ml-2 text-xs text-slate-500">
                    {p.area ? `${p.area}, ` : ''}{p.city}
                  </span>
                </span>
                {p.violation_count > 0 ? (
                  <span className="text-xs font-medium text-orange-600">
                    {p.violation_count} prior DRAP violation
                    {p.violation_count === 1 ? '' : 's'}
                  </span>
                ) : (
                  <span className="text-xs text-slate-500">Known chain</span>
                )}
              </div>
            )}
            placeholder="e.g. City Pharmacy"
            disabled={disabled}
            emptyHint={
              pharmacyInput.trim().length >= 1
                ? 'No prior DRAP enforcement on file — ok to proceed if spelling is correct'
                : null
            }
          />
          {isPharmacyKnown && pharmacy.violation_count > 0 && (
            <div className="mt-1 text-xs text-orange-700">
              ⚠ This pharmacy has <strong>{pharmacy.violation_count}</strong> prior DRAP
              enforcement action{pharmacy.violation_count === 1 ? '' : 's'} on file.
            </div>
          )}
          {isPharmacyKnown && pharmacy.violation_count === 0 && (
            <div className="mt-1 text-xs text-green-700">
              ✓ Recognised pharmacy chain — no DRAP enforcement on file.
            </div>
          )}
          {isPharmacyTypedButUnknown && (
            <div className="mt-1 text-xs text-slate-500">
              ℹ First time we&rsquo;ve seen this pharmacy. Double-check the spelling — your
              report will be public on the heatmap.
            </div>
          )}
        </Field>

        <Field label="City">
          <select
            value={city}
            onChange={(e) => setCity(e.target.value)}
            disabled={disabled}
            className="block w-full rounded-md border border-slate-300 p-2.5 text-sm shadow-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:bg-slate-100"
          >
            <option value="">— Select —</option>
            {PAKISTANI_CITIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </Field>
      </div>

      {/* Row 3: Area + date */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-[2fr_1fr]">
        <Field label="Area / neighbourhood (optional)">
          <input
            type="text"
            value={area}
            onChange={(e) => setArea(e.target.value)}
            disabled={disabled}
            placeholder="e.g. Saddar, DHA Phase 5, F-7 Markaz"
            className="block w-full rounded-md border border-slate-300 p-2.5 text-sm shadow-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:bg-slate-100"
          />
        </Field>

        <Field label="Incident date">
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            max={TODAY}
            disabled={disabled}
            className="block w-full rounded-md border border-slate-300 p-2.5 text-sm shadow-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:bg-slate-100"
          />
        </Field>
      </div>

      <div className="flex items-center justify-between border-t border-slate-100 pt-3">
        <button
          type="button"
          onClick={loadDemo}
          disabled={disabled}
          className="text-xs text-brand-500 hover:underline disabled:no-underline"
        >
          Use the demo example
        </button>
        <button type="submit" disabled={!canSubmit} className="btn-primary">
          {disabled ? 'Investigating…' : 'Investigate'}
        </button>
      </div>
    </form>
  );
}

function Field({ label, hint, children }) {
  return (
    <label className="block">
      <span className="block text-sm font-medium text-slate-800">{label}</span>
      {hint && <span className="mt-0.5 block text-xs text-slate-500">{hint}</span>}
      <div className="mt-1.5">{children}</div>
    </label>
  );
}

function buildAgentInput({ medicine, chargedPrice, pharmacyName, area, city, date }) {
  const areaPart = area ? `, ${area}` : '';
  return (
    `I was charged Rs. ${chargedPrice} for ${medicine.brand_name} ${medicine.strength} ` +
    `(DRAP registration ${medicine.reg_number}, official MRP Rs. ${medicine.mrp_pkr}) ` +
    `at ${pharmacyName}${areaPart}, ${city} on ${date}.`
  );
}
