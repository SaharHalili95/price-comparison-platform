import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import HomePage from './pages/HomePage';

function App() {
  const [categorySearch, setCategorySearch] = useState<string | null>(null);
  const [showFavorites, setShowFavorites] = useState(false);

  const handleHome = () => {
    setCategorySearch(null);
    setShowFavorites(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCategorySearch = (category: string) => {
    setCategorySearch(category);
    setShowFavorites(false);
  };

  const handleShowFavorites = () => {
    setShowFavorites(true);
    setCategorySearch(null);
  };

  return (
    <Layout
      onHome={handleHome}
      onCategorySearch={handleCategorySearch}
      onShowFavorites={handleShowFavorites}
      favoritesCount={0}
    >
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <HomePage
              onCategorySearch={categorySearch}
              showFavoritesView={showFavorites}
              onResetFavoritesView={() => setShowFavorites(false)}
            />
          }
        />
      </Routes>
    </Layout>
  );
}

export default App;
