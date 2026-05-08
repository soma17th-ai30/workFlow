type DebugPanelProps = {
  debugOutput: string;
};

export default function DebugPanel({ debugOutput }: DebugPanelProps) {
  return (
    <div className="debug-panel">
      <div className="debug-title">Debug Output</div>
      <pre>{debugOutput || "분석 결과가 아직 없습니다."}</pre>
    </div>
  );
}
