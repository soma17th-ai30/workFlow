import { Navigate, Route, Routes } from "react-router-dom";
import GuidePage from "./pages/GuidePage";
import PolishPage from "./pages/PolishPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<GuidePage />} />
      <Route path="/polish" element={<PolishPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
