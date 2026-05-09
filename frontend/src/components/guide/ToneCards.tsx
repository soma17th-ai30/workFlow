const toneCards = [
  {
    badge: "Professional",
    title: "격식 있는 (Formal)",
    body: "비즈니스 메일, 보고서, 공식적인 제안서에 적합합니다. 신뢰감 있는 문장으로 정돈합니다.",
    variant: "wide"
  },
  {
    badge: "Efficient",
    title: "간결하게 (Concise)",
    body: "불필요한 수식어를 제거하고 핵심 메시지만 명확하게 전달합니다.",
    variant: "visual"
  },
  {
    badge: "Friendly",
    title: "다정하게 (Warm)",
    body: "부드러운 어조와 공감을 더해 관계를 해치지 않는 메시지로 바꿉니다.",
    variant: "small"
  },
  {
    badge: "Polite",
    title: "예의 바르게 (Polite)",
    body: "상대의 상황을 배려하면서도 요청 의도를 분명히 드러냅니다.",
    variant: "small"
  },
  {
    badge: "Before / After",
    title: "문장 흐름 비교",
    body: "원문과 결과를 나란히 보며 어떤 표현이 조정됐는지 확인합니다.",
    variant: "compare"
  }
];

export default function ToneCards() {
  return (
    <section className="tone-card-grid" aria-label="톤 매너 예시">
      {toneCards.map((card) => (
        <article className={`tone-card ${card.variant}`} key={card.title}>
          <span className="guide-badge">{card.badge}</span>
          <h2>{card.title}</h2>
          <p>{card.body}</p>
          {card.variant === "wide" && (
            <div className="tone-flow">
              <div>“제가 사정이 생겼는데 조금 늦춰주실 수 있나요?”</div>
              <span>⌄</span>
              <strong>“문맥에 맞게 표현을 정돈하여, 핵심 메시지를 공손하게 제안합니다.”</strong>
            </div>
          )}
          {card.variant === "visual" && <div className="desk-visual" />}
          {card.variant === "compare" && (
            <div className="mini-compare">
              <span>Original</span>
              <p>“나중에 좀 해도 돼요?”</p>
              <strong>Polished</strong>
              <p>“일정을 조금 조정할 수 있을지 여쭙고 싶습니다.”</p>
            </div>
          )}
        </article>
      ))}
    </section>
  );
}
