import { Route, Routes } from 'react-router-dom';

import Layout from './components/Layout.jsx';
import HomePage from './pages/HomePage.jsx';
import InvestigatePage from './pages/InvestigatePage.jsx';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/investigate" element={<InvestigatePage />} />
      </Routes>
    </Layout>
  );
}
