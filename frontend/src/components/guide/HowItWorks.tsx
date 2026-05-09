const steps = [
  ["문맥 분석 (Contextual Analysis)", "작성자의 의도와 상대, 상황을 분석해 문장의 기준점을 찾습니다."],
  ["톤 매핑 (Tone Mapping)", "선택한 톤에 맞는 어휘와 문장 리듬을 적용합니다."],
  ["최종 정제 (Refinement)", "자연스러운 흐름과 핵심 전달력을 마지막으로 조정합니다."]
];

export default function HowItWorks() {
  return (
    <section className="how-it-works">
      <h2>How It Works</h2>
      <ol>
        {steps.map(([title, body], index) => (
          <li key={title}>
            <span>{index + 1}</span>
            <div>
              <strong>{title}</strong>
              <p>{body}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
