import './style.css';
import { createRoot } from 'react-dom/client';
import App from './App';

const app = document.querySelector<HTMLDivElement>('#app');

if (app) {
  createRoot(app).render(<App />);
}