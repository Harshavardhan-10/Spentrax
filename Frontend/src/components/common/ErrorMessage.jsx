export default function ErrorMessage({ message }) {
  if (!message) return null;
  return (
    <div className="error-state" role="alert">
      <p>{message}</p>
    </div>
  );
}
