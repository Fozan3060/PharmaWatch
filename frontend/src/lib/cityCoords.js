// Approximate lat/lng for the pharmacy areas seeded in the demo + city
// fallbacks. Used by the heatmap component to plot pharmacy markers.
//
// For production, Phase 2 should geocode area+city via Google Maps Geocoding
// API and persist coordinates on report write.

import slugify from './slugify.js';

const AREAS = {
  'karachi:saddar': { lat: 24.8607, lng: 67.0011 },
  'karachi:gulshan-e-iqbal': { lat: 24.9197, lng: 67.0989 },
  'karachi:dha': { lat: 24.8023, lng: 67.0457 },
  'karachi:dha-phase-5': { lat: 24.8023, lng: 67.0457 },
  'lahore:liberty-market': { lat: 31.5204, lng: 74.3587 },
  'lahore:dha-phase-5': { lat: 31.4697, lng: 74.408 },
  'islamabad:f-7-markaz': { lat: 33.7117, lng: 73.0533 },
  'rawalpindi:saddar': { lat: 33.5973, lng: 73.0479 },
  'peshawar:university-town': { lat: 34.0123, lng: 71.4825 },
};

const CITIES = {
  karachi: { lat: 24.8607, lng: 67.0011 },
  lahore: { lat: 31.5204, lng: 74.3587 },
  islamabad: { lat: 33.6844, lng: 73.0479 },
  rawalpindi: { lat: 33.5973, lng: 73.0479 },
  peshawar: { lat: 34.015, lng: 71.5805 },
  faisalabad: { lat: 31.4504, lng: 73.135 },
  multan: { lat: 30.1575, lng: 71.5249 },
  quetta: { lat: 30.1798, lng: 66.975 },
};

export const PAKISTAN_CENTER = { lat: 30.3753, lng: 69.3451 };

export function coordsFor(city, area) {
  if (!city) return PAKISTAN_CENTER;
  const cityKey = slugify(city);
  if (area) {
    const key = `${cityKey}:${slugify(area)}`;
    if (AREAS[key]) return AREAS[key];
  }
  return CITIES[cityKey] || PAKISTAN_CENTER;
}
