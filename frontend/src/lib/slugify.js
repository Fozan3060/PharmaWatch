// Tiny ASCII slugifier matching the backend's python-slugify behavior for
// the strings we deal with (city + area names).

export default function slugify(s) {
  return String(s || '')
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-');
}
