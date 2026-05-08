export const purposeOptions = ["요청", "사과", "거절", "피드백", "리마인드", "고객 응대", "감사"];

export const relationshipOptions = ["교수님", "상사", "동료", "고객", "친구", "연인", "기타"];

export const channelOptions = ["카카오톡", "문자", "이메일", "Slack", "DM"];

export const toneOptions = ["정중하게", "부드럽게", "간결하게", "전문적으로", "친근하게", "단호하지만 무례하지 않게"];

export const exampleMessage = "교수님 제가 일이 있어서 과제 제출 좀 늦게 해도 될까요?";

export const scenarioExamples = [
  {
    label: "교수님께 요청",
    purpose: "요청",
    relationship: "교수님",
    channel: "이메일",
    tone: "정중하게",
    message: "교수님 제가 일이 있어서 과제 제출 좀 늦게 해도 될까요?"
  },
  {
    label: "팀원에게 피드백",
    purpose: "피드백",
    relationship: "동료",
    channel: "Slack",
    tone: "부드럽게",
    message: "이거 방향이 좀 안 맞는 것 같아요. 다시 해주세요."
  },
  {
    label: "고객 불만 응대",
    purpose: "고객 응대",
    relationship: "고객",
    channel: "문자",
    tone: "전문적으로",
    message: "배송이 늦어서 죄송합니다. 조금만 더 기다려주세요."
  },
  {
    label: "친구 약속 거절",
    purpose: "거절",
    relationship: "친구",
    channel: "카카오톡",
    tone: "친근하게",
    message: "오늘은 못 가. 좀 피곤해."
  }
];
