import ComparisonTable from "../components/guide/ComparisonTable";
import GuideHero from "../components/guide/GuideHero";
import HowItWorks from "../components/guide/HowItWorks";
import ToneCards from "../components/guide/ToneCards";
import GuideSidebar from "../components/layout/GuideSidebar";
import SiteHeader from "../components/layout/SiteHeader";

export default function GuidePage() {
  return (
    <div className="guide-page">
      <SiteHeader />
      <div className="guide-layout">
        <main className="guide-content">
          <GuideHero />
          <ToneCards />
          <HowItWorks />
          <ComparisonTable />
        </main>
      </div>
    </div>
  );
}
