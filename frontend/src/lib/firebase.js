// Firebase Web SDK init. Live heatmap uses onSnapshot to push real-time
// updates from the community_reports collection.

import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

let _app = null;
let _db = null;

export function isFirebaseConfigured() {
  return Boolean(config.apiKey && config.projectId);
}

export function getDb() {
  if (!isFirebaseConfigured()) return null;
  if (_db) return _db;
  _app = initializeApp(config);
  _db = getFirestore(_app);
  return _db;
}
