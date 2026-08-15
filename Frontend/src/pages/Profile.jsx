import { useCallback, useState } from "react";
import Navbar from "../components/common/Navbar";
import Sidebar from "../components/common/Sidebar";
import ErrorMessage from "../components/common/ErrorMessage";
import Button from "../components/common/Button";
import { authService } from "../services/authService";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user, setUser } = useAuth();
  const [profileForm, setProfileForm] = useState({ name: user?.name || "", email: user?.email || "" });
  const [passwordForm, setPasswordForm] = useState({ current_password: "", new_password: "", confirm: "" });
  const [profileError, setProfileError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [profileMessage, setProfileMessage] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  const handleProfileSubmit = useCallback(
    async (event) => {
      event.preventDefault();
      setProfileError("");
      setProfileMessage("");
      setSavingProfile(true);
      try {
        const updated = await authService.updateProfile(profileForm);
        setUser(updated);
        setProfileMessage("Profile updated.");
      } catch (err) {
        setProfileError(err.message);
      } finally {
        setSavingProfile(false);
      }
    },
    [profileForm, setUser]
  );

  const handlePasswordSubmit = useCallback(
    async (event) => {
      event.preventDefault();
      setPasswordError("");
      setPasswordMessage("");
      if (passwordForm.new_password.length < 8) {
        setPasswordError("New password must be at least 8 characters.");
        return;
      }
      if (passwordForm.new_password !== passwordForm.confirm) {
        setPasswordError("Passwords do not match.");
        return;
      }
      setSavingPassword(true);
      try {
        await authService.changePassword({
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password,
        });
        setPasswordForm({ current_password: "", new_password: "", confirm: "" });
        setPasswordMessage("Password changed.");
      } catch (err) {
        setPasswordError(err.message);
      } finally {
        setSavingPassword(false);
      }
    },
    [passwordForm]
  );

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar title="Profile" />
        <main className="page">
          <div className="dashboard-grid">
            <div className="card">
              <h3>Profile details</h3>
              <form onSubmit={handleProfileSubmit}>
                <ErrorMessage message={profileError} />
                {profileMessage && <div className="notice success">{profileMessage}</div>}
                <label>
                  Name
                  <input type="text" value={profileForm.name} onChange={(event) => setProfileForm((prev) => ({ ...prev, name: event.target.value }))} required minLength={2} />
                </label>
                <label>
                  Email
                  <input type="email" value={profileForm.email} onChange={(event) => setProfileForm((prev) => ({ ...prev, email: event.target.value }))} required />
                </label>
                <div className="form-actions">
                  <Button type="submit" disabled={savingProfile}>
                    {savingProfile ? "Saving…" : "Save profile"}
                  </Button>
                </div>
              </form>
            </div>
            <div className="card">
              <h3>Change password</h3>
              <form onSubmit={handlePasswordSubmit}>
                <ErrorMessage message={passwordError} />
                {passwordMessage && <div className="notice success">{passwordMessage}</div>}
                <label>
                  Current password
                  <input type="password" value={passwordForm.current_password} onChange={(event) => setPasswordForm((prev) => ({ ...prev, current_password: event.target.value }))} required />
                </label>
                <label>
                  New password (min 8 characters)
                  <input type="password" value={passwordForm.new_password} onChange={(event) => setPasswordForm((prev) => ({ ...prev, new_password: event.target.value }))} required />
                </label>
                <label>
                  Confirm new password
                  <input type="password" value={passwordForm.confirm} onChange={(event) => setPasswordForm((prev) => ({ ...prev, confirm: event.target.value }))} required />
                </label>
                <div className="form-actions">
                  <Button type="submit" disabled={savingPassword}>
                    {savingPassword ? "Changing…" : "Change password"}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
