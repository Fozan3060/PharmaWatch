import { useEffect, useRef, useState } from 'react';

// Lightweight autocomplete combobox. Debounces input, calls fetchOptions, shows
// a dropdown with renderOption, calls onSelect with the chosen option object.
// Free-text typing without a selection is allowed — the parent decides what to
// do with raw `inputValue` when there's no selected option.

export default function Combobox({
  inputValue,
  onInputChange,
  selected,
  onSelect,
  fetchOptions,
  getOptionKey,
  getOptionLabel,
  renderOption,
  placeholder,
  disabled = false,
  emptyHint = null,
  id,
  className = '',
}) {
  const [options, setOptions] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const blurTimer = useRef(null);

  useEffect(() => {
    const q = (inputValue || '').trim();
    if (!q) {
      setOptions([]);
      return undefined;
    }
    let cancelled = false;
    const t = setTimeout(async () => {
      setLoading(true);
      try {
        const opts = await fetchOptions(q);
        if (!cancelled) setOptions(opts);
      } catch {
        if (!cancelled) setOptions([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [inputValue, fetchOptions]);

  function handleSelect(opt) {
    onSelect(opt);
    onInputChange(getOptionLabel(opt));
    setOpen(false);
  }

  function handleInputChange(e) {
    onInputChange(e.target.value);
    if (selected) onSelect(null);
    setOpen(true);
  }

  function handleFocus() {
    if (blurTimer.current) clearTimeout(blurTimer.current);
    setOpen(true);
  }

  function handleBlur() {
    blurTimer.current = setTimeout(() => setOpen(false), 150);
  }

  const showDropdown = open && (loading || options.length > 0 || emptyHint);

  return (
    <div className={`relative ${className}`}>
      <input
        type="text"
        id={id}
        value={inputValue}
        onChange={handleInputChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder={placeholder}
        disabled={disabled}
        autoComplete="off"
        className="block w-full rounded-md border border-slate-300 p-2.5 text-sm shadow-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 disabled:bg-slate-100"
      />
      {showDropdown && (
        <ul className="absolute z-20 mt-1 max-h-64 w-full overflow-auto rounded-md border border-slate-200 bg-white py-1 text-sm shadow-lg">
          {loading && <li className="px-3 py-2 text-slate-400">Loading…</li>}
          {!loading && options.length === 0 && emptyHint && (
            <li className="px-3 py-2 text-slate-500">{emptyHint}</li>
          )}
          {options.map((opt) => (
            <li
              key={getOptionKey(opt)}
              onMouseDown={(e) => {
                e.preventDefault();
                handleSelect(opt);
              }}
              className="cursor-pointer px-3 py-2 hover:bg-slate-100"
            >
              {renderOption(opt)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
