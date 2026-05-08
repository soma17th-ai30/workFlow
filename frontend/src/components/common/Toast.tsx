type ToastProps = {
  message: string;
  variant?: "success" | "error";
};

export default function Toast({ message, variant = "success" }: ToastProps) {
  if (!message) {
    return null;
  }

  return (
    <div className={`toast ${variant}`} role="status" aria-live="polite">
      <span aria-hidden="true">{variant === "success" ? "✓" : "!"}</span>
      {message}
    </div>
  );
}
