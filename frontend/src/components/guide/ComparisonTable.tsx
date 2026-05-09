const rows = [
  ["“회의 늦을 것 같아요.”", "격식", "“부득이한 사정으로 회의 참석이 다소 늦어질 예정입니다. 양해 부탁드립니다.”"],
  ["“회의 좀 미뤄도 돼?”", "공손", "“회의 일정을 여유롭게 조정할 수 있을지 여쭙습니다.”"],
  ["“죄송해요, 회의에 조금 늦을 것 같아요!”", "다정", "“죄송해요. 회의에 조금 늦을 것 같아 미리 말씀드립니다.”"]
];

export default function ComparisonTable() {
  return (
    <section className="comparison-section">
      <h2>한 눈에 비교하기</h2>
      <p>동일한 문장이 톤에 따라 어떻게 바뀌는지 확인하세요.</p>
      <table>
        <thead>
          <tr>
            <th>기본 문장 (Original)</th>
            <th>선택 톤</th>
            <th>교정 결과 (Polished)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([original, tone, polished]) => (
            <tr key={`${original}-${tone}`}>
              <td>{original}</td>
              <td>
                <span>{tone}</span>
              </td>
              <td>{polished}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
